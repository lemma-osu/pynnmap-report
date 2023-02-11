"""
Formatter to report species accuracy including kappas
"""
from typing import Any, List

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

    def build_header_cell_count_table(self) -> p.Table:
        def _paragraph(contents: str) -> p.Paragraph:
            return p.Paragraph(
                f"<strong>{contents}</strong>",
                self.styles["contact_style_right"],
            )

        header_cells = [
            list(map(_paragraph, ("OP/PP", "OP/PA"))),
            list(map(_paragraph, ("OA/PP", "OA/PA"))),
        ]
        table = p.Table(header_cells, colWidths=[0.75 * u.inch, 0.75 * u.inch])
        table.setStyle(self.table_styles["default_shaded"])
        return table

    def species_name(
        self, spp: str, metadata: xrmp.XMLReportMetadataParser = None
    ) -> p.Paragraph:
        if metadata is not None:
            try:
                spp_plain = spp.split("_")[0]
                spp_info = metadata.get_species(spp_plain)
                spp_str = (
                    f"{spp_info.spp_symbol}<br/>"
                    f"{spp_info.scientific_name}/{spp_info.common_name}"
                )
            except IndexError:
                spp_str = spp
        else:
            spp_str = spp
        return p.Paragraph(spp_str, self.styles["contact_style"])

    def count_table(self, plot_counts: List[int]) -> p.Table:
        def _paragraph(value: int) -> p.Paragraph:
            return p.Paragraph(f"{value}", self.styles["contact_style_right"])

        cells = [
            list(map(_paragraph, plot_counts[:2])),
            list(map(_paragraph, plot_counts[2:])),
        ]
        count_table = p.Table(cells, colWidths=[0.75 * u.inch, 0.75 * u.inch])
        count_table.setStyle(self.table_styles["default_shaded"])
        return count_table

    def build_species_table_row(
        self,
        spp: str,
        spp_df: pd.DataFrame,
        metadata: xrmp.XMLReportMetadataParser = None,
    ) -> List[Any]:
        spp_data = spp_df[spp_df.SPECIES == spp].squeeze()
        plot_counts = [
            getattr(spp_data, x) for x in ("OP_PP", "OP_PA", "OA_PP", "OA_PA")
        ]
        return [
            self.species_name(spp, metadata),
            p.Paragraph(
                f"{spp_data.PREVALENCE:.4f}", self.styles["contact_style_right"]
            ),
            self.count_table(plot_counts),
            p.Paragraph(
                f"{spp_data.KAPPA:.4f}", self.styles["contact_style_right"]
            ),
        ]

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
        story.extend(
            [
                p.Paragraph(intro_str, self.styles["body_style"]),
                p.Spacer(0, 0.05 * u.inch),
            ]
        )

        kappa_str = """
           kappa = (Pr(a) - Pr(e)) / (1.0 - Pr(e))
        """
        story.extend(
            [
                p.Paragraph(kappa_str, self.styles["indented"]),
                p.Spacer(0, 0.05 * u.inch),
            ]
        )

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
        story.extend(
            [
                p.Paragraph(kappa_str, self.styles["body_style"]),
                p.Spacer(0, 0.2 * u.inch),
            ]
        )

        spp_str = (
            "<strong>Species PLANTS Code<br/>Scientific Name / Common"
            " Name</strong>"
        )
        header_row = [p.Paragraph(spp_str, self.styles["contact_style"])]

        spp_str = "<strong>Species prevalence</strong>"
        header_row.append(p.Paragraph(spp_str, self.styles["contact_style"]))

        table = self.build_header_cell_count_table()
        header_row.append(table)

        kappa_str = "<strong>Kappa coefficient</strong>"
        header_row.append(p.Paragraph(kappa_str, self.styles["contact_style"]))
        species_table = [header_row]

        # Open the species accuracy file into a dataframe
        spp_df = pd.read_csv(self.species_accuracy_file)

        # Read in the stand attribute metadata
        metadata_parser = xsmp.XMLStandMetadataParser(self.stand_metadata_file)

        # Read in the report metadata if it exists
        if self.report_metadata_file:
            rmp = xrmp.XMLReportMetadataParser(self.report_metadata_file)
        else:
            rmp = None

        # Subset the attributes to just species
        attrs = [
            attr.field_name
            for attr in metadata_parser.attributes
            if attr.is_species_attr() and "NOTALY" not in attr.field_name
        ]

        # Subset species to just those with 0.5% prevalence
        common_species = spp_df[spp_df.PREVALENCE >= 0.005].SPECIES
        attrs = sorted(list(set(attrs) & set(common_species)))

        # Build the table with accuracy information
        species_table.extend(
            [self.build_species_table_row(spp, spp_df, rmp) for spp in attrs]
        )

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
