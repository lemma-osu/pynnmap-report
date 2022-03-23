"""
Chart classes for creating scatterplots and histograms
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, patches
from scipy.stats import gaussian_kde

from pynnmap.misc import statistics


mpl.rcParams["font.family"] = "Open Sans"


def get_global_limits(*iterables):
    """
    Return the global minimum/maximum across multiple iterables
    """
    return min(min(x) for x in iterables), max(max(x) for x in iterables)


class Scatterplot:
    """
    Simple scatterplot using matplotlib and accommodating kernel density
    estimation coloring using the kde keyword in __call__
    """

    def __init__(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)
        self.min, self.max = get_global_limits(self.x, self.y)

    def __call__(self, **kwargs):
        self._initialize_figure(3.2, 3.2)
        kde = kwargs.get("kde", True)
        self._draw(*self._symbolize_series(kde=kde), **kwargs)

    def _initialize_figure(self, width, height, dpi=250):
        """
        Initialize the scatterplot
        """
        fig = plt.gcf()
        fig.clf()
        fig.set_figwidth(width)
        fig.set_figheight(height)
        fig.set_dpi(dpi)
        buf = 0.01 * (self.max - self.min)
        plt.xlim(self.min - buf, self.max + buf)
        plt.ylim(self.min - buf, self.max + buf)

    def _symbolize_series(self, kde=True):
        """
        Return x and y series optionally symbolized by kernel density estimator
        """
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

        axes.scatter(x, y, s=4, c=z, linewidth=0.25)
        self._draw_axes(axes, **kwargs)
        # self._draw_grid_lines(axes)

        # Position the main axes within the figure
        axes.set_position([0.14, 0.100, 0.85, 0.880])
        _ = [axes.spines[x].set_linewidth(0.2) for x in axes.spines]

        # Set fill and edge for the figure
        fig.patch.set_edgecolor("k")
        fig.patch.set_linewidth(2.0)


class ObservedPredictedScatterplot(Scatterplot):
    """
    Specialization of Scatterplot to explicitly label graph as an observed-
    predicted scatterplot - observed is Y-axis, predicted is X-axis.  This
    adds labels for X and Y axes, adds a 1-to-1 line, and adds some simple
    statistics relevant to observed-predicted comparisons.
    """

    def _draw_1_to_1(self, axes):
        plt.plot(
            [self.min, self.max], [self.min, self.max], "k-", linewidth=0.5
        )
        plt.text(
            0.89, 0.93, "1:1", transform=axes.transAxes, size=4.5, rotation=45
        )

    def _draw(self, x, y, z, **kwargs):
        super()._draw(y, x, z, **kwargs)
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
        rect_y_min, rect_y_size = 0.84, 0.12

        if "avg_plot_count" in kwargs:
            _write_statistic(
                0.05,
                0.81,
                "Average plot count: %.1f" % kwargs["avg_plot_count"],
            )
            rect_y_min, rect_y_size = 0.80, 0.16

        if "hexagon_count" in kwargs:
            _write_statistic(
                0.05,
                0.77,
                "Hexagon count: %d" % kwargs["hexagon_count"],
            )
            rect_y_min, rect_y_size = 0.76, 0.20

        # Set patch to highlight text in case data points obscure it
        rect = patches.Rectangle(
            (0.04, rect_y_min),
            0.38,
            rect_y_size,
            transform=axes.transAxes,
            facecolor="white",
            edgecolor="none",
        )
        axes.add_patch(rect)


def draw_scatterplot(df, attr, output_file="foo.png", **kwargs):
    """
    Render a scatterplot from LEMMA paired dataframe using the specified
    attribute
    """
    # Extract the observed and predicted series from the data frame
    name, units = attr.field_name, attr.units
    obs, prd = df[name + "_O"], df[name + "_P"]
    kwargs["xlabel"] = kwargs.get(
        "xlabel", "Predicted {} ({})".format(name, units)
    )
    kwargs["ylabel"] = kwargs.get(
        "ylabel", "Observed {} ({})".format(name, units)
    )
    ObservedPredictedScatterplot(obs, prd)(**kwargs)
    plt.draw()
    plt.savefig(output_file, edgecolor="k")


class Series:
    """
    An individual series in a bar plot.  Series have names and, optionally,
    error bar values.
    """

    def __init__(self, values, name="series", err=None):
        self.values = values
        self.name = name
        self.err = err

    def __len__(self):
        return len(self.values)

    def max(self):
        """
        Return the maximum value of either the values or, if err is present,
        the error added to the value.  Used for scaling figure limits.
        """
        if self.err is not None:
            return max((val + err) for val, err in zip(self.values, self.err))
        return max(self.values)


class SeriesGroup:
    """
    Collection of Series along with information on spacing between groups
    and total relative width of all bars
    """

    # Set colors for the different series
    COLORS = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]

    def __init__(self, series, total_width=0.9, spacing=0.03):
        self.series = series
        self.total_width = total_width
        self.spacing = spacing

    def __getitem__(self, item):
        return self.series[item]

    def __iter__(self):
        for series in self.series:
            yield series

    @property
    def names(self):
        """
        Return the names for all series in this group
        """
        return [x.name for x in self.series]

    def draw(self, axes):
        """
        Draw all series onto the given axes
        """
        num = len(self.series)
        series_width = (self.total_width - (self.spacing * num)) / num
        first_space = (1.0 - self.total_width) / 2.0 + (self.spacing / 2.0)
        bin_idx = np.arange(len(self.series[0]))
        for series_idx in range(len(self.series)):
            axes.bar(
                bin_idx
                + ((series_width + self.spacing) * series_idx)
                + first_space,
                self.series[series_idx].values,
                color=self.COLORS[series_idx],
                linewidth=0.0,
                width=series_width,
                align="edge",
                yerr=self.series[series_idx].err,
                error_kw={"ecolor": "k", "capsize": 2.0, "elinewidth": 0.7},
            )


class SeriesGroupLemma(SeriesGroup):
    def draw(self, axes):
        super().draw(axes)
        self.draw_annotations(axes)

    def draw_annotations(self, axes):
        num = len(self.series)
        series_width = (self.total_width - (self.spacing * num)) / num
        first_space = (1.0 - self.total_width) / 2.0 + (self.spacing / 2.0)
        for series_idx in range(len(self.series)):
            if self.series[series_idx].err is not None:
                for x in range(0, 2):
                    axes.text(
                        x
                        + ((series_width + self.spacing) * series_idx)
                        + first_space
                        + series_width / 2.0,
                        0.0,
                        "*",
                        ha="center",
                        va="bottom",
                        color="k",
                    )


class Legend:
    """
    Legend for series placed in upper right corner
    """

    def __init__(self, names):
        self.names = names

    def draw(self, axes):
        """
        Draw the legend onto the given axes
        """
        legend = axes.legend(
            self.names,
            prop=font_manager.FontProperties(size=5.0),
            borderpad=0.6,
            loc=(0.85, 0.80),
        )
        legend.get_frame().set_linewidth(0.2)


class Labels:
    """
    Labels for the x-axis to label the series categories
    """

    def __init__(self, labels):
        self.labels = labels

    def get_label_rotation(self, figure, frame_width):
        """
        Figure out the needed rotation in order to fit labels within the
        allowable space.  Returns the rotation angle and the length
        of the longest label
        """
        label_width = frame_width * figure.get_figwidth()
        label_width /= len(self.labels)

        # Find the longest label (in characters)
        max_length = max(len(x) for x in self.labels)

        # Find the minimum ratio between space and label size that will
        # fit in the space provided.  This was determined outside the code
        # and really should take into account the space consumed by the label
        min_ratio = 0.04
        if (label_width / max_length) < min_ratio:
            # Set the rotation based on this ratio
            slope = 60.0 / min_ratio
            x = min_ratio - (label_width / max_length)
            y = slope * x
            rotation = 30.0 + y
        else:
            rotation = 0.0
        return rotation, max_length

    def draw(self, axes):
        """
        Draw the labels onto the given axes
        """
        idx = np.arange(len(self.labels))
        axes.ticklabel_format(scilimits=(-10, 10))
        axes.tick_params(axis="x", bottom=False, top=False)
        axes.set_xticks(idx + 0.5)
        axes.set_xticklabels(self.labels, size=5.0)


class Histogram:
    """
    Simple histogram of multiple series using matplotlib.  This class is
    very opinionated about spacing, sizing, etc. and is likely only useful
    for use in these accuracy assessment reports.
    """

    def __init__(self, series_group, labels, x_title="X", y_title="Y"):
        self.series_group = series_group
        self.legend = Legend(series_group.names)
        self.labels = Labels(labels)
        self.x_title = x_title
        self.y_title = y_title
        self.figure, self.axes = plt.subplots()

    def __call__(self):
        self._initialize_figure()
        self._draw()
        return self.figure

    def _initialize_figure(self):
        """
        Initialize the width, height and resolution of the image
        """
        self.figure.set_figwidth(7.5)
        self.figure.set_figheight(2.5)
        self.figure.set_dpi(250)

    def draw_axes(self):
        """
        Draw the axes titles and set miscellaneous axis parameters
        """
        self.axes.tick_params(axis="y", labelsize=5.0)
        self.axes.set_xlim(0, len(self.series_group[0]))
        self.axes.set_ylabel(self.y_title, size=5.0)
        self.axes.set_xlabel(self.x_title, size=5.0)

    def adjust_spacing(self):
        """
        Adjust spacing for the chart based on the data rendered.  This
        accommodates adjustment of the y domain and possibly rotates x labels
        """
        global_max = max(x.max() for x in self.series_group)
        self.axes.set_ylim(0, global_max * 1.10)

        frame_x, frame_y = 0.08, 0.13
        frame_width, frame_height = 0.90, 0.83

        # Figure out if x labels need to be rotated
        rotation, max_label = self.labels.get_label_rotation(
            self.figure, frame_width
        )
        plt.setp(self.axes.get_xticklabels(), "rotation", rotation)

        # Adjustment factor is based on rotation angle and max_label
        adj_factor = 0.00014 * (rotation * max_label)
        frame_y += adj_factor
        frame_height -= adj_factor
        self.axes.set_position([frame_x, frame_y, frame_width, frame_height])

    def style_borders(self):
        """
        Style the border elements in the figure
        """
        self.axes.patch.set_linewidth(0.2)
        for spine in self.axes.spines:
            self.axes.spines[spine].set_linewidth(0.2)
        self.figure.patch.set_edgecolor("k")
        self.figure.patch.set_linewidth(2.0)

    def _draw(self):
        """
        Draw the individual components
        """
        self.series_group.draw(self.axes)
        self.legend.draw(self.axes)
        self.labels.draw(self.axes)
        self.draw_axes()
        self.adjust_spacing()
        self.style_borders()


def draw_histogram(area_df, olofsson_df, attr, output_file="foo.png"):
    """
    Render a histogram from LEMMA paired dataframe using the specified
    attribute
    """
    attr_df = area_df[area_df.VARIABLE == attr.field_name]
    obs = attr_df[attr_df.DATASET == "OBSERVED"].AREA
    prd = attr_df[attr_df.DATASET == "PREDICTED"].AREA
    labels = attr_df[attr_df.DATASET == "OBSERVED"].BIN_NAME

    adjusted_df = olofsson_df[olofsson_df.VARIABLE == attr.field_name]
    error_adjusted = np.hstack(([0.0, 0.0], adjusted_df.ADJUSTED))
    ci_adjusted = np.hstack(([0.0, 0.0], adjusted_df.CI_ADJUSTED))

    series_group = SeriesGroupLemma(
        [
            Series(obs, name="Plots"),
            Series(prd, name="GNN"),
            Series(error_adjusted, name="Error-Adjusted", err=ci_adjusted),
        ]
    )

    # Create the figure
    x_title = "{} ({})".format(attr.field_name, attr.units)
    figure = Histogram(
        series_group, labels, x_title=x_title, y_title="Area (ha)"
    )()
    figure.savefig(output_file, edgecolor="k")
    plt.close(figure)
