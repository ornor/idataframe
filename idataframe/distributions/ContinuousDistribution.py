import re
import numpy as np
import pandas as pd
import plotnine as pn
from scipy import stats, signal # , interpolate

from idataframe.tools import display_auto, display_hide
from idataframe.distributions.BaseDistribution import BaseDistribution

__all__ = ['ContinuousDistribution']


#-----------------------------------------------------------------------------


class ContinuousDistribution(BaseDistribution):
    """
    Creates a continuous distribution object based an a SciPy distribution object.

    It is also possible to create the distribution from a Pandas Series (it will fit the data):
    ```
    pandas_series = pd.read_csv("test.csv")['test_column_series_name']
    distr = ContinuousDistribution.from_pandas_series(pandas_series)

    print(distr.type, '\n')
    print(distr.cdf(60) - distr.cdf(20), '\n')
    print(distr.cdf_inv(0.50), '\n')
    print(distr.median, '\n')
    print(distr.random(100), '\n')
    print(distr.data, '\n')
    print(distr.data[distr.is_dirty], '\n')
    ```

    """

    def __init__(self, scipy_distr_name, scipy_distr_object, parameters):
        super().__init__()

        self.type = scipy_distr_name
        self.scipy_obj = scipy_distr_object
        self.parameters = parameters

        self.data = None        # from_pandas_series  -->  original data series
        self.is_dirty = None    # from_pandas_series  -->  mask (boolean) whether index is outlier or null
        self.is_clean = None    # from_pandas_series  -->  mask (boolean) whether index is NOT outlier or null

        self.stdev = self.scipy_obj.std(*self.parameters)
        self.median = self.scipy_obj.median(*self.parameters)
        (self.mean,
        self.variance,
        self.skew,
        self.kurtosis) = self.scipy_obj.stats(*self.parameters, moments='mvsk')

    def pdf(self, x):
        "Probability density function"
        p = self.scipy_obj.pdf(x, *self.parameters)
        return p

    def cdf(self, x):
        "Cumulative distribution function"
        p = self.scipy_obj.cdf(x, *self.parameters)
        return p

    def cdf_inv(self, p):
        "Inverse of cdf (is equal to percent point function)"
        x = self.scipy_obj.ppf(p, *self.parameters)
        return x

    def random(self, n):
        "Generate a list of a certain amount of random values"
        return self.scipy_obj.rvs(*self.parameters, n)


    @classmethod
    def from_pandas_series(cls, data:pd.Series,
            # function to display output of analysis (None --> hide output); available functions are defined inside IDataFrame.tools module
            display=display_auto,   # display_hide

            # list of continuous distribution names (https://docs.scipy.org/doc/scipy/reference/stats.html#continuous-distributions) seperated by ','
            distributions="beta,cauchy,expon,gamma,gumbel_l,gumbel_r,logistic,lognorm,norm,weibull_min,weibull_max",

            # check data for outliers removal, given a certain significance level
            outliers_number_of_checks=100,     # if more than 10% of this number is positive (is an outlier), then an equal amount of checks will be added
            outliers_significance_level=5,     # in percentage, alpha value; also used by normality test (Shapiro)

            # number of x-coordinates in pdf and cdf (fit) plots (number of plotting points per line)
            n_x=1000,

            # TODO     unsigned number -> x_min = 0      ensure that pdf function follows x_min and x_max
            x_min=None,
            x_max=None,

            # number of histogram bins (manual) used by pdf function
            n_bins=None,                       # manually given number of bins
            smooth_factor=1,                   # from histogram (horizontal steps) untill pdf line, this smooth factor will be used (if 0 or None, then the pdf line is the histogram-step-line)

            # if n_bins is None, then number of bins is determined automatically
            n_bins_auto_start=100,             # this is starting number, from here this number will be decreased (if the number of peaks/maxima is greater than max_peaks)
            n_bins_auto_decrease_by=0.90,      # every step, the number of bins will be decreased by a factor of
            interval=None,                     # interval step value; when set, the width of bin has a minimum value of 'interval'; the n_bins_auto_start will be overruled using this width
            n_bins_min=5,                      # always use this minimum number of bins
            max_peaks=5,                       # the iterative process will stop when a number of peaks has reached; a peak is a value with lower neigbouring values (left AND right)

            # if True, all value's of zero, will be treated as nan (not a number)
            treat_zero_as_nan=True,

            # if True, all the plots will have a logoritmic axis; there is also a normality check which auto enable log_scale
            log_scale=False,

            # draw a histogram plot inside pdf plot
            draw_histogram_plot=True,

            # maximum number of fitting plots (with the lowest average error)
            max_plot_distributions = 10,

            # draw a density plot using ggplot to check if drawn pdf simplification is valid (this can be a time consuming process)
            draw_control_pdf_plot=False,

            # sets a default width size of the plots
            default_plot_width=9):

        if display is None:
            display = display_hide

        if distributions == 'ALL':
            distributions = """
                alpha,anglit,arcsine,argus,beta,betaprime,bradford,burr,burr12,cauchy,chi,chi2,
                cosine,crystalball,dgamma,dweibull,erlang,expon,exponnorm,exponweib,exponpow,f,
                fatiguelife,fisk,foldcauchy,foldnorm,genlogistic,gennorm,genpareto,genexpon,
                genextreme,gausshyper,gamma,gengamma,genhalflogistic,genhyperbolic,geninvgauss,
                gibrat,gompertz,gumbel_r,gumbel_l,halfcauchy,halflogistic,halfnorm,halfgennorm,
                hypsecant,invgamma,invgauss,invweibull,jf_skew_t,johnsonsb,johnsonsu,kappa4,
                kappa3,ksone,kstwobign,laplace,laplace_asymmetric,levy,levy_l,
                logistic,loggamma,loglaplace,lognorm,loguniform,lomax,maxwell,mielke,moyal,
                nakagami,ncx2,ncf,nct,norm,norminvgauss,pareto,pearson3,powerlaw,powerlognorm,
                powernorm,rdist,rayleigh,rel_breitwigner,rice,recipinvgauss,semicircular,
                skewcauchy,skewnorm,t,trapezoid,triang,truncexpon,truncnorm,
                truncpareto,truncweibull_min,tukeylambda,uniform,vonmises,vonmises_line,wald,
                weibull_min,weibull_max,wrapcauchy
            """
            # list of all distributions that takes too long or give many errors:
            #     kstwo,levy_stable,studentized_range

        self_data = data
        self_is_dirty = pd.Series(np.full(len(data), False))  # create empty series

        data_dirty = self_data.copy()
        data_name = data_dirty.name if hasattr(data_dirty, 'name') and data_dirty.name is not None else '<no name>'
        display('<hr/>')
        display('fitting data: {}'.format(data_name))
        display('<hr/>')
        display()

        # check on empty/falsy values
        n_dirty = len(data_dirty)
        self_is_dirty = self_is_dirty | self_data.isna()
        data_dirty = data_dirty.dropna()
        display('dropped {} empty values'.format(n_dirty - len(data_dirty)))
        if treat_zero_as_nan:
            n_dirty = len(data_dirty)
            self_is_dirty = self_is_dirty | self_data[(self_data >= -1e-5) & (self_data <= 1e-5)]
            data_dirty = data_dirty[(data_dirty < -1e-5) | (data_dirty > 1e-5)]
            display('dropped {} zero values'.format(n_dirty - len(data_dirty)))
        n_dirty = len(data_dirty)
        if n_dirty == 0:
            display('there are no values (remaining) -->  exit analysis')
            return
        display()

        # plot the initial non empty/falsy values in a box plot
        pn.options.set_option('figure_size', (default_plot_width,2))
        plot_boxplot_dirty = (pn.ggplot(pd.DataFrame({'data': data_dirty}))
            + pn.ggtitle(data_name)
            + pn.geom_boxplot(pn.aes(y='data'))
            + pn.coord_flip()
            + pn.xlab(' ')
            + pn.ylab(' ')
            + pn.theme(axis_text_y=pn.element_blank(),
                       axis_ticks_y=pn.element_blank(),
                       panel_grid_major_y=pn.element_blank(),
                       panel_grid_minor_y=pn.element_blank())
        )
        display(plot_boxplot_dirty)

        # determine and drop the outliers
        display('start removing outliers')
        # Generalized ESD Many-Oulier Procedure (Boris Iglewicz & David C. Hoaglin: Volume 16 - How to detect and handle outliers - paragraph 5.2.1)
        # test normality using Shapiro-Wilk (https://www.statology.org/normality-test-python/)
        # if not normal, than pre and post transform data to approx normal to remove outliers
        pre_transform_fn = lambda series: series
        post_transform_fn = lambda series: series
        shapiro_pvalue_reject_value = outliers_significance_level/100  # if greater, then normal
        normality_test = stats.shapiro(data_dirty)
        if normality_test.pvalue > shapiro_pvalue_reject_value:
            display('performing Shapiro-Wilk test (normal):     p-value = {:.2e}  -->  since it is greater than {:.2f}, data seams to be normal'.format(normality_test.pvalue, shapiro_pvalue_reject_value))
        else:
            display('performing Shapiro-Wilk test (normal):     p-value = {:.2e}  -->  since it is less than {:.2f}, data seams to be NOT normal'.format(normality_test.pvalue, shapiro_pvalue_reject_value))
            log_test = stats.shapiro(np.log(data_dirty))
            sqrt_test = stats.shapiro(np.sqrt(data_dirty))
            cbrt_test = stats.shapiro(np.cbrt(data_dirty))
            display('  -->  trying log transformation:          p-value = {:.2e}'.format(log_test.pvalue))
            display('  -->  trying square root transformation:  p-value = {:.2e}'.format(sqrt_test.pvalue))
            display('  -->  trying cube root transformation:    p-value = {:.2e}'.format(cbrt_test.pvalue))
            if normality_test.pvalue >= log_test.pvalue and normality_test.pvalue >= sqrt_test.pvalue and normality_test.pvalue >= cbrt_test.pvalue:
                display('p-value of normal test is still greatest  -->  NOT using transformations')
            elif log_test.pvalue >= sqrt_test.pvalue and log_test.pvalue >= cbrt_test.pvalue:
                display('p-value of log test is greatest  -->  using log transformation')
                pre_transform_fn = lambda series: np.log(series)
                post_transform_fn = lambda series: np.exp(series)
                log_scale = True
            elif sqrt_test.pvalue >= cbrt_test.pvalue:
                display('p-value of square root test is greatest  -->  using square root transformation')
                pre_transform_fn = lambda series: np.sqrt(series)
                post_transform_fn = lambda series: np.power(series, 2)
                log_scale = True
            else:
                display('p-value of cube root test is greatest  -->  using cube root transformation')
                pre_transform_fn = lambda series: np.cbrt(series)
                post_transform_fn = lambda series: np.power(series, 3)
                log_scale = True

        # helper function
        def remove_outliers(input_series, previously_found_number_of_outliers=0):
            nonlocal self_is_dirty
            alpha = outliers_significance_level/100
            max_outliers = outliers_number_of_checks
            number_of_outliers = 0
            for iteration in range(1, max_outliers + 1):
                std_dev = np.std(input_series)
                avg_input_series = np.mean(input_series)
                abs_val_minus_avg = abs(input_series - avg_input_series)
                max_of_deviations = max(abs_val_minus_avg)
                max_index = np.argmax(abs_val_minus_avg)
                stat = max_of_deviations / std_dev
                size = len(input_series)
                t_dist = stats.t.ppf(1 - alpha / (2 * size), size - 2)
                critical = ((size - 1) * np.sqrt(np.square(t_dist))) / (np.sqrt(size) * np.sqrt(size - 2 + np.square(t_dist)))
                if stat > critical:
                    outlier_value = input_series[max_index]
                    display('found outlier number {}  ::  {}  -->  R {:.4f} > λ {:.4f}'.format(previously_found_number_of_outliers + number_of_outliers,
                                                                                             outlier_value, stat, critical), end='\r')
                    number_of_outliers += 1
                    self_is_dirty = self_is_dirty | (self_data == outlier_value)
                    input_series = np.delete(input_series, max_index)

            total_number_of_outliers = previously_found_number_of_outliers + number_of_outliers
            if number_of_outliers > 0.1 * max_outliers:
                # if found that more than 10% is outlier; check an extra set of posible outliers
                # iterative callback of the helper function
                return remove_outliers(input_series, total_number_of_outliers)
            else:
                return pd.Series(input_series), total_number_of_outliers

        data_dirty = pre_transform_fn(data_dirty)
        data, number_of_outliers = remove_outliers(data_dirty)  # start iterative process
        data = post_transform_fn(data)

        n_data = len(data)
        display(200*' ', end='\r')
        display(('dropped {} outliers from data'.format(number_of_outliers) if number_of_outliers != 1 else 'removed 1 outlier from data') + ' using generalized ESD (many-outlier) procedure')
        display('total number of valid values is: {}'.format(n_data))
        display()

        display('final data set:')
        if n_data < 26:
            display('' + ', '.join((str(v) for v in data)) + '')
        else:
            display('' + ', '.join((str(v) for v in data[:10])) + ',  ...  , ' + ', '.join((str(v) for v in data[-10:])) + '')
        display()

        # show a boxplot of cleaned data (without outliers)
        if log_scale:
            display('using a logarithmic scale (base=10) for plots and histogram bins')
            display()
        if number_of_outliers > 0 or log_scale:
            pn.options.set_option('figure_size', (default_plot_width,2))
            plot_boxplot_data =  (pn.ggplot(pd.DataFrame({'data': data}))
                + pn.ggtitle(data_name + '')
                + pn.geom_boxplot(pn.aes(y='data'))
                + pn.coord_flip()
                + pn.xlab(' ')
                + pn.ylab(' ')
                + pn.theme(axis_text_y=pn.element_blank(),
                           axis_ticks_y=pn.element_blank(),
                           panel_grid_major_y=pn.element_blank(),
                           panel_grid_minor_y=pn.element_blank())
            )
            if log_scale:
                plot_boxplot_data = plot_boxplot_data + pn.scale_y_continuous(trans='log10')
            display(plot_boxplot_data)

        data_sorted = data.sort_values()
        data_min = data.min()
        data_max = data.max()

        # create x values on horizontal axis
        if log_scale:
            x = np.logspace(np.log10(data_min), np.log10(data_max), n_x, base=10.0)
        else:
            x = np.linspace(data_min, data_max, n_x)

        # calculate number of histogram bins
        # pdf data line uses bins on horizontal axis; after that it uses x values
        auto_n_bins = True if n_bins is None else False
        n_bins = (n_bins if not auto_n_bins
                         else (n_bins_auto_start if interval is None
                                                 else int(np.floor((data_max - data_min)/interval))))
        n_bins = max(n_bins, n_bins_min)
        if log_scale:
            x_bins = np.logspace(np.log10(data_min), np.log10(data_max), n_bins, base=10.0)
        else:
            x_bins = np.linspace(data_min, data_max, n_bins)
        pdf_values_bins = None
        calculate_bins = True
        if auto_n_bins:
            display('start auto determine number of histogram bins using: max_peaks = {}'.format(max_peaks))
            display('begin using n_bins = {} and decrease n_bins using a factor of {}'.format(n_bins, n_bins_auto_decrease_by))
        else:
            display('start calculating histogram using an amount of bins: n_bins = {}'.format(n_bins))
            display()
        while calculate_bins:
            # iterative process to determine optimal number of bins
            pdf_values_bins = []
            n_bins = n_bins if n_bins is not None else n_bins_auto_start
            if log_scale:
                x_bins = np.logspace(np.log10(data_min), np.log10(data_max), n_bins, base=10.0)
            else:
                x_bins = np.linspace(data_min, data_max, n_bins)
            i = 0  # number of data items
            n_peaks = 0
            total_area = 0
            minus0_value = None
            minus1_value = None
            minus2_value = None
            for i_bin in range(n_bins):
                # for every bin, calculute the pdf value
                count = 0   # count number of data items inside bin
                if i_bin == 0:         # first bin
                    while (i < n_data
                           and data_sorted.iloc[i] < (x_bins[i_bin] + x_bins[i_bin+1])/2):
                        count += 1
                        i += 1
                    total_area += ((x_bins[i_bin] + x_bins[i_bin+1])/2 - x_bins[i_bin]) * count
                elif i_bin >= n_bins-1:  # last bin
                    while (i < n_data
                           and data_sorted.iloc[i] >= (x_bins[i_bin-1] + x_bins[i_bin])/2):
                        count += 1
                        i += 1
                    total_area += (x_bins[i_bin] - (x_bins[i_bin] + x_bins[i_bin-1])/2) * count
                else:
                    while (i < n_data
                           and data_sorted.iloc[i] >= (x_bins[i_bin-1] + x_bins[i_bin])/2
                           and data_sorted.iloc[i] < (x_bins[i_bin] + x_bins[i_bin+1])/2):
                        count += 1
                        i += 1
                    total_area += ((x_bins[i_bin] + x_bins[i_bin+1])/2 - (x_bins[i_bin] + x_bins[i_bin-1])/2) * count
                pdf_values_bins.append(count)
                # check if new value is a peak (used by auto binning)
                minus2_value = minus1_value
                minus1_value = minus0_value
                minus0_value = count
                if (minus2_value is not None and minus1_value is not None) and (minus2_value < minus1_value and minus0_value < minus1_value):
                    n_peaks += 1
                if auto_n_bins and n_peaks >= max_peaks:
                    break   # reached maximum number of peaks, don't continue calculating values and recalculate all bins using less bins
            pdf_values_bins = np.array(pdf_values_bins) / total_area
            if not auto_n_bins or n_peaks < max_peaks or n_bins <= n_bins_min or int(round(n_bins * n_bins_auto_decrease_by)) == n_bins:
                calculate_bins = False
            else:
                n_bins = int(round(n_bins * n_bins_auto_decrease_by))    # make smaller amount of bins and calculate again
                x_bins = np.linspace(data_min, data_max, n_bins)
        if auto_n_bins:
            display('found (approx) maximum number of peaks using: n_bins = {}'.format(n_bins))
            display()

        # TODO  log PDF curve doesn't match the scipy curves -> fix

        # calculate histogram x values (also calculate all the y values on the horizontal bin lines)
        pdf_values_bins_x = []
        i_bin = 0
        for i_x in range(n_x):
            pdf_values_bins_x.append(pdf_values_bins[i_bin])
            while (i_bin < n_bins-1
                   and x[i_x] >= (x_bins[i_bin] + x_bins[i_bin+1])/2):
                i_bin += 1

        # pdf values using convolutions (more info: https://www.youtube.com/watch?v=KuXjwB4LzSA)
        if smooth_factor == 0 or smooth_factor is None:
            pdf_values = pdf_values_bins_x
        else:
            convolution_key_deviation = 0.5 * smooth_factor * n_x/n_bins
            convolution_key = ([stats.norm.pdf(i, 0, convolution_key_deviation) for i in range(-1*int(n_x/2), 0)]
                                + [stats.norm.pdf(0, 0, convolution_key_deviation) ]
                                + [stats.norm.pdf(i, 0, convolution_key_deviation) for i in range(int(n_x/2))])
            pdf_values = signal.fftconvolve(pdf_values_bins_x, convolution_key, mode='same')

        # calculate cdf values
        cdf_values_data = [i/n_data for i in range(n_data)]
        cdf_values = [0]
        i_x = 0
        for i in range(n_data-1):
            while (data_sorted.iloc[i+1] >= x[i_x]
                   and i_x < n_x-1):
                cdf_values.append(cdf_values_data[i+1])
                i_x += 1
            if i_x >= n_x-1:
                break
        cdf_values[-1] = 1.0  # fix endpoint

        pn.options.set_option('figure_size', (default_plot_width,5))
        plot_pdf = (pn.ggplot(pd.DataFrame({'x':x, 'pdf_values':pdf_values}))
            + pn.ggtitle('{} pdf'.format(data_name))
            # + pn.theme(legend_position='top')
            + pn.geom_line(pn.aes(x='x', y='pdf_values'), color='black', size=1.5)
            + pn.xlim(data_min, data_max)
            + pn.ylim(0, 1.25 * max(max(pdf_values), max(pdf_values_bins)))
            + pn.xlab(' ')
            + pn.ylab(' ')
        )
        if log_scale:
            plot_pdf = plot_pdf + pn.scale_x_continuous(trans='log10')
        if draw_histogram_plot:
            plot_pdf = plot_pdf + pn.geom_area(pd.DataFrame({'histogram_data':pdf_values_bins_x}), pn.aes(x='x', y='histogram_data'), color='grey', fill='grey', alpha=0.2, size=0.5)

        pn.options.set_option('figure_size', (default_plot_width,5))
        plot_cdf = (pn.ggplot(pd.DataFrame({'x':x, 'cdf_values':cdf_values}))
            + pn.ggtitle('{} cdf'.format(data_name))
            + pn.geom_area(pn.aes(x='x', y='cdf_values'), color='black', fill='grey', alpha=0.2, size=1.5)
            + pn.xlim(data_min, data_max)
            + pn.ylim(0, 1)
            + pn.xlab(' ')
            + pn.ylab(' ')
        )
        if log_scale:
            plot_cdf = plot_cdf + pn.scale_x_continuous(trans='log10')

        fit_data = data
        avg_errors = []
        best_fit_error = None
        best_fit_distribution = None
        def calc_distr(scipy_distr_name, fit_df):
            nonlocal best_fit_error, best_fit_distribution
            distr = getattr(stats, scipy_distr_name)
            display('start fitting', scipy_distr_name.upper())

            try:
                distr_params = distr.fit(fit_data)
            except Exception as e:
                display('    ERROR  {}  -->  ignore distribution'.format( str(e.message if hasattr(e, 'message') else e) ))
                return None
            pdf_fit = distr.pdf(x, *distr_params)
            cdf_fit = distr.cdf(x, *distr_params)

            avg_error = sum([(cdf_values[i] - cdf_fit[i])**2 for i, value in enumerate(x)]) / n_x
            statistics = distr.stats(*distr_params, moments='mvsk')
            mean = statistics[0]
            variance = statistics[1]
            skew = statistics[2]
            kurtosis = statistics[3]
            avg_errors.append((avg_error, '- {:>6}  {:<16} {:<60}  {:>10.3f} (m)  {:>10.3f} (v)  {:>10.3f} (s)  {:>10.3f} (k)'.format(str(int(round(avg_error * 10**6))),
                                                                            scipy_distr_name,
                                                                            str(tuple(np.round(distr_params, 6))),
                                                                            mean, variance, skew, kurtosis )))
            if best_fit_error is None or avg_error < best_fit_error:
                best_fit_error = avg_error
                best_fit_distribution = (scipy_distr_name, distr, distr_params)

            fit_df_dist = pd.DataFrame({'x': x, 'pdf': pdf_fit, 'cdf': cdf_fit})
            fit_df_dist['error'] = avg_error
            fit_df_dist['distribution'] = '{:.6f} {}'.format(avg_error, scipy_distr_name)  # must match with plot line here below
            fit_df = pd.concat([fit_df, fit_df_dist], ignore_index=True)

            return fit_df

        fit_df = pd.DataFrame(columns=['x', 'pdf', 'cdf', 'distribution'])
        for dist_name in distributions.split(','):
            dist_name = re.sub('\s+', '', dist_name)
            if dist_name:
                calc_result = calc_distr(dist_name, fit_df)
                if calc_result is not None:
                    fit_df = calc_result

        fit_df_head = fit_df.sort_values(by=['error'], ascending=True).head(max_plot_distributions*n_x)
        plot_pdf = plot_pdf + pn.geom_line(fit_df_head, pn.aes(x='x', y='pdf', color='distribution'), size=1.0, alpha=0.8)
        plot_cdf = plot_cdf + pn.geom_line(fit_df_head, pn.aes(x='x', y='cdf', color='distribution'), size=1.0, alpha=0.8)

        fit_df_best = fit_df[fit_df['distribution'] == '{:.6f} {}'.format(best_fit_error, best_fit_distribution[0])]   # must match with line here above
        plot_pdf = plot_pdf + pn.geom_line(fit_df_best, pn.aes(x='x', y='pdf'), size=1.0, alpha=0.8, color='red')
        plot_cdf = plot_cdf + pn.geom_line(fit_df_best, pn.aes(x='x', y='cdf'), size=1.0, alpha=0.8, color='red')

        if draw_control_pdf_plot:
            plot_pdf = plot_pdf + pn.geom_density(pd.DataFrame({'density_data':data}), pn.aes(x='density_data'), color='red', size=1)

        display()
        display(plot_pdf)
        display(plot_cdf)
        display()
        display('(sorted) average error (* 10^-6) using distribution (+ fitted parameters + mean/variance/skew/kurtosis):\n' + '\n'.join([e[1] for e in sorted(avg_errors, key=lambda e: e[0])]))
        display()

        instance = cls(*best_fit_distribution)
        instance.data = self_data
        instance.is_dirty = self_is_dirty
        instance.is_clean = -self_is_dirty

        return instance

    # -------------   end of classmethod 'from_pandas_series'   ---------------------------------