"""
Accuracy formatter for all information in a single page
"""
import os
from copy import deepcopy

import numpy as np
import pandas as pd
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
)

from pynnmap.misc import utilities
from pynnmap.misc.classification_accuracy import Classifier, Classification
from pynnmap.parser.xml_stand_metadata_parser import (
    Flags,
    XMLStandMetadataParser,
)

from . import chart_func as cf
from .report_formatter import ReportFormatter
from .accuracy_intro_formatter import AccuracyIntroductionFormatter


def local_image_fn(attr):
    """File name for local accuracy scatterplot image"""
    return "{}.png".format(attr.field_name.lower())


def create_local_figures(df, attrs):
    """
    Given a set of attributes and a dataframe of predicted and observed
    values, create a set of scatterplots and return the list of filenames
    """
    files = []
    for attr in attrs:
        fn = local_image_fn(attr)
        cf.draw_scatterplot(df, attr, output_file=fn, kde=True)
        files.append(fn)
    return files


def regional_image_fn(attr):
    """File name for regional accuracy histogram image"""
    return "{}_area.png".format(attr.field_name.lower())


def create_regional_figures(area_df, olofsson_df, attrs):
    """
    Given a set of attributes and a dataframe of predicted and observed
    area values, create a set of histograms and return the list of filenames
    """
    files = []
    for attr in attrs:
        fn = regional_image_fn(attr)
        cf.draw_histogram(area_df, olofsson_df, attr, output_file=fn)
        files.append(fn)
    return files


def riemann_image_fn(attr, resolution):
    """File name for Riemann mid-scale accuracy image based on resolution"""
    return "hex_{}_{}.png".format(resolution, attr.field_name.lower())


def get_riemann_fn(riemann_dir, resolution, k=7, observed=True):
    """File name for Riemann observed/predicted files"""
    if observed:
        return "{root}/hex_{res}/hex_{res}_observed_mean.csv".format(
            root=riemann_dir, res=resolution
        )
    return "{root}/hex_{res}/hex_{res}_predicted_k{k}_mean.csv".format(
        root=riemann_dir, res=resolution, k=k
    )


def create_riemann_figures(riemann_dir, k, attrs):
    """
    Given a set of attributes, create a set of scatterplots across all
    Riemann resolutions and return the list of filenames
    """
    files = []
    attr_fields = [a.field_name for a in attrs]
    for resolution in (10, 30, 50):
        id_field = "HEX_{}_ID".format(resolution)
        observed_file = get_riemann_fn(riemann_dir, resolution, observed=True)
        predicted_file = get_riemann_fn(
            riemann_dir, resolution, k=k, observed=False
        )
        merged_df = utilities.build_paired_dataframe_from_files(
            observed_file, predicted_file, id_field, attr_fields
        )
        for attr in attrs:
            fn = riemann_image_fn(attr, resolution)
            cf.draw_scatterplot(merged_df, attr, output_file=fn, kde=False)
            files.append(fn)
    return files


class AttributeAccuracyFormatter(ReportFormatter):
    """
    Formatter for a continuous attribute which creates local, regional,
    and mid-scale graphics for inclusion into a single page
    """

    def __init__(self, parameter_parser):
        super().__init__()
        self.stand_metadata_file = parameter_parser.stand_metadata_file
        self.observed_file = parameter_parser.stand_attribute_file
        self.predicted_file = parameter_parser.independent_predicted_file
        self.id_field = parameter_parser.plot_id_field
        self.riemann_dir = parameter_parser.riemann_output_folder
        self.k = parameter_parser.k
        self.image_files = []

        self.error_matrix_df = pd.read_csv(
            parameter_parser.error_matrix_accuracy_file
        )
        self.bins_df = pd.read_csv(parameter_parser.error_matrix_bin_file)
        self.area_df = pd.read_csv(parameter_parser.regional_accuracy_file)
        self.olofsson_df = pd.read_csv(parameter_parser.regional_olofsson_file)

    def run_formatter(self):
        """
        Run formatter for all continuous attributes
        """
        # Read in the stand attribute metadata and get the continuous fields
        metadata_parser = XMLStandMetadataParser(self.stand_metadata_file)
        attrs = metadata_parser.filter(
            Flags.CONTINUOUS
            | Flags.ACCURACY
            | Flags.PROJECT
            | Flags.NOT_SPECIES
        )

        # Create the figures
        self.create_figures(attrs)

        # Create the introduction to the figures
        flowables = AccuracyIntroductionFormatter().run_formatter()

        # Build the individual attribute pages
        for attr in attrs:
            page = self.build_flowable_page(attr)
            flowables.extend(page)
        return flowables

    def create_figures(self, attrs):
        """
        Create all figures in advance of building page.  Store all filenames
        in the image_files instance attribute.
        """
        attr_fields = [a.field_name for a in attrs]

        # Create the paired dataframe for the local data
        merged_df = utilities.build_paired_dataframe_from_files(
            self.observed_file, self.predicted_file, self.id_field, attr_fields
        )

        # Create the figures
        local_figures = create_local_figures(merged_df, attrs)
        self.image_files.extend(local_figures)

        regional_figures = create_regional_figures(
            self.area_df, self.olofsson_df, attrs
        )
        self.image_files.extend(regional_figures)

        riemann_figures = create_riemann_figures(
            self.riemann_dir, self.k, attrs
        )
        self.image_files.extend(riemann_figures)

    def build_error_matrix(self, attr):
        """
        Build a binned error matrix from continuous data
        """
        fn = attr.field_name

        # Get the subsets of the dataframes associated with this attribute
        em_data = self.error_matrix_df[self.error_matrix_df.VARIABLE == fn]
        bins = self.bins_df[self.bins_df.VARIABLE == fn]

        # Construct the error matrix and get row/column totals
        cats = np.arange(1, len(bins) + 1)
        obs = pd.Categorical(em_data.OBSERVED_CLASS, categories=cats)
        prd = pd.Categorical(em_data.PREDICTED_CLASS, categories=cats)
        err_matrix = pd.crosstab(
            index=obs,
            columns=prd,
            values=np.array(em_data.COUNT),
            aggfunc=sum,
            margins=True,
            dropna=False,
        ).values

        # Create a new buffered array to accommodate labels and accuracy and
        # copy in the calculated error matrix
        n_cells, _ = err_matrix.shape
        arr = np.empty((n_cells + 4, n_cells + 4), dtype=np.object)
        arr[:] = ""

        # Label the axes
        arr[2, 0] = "Observed class"
        arr[0, 2] = "Predicted class"

        # Assign class labels
        def get_labels(bin_df):
            def exp_range(low, high):
                def _exp(x):
                    base, exponent = "{:.1e}".format(x).split("e")
                    return "{:.1f}e{:d}".format(float(base), int(exponent))

                return "{}-{}".format(_exp(low), _exp(high))

            def reg_range(low, high):
                def _reg(x):
                    return "{:.1f}".format(x)

                return "{}-{}".format(_reg(low), _reg(high))

            func = exp_range if bin_df.HIGH.max() > 1000.0 else reg_range
            return [
                func(low, high) for low, high in zip(bin_df.LOW, bin_df.HIGH)
            ]

        bin_labels = np.array(
            get_labels(bins) + ["Total", "% correct", "% fuzzy correct"]
        )
        arr[1, 2:] = bin_labels
        arr[2:, 1] = bin_labels.transpose()

        # Fill in the error matrix cells
        arr[2:-2, 2:-2] = err_matrix

        # Calculate row/column/total percent correct
        diag = np.diag(err_matrix)[:-1]
        row_sums, col_sums = err_matrix[-1, :-1], err_matrix[:-1, -1]
        out = np.zeros_like(diag, dtype=np.float)
        pct_r = np.divide(diag, row_sums, out=out, where=row_sums != 0)
        out = np.zeros_like(diag, dtype=np.float)
        pct_c = np.divide(diag, col_sums, out=out, where=col_sums != 0)
        arr[-2, 2 : n_cells + 1] = pct_r * 100.0
        arr[2 : n_cells + 1, -2] = pct_c * 100.0
        arr[-2, -2] = diag.sum() / row_sums.sum() * 100.0

        # Calculate row/column/total percent fuzzy correct
        classifiers = {}
        for i in range(len(diag)):
            if i == 0:
                classification = Classification(i, f"{i}", [i, i + 1])
            elif i == len(diag) - 1:
                classification = Classification(i, f"{i}", [i - 1, i])
            else:
                classification = Classification(i, f"{i}", [i - 1, i, i + 1])
            classifiers[i] = classification
        clf = Classifier(classifiers)
        incorrect = 0
        em_data = err_matrix[:-1, :-1]
        em_size, _ = em_data.shape
        r_totals = em_data.sum(axis=1).astype(np.float64)
        c_totals = em_data.sum(axis=0).astype(np.float64)
        total = em_data.sum()
        r_correct = np.zeros_like(r_totals)
        c_correct = np.zeros_like(c_totals)
        for i in range(len(diag)):
            f_classes = clf.fuzzy_classification(i)
            r_correct[i] = em_data[i, f_classes].sum()
            c_correct[i] = em_data[f_classes, i].sum()
            incorrect += r_totals[i] - r_correct[i]

        def calc_percent(num, denom):
            with np.errstate(divide="ignore", invalid="ignore"):
                return np.where(denom, num / denom * 100.0, 0.0)

        arr[-1, 2 : em_size + 2] = calc_percent(c_correct, c_totals)
        arr[2 : em_size + 2, -1] = calc_percent(r_correct, r_totals)
        arr[-1, -1] = calc_percent(total - incorrect, total)

        # At this point, the correct elements are in the error matrix, but
        # they have not yet been formatted.
        # TODO: Separate into functions

        # Style for error matrix
        em_style = self.styles["error_matrix"]
        em_rot_style = self.styles["error_matrix_rot"]
        em_style_center = self.styles["error_matrix_center"]

        # Change column labels to rotated paragraphs
        # Rotate the column labels
        class RotatedParagraph(Paragraph):
            """Rotated platypus paragraph"""

            def wrap(self, _dummy_width, _dummy_height):
                new_width = self.canv.stringWidth(self.text) + 0.1 * inch
                height, width = Paragraph.wrap(
                    self,
                    new_width,
                    self.canv._leading,  # pylint: disable=protected-access
                )
                return width, height

            def draw(self):
                self.canv.rotate(90)
                self.canv.translate(0.0, -10.0)
                Paragraph.draw(self)

        def rotated_label(x, style):
            return RotatedParagraph(x, style)

        rotated_labels = np.vectorize(rotated_label, excluded=["style"])
        arr[1, 2:] = rotated_labels(arr[1, 2:], em_rot_style)
        arr[2, 0] = rotated_label(arr[2, 0], em_rot_style)

        # For all others, just turn into paragraphs based on type
        def to_paragraph(x, style):
            try:
                return Paragraph("{:d}".format(x), style)
            except ValueError:
                try:
                    return Paragraph("{:.1f}".format(x), style)
                except ValueError:
                    return Paragraph("{}".format(x), style)

        paragraph_cells = np.vectorize(to_paragraph, excluded=["style"])
        arr[2:, 1:] = paragraph_cells(arr[2:, 1:], em_style)
        arr[0, 2] = to_paragraph(arr[0, 2], em_style_center)

        def format_table(data):
            def get_spacing(
                total_spacing,
                n_elem,
                label_spacing=0.25 * inch,
                names_spacing=0.80 * inch,
                percent_spacing=None,
            ):
                # If percent_spacing is None, use standard widths for all
                # rows/columns other than first two; otherwise set the last
                # three rows/columns to percent_spacing
                if percent_spacing is None:
                    available = total_spacing - (label_spacing + names_spacing)
                    standard = available / (n_elem - 2)
                    percent_spacing = standard
                else:
                    available = total_spacing - (
                        label_spacing + names_spacing + 3 * percent_spacing
                    )
                    standard = available / (n_elem - 5)
                return (
                    [label_spacing]
                    + [names_spacing]
                    + [standard] * (n_elem - 5)
                    + [percent_spacing] * 3
                )

            n_rows, n_cols = data.shape
            widths = get_spacing(
                4.10 * inch, n_cols, percent_spacing=0.35 * inch
            )
            heights = get_spacing(3.20 * inch, n_rows)
            return Table(data.tolist(), colWidths=widths, rowHeights=heights)

        table = format_table(arr)

        # Bring in the table style and add correct and fuzzy shading based
        # on this attribute's values
        ts = deepcopy(self.table_styles["error_matrix"])
        for i in range(2, len(diag) + 2):
            ts.add("BACKGROUND", (i, i), (i, i), "#aaaaaa")
        for i in range(2, len(diag) + 1):
            ts.add("BACKGROUND", (i, i + 1), (i, i + 1), "#dddddd")
            ts.add("BACKGROUND", (i + 1, i), (i + 1, i), "#dddddd")
        table.setStyle(ts)
        return table

    def clean_up(self):
        """
        Remove all image files
        """
        for fn in self.image_files:
            if os.path.exists(fn):
                os.remove(fn)

    def build_flowable_page(self, attr):
        """
        Create a single page of accuracy assessment graphics
        """
        # Build the error matrix for this attribute
        error_matrix = self.build_error_matrix(attr)

        # Get the image files
        scatter_fn = local_image_fn(attr)
        regional_fn = regional_image_fn(attr)
        riemann_10_fn = riemann_image_fn(attr, 10)
        riemann_30_fn = riemann_image_fn(attr, 30)
        riemann_50_fn = riemann_image_fn(attr, 50)

        title = attr.field_name + " (units: " + attr.units + ")"
        default_style = self.styles["body_11"]
        title_style = self.styles["body_16"]
        subheading_style = self.styles["subheading"]

        return [
            PageBreak(),
            Paragraph(title, title_style),
            Spacer(1, 0.1 * inch),
            Paragraph(attr.short_description, default_style),
            Spacer(1, 0.2 * inch),
            Paragraph("Local Accuracy", default_style),
            Spacer(1, 0.17 * inch),
            Table(
                [
                    [
                        Image(scatter_fn, width=3.2 * inch, height=3.2 * inch),
                        error_matrix,
                    ]
                ],
                style=self.table_styles["no_padding"],
                hAlign="LEFT",
            ),
            Spacer(1, 0.10 * inch),
            Paragraph("Regional Accuracy", default_style),
            Spacer(1, 0.17 * inch),
            Image(regional_fn, width=7.5 * inch, height=2.5 * inch),
            Spacer(1, 0.10 * inch),
            Paragraph("Accuracy Across Scales", default_style),
            Spacer(1, 0.17 * inch),
            Table(
                [
                    [
                        Image(
                            riemann_10_fn, width=2.4 * inch, height=2.4 * inch
                        ),
                        Image(
                            riemann_30_fn, width=2.4 * inch, height=2.4 * inch
                        ),
                        Image(
                            riemann_50_fn, width=2.4 * inch, height=2.4 * inch
                        ),
                    ],
                    [
                        Spacer(1, 0.05 * inch),
                        Spacer(1, 0.05 * inch),
                        Spacer(1, 0.05 * inch),
                    ],
                    [
                        Paragraph("8,660 ha hexagons", subheading_style),
                        Paragraph("78,100 ha hexagons", subheading_style),
                        Paragraph("216,5000 ha hexagons", subheading_style),
                    ],
                ],
                style=self.table_styles["no_padding"],
                hAlign="LEFT",
            ),
        ]
