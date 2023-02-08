"""
Formatter to report species accuracy including kappas
"""
import pandas as pd
from reportlab import platypus as p
from reportlab.lib import colors
from reportlab.lib import units as u

from pynnmap.parser import xml_report_metadata_parser as xrmp
from pynnmap.parser import xml_stand_metadata_parser as xsmp

from .report_formatter import ReportFormatter, page_break


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
        story = page_break(self.PORTRAIT)

        # Section title
        title = (
            "Local-Scale Accuracy Assessment:\n"
            "Species Accuracy at Plot Locations"
        )
        story.extend(self.create_section_title(title))

        # Species introduction
        intro_str = """
            In this section, we present accuracies and kappa coefficients for
            all tree species that occur on at least 0.5% of observed model
            plots.  The measure of accuracy is based on species presence or
            absence.  Observed presence is defined as a given species occurring
            on the measured plot, whereas predicted presence is defined
            as the species being predicted on any of the nine pixels in the
            plot footprint. As such, errors of commission (observed absent
            and predicted present) tend to be greater than errors of omission
            (observed present and predicted absent).
            <br/><br/>
            Cohen's kappa coefficient (Cohen, 1960) is a statistical measure
            measure of reliability, accounting for agreement occurring by 
            chance. The equation for kappa is:
        """
        story.append(p.Paragraph(intro_str, self.styles["body_style"]))
        story.append(p.Spacer(0, 0.05 * u.inch))

        kappa_str = """
           kappa = (Pr(a) - Pr(e)) / (1.0 - Pr(e))
        """
        story.append(p.Paragraph(kappa_str, self.styles["indented"]))
        story.append(p.Spacer(0, 0.05 * u.inch))

        kappa_str = """
            where Pr(a) is the relative observed agreement among
            raters, and Pr(e) is the probability that agreement is
            due to chance.
            <br/><br/>
            <strong>Abbreviations Used:</strong><br/>
            OP/PP = Observed Present / Predicted Present<br/>
            OA/PP = Observed Absent / Predicted Present
            (errors of commission)<br/>
            OP/PA = Observed Present / Predicted Absent
            (errors of omission)<br/>
            OA/PA = Observed Absent / Predicted Absent
        """
        story.append(p.Paragraph(kappa_str, self.styles["body_style"]))
        story.append(p.Spacer(0, 0.2 * u.inch))

        # Create a list of lists to hold the species accuracy information
        species_table = []

        # Header row
        header_row = []

        spp_str = "<strong>Species PLANTS Code<br/>"
        spp_str += "Scientific Name / Common Name</strong>"
        para = p.Paragraph(spp_str, self.styles["contact_style"])
        header_row.append(para)

        spp_str = "<strong>Species prevalence</strong>"
        para = p.Paragraph(spp_str, self.styles["contact_style"])
        header_row.append(para)

        header_cells = [
            [
                p.Paragraph(
                    "<strong>OP/PP</strong>", self.styles["contact_style_right"]
                ),
                p.Paragraph(
                    "<strong>OP/PA</strong>", self.styles["contact_style_right"]
                ),
            ],
            [
                p.Paragraph(
                    "<strong>OA/PP</strong>", self.styles["contact_style_right"]
                ),
                p.Paragraph(
                    "<strong>OA/PA</strong>", self.styles["contact_style_right"]
                ),
            ],
        ]
        table = p.Table(header_cells, colWidths=[0.75 * u.inch, 0.75 * u.inch])
        table.setStyle(self.table_styles["default_shaded"])
        header_row.append(table)

        kappa_str = "<strong>Kappa coefficient</strong>"
        para = p.Paragraph(kappa_str, self.styles["contact_style"])
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

        # Subset species to just those with 0.5% prevalence
        common_species = spp_df[spp_df.PREVALENCE >= 0.005].SPECIES
        attrs = sorted(list(set(attrs) & set(common_species)))

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
            para = p.Paragraph(spp_str, self.styles["contact_style"])
            species_row.append(para)

            # Get the statistical information
            data = spp_df[spp_df.SPECIES == spp]
            counts = [data.OP_PP, data.OP_PA, data.OA_PP, data.OA_PA]
            prevalence = data.PREVALENCE
            kappa = data.KAPPA

            # Species prevalence
            prevalence_str = "%.4f" % prevalence
            para = p.Paragraph(
                prevalence_str, self.styles["contact_style_right"]
            )
            species_row.append(para)

            # Capture the plot counts in an inner table
            count_cells = []
            count_row = []
            for i in range(0, 4):
                para = p.Paragraph(
                    "%d" % counts[i], self.styles["contact_style_right"]
                )
                count_row.append(para)
                if i % 2 == 1:
                    count_cells.append(count_row)
                    count_row = []
            table = p.Table(
                count_cells, colWidths=[0.75 * u.inch, 0.75 * u.inch]
            )
            table.setStyle(self.table_styles["default_shaded"])
            species_row.append(table)

            # Print out the kappa statistic
            kappa_str = "%.4f" % kappa
            para = p.Paragraph(kappa_str, self.styles["contact_style_right"])
            species_row.append(para)

            # Push this row to the master species table
            species_table.append(species_row)

        # Style this into a reportlab table and add to the story
        col_widths = [(x * u.inch) for x in [4.0, 1.0, 1.5, 1.0]]
        table = p.Table(species_table, colWidths=col_widths)
        table.setStyle(self.table_styles["species_accuracy"])
        story.append(table)
        story.append(p.Spacer(0, 0.1 * u.inch))

        # Return this story
        return story

    def clean_up(self):
        pass
