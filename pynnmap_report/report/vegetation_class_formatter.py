"""
Formatter to create an error matrix of vegetation class
"""
import re

import pandas as pd
from reportlab import platypus as p
from reportlab.lib import colors
from reportlab.lib import units as u

from pynnmap.parser import xml_stand_metadata_parser as xsmp

from . import report_styles
from .report_formatter import ReportFormatter, page_break, txt_to_html


class VegetationClassFormatter(ReportFormatter):
    """
    Formatter to create an error matrix of vegetation class
    """

    _required = ["vc_errmatrix_file", "stand_metadata_file"]

    def __init__(self, parameter_parser):
        self.vc_errmatrix_file = parameter_parser.vegclass_errmatrix_file
        self.stand_metadata_file = parameter_parser.stand_metadata_file
        self.check_missing_files()

    def run_formatter(self):
        """
        Run formatter for the VEGCLASS attribute
        """
        # Set up an empty list to hold the story
        story = []

        # Import the report styles
        styles = report_styles.get_report_styles()

        # Create a page break
        story.extend(page_break(self.LANDSCAPE))

        class RotatedParagraph(p.Paragraph):
            """Rotated platypus paragraph"""

            def wrap(self, _dummy_width, _dummy_height):
                height, width = p.Paragraph.wrap(
                    self,
                    self.canv.stringWidth(self.text),
                    self.canv._leading,  # pylint: disable=protected-access
                )
                return width, height

            def draw(self):
                self.canv.rotate(90)
                self.canv.translate(0.0, -10.0)
                p.Paragraph.draw(self)

        title_str = (
            "<strong>Local-Scale Accuracy Assessment: "
            + "Error Matrix for Vegetation Classes at Plot "
        )
        title_str += "Locations</strong>"

        para = p.Paragraph(title_str, styles["section_style"])
        table = p.Table([[para]], colWidths=[10.0 * u.inch])
        table.setStyle(
            p.TableStyle(
                [
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("BACKGROUND", (0, 0), (-1, -1), "#957348"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )
        story.extend((table, p.Spacer(0, 0.1 * u.inch)))
        # Read in the vegclass error matrix
        names = [f"P_{str(x)}" for x in range(1, 12)]
        names.insert(0, "OBSERVED")
        names.extend(["TOTAL", "CORRECT", "FUZZY_CORRECT"])
        vc_df = pd.read_csv(self.vc_errmatrix_file, skiprows=1, names=names)
        vc_df.drop(columns=["OBSERVED"], inplace=True)

        # Read in the stand attribute metadata
        metadata_parser = xsmp.XMLStandMetadataParser(self.stand_metadata_file)

        # Get the class names from the metadata
        vegclass_metadata = metadata_parser.get_attribute("VEGCLASS")
        vc_codes = vegclass_metadata.codes

        header_row = ["" for _ in range(2)]
        prd_str = "<strong>Predicted Class</strong>"
        para = p.Paragraph(prd_str, styles["body_style_10_center"])
        header_row.append(para)
        header_row.extend("" for _ in range(len(vc_df) - 1))
        vegclass_table = [header_row]
        # Add the predicted labels
        summary_labels = ("Total", "% Correct", "% FCorrect")
        header_row = ["" for _ in range(2)]
        for code in vc_codes:
            label = re.sub("-", "-<br/>", code.label)
            para = p.Paragraph(label, styles["body_style_10_right"])
            header_row.append(para)
        for label in summary_labels:
            label = re.sub(" ", "<br/>", label)
            para = p.Paragraph(label, styles["body_style_10_right"])
            header_row.append(para)
        vegclass_table.append(header_row)

        # Set a variable to distinguish between plot counts and percents
        # in order to format them differently
        format_break = 11

        # Set the cells which should be blank
        blank_cells = [
            (11, 12),
            (11, 13),
            (12, 11),
            (12, 13),
            (13, 11),
            (13, 12),
        ]

        # Add the data
        for (i, row) in enumerate(vc_df.itertuples(index=False)):
            vegclass_row = []
            for (j, elem) in enumerate(row):

                # Blank cells
                if (i, j) in blank_cells:
                    elem_str = ""

                # Cells that represent plot counts
                elif i <= format_break and j <= format_break:
                    elem_str = "%d" % int(elem)

                # Cells that represent percentages
                else:
                    elem_str = "%.1f" % float(elem)
                para = p.Paragraph(elem_str, styles["body_style_10_right"])
                vegclass_row.append(para)

            # Add the observed labels at the beginning of each data row
            if i == 0:
                obs_str = "<strong>Observed Class</strong>"
                para = RotatedParagraph(obs_str, styles["body_style_10_center"])
            else:
                para = ""
            vegclass_row.insert(0, para)

            if i < len(vc_codes):
                label = vc_codes[i].label
            else:
                index = i - len(vc_codes)
                label = summary_labels[index]
            para = p.Paragraph(label, styles["body_style_10_right"])
            vegclass_row.insert(1, para)

            # Add this row to the table
            vegclass_table.append(vegclass_row)

        # Set up the widths for the table cells
        widths = [0.3, 0.85]
        widths.extend(0.56 for _ in range(len(vc_codes)))
        widths.extend(0.66 for _ in range(3))
        widths = [x * u.inch for x in widths]

        # Convert the vegclass table into a reportlab table
        table = p.Table(vegclass_table, colWidths=widths)
        table.setStyle(
            p.TableStyle(
                [
                    ("SPAN", (0, 0), (1, 1)),
                    ("SPAN", (0, 2), (0, -1)),
                    ("SPAN", (2, 0), (-1, 0)),
                    ("BACKGROUND", (0, 0), (-1, -1), "#f1efe4"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.white),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("VALIGN", (0, 2), (0, -1), "MIDDLE"),
                    ("VALIGN", (2, 1), (-1, 1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )

        # Set up the shading for the truly correct cells
        correct = {}
        for i in range(len(vc_codes)):
            val = i + 1
            correct[val] = val

        for key in correct:
            val = correct[key]
            table.setStyle(
                p.TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (key + 1, val + 1),
                            (key + 1, val + 1),
                            "#aaaaaa",
                        ),
                    ]
                )
            )

        # Set up the shading for the fuzzy correct cells
        fuzzy = {
            1: [2],
            2: [1, 3, 5, 8],
            3: [2, 4, 5],
            4: [3, 6, 7],
            5: [2, 3, 6, 8],
            6: [4, 5, 7, 9],
            7: [4, 6, 10, 11],
            8: [2, 5, 9],
            9: [6, 8, 10],
            10: [7, 9, 11],
            11: [7, 10],
        }

        for key, value in fuzzy.items():
            for elem in value:
                table.setStyle(
                    p.TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (key + 1, elem + 1),
                                (key + 1, elem + 1),
                                "#dddddd",
                            ),
                        ]
                    )
                )

        story.extend((table, p.Spacer(0, 0.1 * u.inch)))
        # Explanation and definitions of vegetation class categories
        cell_str = """
            Cell values are model plot counts.  Dark gray cells represent
            plots where the observed class matches the predicted class
            and are included in the percent correct.  Light gray cells
            represent cases where the observed and predicted differ
            slightly (within +/- one class) based on canopy cover,
            hardwood proportion or average stand diameter, and are
            included in the percent fuzzy correct.
        """
        para = p.Paragraph(cell_str, styles["body_style_9"])
        story.extend((para, p.Spacer(0, 0.1 * u.inch)))
        head_str = """
            <strong>Vegetation Class (VEGCLASS) Definitions</strong> --
            CANCOV (canopy cover of all live trees), BAH_PROP (proportion of
            hardwood basal area), and QMD_DOM (quadratic mean diameter of
            all dominant and codominant trees).
        """
        para = p.Paragraph(head_str, styles["body_style_9"])
        story.extend((para, p.Spacer(0, 0.1 * u.inch)))
        # Print out the vegclass code definitions
        for code in vc_codes:
            label = code.label
            desc = txt_to_html(code.description)
            doc_str = "<strong>" + label + ":</strong> " + desc
            para = p.Paragraph(doc_str, styles["body_style_9"])
            story.append(para)

        return story

    def clean_up(self):
        pass
