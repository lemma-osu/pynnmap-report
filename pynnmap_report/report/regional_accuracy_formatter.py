import os

import numpy as np
import pandas as pd
from reportlab import platypus as p
from reportlab.lib import units as u

from pynnmap_report.report import report_formatter
from pynnmap_report.report import report_styles
from pynnmap.misc import mpl_figures as mplf
from pynnmap.parser import xml_stand_metadata_parser as xsmp


class RegionalAccuracyFormatter(report_formatter.ReportFormatter):
    def __init__(self, parameter_parser):
        super(RegionalAccuracyFormatter, self).__init__()
        pp = parameter_parser
        self.regional_accuracy_file = pp.regional_accuracy_file
        self.stand_metadata_file = pp.stand_metadata_file
        self.id_field = pp.plot_id_field
        self.histogram_files = []

        # Ensure all input files are present
        files = [self.regional_accuracy_file, self.stand_metadata_file]
        try:
            self.check_missing_files(files)
        except report_formatter.MissingConstraintError as e:
            e.message += "\nSkipping RegionalAccuracyFormatter\n"
            raise e

    def run_formatter(self):
        # Create the histograms
        self.histogram_files = self._create_histograms()

        # Format the histograms into the main story
        return self._create_story(self.histogram_files)

    def clean_up(self):
        # Remove the histograms
        for fn in self.histogram_files:
            if os.path.exists(fn):
                os.remove(fn)

    def _create_histograms(self):
        # Open the area estimate file into a recarray
        ae_data = pd.read_csv(self.regional_accuracy_file)

        # Read in the stand attribute metadata
        mp = xsmp.XMLStandMetadataParser(self.stand_metadata_file)

        # Subset the attributes to those that are accuracy attributes,
        # are identified to go into the report, and are not species variables
        attrs = [
            attr.field_name
            for attr in mp.attributes
            if (
                attr.is_accuracy_attr()
                and attr.is_project_attr()
                and not attr.is_species_attr()
            )
        ]

        # Iterate over the attributes and create a histogram file of each
        histogram_files = []
        for attr in attrs:
            # Metadata for this attribute
            metadata = mp.get_attribute(attr)

            # Get the observed and predicted data for this attribute
            obs_vals = self._get_histogram_data(ae_data, attr, "OBSERVED")
            prd_vals = self._get_histogram_data(ae_data, attr, "PREDICTED")

            if len(obs_vals) == 0:
                continue

            # Set the areas for the observed and predicted data
            obs_area = obs_vals.AREA
            prd_area = prd_vals.AREA

            # Set the bin names (same for both observed and predicted series)
            bin_names = obs_vals.BIN_NAME
            if not np.array_equal(bin_names.values, prd_vals.BIN_NAME.values):
                err_msg = "Bin names are not the same for " + attr
                raise ValueError(err_msg)

            # Create the output file name
            output_file = attr.lower() + "_histogram.png"

            # Create the histogram
            mplf.draw_histogram(
                [obs_area, prd_area],
                bin_names,
                metadata,
                output_type=mplf.FILE,
                output_file=output_file,
            )

            # Add this to the list of histogram files
            histogram_files.append(output_file)

        # Return the list of histograms just created
        return histogram_files

    @staticmethod
    def _get_histogram_data(ae_data, attr, dataset):
        conds = (ae_data.VARIABLE == attr) & (ae_data.DATASET == dataset)
        return ae_data[conds]

    def _create_story(self, histogram_files):
        # Set up an empty list to hold the story
        story = []

        # Import the report styles
        styles = report_styles.get_report_styles()

        # Create a page break
        story = self._make_page_break(story, self.PORTRAIT)

        # Section title
        title_str = (
            "<strong>Regional-Scale Accuracy Assessment:<br/> Area"
            " Distributions from Regional Inventory Plots vs. GNN</strong>"
        )
        story.extend((self._make_title(title_str), p.Spacer(0, 0.20 * u.inch)))

        # Histogram explanation
        histo_str = """
            These histograms compare the distributions of land area in
            different vegetation conditions as estimated from a regional,
            sample- (plot-) based inventory (FIA Annual Plots) to model
            predictions from GNN (based on counts of 30-m pixels).
            <br/><br/>

            For the FIA annual plots, the distributions of forest area
            are determined by summing the 'area expansion factors' at the
            plot condition-class level. The plot-based estimates are
            subject to sampling error, but this is not shown in the graphs
            due to complexities involved.  For more information about the
            FIA Annual inventory sample design, see the
            <link href="http://fia.fs.fed.us/library/database-documentation"
            color="blue">FIADB Users Manual</link>.
            <br/><br/>

            Some plots were not visited on the ground due to denied
            access or hazardous conditions, so the area these plots
            represent cannot be characterized and is included in the bar
            labeled 'unsampled.'
            <br/><br/>

            The bars labeled 'nonforest' also require explanation. For GNN,
            this is the area of nonforest in the map, which is derived
            from ancillary (non-GNN) spatial data sources such as the
            National Land Cover Data (NLCD) or Ecological Systems maps
            from the Gap Analysis Program (GAP). This mapped nonforest is
            referred to as the GNN 'nonforest mask.'
            <br/><br/>

            For the plots, the 'nonforest' bar represents the nonforest area
            as estimated from the FIA Annual sample.
        """
        story.append(p.Paragraph(histo_str, styles["body_style"]))
        story.append(p.Spacer(0, 0.1 * u.inch))

        # Create a table of histograms and add to story
        story.append(self._make_figure_table(histogram_files))

        # Return this story
        return story
