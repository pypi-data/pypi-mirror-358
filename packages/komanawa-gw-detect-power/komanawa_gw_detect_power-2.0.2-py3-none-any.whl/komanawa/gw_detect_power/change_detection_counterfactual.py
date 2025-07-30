"""
created matt_dumont 
on: 25/01/24
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import warnings
import logging
from komanawa.gw_detect_power.base_detection_calculator import BaseDetectionCalculator


class DetectionPowerCounterFactual(BaseDetectionCalculator):
    """
    This class is used to calculate the counterfactual detection power of a pair of concentration time series The user specifies the true concentration time series for the base and alt scenarios and the noise level for both scenarios.  The power is calculated by adding many noise realisations to the true concentration time series and running a paired t test or wilcoxon signed rank test to determine if the null hypothesis (The scenarios are the same) can be rejected.

    The Power is calculated as the percentage (0-100) of simulations which reject the null hypothesis.

    :param significance_mode: str, one of:

                                * 'paired-t-test': paired t test (parametric), scipy.stats.ttest_rel
                                * 'wilcoxon-signed-rank-test': wilcoxon signed rank test (non-parametric), scipy.stats.wilcoxon

    :param nsims: number of noise simulations to run for each change detection (e.g. nsims=1000, power= number of detected changes/1000 noise simulations)
    :param p_value: minimum p value (see also alternative), if:

                      * p >= p_value the null hypothesis will not be rejected (base and alt are the same)
                      * p < p_value the null hypothesis will be rejected (base and alt are different)

    :param min_samples: minimum number of samples required, less than this number of samples will raise an exception
    :param alternative: str, one of:

                            * 'alt!=base': two sided test (default),
                            * 'alt<base': one sided test ~
                            * 'alt>base'

    :param wx_zero_method: str, one of:

                               * “wilcox”: Discards all zero-differences (default); see [4].
                               * “pratt”: Includes zero-differences in the ranking process, but drops the ranks of the zeros (more conservative); see [3]. In this case, the normal approximation is adjusted as in [5].
                               * “zsplit”: Includes zero-differences in the ranking process and splits the zero rank between positive and negative ones.

                            for more info see: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html

    :param wx_correction: bool, If True, apply continuity correction by adjusting the Wilcoxon rank statistic by 0.5 towards the mean value when computing the z-statistic. Default is False.
    :param wx_method: str, see scipy.stats.wilcoxon for more info
    :param ncores: number of cores to use for multiprocessing, None will use all available cores
    :param log_level: logging level for multiprocessing subprocesses
    :param return_true_conc: return the true concentration time series for each simulation with power calcs (not supported with multiprocessing power calcs)
    :param return_noisy_conc_itters: int <= nsims, default = 0 Number of noisy simulations to return if 0 then no noisy simulations are returned, not supported with multiprocessing power calcs
    :param only_significant_noisy: bool if True then only return noisy simulations where a change was detected if there are fewer noisy simulations with changes detected than return_noisy_conc_itters all significant simulations will be returned. if there are no noisy simulations with changes detected then and empty dataframe is returned
    """

    implemented_mrt_models = ()
    implemented_significance_modes = (
        'paired-t-test',
        'wilcoxon-signed-rank-test',
    )
    _counterfactual = True
    _poss_alternatives = ('alt!=base', 'alt<base', 'alt>base')
    _scipy_alternatives = ('two-sided', 'less', 'greater')

    def __init__(self,
                 significance_mode,
                 nsims=1000,
                 p_value=0.05,
                 min_samples=10,
                 alternative='alt!=base',
                 wx_zero_method='wilcox', wx_correction=False, wx_method='auto',
                 ncores=None,
                 log_level=logging.INFO,
                 return_true_conc=False,
                 return_noisy_conc_itters=0,
                 only_significant_noisy=False,
                 ):

        assert significance_mode in self.implemented_significance_modes, (f'significance_mode {significance_mode} not '
                                                                          f'implemented, must be one of '
                                                                          f'{self.implemented_significance_modes}')
        assert isinstance(only_significant_noisy, bool), 'only_significant_noisy must be a boolean'
        self.only_significant_noisy = only_significant_noisy
        assert isinstance(return_true_conc, bool), 'return_true_conc must be a boolean'
        self.return_true_conc = return_true_conc
        assert isinstance(return_noisy_conc_itters, int), 'return_noisy_conc_itters must be an integer'
        assert return_noisy_conc_itters <= nsims, 'return_noisy_conc_itters must be <= nsims'
        assert return_noisy_conc_itters >= 0, 'return_noisy_conc_itters must be >= 0'
        self.return_noisy_conc_itters = return_noisy_conc_itters

        assert alternative in self._poss_alternatives, (f'alternative {alternative} not implemented, must be one of '
                                                        f'{self._poss_alternatives}')
        alt_dict = dict(zip(self._poss_alternatives, self._scipy_alternatives))
        self.alternative = alt_dict[alternative]
        assert isinstance(wx_zero_method, str), 'wx_zero_method must be a string'
        assert wx_zero_method in ['wilcox', 'pratt', 'zsplit'], 'wx_zero_method must be one of "wilcox", "pratt", ' \
                                                                '"zsplit"'
        self.wx_zero_method = wx_zero_method
        assert isinstance(wx_correction, bool), 'wx_correction must be a boolean'
        self.wx_correction = wx_correction
        assert isinstance(wx_method, str), 'wx_method must be a string'
        assert wx_method in ['auto', 'asymptotic', 'exact'], 'wx_method must be one of "auto", "asymptotic", "exact"'
        self.wx_method = wx_method

        if significance_mode == 'paired-t-test':
            self._power_test = self._power_test_paired_t
        elif significance_mode == 'wilcoxon-signed-rank-test':
            self._power_test = self._power_test_wilcoxon
        else:
            raise NotImplementedError(f'significance_mode {significance_mode} not implemented, must be one of '
                                      f'{self.implemented_significance_modes}')

        assert isinstance(nsims, int), 'nsims must be an integer'
        self.nsims = nsims
        assert isinstance(min_samples, int), 'min_samples must be an integer'
        self.min_samples = min_samples
        self.min_p_value = p_value
        assert self.min_p_value > 0 and self.min_p_value < 1, 'min_p_value must be between 0 and 1'
        assert isinstance(ncores, int) or ncores is None, 'ncores must be an integer or None'
        self.ncores = ncores
        assert log_level in [logging.CRITICAL, logging.FATAL, logging.ERROR, logging.WARNING, logging.WARN,
                             logging.INFO, logging.DEBUG], f'unknown log_level {log_level}'
        self.log_level = log_level
        self.significance_mode = significance_mode

    def plot_iteration(self, y0_base, y0_alt, true_conc_base, true_conc_alt, ax=None):
        """
        plot the concentration data itteration and the true concentration data

        :param y0_base: noisy concentration data for the base scenario
        :param y0_alt: noisy concentration data for the alt scenario
        :param true_conc_base: True concentration data for the base scenario
        :param true_conc_alt: True concentration data for the alt scenario
        :param ax: matplotlib axis to plot to, if None then a new figure and axis will be created
        :return:
        """

        import matplotlib.pyplot as plt
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        else:
            fig = ax.figure
        power, plist, pvals = self._power_test(np.array([y0_base]), np.array([y0_alt]), return_p=True)
        for key, c in zip(['base', 'alt'], ['b', 'r']):
            y0 = eval('y0_' + key)
            true_conc = eval('true_conc_' + key)
            ax.scatter(np.arange(len(y0)), y0, c=c, label=f'{key}: noisy data')
            ax.plot(np.arange(len(true_conc)), true_conc, c=c, label=f'{key}: True data', marker='.')
            ax.axhline(np.median(true_conc), c=c, ls=':', alpha=0.5, label=f'{key}: True median')
        ax.legend(title='pvalue: {:.2f}'.format(pvals.mean()))
        ax.set_xlabel('time')
        ax.set_ylabel('concentration')
        return fig, ax

    def _power_test_paired_t(self, base_with_noise, alt_with_noise, return_p=False):
        assert base_with_noise.shape == alt_with_noise.shape, ('base_with_noise and alt_with_noise must have the same '
                                                               'shape')
        outdata = stats.ttest_rel(alt_with_noise, base_with_noise, axis=1, alternative=self.alternative)
        p_list = outdata.pvalue < self.min_p_value
        power = p_list.mean() * 100
        if return_p:
            return power, p_list, outdata.pvalue
        return power, p_list

    def _power_test_wilcoxon(self, base_with_noise, alt_with_noise, return_p=False):
        assert base_with_noise.shape == alt_with_noise.shape, ('base_with_noise and alt_with_noise must have the same '
                                                               'shape')
        outdata = stats.wilcoxon(alt_with_noise, base_with_noise, axis=1, alternative=self.alternative,
                                 zero_method=self.wx_zero_method, correction=self.wx_correction,
                                 method=self.wx_method)
        assert hasattr(outdata, 'pvalue'), 'scipy changed'
        p_list = outdata.pvalue < self.min_p_value
        power = p_list.mean() * 100
        if return_p:
            return power, p_list, outdata.pvalue
        return power, p_list

    def _run_power_calc(self, idv, testnitter, seed_base, seed_alt, true_conc_base, true_conc_alt, error_base,
                        error_alt, **kwargs):
        if testnitter is not None:
            warnings.warn('testnitter is expected to be None unless you are testing run times')

        if seed_alt is None:
            seed_alt = np.random.randint(21, 54762438)
        if seed_base is None:
            seed_base = np.random.randint(21, 54762438)

        if seed_base == seed_alt:
            raise ValueError('seed_base and seed_alt must be different otherwise the same noise will be added to both '
                             'concentration time series and the effective noise will be zero')

        nsamples = len(true_conc_base)
        assert nsamples == len(true_conc_alt), 'true_conc_base and true_conc_alt must be the same length'
        assert np.isfinite(true_conc_base).all(), 'true_conc_base must not contain any NaN or inf values'
        assert np.isfinite(true_conc_alt).all(), 'true_conc_alt must not contain any NaN or inf values'

        if nsamples < self.min_samples:
            raise ValueError(f'nsamples must be greater than {self.min_samples}, you can change the '
                             f'minimum number of samples in the DetectionPowerCalculator class init')

        assert pd.api.types.is_number(error_base), 'error_base must be a float'
        if error_alt is None:
            error_alt = error_base
        assert pd.api.types.is_number(error_alt), 'error_alt must be a float or None (same error as error_base)'

        # tile to nsims
        if testnitter is not None:
            rand_shape = (testnitter, nsamples)
        else:
            rand_shape = (self.nsims, nsamples)

        base_with_noise = np.tile(true_conc_base, rand_shape[0]).reshape(rand_shape).astype(float)
        alt_with_noise = np.tile(true_conc_alt, rand_shape[0]).reshape(rand_shape).astype(float)

        # generate noise
        np.random.seed(seed_base)
        base_noise = np.random.normal(0, error_base, rand_shape)
        np.random.seed(seed_alt)
        alt_noise = np.random.normal(0, error_alt, rand_shape)

        # add noise
        base_with_noise += base_noise
        alt_with_noise += alt_noise

        # run test
        power, significant = self._power_test(base_with_noise, alt_with_noise)

        out = pd.Series({'idv': idv,
                         'power': power,
                         'error_base': error_base,
                         'error_alt': error_alt,
                         'seed_base': seed_base,
                         'seed_alt': seed_alt,
                         'python_error': None})
        for k, v in kwargs.items():
            out[k] = v

        out_data = {}
        out_data['power'] = out
        if self.return_true_conc:
            out_data['true_conc'] = pd.DataFrame(data=dict(true_conc_base=true_conc_base, true_conc_alt=true_conc_alt))

        if self.return_noisy_conc_itters > 0:
            if self.only_significant_noisy:
                base_with_noise = base_with_noise[significant]
                alt_with_noise = alt_with_noise[significant]
                significant = significant[significant]
            outn = min(self.return_noisy_conc_itters, base_with_noise.shape[0])
            out_data['base_noisy_conc'] = pd.DataFrame(data=base_with_noise[:outn].T,
                                                       columns=np.arange(outn))
            out_data['alt_noisy_conc'] = pd.DataFrame(data=alt_with_noise[:outn].T,
                                                      columns=np.arange(outn))
            out_data['significant'] = significant[:outn]
        if len(out_data) == 1:
            out_data = out_data['power']
        return out_data

    def power_calc(self, idv, error_base: float,
                   true_conc_base: np.ndarray,
                   true_conc_alt: np.ndarray,
                   error_alt: {float, None} = None,
                   seed_base: {int, None} = None,
                   seed_alt: {int, None} = None,
                   testnitter=None,
                   **kwargs
                   ):

        """
        calculate the counterfactual detection power of a pair of concentration time series note the power is calculated using the sampling frequency of the true_conc_base/alt, if you want to test the power at a different sampling frequency then you should resample the true_conc_base/alt before passing it to this function

        :param idv: identifiers for the power calc sites, passed straight through to the output
        :param error_base: standard deviation of the noise to add to the base concentration time series
        :param true_conc_base: the true concentration timeseries for the base scenario
        :param true_conc_alt: the true concentration timeseries for the alt scenario
        :param error_alt: standard deviation of the noise to add to the alt concentration time series, if None then error_alt = error_base
        :param seed_base: seed for the random number generator for the base scenario, if None then a random seed will be generated and returned with the output
        :param seed_alt: seed for the random number generator for the alt scenario, if None then a random seed will be generated and returned with the output
        :param testnitter: None (usually) or a different nitter then self.niter for testing run times
        :param kwargs: any other kwargs to pass directly to the output Series
        :return: pd.Series with the power calc results note power is percent 0-100

        Possible other dataframes if self.return_true_conc is True or self.return_noisy_conc_itters > 0 in which case a dictionary will be returned:
        {'power': power_df, # always
        'true_conc': true_conc_ts, if self.return_true_conc is True
        'noisy_conc' : noisy_conc_ts, if self.return_noisy_conc_itters > 0
        }
        """
        outdata = self._run_power_calc(
            idv=idv,
            testnitter=testnitter,
            seed_base=seed_base,
            seed_alt=seed_alt,
            true_conc_base=true_conc_base,
            true_conc_alt=true_conc_alt,
            error_base=error_base,
            error_alt=error_alt,
            **kwargs
        )
        return outdata

    def mulitprocess_power_calcs(
            self,
            outpath: {Path, None, str},
            idv_vals: np.ndarray,
            true_conc_base_vals: {np.ndarray, list},
            true_conc_alt_vals: {np.ndarray, list},
            error_base_vals: {np.ndarray, None, float},
            error_alt_vals: {np.ndarray, None, float} = None,
            seed_alt_vals_vals: {np.ndarray, int, None} = None,
            seed_base_vals_vals: {np.ndarray, int, None} = None,
            run=True, debug_mode=False,
            **kwargs
    ):
        """
        multiprocessing wrapper for power_calc, see power_calc for details note that if a given run raises and exception the traceback for the exception will be included in the returned dataset under the column 'python_error' if 'python_error' is None then the run was successful to change the number of cores used pass n_cores to the constructor init

        :param outpath: path to save results to or None (no save)
        :param idv_vals: id values for each simulation

        All values from here on out should be either a single value or an array of values with the same shape as id_vals

        :param true_conc_base_vals: time series concentration dta for the 'base' scenario.  Note sampling frequency is assumed to be correct.
        :param true_conc_alt_vals: time series concentration dta for the 'alt' scenario.  Note sampling frequency is assumed to be correct.
        :param error_base_vals: standard deviation of noise to add to the base time series for each simulation
        :param error_alt_vals: standard deviation of noise to add to the alt time series for each simulation
        :param seed_alt_vals_vals: random seed to generate the alternative noise. One of:

                                   * ndarray (integer seeds),
                                   * None (no seeds passed, but will record the seed used)
                                   * int (1 seed for all simulations)

        :param seed_base_vals_vals: random seed to generate the base noise. One of:

                                    * ndarray (integer seeds),
                                    * None (no seeds passed, but will record the seed used)
                                    * int (1 seed for all simulations)

        Note seed_base != seed_alt (the same noise will be added to both time series, making the analysis useless)
        :param run: if True run the simulations, if False just build  the run_dict and print the number of simulations
        :param debug_mode: if True run as single process to allow for easier debugging
        :param kwargs: any other kwargs to pass directly to the output dataframe
        :return: dataframe with input data and the results of all of the power calcs. note power is percent 0-100
        """
        use_kwargs = dict(
            true_conc_base_vals=true_conc_base_vals,
            true_conc_alt_vals=true_conc_alt_vals,
            error_base_vals=error_base_vals,
            error_alt_vals=error_alt_vals,
            seed_alt_vals_vals=seed_alt_vals_vals,
            seed_base_vals_vals=seed_base_vals_vals,
            **kwargs
        )

        return self._run_multiprocess_pass_conc(outpath, idv_vals, run, debug_mode, use_kwargs)


class AutoDetectionPowerCounterFactual(DetectionPowerCounterFactual):
    """
    This class is used to calculate the counterfactual detection power of a pair of auto created concentration time series. The user specifies an initial concentration, and a target concentration for both a base and alternative scenario. Other parameters include groundwater age distribution models and parameters, implementation time and the slope of the previous data.

    The user then specifies the sampling duration, delay, and frequency. The power is calculated by adding many user specified noise realisations to both the base and alternative concentration time series and running a paired t test or wilcoxon signed rank test to determine if the null hypothesis (The scenarios are the same) can be rejected.

    The Power is calculated as the percentage (0-100) of simulations which reject the null hypothesis.

    :param significance_mode: str, one of:

                                * 'paired-t-test': paired t test (parametric), scipy.stats.ttest_rel
                                * 'wilcoxon-signed-rank-test': wilcoxon signed rank test (non-parametric), scipy.stats.wilcoxon

    :param nsims: number of noise simulations to run for each change detection (e.g. nsims=1000, power= number of detected changes/1000 noise simulations)
    :param p_value: minimum p value (see also alternative), if p >= p_value the null hypothesis will not be rejected (base and alt are the same) p < p_value the null hypothesis will be rejected (base and alt are different)
    :param min_samples: minimum number of samples required, less than this number of samples will raise an exception
    :param alternative: str, one of:

                            * 'alt!=base': two sided test (default),
                            * 'alt<base': one sided test ~
                            * 'alt>base'

    :param wx_zero_method: str, one of:

                               * “wilcox”: Discards all zero-differences (default); see [4].
                               * “pratt”: Includes zero-differences in the ranking process, but drops the ranks of the zeros (more conservative); see [3]. In this case, the normal approximation is adjusted as in [5].
                               * “zsplit”: Includes zero-differences in the ranking process and splits the zero rank between positive and negative ones.

                            for more info see: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html

    :param wx_correction: bool, If True, apply continuity correction by adjusting the Wilcoxon rank statistic by 0.5 towards the mean value when computing the z-statistic. Default is False.
    :param wx_method: str, see scipy.stats.wilcoxon for more info
    :param ncores: number of cores to use for multiprocessing, None will use all available cores
    :param log_level: logging level for multiprocessing subprocesses
    :param return_true_conc: return the true concentration time series for each simulation with power calcs (not supported with multiprocessing power calcs)
    :param return_noisy_conc_itters: int <= nsims, default = 0 Number of noisy simulations to return if 0 then no noisy simulations are returned, not supported with multiprocessing power calcs
    :param only_significant_noisy: bool if True then only return noisy simulations where a change was detected if there are fewer noisy simulations with changes detected than return_noisy_conc_itters all significant simulations will be returned. if there are no noisy simulations with changes detected then and empty dataframe is returned
    """
    implemented_mrt_models = (
        'piston_flow',
        'binary_exponential_piston_flow',
    )
    _auto_mode = True
    _counterfactual = True
    condensed_mode = False

    def set_condensed_mode(self,
                           target_conc_per=1,
                           initial_conc_per=1,
                           error_per=2,
                           prev_slope_per=2,
                           max_conc_lim_per=1,
                           min_conc_lim_per=1,
                           mrt_per=0,
                           mrt_p1_per=2,
                           frac_p1_per=2,
                           f_p1_per=2,
                           f_p2_per=2):
        """
        set calculator to condense the number of runs based by rounding the inputs to a specified precision

        :param target_conc_per: precision to round target_conc to (2 = 0.01)
        :param initial_conc_per: precision to round initial_conc to (2 = 0.01)
        :param error_per: precision to round error to (2 = 0.01)
        :param prev_slope_per: precision to round previous_slope to (2 = 0.01)
        :param max_conc_lim_per: precision to round max_conc_lim to (2 = 0.01)
        :param min_conc_lim_per: precision to round min_conc_lim to (2 = 0.01)
        :param mrt_per: precision to round mrt to
        :param mrt_p1_per: precision to round mrt_p1 to
        :param frac_p1_per: precision to round frac_p1 to
        :param f_p1_per: precision to round f_p1 to
        :param f_p2_per: precision to round f_p2 to
        :return:
        """

        self.condensed_mode = True

        self.target_conc_base_per = target_conc_per
        self.target_conc_alt_per = target_conc_per
        self.initial_conc_per = initial_conc_per
        self.error_base_per = error_per
        self.error_alt_per = error_per
        self.prev_slope_per = prev_slope_per
        self.max_conc_lim_per = max_conc_lim_per
        self.min_conc_lim_per = min_conc_lim_per
        self.mrt_per = mrt_per
        self.mrt_p1_per = mrt_p1_per
        self.frac_p1_per = frac_p1_per
        self.f_p1_per = f_p1_per
        self.f_p2_per = f_p2_per

    def power_calc(
            self,
            idv,
            error_base: float,
            mrt_model: str,
            samp_years: int,
            samp_per_year: int,
            implementation_time_alt: int,
            initial_conc: float,
            target_conc_alt: float,
            prev_slope: float,
            max_conc_lim: float,
            min_conc_lim: float,
            mrt: float = 0,

            target_conc_base: {float, None} = None,
            implementation_time_base: {int, None} = None,
            error_alt: {float, None} = None,
            delay_years: {int} = 0,

            # options for binary_exponential_piston_flow model
            mrt_p1: {float, None} = None,
            frac_p1: {float, None} = None,
            f_p1: {float, None} = None,
            f_p2: {float, None} = None,

            # options for the model run
            seed_base: {int, None} = None,
            seed_alt: {int, None} = None,
            testnitter=None,
            **kwargs

    ):
        """
        calculate the counterfactual detection power of auto created concentration time series

        :param idv: identifiers for the power calc sites, passed straight through to the output
        :param error_base: standard deviation of the noise to add to the base concentration time series
        :param mrt_model: the model to use for the mean residence time options:

                          * 'piston_flow': use the piston flow model (no mixing, default)
                          * 'binary_exponential_piston_flow': use the binary exponential piston flow model
                          * For unitary exponential_piston_flow model set frac_1 = 1 and mrt_p1 = mrt
                          * For no lag, set mrt=0, mrt_model='piston_flow'

        :param samp_years: number of years to sample
        :param samp_per_year: number of samples to collect each year
        :param implementation_time_alt: number of years over which the target concentration_alt is reached
        :param initial_conc: initial median value of the concentration
        :param target_conc_alt: target concentration for the alt scenario
        :param prev_slope: slope of the previous data (e.g. prior to the initial concentration)
        :param max_conc_lim: maximum concentration limit user specified or None (default)
        :param min_conc_lim: minimum concentration limit for the source, only used for the binary_exponential_piston_flow model
        :param mrt: the mean residence time of the site
        :param target_conc_base: the target concentration for the base scenario, if None then target_conc_base = initial_conc
        :param implementation_time_base: number of years over which the target concentration_base is reached, if None then implementation_time_base = implementation_time_alt
        :param error_alt: standard deviation of the noise to add to the alt concentration time series, if None then error_alt = error_base
        :param delay_years: number of years to delay the start of the monitoring, If the delay_years does not allow enough samples to be collected then an exception will be raised. If delay_years is 0 then the full length of the concentration time series will be used

        Options for binary_exponential_piston_flow model:

        :param mrt_p1: the mean residence time of the first piston flow model (only used for binary_exponential_piston_flow model)
        :param frac_p1: the fraction of the first piston flow model (only used for binary_exponential_piston_flow model)
        :param f_p1: the fraction of the first piston flow model (only used for binary_exponential_piston_flow model)
        :param f_p2: the fraction of the first piston flow model (only used for binary_exponential_piston_flow model)
        :param seed_base: seed for the random number generator for the base scenario, if None then a random seed will be generated and returned with the output
        :param seed_alt: seed for the random number generator for the alt scenario, if None then a random seed will be generated and returned with the output
        :param testnitter: None (usually) or a different nitter then self.niter for testing run times
        :param kwargs: any other kwargs to pass directly to the output Series
        :return: pd.Series with the power calc results note power is percent 0-100

        Possible other dataframes if self.return_true_conc is True or self.return_noisy_conc_itters > 0 in which case a dictionary will be returned:
        {'power': power_df, # always
        'true_conc': true_conc_ts, if self.return_true_conc is True
        'noisy_conc' : noisy_conc_ts, if self.return_noisy_conc_itters > 0
        }
        """

        if target_conc_base is None:
            target_conc_base = initial_conc
        if implementation_time_base is None:
            implementation_time_base = implementation_time_alt
        if error_alt is None:
            error_alt = error_base

        if testnitter is not None:
            warnings.warn('testnitter is expected to be None unless you are testing run times')

        assert mrt_model in self.implemented_mrt_models, f'mrt_model must be one of: {self.implemented_mrt_models}'
        assert pd.api.types.is_integer(samp_years), 'samp_years must be an integer'
        assert pd.api.types.is_integer(samp_per_year), 'samp_per_year must be an integer'
        assert pd.api.types.is_integer(delay_years), 'delay_years must be an integer'
        assert delay_years >= 0, 'delay_years must be >= 0'
        assert pd.api.types.is_number(initial_conc), 'initial_conc must be a number'
        assert pd.api.types.is_number(target_conc_base), 'target_conc(s) must be a number'
        assert pd.api.types.is_number(target_conc_alt), 'target_conc(s) must be a number'
        assert pd.api.types.is_number(prev_slope), 'prev_slope must be a number'
        assert pd.api.types.is_number(max_conc_lim), 'max_conc must be a number'
        assert max_conc_lim >= initial_conc, 'max_conc must be greater than or equal to initial_conc'
        assert max_conc_lim >= max(target_conc_alt, target_conc_base), ('max_conc must be greater than or '
                                                                        'equal to target_conc(s)')
        assert pd.api.types.is_integer(implementation_time_base)
        assert pd.api.types.is_integer(implementation_time_alt)

        # mange lag
        if mrt_model == 'piston_flow':

            (true_conc_ts_base,
             max_conc_val_base,
             max_conc_time_base,
             mrt_p2) = self.truets_from_piston_flow(mrt,
                                                    initial_conc, target_conc_base,
                                                    prev_slope, max_conc_lim,
                                                    samp_per_year, samp_years,
                                                    implementation_time_base)
            (true_conc_ts_alt,
             max_conc_val_alt,
             max_conc_time_alt,
             mrt_p2) = self.truets_from_piston_flow(mrt,
                                                    initial_conc, target_conc_alt,
                                                    prev_slope, max_conc_lim,
                                                    samp_per_year, samp_years,
                                                    implementation_time_alt)

        elif mrt_model == 'binary_exponential_piston_flow':
            tvs = ['mrt_p1', 'frac_p1', 'f_p1', 'f_p2', 'min_conc_lim']
            bad = []
            for t in tvs:
                if eval(t) is None:
                    bad.append(t)
            if len(bad) > 0:
                raise ValueError(f'for binary_exponential_piston_flow model the following must be specified: {bad}')

            (true_conc_ts_base,
             max_conc_val_base,
             max_conc_time_base,
             mrt_p2) = self.truets_from_binary_exp_piston_flow(
                mrt, mrt_p1, frac_p1, f_p1, f_p2,
                initial_conc, target_conc_base, prev_slope, max_conc_lim, min_conc_lim,
                samp_per_year, samp_years, implementation_time_base,
                return_extras=False)
            (true_conc_ts_alt,
             max_conc_val_alt,
             max_conc_time_alt,
             mrt_p2) = self.truets_from_binary_exp_piston_flow(
                mrt, mrt_p1, frac_p1, f_p1, f_p2,
                initial_conc, target_conc_alt, prev_slope, max_conc_lim, min_conc_lim,
                samp_per_year, samp_years, implementation_time_alt,
                return_extras=False)

        else:
            raise NotImplementedError(f'mrt_model {mrt_model} not currently implemented')

        assert not np.allclose(true_conc_ts_base, true_conc_ts_alt), ('true_conc_ts_base and true_conc_ts_alt are '
                                                                      'the same, this should not be')

        delay_years = int(delay_years)
        if delay_years > 0:
            samp_delay = delay_years * samp_per_year
            if (len(true_conc_ts_base) - samp_delay) < self.min_samples:
                raise ValueError(
                    f'Cannot delay the start of the monitoring by {delay_years} years, there are not'
                    f' enough samples ({len(true_conc_ts_base)}).'
                    f'there are {len(true_conc_ts_base) - samp_delay} samples after delay,'
                    f'which is < mimimum samples ({self.min_samples})'
                    f' try reducing the delay_years, increasing the samp_years, or increasing n_amp_per_year')
            true_conc_ts_base = true_conc_ts_base[samp_delay:]
            true_conc_ts_alt = true_conc_ts_alt[samp_delay:]

        outdata = self._run_power_calc(
            idv=idv,
            testnitter=testnitter,
            seed_base=seed_base,
            seed_alt=seed_alt,
            true_conc_base=true_conc_ts_base,
            true_conc_alt=true_conc_ts_alt,
            error_base=error_base,
            error_alt=error_alt,
            mrt_model=mrt_model,
            samp_years=samp_years,
            samp_per_year=samp_per_year,
            implementation_time_alt=implementation_time_alt,
            initial_conc=initial_conc,
            target_conc_alt=target_conc_alt,
            prev_slope=prev_slope,
            max_conc_lim=max_conc_lim,
            min_conc_lim=min_conc_lim,
            max_conc_val_base=max_conc_val_base,
            max_conc_time_base=max_conc_time_base,
            max_conc_val_alt=max_conc_val_alt,
            max_conc_time_alt=max_conc_time_alt,
            mrt=mrt,
            target_conc_base=target_conc_base,
            implementation_time_base=implementation_time_base,
            mrt_p1=mrt_p1,
            frac_p1=frac_p1,
            f_p1=f_p1,
            f_p2=f_p2,
            **kwargs
        )
        return outdata

    def mulitprocess_power_calcs(self,
                                 outpath: {Path, None, str},
                                 idv_vals: np.ndarray,
                                 error_base_vals: {np.ndarray, float},
                                 samp_years_vals: {np.ndarray, int},
                                 samp_per_year_vals: {np.ndarray, int},
                                 implementation_time_alt_vals: {np.ndarray, int},
                                 initial_conc_vals: {np.ndarray, float},
                                 target_conc_alt_vals: {np.ndarray, float},
                                 prev_slope_vals: {np.ndarray, float},
                                 max_conc_lim_vals: {np.ndarray, float},
                                 min_conc_lim_vals: {np.ndarray, float},
                                 mrt_model_vals: {np.ndarray, str},
                                 mrt_vals: {np.ndarray, float},
                                 target_conc_base_vals: {np.ndarray, float, None} = None,
                                 implementation_time_base_vals: {np.ndarray, int, None} = None,
                                 error_alt_vals: {np.ndarray, float, None} = None,
                                 delay_years_vals: {np.ndarray, int, None} = None,
                                 mrt_p1_vals: {np.ndarray, float, None} = None,
                                 frac_p1_vals: {np.ndarray, float, None} = None,
                                 f_p1_vals: {np.ndarray, float, None} = None,
                                 f_p2_vals: {np.ndarray, float, None} = None,
                                 seed_alt_vals: {np.ndarray, int, None} = None,
                                 seed_base_vals: {np.ndarray, int, None} = None,
                                 run=True, debug_mode=False, **kwargs
                                 ):
        """
        multiprocessing wrapper for power_calc, see power_calc for details

        :param outpath: path to save results to or None (no save)
        :param idv_vals: id values for each simulation
        :param error_base_vals: standard deviation of noise to add to the base time series for each simulation
        :param samp_years_vals: sampling years for each simulation
        :param samp_per_year_vals: sampling per year for each simulation
        :param implementation_time_alt_vals: implementation time for the alternative scenario for each simulation
        :param initial_conc_vals: initial concentration for each simulation
        :param target_conc_alt_vals: target concentration for the alternative scenario for each simulation
        :param prev_slope_vals: previous slope for each simulation
        :param max_conc_lim_vals: maximum concentration limit for each simulation
        :param min_conc_lim_vals: minimum concentration limit for the source for each simulation
        :param mrt_model_vals: mrt model for each simulation
        :param mrt_vals: mean residence time for each simulation
        :param target_conc_base_vals: target concentration for the base scenario for each simulation, if None then target_conc_base = initial_conc
        :param implementation_time_base_vals: implementation time for the base scenario for each simulation, if None then implementation_time_base = implementation_time_alt
        :param error_alt_vals: standard deviation of the noise to add to the alt concentration time series, if None then error_alt = error_base
        :param delay_years_vals: number of years to delay the start of the monitoring for each simulation, If the delay_years does not allow enough samples to be collected then an exception will be raised. If delay_years is 0 then the full length of the concentration time series will be used
        :param mrt_p1_vals: mean residence time of the first piston flow model for each simulation
                            Only used for binary_exponential_piston_flow model
        :param frac_p1_vals: fraction of the first piston flow model for each simulation
                            Only used for binary_exponential_piston_flow model
        :param f_p1_vals: the exponential fraction of the first piston flow model for each simulation
                            Only used for binary_exponential_piston_flow model
        :param f_p2_vals: the exponential fraction of the second piston flow model for each simulation
                            Only used for binary_exponential_piston_flow model
        :param seed_alt_vals:  random seed to generate the alternative noise for each simulation. One of:
                                    ndarray (integer seeds), int, None (no seeds passed, but will record the seed used)
        :param seed_base_vals: random seed to generate the base noise for each simulation. One of:  ndarray (integer seeds), int, None (no seeds passed, but will record the seed used)

        Note seed_base != seed_alt (the same noise will be added to both time series, making the analysis useless)

        :param run: if True run the simulations, if False just build  the run_dict and print the number of simulations
        :param debug_mode: if True run as single process to allow for easier debugging
        :param kwargs: other kwargs to pass directly to the output dataframe must be either a single value or an array of values with the same shape as id_vals
        :return: pd.DataFrame with the power calc results note power is percent 0-100
        """

        use_kwargs = dict(
            error_base_vals=error_base_vals,
            samp_years_vals=samp_years_vals,
            samp_per_year_vals=samp_per_year_vals,
            implementation_time_alt_vals=implementation_time_alt_vals,
            initial_conc_vals=initial_conc_vals,
            target_conc_alt_vals=target_conc_alt_vals,
            prev_slope_vals=prev_slope_vals,
            max_conc_lim_vals=max_conc_lim_vals,
            min_conc_lim_vals=min_conc_lim_vals,
            mrt_model_vals=mrt_model_vals,
            mrt_vals=mrt_vals,
            target_conc_base_vals=target_conc_base_vals,
            implementation_time_base_vals=implementation_time_base_vals,
            error_alt_vals=error_alt_vals,
            delay_years_vals=delay_years_vals,
            mrt_p1_vals=mrt_p1_vals,
            frac_p1_vals=frac_p1_vals,
            f_p1_vals=f_p1_vals,
            f_p2_vals=f_p2_vals,
            seed_alt_vals=seed_alt_vals,
            seed_base_vals=seed_base_vals,

            **kwargs)

        return self._run_multiprocess_auto(outpath, idv_vals, run, debug_mode, use_kwargs)
