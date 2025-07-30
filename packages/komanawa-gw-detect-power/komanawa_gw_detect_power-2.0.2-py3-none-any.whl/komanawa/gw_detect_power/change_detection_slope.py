"""
simplification of Mike's code (utils.py power_sims) to propagate the uncertainty from various assumptions to the stats
power calcs
created matt_dumont
on: 18/05/23
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import logging
import warnings
from komanawa.gw_detect_power.base_detection_calculator import BaseDetectionCalculator
from pyhomogeneity import pettitt_test
from komanawa.kendall_stats import MannKendall, MultiPartKendall


class DetectionPowerCalculator:
    def __init__(self, *args, **kwargs):
        """
        The DetectionPowerCalculator has been depreciated in version v2.0.0. To retain the old capability use v1.0.0.

        :param args: dummy
        :param kwargs: dummy
        """
        raise NotImplementedError('The DetectionPowerCalculator has been depreciated in version'
                                  'v2.0.0. To retain the old capability use v1.0.0.')
        # Keynote as a place holder to refactor tests and others using the repo


class DetectionPowerSlope(BaseDetectionCalculator):
    """
    The DetectionPowerSlope class is used to calculate the power of a change detection test based on observing
    a slope in the concentration data. The user passes a True concentration time series and the power is calculated
    by adding many noise realisations to the concentration data and then running one of multiple change detection tests on the noisy
    data.

    The Power is calculated as the percentage (0-100) of simulations which detect a slope.

    :param significance_mode: significance mode to use, options:

             * linear-regression: linear regression of the concentration data from time 0 to the end change detected if p < min_p_value
             * linear-regression-from-[max|min]: linear regression of the concentration data from the maximum concentration of the noise free concentration data to the end change detected if p < min_p_value
             * mann-kendall: mann-kendall test of the concentration data from time 0 to the end, change detected if p < min_p_value
             * mann-kendall-from-[max|min]: mann-kendall test of the concentration data from the maximum/minimum of the noise free concentration data to the end, change detected if p < min_p_value
             * n-section-mann-kendall: 2+ part mann-kendall test to identify change points. if change points are detected then a change is detected
             * pettitt-test: pettitt test to identify change points. if change points are detected then a change is detected

    :param nsims: number of noise simulations to run for each change detection (e.g. nsims=1000, power= number of detected changes/1000 noise simulations)
    :param min_p_value: minimum p value to consider a change detected
    :param min_samples: minimum number of samples required, less than this number of samples will raise an exception
    :param expect_slope: expected slope of the concentration data, use depends on significance mode:

                          * linear-regression, linear-regression-from-max, mann-kendall, or mann-kendall-from-max:
                            * one of 1 (increasing), -1 (decreasing), or 'auto' will match the slope of the concentration data before noise is added

                          * n-section-mann-kendall: expected trend in each part of the time series (1 increasing, -1 decreasing, 0 no trend)
                          * pettitt-test: not used.

    :param efficent_mode: bool, default = True, if True then

                         * For linear regression and MannKendall based tests:  run the test on the noise free data to see if any change can be detected, if no change is detected then the test will not be on the noisy data
                         * For MultiPartMannKendall test: the test will be run on the noise free data to detect best change points and then the test will be run on the noisy data for a smaller window centered on the True change point see: * mpmk_efficent_min, * mpmk_window
                         * For Pettitt Test:  Not implemented, will be ignored and a waring passed

    :param nparts: number of parts to use for the n-section-mann-kendall test (not used for other tests)
    :param min_part_size: minimum number of samples in each part for the n-section-mann-kendall test (not used for other tests)
    :param no_trend_alpha: alpha value to use for the no trend sections in the n-section-mann-kendall test trendless sections are only accepted if p > no_trend_alpha (not used for other tests)
    :param mpmk_check_step: int or function, default = 1, number of samples to check for a change point in the MultiPartMannKendall test, used in both efficent_mode=True and efficent_mode=False if mpmk is a function it must take a single argument (n, number of samples) and return an integer check step
    :param mpmk_efficent_min: int, default = 10, minimum number of possible change points to assess only used if efficent_mode = True  The minimum number of breakpoints to test (mpmk_efficent_min) is always respected (i.e. if the window size is less than the minimum number of breakpoints to test, then the window size will be increased to the minimum number of breakpoints to test, but the space between breakpoints will still be defined by check_step). You can specify the exact number of breakpoints to check by setting mpmk_efficent_min=n breakpoints and setting mpmk_window=0
    :param mpmk_window: float, default = 0.05, define the window around the true detected change point to run the MultiPartMannKendall.  The detction window is defined as: (cp - mpmk_window*n, cp + mpmk_window*n) where cp is the detected change `point and n is the number of samples in the time series Whe`re both a mpmk_window and a check_step>1 is passed the mpmk_window will be used to de`fine the window size and the check_step` will be used to define the step size within the window.`
    :param nsims_pettit: number of simulations to run for calc`ulating the pvalue of the pettitt test (not used for other tests)
    :param ncores: number of cores to use for multiprocessing, None will use all available cores
    :param log_level: logging level for multiprocessing subprocesses
    :param return_true_conc: return the true concentration time series for each simulation with power calcs (not supported with multiprocessing power calcs)
    :param return_noisy_conc_itters: int <= nsims, default = 0 Number of noisy simulations to return. if 0 then no noisy simulations are returned, not supported with multiprocessing power calcs
    :param only_significant_noisy: bool if True then only return noisy simulations where a change was detected if there are fewer noisy simulations with changes detected than return_noisy_conc_itters all significant simulations will be returned. if there are no noisy simulations with changes detected then and empty dataframe is returned
    :param print_freq: None or int:  if None then no progress will be printed, if int then progress will be printed every print_freq simulations (n%print_freq==0)
    :param raise_from_minmax_nsamples: bool, if True then raise an exception if the maximum concentration is too far along the time series to be detected, if False then return 0 power and no change detected
    """

    implemented_mrt_models = ()
    implemented_significance_modes = (
        'linear-regression',
        'linear-regression-from-max',
        'linear-regression-from-min',
        'mann-kendall',
        'mann-kendall-from-max',
        'mann-kendall-from-min',
        'n-section-mann-kendall',
        'pettitt-test',
    )

    def __init__(self, significance_mode='linear-regression', nsims=1000, min_p_value=0.05, min_samples=10,
                 expect_slope='auto', efficent_mode=True, nparts=None, min_part_size=10, no_trend_alpha=0.50,
                 mpmk_check_step=1, mpmk_efficent_min=10, mpmk_window=0.05,
                 nsims_pettit=2000,
                 ncores=None, log_level=logging.INFO, return_true_conc=False, return_noisy_conc_itters=0,
                 only_significant_noisy=False, print_freq=None, raise_from_minmax_nsamples=True):
        self.raise_from_minmax_nsamples = raise_from_minmax_nsamples
        assert print_freq is None or isinstance(print_freq, int), 'print_freq must be None or an integer'
        self.print_freq = print_freq
        assert significance_mode in self.implemented_significance_modes, (f'significance_mode {significance_mode} not '
                                                                          f'implemented, must be one of '
                                                                          f'{self.implemented_significance_modes}')
        self.nsims_pettitt = nsims_pettit
        if significance_mode in ['linear-regression', 'linear-regression-from-max', 'linear-regression-from-min',
                                 'mann-kendall', 'mann-kendall-from-max', 'mann-kendall-from-min']:
            assert expect_slope in ['auto', 1, -1], 'expect_slope must be "auto", 1, or -1'
            assert isinstance(efficent_mode, bool), 'efficent_mode must be a boolean'
            self.efficent_mode = efficent_mode

        assert isinstance(only_significant_noisy, bool), 'only_significant_noisy must be a boolean'
        self.only_significant_noisy = only_significant_noisy
        assert isinstance(return_true_conc, bool), 'return_true_conc must be a boolean'
        self.return_true_conc = return_true_conc
        assert isinstance(return_noisy_conc_itters, int), 'return_noisy_conc_itters must be an integer'
        assert return_noisy_conc_itters <= nsims, 'return_noisy_conc_itters must be <= nsims'
        assert return_noisy_conc_itters >= 0, 'return_noisy_conc_itters must be >= 0'
        self.return_noisy_conc_itters = return_noisy_conc_itters

        self._power_from_max = False
        self._power_from_min = False
        if significance_mode == 'linear-regression':
            self.power_test = self._power_test_lr
        elif significance_mode == 'linear-regression-from-max':
            self._power_from_max = True
            self.power_test = self._power_test_lr
        elif significance_mode == 'linear-regression-from-min':
            self._power_from_min = True
            self.power_test = self._power_test_lr
        elif significance_mode == 'mann-kendall':
            self.power_test = self._power_test_mann_kendall
        elif significance_mode == 'mann-kendall-from-max':
            self._power_from_max = True
            self.power_test = self._power_test_mann_kendall
        elif significance_mode == 'mann-kendall-from-min':
            self._power_from_min = True
            self.power_test = self._power_test_mann_kendall
        elif significance_mode == 'n-section-mann-kendall':
            assert isinstance(nparts, int), 'nparts must be an integer'
            assert nparts > 1, 'nparts must be greater than 1'
            self.kendall_mp_nparts = nparts
            assert isinstance(min_part_size, int), 'min_part_size must be an integer'
            assert min_part_size > 1, 'min_part_size must be greater than 1'
            self.kendall_mp_min_part_size = min_part_size
            assert isinstance(no_trend_alpha, float), 'no_trend_alpha must be a float'
            assert no_trend_alpha > 0 and no_trend_alpha < 1, 'no_trend_alpha must be between 0 and 1'
            self.kendall_mp_no_trend_alpha = no_trend_alpha
            assert len(np.atleast_1d(expect_slope)) == self.kendall_mp_nparts, 'expect_slope must be of length nparts'
            assert set(np.atleast_1d(expect_slope)).issubset([1, 0, -1]), (
                f'expect_slope must be 1 -1, or 0, got:{set(np.atleast_1d(expect_slope))}')

            # mpmk_check_step
            if callable(mpmk_check_step):
                n = mpmk_check_step(100)
                assert isinstance(n, int), 'if mpmk_check_step is a function must return an integer'
                assert n > 0, 'if mpmk_check_step is a function must return an integer greater than 0'
            elif isinstance(mpmk_check_step, int):
                assert mpmk_check_step > 0, 'mpmk_check_step must be greater than 0'
            else:
                raise ValueError('mpmk_check_step must be an integer or function')
            self.mpmk_check_step = mpmk_check_step

            assert isinstance(efficent_mode, bool), 'efficent_mode must be a boolean'
            self.efficent_mode = efficent_mode
            assert isinstance(mpmk_efficent_min, int), 'mpmk_efficent_min must be an integer'
            assert mpmk_efficent_min > 0, 'mpmk_efficent_min must be greater than 0'
            self.mpmpk_efficent_min = mpmk_efficent_min
            assert isinstance(mpmk_window, float), 'mpmk_window must be a float'
            assert mpmk_window > 0 and mpmk_window < 1 / nparts, f'mpmk_window must be between 0 and {1 / nparts}'
            self.mpmk_window = mpmk_window
            self.power_test = self._power_test_mp_kendall
        elif significance_mode == 'pettitt-test':
            assert isinstance(nsims_pettit, int), 'nsims_pettit must be an integer'
            assert isinstance(efficent_mode, bool), 'efficent_mode must be a boolean'
            if efficent_mode:
                warnings.warn('efficent_mode not implemented for pettitt test, setting efficent_mode=False')
            self.efficent_mode = False  # todo longterm fix this if needed
            self.power_test = self._power_test_pettitt
        else:
            raise NotImplementedError(f'significance_mode {significance_mode} not implemented, shouldnt get here')

        self.expect_slope = expect_slope

        assert isinstance(nsims, int), 'nsims must be an integer'
        self.nsims = nsims
        assert isinstance(min_samples, int), 'min_samples must be an integer'
        assert min_samples >= 3, ('min_samples must be at least 3 otherwise the slope regresion will either'
                                  'fail or be meaningless')
        self.min_samples = min_samples
        self.min_p_value = min_p_value
        assert self.min_p_value > 0 and self.min_p_value < 1, 'min_p_value must be between 0 and 1'
        assert isinstance(ncores, int) or ncores is None, 'ncores must be an integer or None'
        self.ncores = ncores
        assert log_level in [logging.CRITICAL, logging.FATAL, logging.ERROR, logging.WARNING, logging.WARN,
                             logging.INFO, logging.DEBUG], f'unknown log_level {log_level}'
        self.log_level = log_level
        self.significance_mode = significance_mode

    def plot_iteration(self, y0, true_conc, ax=None):
        """
        plot the concentration data itteration and the true concentration data if provided as well as the power test results and any predictions from the power test (e.g. the slope of the line used)

        :param y0: noisy concentration data
        :param true_conc: true concentration data
        :return: fig, ax
        """
        istart = 0
        import matplotlib.pyplot as plt
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        else:
            fig = ax.get_figure()
        ax.scatter(np.arange(len(y0)), y0, c='k', label=f'noisy data')
        ax.plot(np.arange(len(true_conc)), true_conc, c='r', label=f'True data', marker='.')
        if self.significance_mode in ['linear-regression', 'linear-regression-from-max', 'linear-regression-from-min']:
            if self._power_from_max:
                istart = np.argmax(true_conc)
            elif self._power_from_min:
                istart = np.argmin(true_conc)
            o2 = stats.linregress(np.arange(len(y0))[istart:], y0[istart:])
            ax.plot(np.arange(len(y0))[istart:], o2.intercept + o2.slope * np.arange(len(y0))[istart:], c='b',
                    ls='--', label='regression, p={:.3f}'.format(o2.pvalue))

        elif self.significance_mode in ['mann-kendall', 'mann-kendall-from-max', 'mann-kendall-from-min']:
            if self._power_from_max:
                istart = np.argmax(true_conc)
            elif self._power_from_min:
                istart = np.argmin(true_conc)
            mk = MannKendall(data=y0[istart:], alpha=self.min_p_value)
            mk.plot_data(ax=ax)

        elif self.significance_mode == 'n-section-mann-kendall':
            mpmk = MultiPartKendall(data=y0, nparts=self.kendall_mp_nparts,
                                    expect_part=self.expect_slope, min_size=self.kendall_mp_min_part_size,
                                    alpha=self.min_p_value, no_trend_alpha=self.kendall_mp_no_trend_alpha)
            bp = mpmk.get_maxz_breakpoints(raise_on_none=False)
            if bp is None:
                warnings.warn('no breakpoints found, not plotting multipart mann kendall')
            else:
                mpmk.plot_data_from_breakpoints(bp, ax=ax)
        elif self.significance_mode == 'pettitt-test':
            h, cp, p, U, mu = pettitt_test(y0, alpha=self.min_p_value,
                                           sim=self.nsims_pettitt)
            p = round(p, 3)
            ax.axvline(x=cp, color='r', label=f'change_point, {p=}')
        else:
            raise ValueError(f'unknown significance_mode {self.significance_mode}, should not get here')

        if istart > 0:
            ax.axvline(istart, c='k', ls=':', label='start of power test')
        ax.legend()
        return fig, ax

    def _power_test_lr(self, idv, y, expected_slope, imax, imin, true_data, return_slope=False):
        """
        power calculations, probability of detecting a change via linear regression (slope is significant and in the correct direction)

        :param idv: identifier for the power calc site
        :param y: np.array of shape (nsims, n_samples)
        :param expected_slope: used to determine sign of slope predicted is same as expected
        :param imax: index of the maximum concentration
        :param imin: index of the minimum concentration
        :param return_slope: return the slope of the concentration data used to calculate expect slope
        :return:
        """
        n_samples0 = y.shape[1]
        if self._power_from_max:
            y = y[:, imax:]
            true_data = true_data[imax:]
        if self._power_from_min:
            y = y[:, imin:]
            true_data = true_data[imin:]
        n_sims, n_samples = y.shape
        if n_samples < self.min_samples:
            if self.raise_from_minmax_nsamples:
                raise ValueError('n_samples must be greater than min_samples, '
                                 'raised here that means that the max concentration is too far along'
                                 f'the timeseries to be detected: {imax=}, {n_samples0}')
            else:
                if return_slope:
                    return 0., np.zeros(n_sims, dtype=bool), 0.
                return 0., np.zeros(n_sims, dtype=bool)
        x = np.arange(n_samples)
        p_val = []
        slopes = []
        if self.efficent_mode and not return_slope:
            o2 = stats.linregress(x, true_data)
            pval_bad = o2.pvalue > self.min_p_value
            sign_bad = False
            if expected_slope is not None:
                sign_bad = np.sign(o2.slope) != np.sign(expected_slope)

            if pval_bad or sign_bad:  # cannot reject null hypothesis on noise free data
                return 0., np.zeros(n_sims, dtype=bool)

        for i, y0 in enumerate(y):
            if self.print_freq is not None:
                if i % self.print_freq == 0:
                    print(f'{idv} {i + 1} of {n_sims}')
            o2 = stats.linregress(x, y0)
            slopes.append(o2.slope)
            p_val.append(o2.pvalue)
        p_val = np.array(p_val)
        slopes = np.array(slopes)
        p_list = p_val < self.min_p_value
        if expected_slope is not None:
            sign_corr = np.sign(slopes) == np.sign(expected_slope)
            p_list = p_list & sign_corr
        power = p_list.sum() / n_sims * 100

        if return_slope:
            slope_out = np.sign(np.nanmedian(slopes[p_list]))
            return power, p_list, slope_out
        return power, p_list

    def _power_test_mann_kendall(self, idv, y, expected_slope, imax, imin, true_data,
                                 return_slope=False):
        """
        power calculations, probability of detecting a change via linear regression
        (slope is significant and in the correct direction)
        :param y: np.array of shape (nsims, n_samples)
        :param expected_slope: used to determine sign of slope predicted is same as expected
        :param imax: index of the maximum concentration
        :param imin: index of the minimum concentration
        :param return_slope: return the slope of the concentration data used to calculate expect slope
        :return:
        """
        n_samples0 = y.shape[1]
        if self._power_from_max:
            y = y[:, imax:]
            true_data = true_data[imax:]
        if self._power_from_min:
            y = y[:, imin:]
            true_data = true_data[imin:]
        n_sims, n_samples = y.shape
        if n_samples < self.min_samples:
            if self.raise_from_minmax_nsamples:
                raise ValueError('n_samples must be greater than min_samples, '
                                 'raised here that means that the max concentration is too far along'
                                 f'the timeseries to be detected: {imax=}, {n_samples0}')
            else:
                if return_slope:
                    return 0., np.zeros(n_sims, dtype=bool), 0.
                return 0., np.zeros(n_sims, dtype=bool)

        if self.efficent_mode and not return_slope:
            mk = MannKendall(data=true_data, alpha=self.min_p_value)
            pval_bad = mk.p > self.min_p_value
            sign_bad = False
            if expected_slope is not None:
                sign_bad = np.sign(mk.trend) != np.sign(expected_slope)
            if pval_bad or sign_bad:  # cannot reject null hypothesis on noise free data
                return 0., np.zeros(n_sims, dtype=bool)

        p_val = []
        slopes = []
        for i, y0 in enumerate(y):
            if self.print_freq is not None:
                if i % self.print_freq == 0:
                    print(f'{idv} {i + 1} of {n_sims}')
            mk = MannKendall(data=y0, alpha=self.min_p_value)
            slopes.append(mk.trend)
            p_val.append(mk.p)
        p_val = np.array(p_val)
        slopes = np.array(slopes)
        p_list = p_val < self.min_p_value
        if expected_slope is not None:
            sign_corr = np.sign(slopes) == np.sign(expected_slope)
            p_list = p_list & sign_corr
        power = p_list.sum() / n_sims * 100
        slope_out = np.sign(np.nanmedian(slopes[p_list]))

        if return_slope:
            return power, p_list, slope_out
        return power, p_list

    def _power_test_pettitt(self, idv, y, expected_slope, imax, imin, true_data, return_slope=False):
        """

        :param y:data
        :param expected_slope: not used
        :param imax: not used
        :param imin: not used
        :param return_slope: not really used, dummy
        :return:
        """
        n_sims, n_samples = y.shape
        assert n_samples >= self.min_samples, ('n_samples must be greater than min_samples')
        num_pass = 0
        passed = []
        for i, y0 in enumerate(y):
            if self.print_freq is not None:
                if i % self.print_freq == 0:
                    print(f'{idv} {i + 1} of {n_sims}')
            h, cp, p, U, mu = pettitt_test(y0, alpha=self.min_p_value,
                                           sim=self.nsims_pettitt)
            num_pass += h
            passed.append(h)
        passed = np.atleast_1d(passed)
        power = num_pass / n_sims * 100
        if return_slope:
            return power, passed, None
        return power, passed

    def _power_test_mp_kendall(self, idv, y, expected_slope, imax, imin, true_data,
                               return_slope=False):
        """
        :param y: data
        :param expected_slope: expected slope values
        :param imax: not used
        :param imin: not used
        :param return_slope: dummy
        :return:
        """
        n_sims, n_samples = y.shape
        if callable(self.mpmk_check_step):
            use_check_step = self.mpmk_check_step(n_samples)
        else:
            use_check_step = self.mpmk_check_step
        assert (
                (n_samples >= self.min_samples)
                and (n_samples >= self.kendall_mp_min_part_size * self.kendall_mp_nparts)
        ), (f'{n_samples=} must be greater than min_samples={self.min_samples},'
            f' or nparts={self.kendall_mp_nparts} * min_part_size={self.kendall_mp_min_part_size}')
        power = []
        window = None
        if self.efficent_mode:
            mpmk = MultiPartKendall(data=true_data, nparts=self.kendall_mp_nparts,
                                    expect_part=expected_slope, min_size=self.kendall_mp_min_part_size,
                                    alpha=self.min_p_value, no_trend_alpha=self.kendall_mp_no_trend_alpha,
                                    check_step=use_check_step, check_window=None)
            best = mpmk.get_maxz_breakpoints(raise_on_none=False)
            if best is None:  # no matches on the True data not worth running the power calc
                return 0., np.zeros(n_sims, dtype=bool)

            if len(best) > 1:
                warnings.warn(f'multiple best breakpoints returned, cannot use efficent mode: {best}, '
                              f'reverting to original mode')
            else:
                best = np.atleast_1d(best[0])
                assert len(best) == self.kendall_mp_nparts - 1, (f'shouldnt get here '
                                                                 f'best breakpoints must have'
                                                                 f' length {self.kendall_mp_nparts - 1}')
                window = []
                for part, bp in zip(range(1, self.kendall_mp_nparts), best):
                    delta = max(self.mpmpk_efficent_min // 2 * use_check_step,
                                int(np.ceil(self.mpmk_window * len(true_data))))
                    wmin = max(0 + self.kendall_mp_min_part_size, bp - delta)
                    wmax = min(len(true_data) - self.kendall_mp_min_part_size,
                               bp + delta)
                    window.append((wmin, wmax))

        for i, y0 in enumerate(y):
            if self.print_freq is not None:
                if i % self.print_freq == 0:
                    print(f'{idv} {i + 1} of {n_sims}')
            mpmk = MultiPartKendall(data=y0, nparts=self.kendall_mp_nparts,
                                    expect_part=expected_slope, min_size=self.kendall_mp_min_part_size,
                                    alpha=self.min_p_value, no_trend_alpha=self.kendall_mp_no_trend_alpha,
                                    check_step=use_check_step, check_window=window)
            power.append(mpmk.acceptable_matches.any())

        power_array = np.array(power)
        power_out = power_array.sum() / n_sims * 100
        if return_slope:
            return power_out, power_array, None
        return power_out, power_array

    def _run_power_calc(self, testnitter, seed, true_conc_ts, idv, error, expect_slope, max_conc_val,
                        max_conc_time, **kwargs):
        if testnitter is not None:
            warnings.warn('testnitter is expected to be None unless you are testing run times')

        if seed is None:
            seed = np.random.randint(21, 54762438)

        nsamples = len(true_conc_ts)
        if nsamples < self.min_samples:
            raise ValueError(f'nsamples must be greater than {self.min_samples}, you can change the '
                             f'minimum number of samples in the DetectionPowerCalculator class init')
        assert np.isfinite(true_conc_ts).all(), 'true_conc_ts must be finite'

        # tile to nsims
        if testnitter is not None:
            rand_shape = (testnitter, nsamples)
            conc_with_noise = np.tile(true_conc_ts, testnitter).reshape(rand_shape).astype(float)
        else:
            rand_shape = (self.nsims, nsamples)
            conc_with_noise = np.tile(true_conc_ts, self.nsims).reshape(rand_shape).astype(float)

        # generate noise
        np.random.seed(seed)
        all_seeds = list(np.random.randint(21, 54762438, 2))
        np.random.seed(all_seeds.pop(0))
        noise = np.random.normal(0, error, rand_shape)
        conc_with_noise += noise

        # run slope test
        power, significant = self.power_test(idv, conc_with_noise,
                                             expected_slope=expect_slope,  # just used for sign
                                             imax=np.argmax(true_conc_ts), imin=np.argmin(true_conc_ts),
                                             true_data=true_conc_ts,
                                             return_slope=False)

        out = pd.Series({'idv': idv,
                         'power': power,
                         'max_conc': max_conc_val,
                         'max_conc_time': max_conc_time,
                         'error': error,
                         'seed': seed,
                         'python_error': None
                         })
        for k, v in kwargs.items():
            out[k] = v

        out_data = {}
        out_data['power'] = out
        if self.return_true_conc:
            out_data['true_conc'] = pd.DataFrame(data=true_conc_ts, columns=['true_conc'])

        if self.return_noisy_conc_itters > 0:
            if self.only_significant_noisy:
                conc_with_noise = conc_with_noise[significant]
                significant = significant[significant]
            outn = min(self.return_noisy_conc_itters, conc_with_noise.shape[0])
            out_data['noisy_conc'] = pd.DataFrame(data=conc_with_noise[:outn].T,
                                                  columns=np.arange(outn))
            out_data['significant'] = significant[:outn]
        if len(out_data) == 1:
            out_data = out_data['power']
        return out_data

    def power_calc(self, idv, error: float, true_conc_ts: np.ndarray,
                   seed: {int, None} = None, testnitter=None, **kwargs):
        """
        calculate the slope detection power of a given concentration time series, note the power is calculated using the sampling frequency of the true_conc_ts, if you want to test the power at a different sampling frequency then you should resample the true_conc_ts before passing it to this function

        :param idv: identifiers for the power calc sites, passed straight through to the output
        :param error: standard deviation of the noise
        :param true_conc_ts: the true concentration timeseries for the power calc
        :param seed: int or None for random seed
        :param testnitter: None (usually) or a different nitter then self.niter for testing run times
        :param kwargs: any other kwargs to pass directly to the output Series
        :return: pd.Series with the power calc results note power is percent 0-100

        Possible other dataframes if self.return_true_conc is True or self.return_noisy_conc_itters > 0 in which case a dictionary will be returned:

        {'power': power_df, # always
        'true_conc': true_conc_ts, if self.return_true_conc is True
        'noisy_conc' : noisy_conc_ts, if self.return_noisy_conc_itters > 0
        }
        """

        assert true_conc_ts is not None
        max_conc_val = np.max(true_conc_ts)
        max_conc_time = np.argmax(true_conc_ts)
        if self.expect_slope == 'auto':
            power, significant, expect_slope = self.power_test('auto_slope_finder',
                                                               np.atleast_1d(true_conc_ts)[np.newaxis, :],
                                                               expected_slope=None, imax=np.argmax(true_conc_ts),
                                                               imin=np.argmin(true_conc_ts), true_data=true_conc_ts,
                                                               return_slope=True)
        else:
            expect_slope = self.expect_slope

        outdata = self._run_power_calc(testnitter=testnitter,
                                       seed=seed,
                                       true_conc_ts=true_conc_ts,
                                       idv=idv,
                                       error=error,
                                       expect_slope=expect_slope,
                                       max_conc_val=max_conc_val,
                                       max_conc_time=max_conc_time,
                                       **kwargs)
        return outdata

    def mulitprocess_power_calcs(self,
                                 outpath: {Path, None, str},
                                 idv_vals: np.ndarray,
                                 error_vals: {np.ndarray, float},
                                 true_conc_ts_vals: {np.ndarray, list},
                                 seed_vals: {np.ndarray, int, None} = None,
                                 run=True, debug_mode=False,
                                 **kwargs
                                 ):
        """
        multiprocessing wrapper for power_calc, see power_calc for details note that if a given run raises and exception the traceback for the exception will be included in the returned dataset under the column 'python_error' if 'python_error' is None then the run was successful to change the number of cores used pass n_cores to the constructor init

        :param outpath: path to save results to or None (no save)
        :param idv_vals: id values for each simulation

        All values from here on out should be either a single value or an array of values with the same shape as id_vals

        :param error_vals: standard deviation of noise to add for each simulation
        :param true_conc_ts_vals: the true concentration time series for each simulation, note that this can be a list of arrays of different lengths for each simulation, as Numpy does not support jagged arrays
        :param seed: ndarray (integer seeds), None (no seeds), or int (1 seed for all simulations)
        :param run: if True run the simulations, if False just build  the run_dict and print the number of simulations
        :param debug_mode: if True run as single process to allow for easier debugging
        :param kwargs: any other kwargs to pass directly to the output dataframe
        :return: dataframe with input data and the results of all of the power calcs. note power is percent 0-100
        """

        use_kwargs = dict(error_vals=error_vals,
                          true_conc_ts_vals=true_conc_ts_vals,
                          seed_vals=seed_vals,
                          **kwargs
                          )
        return self._run_multiprocess_pass_conc(outpath, idv_vals, run, debug_mode, use_kwargs)


class AutoDetectionPowerSlope(DetectionPowerSlope):
    """
    This class is used to calculate the slope detection power of an auto created concentration
    time series. The user specifies an initial concentration, a target concentration. Other parameters
    include groundwater age distribution models and parameters, implementation time and the slope of
    the previous data. The user then specifies the sampling duration, and frequency.
    The power is calculated by adding many noise realisations to the concentration data and then running one of
    multiple change detection tests on the noisy data.

    The Power is calculated as the percentage (0-100) of simulations which detect a slope.

    :param significance_mode: significance mode to use, options:

             * linear-regression: linear regression of the concentration data from time 0 to the end change detected if p < min_p_value
             * linear-regression-from-[max|min]: linear regression of the concentration data from the maximum concentration of the noise free concentration data to the end change detected if p < min_p_value
             * mann-kendall: mann-kendall test of the concentration data from time 0 to the end, change detected if p < min_p_value
             * mann-kendall-from-[max|min]: mann-kendall test of the concentration data from the maximum/minimum of the noisefree concentration data to the end, change detected if p < min_p_value
             * n-section-mann-kendall: 2+ part mann-kendall test to identify change points. if change points are detected then a change is detected
             * pettitt-test: pettitt test to identify change points. if change points are detected then a change is detected

    :param nsims: number of noise simulations to run for each change detection (e.g. nsims=1000, power= number of detected changes/1000 noise simulations)
    :param min_p_value: minimum p value to consider a change detected
    :param min_samples: minimum number of samples required, less than this number of samples will raise an exception
    :param expect_slope: expected slope of the concentration data, use depends on significance mode:

                          * linear-regression, linear-regression-from-max, mann-kendall, mann-kendall-from-max: one of 1 (increasing), -1 (decreasing), or 'auto' will match the slope of the concentration data before noise is added
                          * n-section-mann-kendall: expected trend in each part of the time series (1 increasing, -1 decreasing, 0 no trend)
                          * pettitt-test: not used.

    :param efficent_mode: bool, default = True, if True then

                         * For linear regression and MannKendall based tests:  run the test on the noise free data to see if any change can be detected, if no change is detected then the test will not be on the noisy data
                         * For MultiPartMannKendall test: the test will be run on the noise free data to detect best change points and then the test will be run on the noisy data for a smaller window centered on the True change point see: "mpmk_efficent_min" and "mpmk_window"
                         * For Pettitt Test:  Not implemented, will be ignored and a waring passed

    :param nparts: number of parts to use for the n-section-mann-kendall test (not used for other tests)
    :param min_part_size: minimum number of samples in each part for the n-section-mann-kendall test (not used for other tests)
    :param no_trend_alpha: alpha value to use for the no trend sections in the n-section-mann-kendall test trend less sections are only accepted if p > no_trend_alpha (not used for other tests)
    :param mpmk_check_step: int or function, default = 1, number of samples to check for a change point in the MultiPartMannKendall test, used in both efficent_mode=True and efficent_mode=False if mpmk is a function it must take a single argument (n, number of samples) and return an integer check step
    :param mpmk_efficent_min: int, default = 10, minimum number of possible change points to assess only used if efficent_mode = True  The minimum number of breakpoints to test (mpmk_efficent_min) is always respected (i.e. if the window size is less than the minimum number of breakpoints to test, then the window size will be increased to the minimum number of breakpoints to test, but the space between breakpoints will still be defined by check_step). You can specify the exact number of breakpoints to check by setting mpmk_efficent_min=n breakpoints and setting mpmk_window=0
    :param mpmk_window: float, default = 0.05, define the window around the true detected change point to run the MultiPartMannKendall.  The detction window is defined as: (cp - mpmk_window*n, cp + mpmk_window*n) where cp is the detected change point and n is the number of samples in the time series Where both a mpmk_window and a check_step>1 is passed the mpmk_window will be used to define the window size and the check_step will be used to define the step size within the window.
    :param nsims_pettit: number of simulations to run for calculating the pvalue of the pettitt test (not used for other tests)
    :param ncores: number of cores to use for multiprocessing, None will use all available cores
    :param log_level: logging level for multiprocessing subprocesses
    :param return_true_conc: return the true concentration time series for each simulation with power calcs (not supported with multiprocessing power calcs)
    :param return_noisy_conc_itters: int <= nsims, default = 0 Number of noisy simulations to return if 0 then no noisy simulations are returned, not supported with multiprocessing power calcs
    :param only_significant_noisy: bool if True then only return noisy simulations where a change was detected if there are fewer noisy simulations with changes detected than return_noisy_conc_itters all significant simulations will be returned. if there are no noisy simulations with changes detected then and empty dataframe is returned
    :param print_freq: None or int:  if None then no progress will be printed, if int then progress will be printed every print_freq simulations (n%print_freq==0)
    """

    implemented_mrt_models = (
        'piston_flow',
        'binary_exponential_piston_flow',
    )
    _auto_mode = True
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

        self.target_conc_per = target_conc_per
        self.initial_conc_per = initial_conc_per
        self.error_per = error_per
        self.prev_slope_per = prev_slope_per
        self.max_conc_lim_per = max_conc_lim_per
        self.min_conc_lim_per = min_conc_lim_per
        self.mrt_per = mrt_per
        self.mrt_p1_per = mrt_p1_per
        self.frac_p1_per = frac_p1_per
        self.f_p1_per = f_p1_per
        self.f_p2_per = f_p2_per

    def power_calc(self, idv, error: float, mrt_model: str, samp_years: int, samp_per_year: int,
                   implementation_time: int, initial_conc: float, target_conc: float, prev_slope: float,
                   max_conc_lim: float, min_conc_lim: float, mrt: float = 0,
                   # options for binary_exponential_piston_flow model
                   mrt_p1: {float, None} = None, frac_p1: {float, None} = None, f_p1: {float, None} = None,
                   f_p2: {float, None} = None,
                   # options for the model run
                   seed: {int, None} = None,
                   testnitter=None,
                   **kwargs):
        """

        calculate the detection power for a given set of parameters

        :param idv: identifiers for the power calc sites, passed straight through to the output
        :param error: standard deviation of the noise
        :param mrt_model: the model to use for the mean residence time options:

                          * 'piston_flow': use the piston flow model (no mixing, default)
                          * 'binary_exponential_piston_flow': use the binary exponential piston flow model for unitary exponential_piston_flow model set frac_1 = 1 and mrt_p1 = mrt for no lag, set mrt=0, mrt_model='piston_flow'

        :param samp_years: number of years to sample
        :param samp_per_year: number of samples to collect each year
        :param implementation_time: number of years over which reductions are implemented
        :param initial_conc: initial median value of the concentration
        :param target_conc: target concentration to reduce to
        :param prev_slope: slope of the previous data (e.g. prior to the initial concentration)
        :param max_conc_lim: maximum concentration limit user specified or None (default)
        :param min_conc_lim: minimum concentration limit for the source, only used for the binary_exponential_piston_flow model)
        :param mrt: the mean residence time of the site

        Options for binary_exponential_piston_flow model:

        :param mrt_p1: the mean residence time of the first piston flow model (only used for binary_exponential_piston_flow model)
        :param frac_p1: the fraction of the first piston flow model (only used for binary_exponential_piston_flow model)
        :param f_p1: the fraction of the first piston flow model (only used for binary_exponential_piston_flow model)
        :param f_p2: the fraction of the first piston flow model (only used for binary_exponential_piston_flow model)

        Model run options:

        :param seed: int or None for random seed
        :param testnitter: None (usually) or a different nitter then self.niter for testing run times
        :param kwargs: kwargs passed to the output series (e.g. region='temp' will yield a 'region' index with a value of 'temp')
        :return: pd.Seris with the power calc results note power is percent 0-100 Possible other dataframes if self.return_true_conc is True or self.return_noisy_conc_itters > 0 in which case a dictionary will be returned:

        {'power': power_df, # always
        'true_conc': true_conc_ts, if self.return_true_conc is True
        'noisy_conc' : noisy_conc_ts, if self.return_noisy_conc_itters > 0
        }
        """
        if testnitter is not None:
            warnings.warn('testnitter is expected to be None unless you are testing run times')

        assert mrt_model in self.implemented_mrt_models, f'mrt_model must be one of: {self.implemented_mrt_models}'
        assert pd.api.types.is_integer(samp_years), 'samp_years must be an integer '
        assert pd.api.types.is_integer(samp_per_year), 'samp_per_year must be an integer '
        assert pd.api.types.is_number(initial_conc), 'initial_conc must be a number '
        assert pd.api.types.is_number(target_conc), 'target_conc must be a number '
        assert pd.api.types.is_number(prev_slope), 'prev_slope must be a number '
        assert pd.api.types.is_number(max_conc_lim), 'max_conc must be a number '
        assert max_conc_lim >= initial_conc, 'max_conc must be greater than or equal to initial_conc'
        assert max_conc_lim >= target_conc, 'max_conc must be greater than or equal to target_conc'
        assert pd.api.types.is_integer(implementation_time)

        # mange lag
        if mrt_model == 'piston_flow':
            if self.significance_mode == 'pettitt-test' and mrt != 0:
                warnings.warn('using the Pettitt test with lagged data can cause some weird results, we do'
                              'not recommend using this combination')

            true_conc_ts, max_conc_val, max_conc_time, mrt_p2 = self.truets_from_piston_flow(mrt,
                                                                                             initial_conc, target_conc,
                                                                                             prev_slope, max_conc_lim,
                                                                                             samp_per_year, samp_years,
                                                                                             implementation_time)
            if self.expect_slope == 'auto':
                expect_slope = (target_conc - initial_conc) / implementation_time
            else:
                expect_slope = self.expect_slope

        elif mrt_model == 'binary_exponential_piston_flow':
            if self.significance_mode == 'pettitt-test' and mrt != 0:
                warnings.warn('using the Pettitt test with lagged data can cause some weird results, we do'
                              'not recommend using this combination')
            tvs = ['mrt_p1', 'frac_p1', 'f_p1', 'f_p2', 'min_conc_lim']
            bad = []
            for t in tvs:
                if eval(t) is None:
                    bad.append(t)
            if len(bad) > 0:
                raise ValueError(f'for binary_exponential_piston_flow model the following must be specified: {bad}')

            (true_conc_ts, max_conc_val,
             max_conc_time, mrt_p2) = self.truets_from_binary_exp_piston_flow(
                mrt, mrt_p1, frac_p1, f_p1, f_p2,
                initial_conc, target_conc, prev_slope, max_conc_lim, min_conc_lim,
                samp_per_year, samp_years, implementation_time,
                return_extras=False)
            if self.expect_slope == 'auto':
                expect_slope = (target_conc - initial_conc) / implementation_time
            else:
                expect_slope = self.expect_slope

        else:
            raise NotImplementedError(f'mrt_model {mrt_model} not currently implemented')

        out_data = self._run_power_calc(testnitter=testnitter,
                                        seed=seed,
                                        true_conc_ts=true_conc_ts,
                                        idv=idv,
                                        error=error,
                                        expect_slope=expect_slope,
                                        max_conc_val=max_conc_val,
                                        max_conc_time=max_conc_time,
                                        mrt_model=mrt_model,
                                        samp_years=samp_years,
                                        samp_per_year=samp_per_year,
                                        implementation_time=implementation_time,
                                        initial_conc=initial_conc,
                                        target_conc=target_conc,
                                        prev_slope=prev_slope,
                                        max_conc_lim=max_conc_lim,
                                        min_conc_lim=min_conc_lim,
                                        mrt=mrt,
                                        mrt_p1=mrt_p1,
                                        mrt_p2=mrt_p2,
                                        frac_p1=frac_p1,
                                        f_p1=f_p1,
                                        f_p2=f_p2,
                                        **kwargs)

        return out_data

    def mulitprocess_power_calcs(
            self,
            outpath: {Path, None, str},
            idv_vals: np.ndarray,
            error_vals: {np.ndarray, float},
            samp_years_vals: {np.ndarray, int},
            samp_per_year_vals: {np.ndarray, int},
            implementation_time_vals: {np.ndarray, int},
            initial_conc_vals: {np.ndarray, float},
            target_conc_vals: {np.ndarray, float},
            prev_slope_vals: {np.ndarray, float},
            max_conc_lim_vals: {np.ndarray, float},
            min_conc_lim_vals: {np.ndarray, float},
            mrt_model_vals: {np.ndarray, str},
            mrt_vals: {np.ndarray, float},
            mrt_p1_vals: {np.ndarray, float, None} = None,
            frac_p1_vals: {np.ndarray, float, None} = None,
            f_p1_vals: {np.ndarray, float, None} = None,
            f_p2_vals: {np.ndarray, float, None} = None,
            seed_vals: {np.ndarray, int, None} = None,
            run=True, debug_mode=False, **kwargs
    ):
        """
        multiprocessing wrapper for power_calc, see power_calc for details

        :param outpath: a path to save the results to or None (no save), df is returned regardless
        :param idv_vals: an array of identifiers for each simulation
        :param error_vals: The standard deviation of the noise for each simulation
        :param samp_years_vals: the number of years to sample
        :param samp_per_year_vals: The number of samples to collect each year
        :param implementation_time_vals: The number of years over which reductions are implemented
        :param initial_conc_vals: The initial concentration for each simulation
        :param target_conc_vals:  target concentration for the simulation
        :param prev_slope_vals: previous slope for each simulation
        :param max_conc_lim_vals: maximum concentration limit for each simulation
        :param min_conc_lim_vals: minimum concentration limit for the source for each simulation
        :param mrt_model_vals: mrt model for each simulation
        :param mrt_vals: mean residence time for each simulation
        :param mrt_p1_vals: mean residence time of the first piston flow model for each simulation Only used for binary_exponential_piston_flow model
        :param frac_p1_vals: fraction of the first piston flow model for each simulation Only used for binary_exponential_piston_flow model
        :param f_p1_vals: the exponential fraction of the first piston flow model for each simulation Only used for binary_exponential_piston_flow model
        :param f_p2_vals: the exponential fraction of the second piston flow model for each simulation Only used for binary_exponential_piston_flow model
        :param seed: the random seed for each simulation, one of the following:

                            * None: no seed, random seed will be generated for each simulation (but it will be recorded in the output dataframe)
                            * int: a single seed for all simulations
                            * np.ndarray: an array of seeds, one for each simulation

        :param run: if True run the simulations, if False just build  the run_dict and print the number of simulations
        :param debug_mode: if True run as single process to allow for easier debugging
        :param kwargs: other kwargs to pass directly to the output dataframe must be either a single value or an array of values with the same shape as id_vals
        :return: dataframe with input data and the results of all of the power calcs. note power is percent 0-100
        """

        use_kwargs = dict(error_vals=error_vals,
                          seed_vals=seed_vals,
                          samp_years_vals=samp_years_vals,
                          samp_per_year_vals=samp_per_year_vals,
                          implementation_time_vals=implementation_time_vals,
                          initial_conc_vals=initial_conc_vals,
                          target_conc_vals=target_conc_vals,
                          prev_slope_vals=prev_slope_vals,
                          max_conc_lim_vals=max_conc_lim_vals,
                          min_conc_lim_vals=min_conc_lim_vals,
                          mrt_model_vals=mrt_model_vals,
                          mrt_vals=mrt_vals,
                          mrt_p1_vals=mrt_p1_vals,
                          frac_p1_vals=frac_p1_vals,
                          f_p1_vals=f_p1_vals,
                          f_p2_vals=f_p2_vals,
                          **kwargs)

        return self._run_multiprocess_auto(outpath, idv_vals, run, debug_mode, use_kwargs)
