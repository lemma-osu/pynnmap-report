import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from scipy.stats import gaussian_kde

from pynnmap.misc import statistics


(SCREEN, FILE) = range(2)
mpl.rcParams['font.family'] = 'Open Sans'


class Scatterplot(object):
    def __init__(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)
        self.limits = self._get_limits()

    def __call__(self, **kwargs):
        # Set up the figure
        self._initialize_figure()

        # Draw the figure
        kde = kwargs.get('kde', True)
        self._draw(*self._get_series(kde=kde), **kwargs)

    def _get_limits(self):
        # Find the min and max of both axes
        x_min, y_min = self.x.min(), self.y.min()
        x_max, y_max = self.x.max(), self.y.max()
        abs_min = x_min if x_min < y_min else y_min
        abs_max = x_max if x_max > y_max else y_max
        return [abs_min, abs_max, abs_max - abs_min]

    def _initialize_figure(self):
        fig = plt.gcf()
        fig.clf()
        fig.set_figwidth(3.2)
        fig.set_figheight(3.2)
        fig.set_dpi(400)
        mn, mx, rng = self.limits
        buf = 0.01 * rng
        plt.xlim(mn - buf, mx + buf)
        plt.ylim(mn - buf, mx + buf)

    def _get_series(self, kde=True):
        # Calculate the point density
        xy = np.vstack([self.x, self.y])
        if kde:
            # Sort the points by density, so that the densest points are
            # plotted last
            z = gaussian_kde(xy)(xy)
            idx = z.argsort()
            return self.x[idx], self.y[idx], z[idx]
        else:
            return self.x, self.y, 'blue'

    def _draw(self, x, y, z, **kwargs):
        # References to current figure and axes
        fig = plt.gcf()
        ax = plt.gca()

        # Draw the scatterplot data
        ax.scatter(x, y, s=4, c=z, edgecolor='', linewidth=0.25)

        # Labels - set the y label to a fixed location
        ax.set_ylabel(kwargs.get('y_label', 'Y'), size=5.0)
        ax.set_xlabel(kwargs.get('x_label', 'X'), size=5.0)
        ax.yaxis.set_label_coords(-0.120, 0.5)

        # Tick formatting - create five ticks and format labels to be
        # consistent
        mn, mx = self.limits[0:2]
        ticks = np.linspace(mn, mx * 0.95, 5)
        if mx > 1000.0:
            labels = []
            for t in ticks:
                base, exponent = '{:.1e}'.format(t).split('e')
                labels.append('{:.1f}e{:d}'.format(float(base), int(exponent)))
        else:
            labels = ['{:.1f}'.format(t) for t in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, size=4.5)
        ax.set_yticks(ticks)
        ax.set_yticklabels(labels, size=4.5)

        # Position the main axes within the figure
        ax.set_position([0.14, 0.100, 0.85, 0.880])
        _ = [ax.spines[x].set_linewidth(0.2) for x in ax.spines]

        # Draw light grid lines
        mn, mx = self.limits[0:2]
        lines = np.linspace(mn, mx, 7)[1:-1]
        for l in lines:
            ax.plot([l, l], [mn, mx], 'k:', linewidth=0.2)
            ax.plot([mn, mx], [l, l], 'k:', linewidth=0.2)

        # Set fill and edge for the figure
        fig.patch.set_edgecolor('k')
        fig.patch.set_linewidth(2.0)


class ObservedPredictedScatterplot(Scatterplot):
    def _draw(self, x, y, z, **kwargs):
        # Call the superclass _draw
        super(ObservedPredictedScatterplot, self)._draw(x, y, z, **kwargs)

        # References to current axes
        ax = plt.gca()

        # Calculate statistics
        corr = statistics.pearson_r(x, y)
        rmse = statistics.rmse(x, y) / x.mean()
        r2 = statistics.r2(x, y)

        # Draw the 1:1 line
        mn, mx = self.limits[0:2]
        plt.plot([mn, mx], [mn, mx], 'k-', linewidth=0.5)

        # Draw the annotation text on the figure
        t = ax.transAxes
        plt.text(
            0.89, 0.93,
            '1:1', transform=t, size=4.5, rotation=45)
        plt.text(
            0.05, 0.93,
            'Correlation coeff.: %.4f' % corr, transform=t, size=5.0)
        plt.text(
            0.05, 0.89,
            'Normalized RMSE: %.4f' % rmse, transform=t, size=5.0)
        plt.text(
            0.05, 0.85,
            'R-square: %.4f' % r2, transform=t, size=5.0)

        # Set patch to highlight text in case data points obscure it
        rect = patches.Rectangle(
            (0.04, 0.84), 0.38, 0.12, transform=t, facecolor='white',
            edgecolor='none', zorder=3)
        ax.add_patch(rect)


class LemmaScatterplot(ObservedPredictedScatterplot):
    def _draw(self, x, y, z, variable='V', units='u', **kwargs):
        # Ensure that axis labels are set for kwargs
        kwargs['x_label'] = 'Predicted {} ({})'.format(variable, units)
        kwargs['y_label'] = 'Observed {} ({})'.format(variable, units)

        # Call the superclass _draw
        super(LemmaScatterplot, self)._draw(x, y, z, **kwargs)


def draw_scatterplot(df, attr, output_file='foo.png', **kwargs):
    # Extract the predicted and observed series from the data frame
    name, units = attr.field_name, attr.units
    x, y = df[name+'_P'], df[name+'_O']

    # Create the figure
    LemmaScatterplot(x, y)(variable=name, units=units, **kwargs)

    # Output to file
    plt.draw()
    plt.savefig(output_file, edgecolor='k')
