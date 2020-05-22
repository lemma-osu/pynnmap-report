import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager, patches
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from scipy.stats import gaussian_kde

from pynnmap.misc import statistics
from pynnmap.parser.xml_stand_metadata_parser import XMLAttributeField


mpl.rcParams["font.family"] = "Open Sans"


def get_global_limits(*iterables):
    return min(min(x) for x in iterables), max(max(x) for x in iterables)


class Scatterplot:
    def __init__(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)
        self.min, self.max = get_global_limits(self.x, self.y)

    def __call__(self, **kwargs):
        self._initialize_figure(3.2, 3.2)
        kde = kwargs.get("kde", True)
        self._draw(*self._symbolize_series(kde=kde), **kwargs)

    def _get_limits(self):
        # Find the min and max of both axes
        x_min, y_min = self.x.min(), self.y.min()
        x_max, y_max = self.x.max(), self.y.max()
        abs_min = x_min if x_min < y_min else y_min
        abs_max = x_max if x_max > y_max else y_max
        return [abs_min, abs_max, abs_max - abs_min]

    def _initialize_figure(self, width, height, dpi=250):
        fig = plt.gcf()
        fig.clf()
        fig.set_figwidth(width)
        fig.set_figheight(height)
        fig.set_dpi(dpi)
        buf = 0.01 * (self.max - self.min)
        plt.xlim(self.min - buf, self.max + buf)
        plt.ylim(self.min - buf, self.max + buf)

    def _symbolize_series(self, kde=True):
        # Calculate the point density
        if kde:
            # Sort the points by density, so that the densest points are
            # plotted last
            stacked = np.vstack([self.x, self.y])
            density_estimate = gaussian_kde(stacked)(stacked)
            idx = density_estimate.argsort()
            return self.x[idx], self.y[idx], density_estimate[idx]
        return self.x, self.y, "blue"

    def _draw_axes(self, axes, **kwargs):
        axes.set_ylabel(kwargs.get("ylabel", "Y"), size=5.0)
        axes.set_xlabel(kwargs.get("xlabel", "X"), size=5.0)
        axes.yaxis.set_label_coords(-0.120, 0.5)

        ticks = np.linspace(self.min, self.max, 8)[:-1]
        if self.max > 1000.0:
            labels = []
            for tick in ticks:
                base, exponent = "{:.1e}".format(tick).split("e")
                labels.append("{:.1f}e{:d}".format(float(base), int(exponent)))
        else:
            labels = ["{:.1f}".format(tick) for tick in ticks]
        axes.set_xticks(ticks)
        axes.set_xticklabels(labels, size=4.5)
        axes.set_yticks(ticks)
        axes.set_yticklabels(labels, size=4.5)

    def _draw_grid_lines(self, axes):
        lines = np.linspace(self.min, self.max, 8)[1:-1]
        for line in lines:
            axes.plot([line, line], [self.min, self.max], "k:", linewidth=0.2)
            axes.plot([self.min, self.max], [line, line], "k:", linewidth=0.2)

    def _draw(self, x, y, z, **kwargs):
        fig = plt.gcf()
        axes = plt.gca()

        axes.scatter(x, y, s=4, c=z, edgecolor="", linewidth=0.25)
        self._draw_axes(axes, **kwargs)
        # self._draw_grid_lines(axes)

        # Position the main axes within the figure
        axes.set_position([0.14, 0.100, 0.85, 0.880])
        _ = [axes.spines[x].set_linewidth(0.2) for x in axes.spines]

        # Set fill and edge for the figure
        fig.patch.set_edgecolor("k")
        fig.patch.set_linewidth(2.0)


class ObservedPredictedScatterplot(Scatterplot):

    def _draw_1_to_1(self, axes):
        plt.plot(
            [self.min, self.max], [self.min, self.max], "k-", linewidth=0.5
        )
        plt.text(
            0.89, 0.93, "1:1", transform=axes.transAxes, size=4.5, rotation=45
        )

    def _draw(self, x, y, z, **kwargs):
        super()._draw(x, y, z, **kwargs)
        axes = plt.gca()
        self._draw_1_to_1(axes)

        correlation = statistics.pearson_r(x, y)
        rmse = statistics.rmse(x, y) / x.mean()
        r2 = statistics.r2(x, y)

        def _write_statistic(x_pos: float, y_pos: float, text: str) -> None:
            plt.text(x_pos, y_pos, text, transform=axes.transAxes, size=5.0)

        _write_statistic(0.05, 0.93, "Correlation coeff.: %.4f" % correlation)
        _write_statistic(0.05, 0.89, "Normalized RMSE: %.4f" % rmse)
        _write_statistic(0.05, 0.85, "R-square: %.4f" % r2)

        # Set patch to highlight text in case data points obscure it
        rect = patches.Rectangle(
            (0.04, 0.84),
            0.38,
            0.12,
            transform=axes.transAxes,
            facecolor="white",
            edgecolor="none",
            zorder=3,
        )
        axes.add_patch(rect)


def draw_scatterplot(df, attr, output_file="foo.png", **kwargs):
    # Extract the observed and predicted series from the data frame
    name, units = attr.field_name, attr.units
    obs, prd = df[name + "_O"], df[name + "_P"]
    kwargs["xlabel"] = "Predicted {} ({})".format(name, units)
    kwargs["ylabel"] = "Observed {} ({})".format(name, units)

    ObservedPredictedScatterplot(obs, prd)(**kwargs)
    plt.draw()
    plt.savefig(output_file, edgecolor="k")
