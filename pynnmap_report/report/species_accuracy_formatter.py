"""
Formatter to report species accuracy including kappas
"""
import pandas as pd
from reportlab import platypus as p
from reportlab.lib import colors
from reportlab.lib import units as u

from pynnmap.parser import xml_report_metadata_parser as xrmp
from pynnmap.parser import xml_stand_metadata_parser as xsmp

from . import report_styles
from .report_formatter import ReportFormatter, page_break, make_title


class SpeciesAccuracyFormatter(ReportFormatter):
    """
    Formatter to report species accuracy including kappas
    """

    _required = ["species_accuracy_file", "stand_metadata_file"]

    def __init__(self, parameter_parser):
        super(SpeciesAccuracyFormatter, self).__init__()
        self.species_accuracy_file = parameter_parser.species_accuracy_file
        self.stand_metadata_file = parameter_parser.stand_metadata_file
        self.report_metadata_file = parameter_parser.report_metadata_file

        self.check_missing_files()

    def run_formatter(self):
        """
        Run this formatter for all species attributes
        """
        # Set up an empty list to hold the story
        story = []

        # Import the report styles
        styles = report_styles.get_report_styles()

        # Create a page break
        story.extend(page_break(self.PORTRAIT))

        # Section title
        title_str = "<strong>Local-Scale Accuracy Assessment:<br/>"
        title_str += "Species Accuracy at Plot Locations"
        title_str += "</strong>"
        story.append(make_title(title_str))
        story.append(p.Spacer(0, 0.2 * u.inch))

        # Kappa explanation
        kappa_str = (
            "Cohen's kappa coefficient (Cohen, 1960) is a statistical "
            "measure of reliability, accounting for agreement occurring by "
            "chance. The equation for kappa is:"
        )
        para = p.Paragraph(kappa_str, styles["body_style"])
        story.append(para)
        story.append(p.Spacer(0, 0.05 * u.inch))

        kappa_str = """
           kappa = (Pr(a) - Pr(e)) / (1.0 - Pr(e))
        """
        para = p.Paragraph(kappa_str, styles["indented"])
        story.append(para)
        story.append(p.Spacer(0, 0.05 * u.inch))

        kappa_str = """
            where Pr(a) is the relative observed agreement among
            raters, and Pr(e) is the probability that agreement is
            due to chance.<br/><br/>

            <strong>Abbreviations Used:</strong><br/>
            OP/PP = Observed Present / Predicted Present<br/>
            OA/PP = Observed Absent / Predicted Present
            (errors of commission)<br/>
            OP/PA = Observed Present / Predicted Absent
            (errors of omission)<br/>
            OA/PA = Observed Absent / Predicted Absent
        """
        para = p.Paragraph(kappa_str, styles["body_style"])
        story.append(para)
        story.append(p.Spacer(0, 0.2 * u.inch))

        # Create a list of lists to hold the species accuracy information
        species_table = []

        # Header row
        header_row = []

        spp_str = "<strong>Species PLANTS Code<br/>"
        spp_str += "Scientific Name / Common Name</strong>"
        para = p.Paragraph(spp_str, styles["body_style_10"])
        header_row.append(para)

        spp_str = "<strong>Species prevalence</strong>"
        para = p.Paragraph(spp_str, styles["body_style_10"])
        header_row.append(para)

        header_cells = [
            [
                p.Paragraph(
                    "<strong>OP/PP</strong>", styles["body_style_10_right"]
                ),
                p.Paragraph(
                    "<strong>OP/PA</strong>", styles["body_style_10_right"]
                ),
            ],
            [
                p.Paragraph(
                    "<strong>OA/PP</strong>", styles["body_style_10_right"]
                ),
                p.Paragraph(
                    "<strong>OA/PA</strong>", styles["body_style_10_right"]
                ),
            ],
        ]
        table = p.Table(header_cells, colWidths=[0.75 * u.inch, 0.75 * u.inch])
        table.setStyle(styles["default_table_style"])
        header_row.append(table)

        kappa_str = "<strong>Kappa coefficient</strong>"
        para = p.Paragraph(kappa_str, styles["body_style_10"])
        header_row.append(para)
        species_table.append(header_row)

        # Open the species accuracy file into a recarray
        spp_df = pd.read_csv(self.species_accuracy_file)

        # Read in the stand attribute metadata
        metadata_parser = xsmp.XMLStandMetadataParser(self.stand_metadata_file)

        # Read in the report metadata if it exists
        if self.report_metadata_file:
            rmp = xrmp.XMLReportMetadataParser(self.report_metadata_file)
        else:
            rmp = None

        # Subset the attributes to just species
        attrs = []
        for attr in metadata_parser.attributes:
            if attr.is_species_attr() and "NOTALY" not in attr.field_name:
                attrs.append(attr.field_name)

        # Iterate over the species and print out the statistics
        for spp in attrs:
            # Empty row to hold the formatted output
            species_row = []

            # Get the scientific and common names from the report metadata
            # if it exists; otherwise, just use the species symbol
            if rmp is not None:

                # Strip off any suffix if it exists
                try:
                    spp_plain = spp.split("_")[0]
                    spp_info = rmp.get_species(spp_plain)
                    spp_str = spp_info.spp_symbol + "<br/>"
                    spp_str += spp_info.scientific_name + " / "
                    spp_str += spp_info.common_name
                except IndexError:
                    spp_str = spp
            else:
                spp_str = spp
            para = p.Paragraph(spp_str, styles["body_style_10"])
            species_row.append(para)

            # Get the statistical information
            data = spp_df[spp_df.SPECIES == spp]
            counts = [data.OP_PP, data.OP_PA, data.OA_PP, data.OA_PA]
            prevalence = data.PREVALENCE
            kappa = data.KAPPA

            # Species prevalence
            prevalence_str = "%.4f" % prevalence
            para = p.Paragraph(prevalence_str, styles["body_style_10_right"])
            species_row.append(para)

            # Capture the plot counts in an inner table
            count_cells = []
            count_row = []
            for i in range(0, 4):
                para = p.Paragraph(
                    "%d" % counts[i], styles["body_style_10_right"]
                )
                count_row.append(para)
                if i % 2 == 1:
                    count_cells.append(count_row)
                    count_row = []
            table = p.Table(
                count_cells, colWidths=[0.75 * u.inch, 0.75 * u.inch]
            )
            table.setStyle(styles["default_table_style"])
            species_row.append(table)

            # Print out the kappa statistic
            kappa_str = "%.4f" % kappa
            para = p.Paragraph(kappa_str, styles["body_style_10_right"])
            species_row.append(para)

            # Push this row to the master species table
            species_table.append(species_row)

        # Style this into a reportlab table and add to the story
        col_widths = [(x * u.inch) for x in [4.0, 0.75, 1.5, 0.75]]
        table = p.Table(species_table, colWidths=col_widths)
        table.setStyle(
            p.TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), "#f1efe4"),
                    ("GRID", (0, 0), (-1, -1), 2, colors.white),
                    ("TOPPADDING", (0, 0), (0, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (0, -1), 2),
                    ("LEFTPADDING", (0, 0), (0, -1), 6),
                    ("RIGHTPADDING", (0, 0), (0, -1), 6),
                    ("ALIGNMENT", (0, 0), (0, -1), "LEFT"),
                    ("VALIGN", (0, 0), (0, -1), "TOP"),
                    ("TOPPADDING", (1, 0), (1, -1), 2),
                    ("BOTTOMPADDING", (1, 0), (1, -1), 2),
                    ("LEFTPADDING", (1, 0), (1, -1), 6),
                    ("RIGHTPADDING", (1, 0), (1, -1), 6),
                    ("ALIGNMENT", (1, 0), (1, -1), "RIGHT"),
                    ("VALIGN", (1, 0), (1, 0), "TOP"),
                    ("VALIGN", (1, 1), (1, -1), "MIDDLE"),
                    ("TOPPADDING", (2, 0), (2, -1), 0),
                    ("BOTTOMPADDING", (2, 0), (2, -1), 0),
                    ("LEFTPADDING", (2, 0), (2, -1), 0),
                    ("RIGHTPADDING", (2, 0), (2, -1), 0),
                    ("ALIGNMENT", (2, 0), (2, -1), "LEFT"),
                    ("VALIGN", (2, 0), (2, -1), "TOP"),
                    ("TOPPADDING", (3, 0), (3, -1), 2),
                    ("BOTTOMPADDING", (3, 0), (3, -1), 2),
                    ("LEFTPADDING", (3, 0), (3, -1), 6),
                    ("RIGHTPADDING", (3, 0), (3, -1), 6),
                    ("ALIGNMENT", (3, 0), (3, -1), "RIGHT"),
                    ("VALIGN", (3, 0), (3, 0), "TOP"),
                    ("VALIGN", (3, 1), (3, -1), "MIDDLE"),
                ]
            )
        )
        story.append(table)
        story.append(p.Spacer(0, 0.1 * u.inch))

        rare_species_str = """
            Note that some very rare species do not appear in this accuracy
            report, because these species were not included when building
            the initial ordination model.  The full set of species is
            available upon request.
        """
        para = p.Paragraph(rare_species_str, styles["body_style"])
        story.append(para)

        # Return this story
        return story

    def clean_up(self):
        pass
