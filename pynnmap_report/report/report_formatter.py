"""
Definition of formatter base class
"""
import re

from reportlab import platypus as p
from reportlab.lib import colors
from reportlab.lib import units as u

from pynnmap.misc import utilities

from . import report_styles

STYLES = report_styles.get_report_styles()


def page_break(orientation):
    """
    Create page break using the specified orientation
    """
    return [
        p.NextPageTemplate(orientation),
        p.PageBreak(),
    ]


def make_title(title_str):
    """
    Render the specified title as a Platypus table
    """
    para = p.Paragraph(title_str, STYLES["section_style"])
    table = p.Table([[para]], colWidths=[7.5 * u.inch])
    table.setStyle(
        p.TableStyle(
            [
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, 0), (-1, -1), "#957348"),
                ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    return table


def make_figure_table(image_files):
    """
    Create a table of images from existing image files
    """
    cols = 2
    table_data = []
    row_data = []
    for i, fn in enumerate(image_files):
        row_data.append(p.Image(fn, 3.4 * u.inch, 3.0 * u.inch))
        if (i % cols) == (cols - 1):
            table_data.append(row_data)
            row_data = []

    # Determine if there are any images left to print
    if len(row_data) != 0:
        for i in range(len(row_data), cols):
            row_data.append(p.Paragraph("", STYLES["body_style"]))
        table_data.append(row_data)

    # Style this into a reportlab table and add to the story
    width = 3.75 * u.inch
    table = p.Table(table_data, colWidths=[width, width])
    table.setStyle(
        p.TableStyle(
            [
                ("ALIGNMENT", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6.0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6.0),
            ]
        )
    )
    return table


def txt_to_html(in_str):
    """
    Convert text values to their HTML equivalents
    """
    replace_list = {
        ">": "&gt;",
        "<": "&lt;",
    }
    for i in replace_list:
        in_str = re.sub(i, replace_list[i], in_str)
    return in_str


class ReportFormatter:
    """
    Base class for all report formatting sections.  A formatter generally
    takes accuracy assessment information from files and formats them into
    the accuracy assessment report.
    """

    _required = []

    # Set up an enumeration for the different pages
    (TITLE, PORTRAIT, LANDSCAPE) = ("title", "portrait", "landscape")

    def check_missing_files(self):
        """
        Before running formatter, ensure that all needed files are present.
        If files are missing, raise error
        """
        files = [getattr(self, attr) for attr in self._required]
        try:
            utilities.check_missing_files(files)
        except utilities.MissingConstraintError as err:
            err.message += "\nSkipping {}\n".format(self.__class__.__name__)
            raise err

    def clean_up(self):
        """
        Optional function to implement by subclasses to clean up temporary
        files
        """
        pass
