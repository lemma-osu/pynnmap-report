import os

import pandas as pd
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, Spacer, Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import black, yellow

from pynnmap.misc import utilities
from pynnmap.parser.xml_stand_metadata_parser import (
    Flags,
    XMLStandMetadataParser,
)

from pynnmap_report.report import chart_func as cf
from pynnmap_report.report.report_formatter import ReportFormatter


def get_stylesheet():
    # Add some fonts
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont("Trebuchet", "trebuc.ttf"))
    pdfmetrics.registerFont(TTFont("TrebuchetBold", "trebucbd.ttf"))
    pdfmetrics.registerFont(TTFont("TrebuchetItalic", "trebucit.ttf"))
    pdfmetrics.registerFont(TTFont("TrebuchetBoldItalic", "trebucbi.ttf"))

    styles = {
        "default": ParagraphStyle(
            "default",
            fontName="Trebuchet",
            fontSize=12,
            leading=12,
            leftIndent=0,
            rightIndent=0,
            firstLineIndent=0,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            bulletFontName="Trebuchet",
            bulletFontSize=10,
            bulletIndent=0,
            textColor=black,
            backColor=None,
            wordWrap=None,
            borderWidth=0,
            borderPadding=0,
            borderColor=None,
            borderRadius=None,
            allowWidows=1,
            allowOrphans=0,
            textTransform=None,
            endDots=None,
            splitLongWords=1,
        ),
    }

    styles["title"] = ParagraphStyle(
        "title",
        parent=styles["default"],
        fontName="TrebuchetBold",
        fontSize=14,
    )

    styles["subheading"] = ParagraphStyle(
        "subheading",
        parent=styles["default"],
        fontSize=10,
        alignment=TA_CENTER,
    )

    styles["alert"] = ParagraphStyle(
        "alert", parent=styles["default"], textColor=yellow
    )
    return styles


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
        self.stylesheet = get_stylesheet()
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

        # Build the individual attribute pages
        flowables = []
        for attr in attrs:
            page = self.build_flowable_page(attr)
            flowables.extend(page)
        return flowables

    def create_figures(self, attrs):
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

    def clean_up(self):
        for fn in self.image_files:
            if os.path.exists(fn):
                os.remove(fn)

    def build_flowable_page(self, attr):
        """
        Create a single page of accuracy assessment graphics
        """
        # Get the image files
        scatter_fn = local_image_fn(attr)
        regional_fn = regional_image_fn(attr)
        riemann_10_fn = riemann_image_fn(attr, 10)
        riemann_30_fn = riemann_image_fn(attr, 30)
        riemann_50_fn = riemann_image_fn(attr, 50)

        title = attr.field_name + " (" + attr.units + ")"
        table_style = [
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ]
        default_style = self.stylesheet["default"]
        subheading_style = self.stylesheet["subheading"]
        title_style = self.stylesheet["title"]

        return [
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
                        Image(scatter_fn, width=3.2 * inch, height=3.2 * inch),
                    ]
                ],
                style=table_style,
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
                style=table_style,
                hAlign="LEFT",
            ),
            PageBreak(),
        ]
