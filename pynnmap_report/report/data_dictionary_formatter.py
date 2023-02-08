"""
Formatter for listing the attribute data dictionary
"""
from reportlab import platypus as p
from reportlab.lib import units as u

from pynnmap.parser import xml_stand_metadata_parser as xsmp

from .report_formatter import ReportFormatter, page_break, txt_to_html


class DataDictionaryFormatter(ReportFormatter):
    """
    Formatter for listing the attribute data dictionary
    """

    _required = ["stand_metadata_file"]

    def __init__(self, parameter_parser):
        super().__init__()
        self.stand_metadata_file = parameter_parser.stand_metadata_file
        self.model_type = parameter_parser.model_type

        self.check_missing_files()

    def run_formatter(self):
        """
        Run formatter to create the data dictionary
        """
        # Set up an empty list to hold the story
        story = []

        # Create a page break
        story.extend(page_break(self.PORTRAIT))

        # Section title
        title = "Data Dictionary"
        story.extend(self.create_section_title(title))

        # Read in the stand attribute metadata
        metadata_parser = xsmp.XMLStandMetadataParser(self.stand_metadata_file)

        # Subset the attributes to those that are accuracy attributes, are
        # identified to go into the report, and are not species variables
        attrs = []
        for attr in metadata_parser.attributes:
            if (
                attr.is_accuracy_attr() is True
                and attr.is_project_attr() is True
                and attr.is_species_attr() is False
            ):
                attrs.append(attr.field_name)

        # Set up the master dictionary table
        dictionary_table = []

        # Iterate through the attributes and print out the field information
        # and codes if present
        for attr in attrs:
            metadata = metadata_parser.get_attribute(attr)
            field_name = metadata.field_name
            units = metadata.units
            description = metadata.description

            field_para = p.Paragraph(field_name, self.styles["body_9"])
            if units != "none":
                description += " (" + units + ")"
            field_desc_para = p.Paragraph(description, self.styles["body_9"])

            # If this field has codes, create a sub table underneath the
            # field description
            if metadata.codes:

                # Set up a container to hold the code rows
                code_table = []

                # Iterate over all code rows and append to the code_table
                for code in metadata.codes:
                    code_para = p.Paragraph(
                        code.code_value, self.styles["code_style"]
                    )
                    description = txt_to_html(code.description)
                    code_desc_para = p.Paragraph(
                        description, self.styles["code_style"]
                    )
                    code_table.append([code_para, code_desc_para])

                # Convert this to a reportlab table
                table = p.Table(
                    code_table, colWidths=[0.75 * u.inch, 4.75 * u.inch]
                )
                table.setStyle(self.table_styles["code_table"])

                # Create a stack of the field description and field codes
                elements = [[field_desc_para], [table]]

            # If no codes exist, just add the field description
            else:
                elements = [[field_desc_para]]

            # Create a reportlab table of the field description and
            # (if present) field codes
            description_table = p.Table(elements, colWidths=[5.5 * u.inch])
            description_table.setStyle(self.table_styles["description_table"])
            dictionary_table.append([field_para, description_table])

        # Format the dictionary table into a reportlab table
        table = p.Table(
            dictionary_table, colWidths=[1.85 * u.inch, 5.65 * u.inch]
        )
        table.setStyle(self.table_styles["data_dictionary"])
        story.append(table)

        # Description of the species information that is attached to ArcInfo
        # grids.  We don't enumerate the codes here, but just give this
        # summary information
        spp_str = """
            Individual species codes are based on the <link color="#0000ff"
            href="http://plants.usda.gov/">USDA PLANTS database</link> from
            the year 2000, and values represent species
        """
        if self.model_type in ["sppsz", "sppba"]:
            spp_str += " basal area (m^2/ha)."
        elif self.model_type in ["trecov", "wdycov"]:
            spp_str += " percent cover."

        para = p.Paragraph(spp_str, self.styles["body_style"])
        story.append(p.Spacer(0, 0.1 * u.inch))
        story.append(para)

        # Return this story
        return story
