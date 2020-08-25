"""
Categorical accuracy formatter showing a subset of the information
"""
import os
from collections import defaultdict
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

from pynnmap.misc.classification_accuracy import Classifier, Classification
from pynnmap.parser.xml_stand_metadata_parser import (
    Flags,
    XMLStandMetadataParser,
)

from . import chart_func as cf
from .report_formatter import ReportFormatter, page_break


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


class CategoricalAccuracyFormatter(ReportFormatter):
    """
    Formatter for a categorical attribute which creates a regional-scale
    graphic and error matrix for inclusion into a single page
    """

    def __init__(self, parameter_parser):
        super().__init__()
        self.stand_metadata_file = parameter_parser.stand_metadata_file
        self.observed_file = parameter_parser.stand_attribute_file
        self.predicted_file = parameter_parser.independent_predicted_file
        self.id_field = parameter_parser.plot_id_field
        self.k = parameter_parser.k
        self.image_files = []

        self.error_matrix_df = pd.read_csv(
            parameter_parser.error_matrix_accuracy_file
        )
        self.bins_df = pd.read_csv(parameter_parser.error_matrix_bin_file)
        self.area_df = pd.read_csv(parameter_parser.regional_accuracy_file)
        self.olofsson_df = pd.read_csv(parameter_parser.regional_olofsson_file)

        # TODO: Hack fix - there are a few pixels that have nearest neighbor
        #   of 0 (missing spatial data in one or more covariates).  This
        #   makes its way into the area_df and that olofsson_df.  Strip out
        #   all records with "Unknown"
        self.area_df = self.area_df[self.area_df.BIN_NAME != "Unknown"]
        self.olofsson_df = self.olofsson_df[self.olofsson_df.CLASS != "Unknown"]

    def run_formatter(self):
        """
        Run formatter for all continuous attributes
        """
        # Read in the stand attribute metadata and get the continuous fields
        metadata_parser = XMLStandMetadataParser(self.stand_metadata_file)
        flags = Flags.CATEGORICAL | Flags.ACCURACY | Flags.PROJECT
        attrs = metadata_parser.filter(flags)

        # Create the figures
        self.create_figures(attrs)

        # Create the introduction
        flowables = self.introduction()

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
        regional_figures = create_regional_figures(
            self.area_df, self.olofsson_df, attrs
        )
        self.image_files.extend(regional_figures)

    def introduction(self):
        flowables = page_break(self.PORTRAIT)

        # Section title
        title = "Categorical Attribute Accuracy Assessment"
        flowables.extend(self.create_section_title(title))

        intro = """
            As with the continuous attributes, we also present accuracy
            assessment for a suite of categorical attributes that are
            distributed with GNN.  For these attributes, we present only
            the local scale confusion matrices and regional scale area
            distributions based on FIA plot estimates, GNN-based model
            predictions and the aforementioned Olofsson et al. (2013) 
            error-corrected area estimates (see explanation in continuous
            attribute section.
            <br/><br/>
            In contrast to the continuous attributes, plot-based predictions
            for categorical attributes are constructed from the single
            nearest neighbor (k=1) at each pixel within the nine pixel
            footprint and the plot predicted value is calculated as the
            majority value across those nine neighbors.
            <br/><br/>
            For some of these categorical attributes, fuzzy classes may
            extend past the traditional +/- one class boundaries.  For
            example, the vegetation class attribute (VEGCLASS) is a synthetic
            attributes that combines canopy cover, hardwood proportion, and
            average tree size in a stand.  When considering fuzzy classes,
            we allow for fuzziness in these three dimensions.  The lighter
            gray shading on fuzzy classes in the confusion matrix will
            indicate these choices.  Users are encouraged to carefully consider
            whether these fuzzy classifications are appropriate in their
            applications.  
        """
        flowables.append(Paragraph(intro, self.styles["body_style"]))
        flowables.append(Spacer(0, 0.15 * inch))
        return flowables

    def build_error_matrix(self, attr):
        """
        Build a binned error matrix from categorical data
        """
        fn = attr.field_name

        # Get the subsets of the dataframes associated with this attribute
        em_data = self.error_matrix_df[self.error_matrix_df.VARIABLE == fn]
        bins = [x.label for x in attr.codes]

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

        bin_labels = np.array(bins + ["Total", "% correct", "% fuzzy correct"])
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
        # Also store row/column indices of fuzzy cells for later formatting
        classifiers = {}
        fuzzy_cells = []
        if len(attr.fuzzy_classes) > 0:
            # Because codes are not necessarily contiguous but they are
            # ordered, create a lookup of unique codes to index
            codes = {x.original_class for x in attr.fuzzy_classes}
            xwalk = {c: i for i, c in enumerate(list(codes))}

            # Set the fuzzy classes, translating codes through xwalk
            d = defaultdict(list)
            for elem in attr.fuzzy_classes:
                orig, fuzzy = (
                    xwalk[elem.original_class],
                    xwalk[elem.fuzzy_class],
                )
                d[orig].append(fuzzy)
                if orig != fuzzy:
                    fuzzy_cells.append((orig, fuzzy))
            for k, v in d.items():
                classifiers[k] = Classification(k, f"{k}", v)
        else:
            for i in range(len(diag)):
                if i == 0:
                    classification = Classification(i, f"{i}", [i, i + 1])
                    fuzzy_cells.append((i, i + 1))
                elif i == len(diag) - 1:
                    classification = Classification(i, f"{i}", [i - 1, i])
                    fuzzy_cells.append((i, i - 1))
                else:
                    classification = Classification(
                        i, f"{i}", [i - 1, i, i + 1]
                    )
                    fuzzy_cells.append((i, i - 1))
                    fuzzy_cells.append((i, i + 1))
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
                names_spacing=1.20 * inch,
            ):
                available = total_spacing - (label_spacing + names_spacing)
                standard = min(0.5 * inch, available / (n_elem - 2))
                return (
                    [label_spacing]
                    + [names_spacing]
                    + [standard] * (n_elem - 2)
                )

            n_rows, n_cols = data.shape
            widths = get_spacing(7.5 * inch, n_cols)
            heights = get_spacing(5.0 * inch, n_rows)
            return Table(data.tolist(), colWidths=widths, rowHeights=heights)

        table = format_table(arr)

        # Bring in the table style and add correct and fuzzy shading based
        # on this attribute's values
        ts = deepcopy(self.table_styles["error_matrix"])
        for i in range(2, len(diag) + 2):
            ts.add("BACKGROUND", (i, i), (i, i), "#aaaaaa")
        for c, r in fuzzy_cells:
            cell = (c + 2, r + 2)
            ts.add("BACKGROUND", cell, cell, "#dddddd")

        # Color the correct and fuzzy correct reporting cells
        ts.add("BACKGROUND", (-2, -2), (-2, -2), "#aaaaaa")
        ts.add("BACKGROUND", (-1, -1), (-1, -1), "#dddddd")
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
        regional_fn = regional_image_fn(attr)

        title = attr.field_name + " (units: " + attr.units + ")"
        table_style = [
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ]
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
            error_matrix,
            Spacer(1, 0.10 * inch),
            Paragraph("Regional Accuracy", default_style),
            Spacer(1, 0.17 * inch),
            Image(regional_fn, width=7.5 * inch, height=2.5 * inch),
            Spacer(1, 0.10 * inch),
        ]
