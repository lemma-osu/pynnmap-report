import os

import pandas as pd
from reportlab import platypus as p
from reportlab.lib import units as u

from pynnmap.misc import mpl_figures as mplf
from pynnmap.parser import xml_stand_metadata_parser as xsmp

from pynnmap_report.report import report_formatter
from pynnmap_report.report import report_styles


class LocalAccuracyFormatter(report_formatter.ReportFormatter):

    def __init__(self, parameter_parser):
        super(LocalAccuracyFormatter, self).__init__()
        pp = parameter_parser
        self.observed_file = pp.stand_attribute_file
        self.predicted_file = pp.independent_predicted_file
        self.stand_metadata_file = pp.stand_metadata_file
        self.id_field = pp.plot_id_field
        self.scatter_files = []

        # Ensure all input files are present
        files = [
            self.observed_file, self.predicted_file, self.stand_metadata_file]
        try:
            self.check_missing_files(files)
        except report_formatter.MissingConstraintError as e:
            e.message += '\nSkipping LocalAccuracyFormatter\n'
            raise e

    def run_formatter(self):
        # Create the scatterplots
        self.scatter_files = self._create_scatterplots()

        # Format the scatterplots into the main story
        return self._create_story(self.scatter_files)

    def clean_up(self):
        # Remove the scatterplots
        for fn in self.scatter_files:
            if os.path.exists(fn):
                os.remove(fn)

    def _create_scatterplots(self):
        # Read in the observed and predicted CSV files
        obs_df = pd.read_csv(self.observed_file, index_col=self.id_field)
        prd_df = pd.read_csv(self.predicted_file, index_col=self.id_field)

        # Subset the obs_df to just those IDs in the predicted data
        obs_df = obs_df[obs_df.index.isin(prd_df.index)]

        # Read in the stand attribute metadata
        mp = xsmp.XMLStandMetadataParser(self.stand_metadata_file)

        # Subset the attributes to those that are continuous, are accuracy
        # attributes, are identified to go into the report, and are not
        # species variables
        attrs = []
        for attr in mp.attributes:
            if attr.field_type == 'CONTINUOUS' and \
                    attr.is_project_attr() is True and \
                    attr.is_accuracy_attr() is True and \
                    attr.is_species_attr() is False:
                attrs.append(attr.field_name)

        # Iterate over the attributes and create a scatterplot file of each
        scatter_files = []
        for attr in attrs:

            # Metadata for this attribute
            metadata = mp.get_attribute(attr)

            # Observed and predicted data matrices for this attribute
            obs_vals, prd_vals = obs_df[attr], prd_df[attr]

            # Create the output file name
            output_file = attr.lower() + '_scatter.png'

            # Create the scatterplot
            mplf.draw_scatterplot(
                prd_vals, obs_vals, metadata, output_type=mplf.FILE,
                output_file=output_file)

            # Add this to the list of scatterplot files
            scatter_files.append(output_file)

        # Return the list of scatterplots just created
        return scatter_files

    def _create_story(self, scatter_files):
        # Set up an empty list to hold the story
        story = []

        # Import the report styles
        styles = report_styles.get_report_styles()

        # Create a page break
        story = self._make_page_break(story, self.PORTRAIT)

        # Section title
        title_str = '<strong>Local-Scale Accuracy Assessment: '
        title_str += 'Scatterplots of Observed vs. Predicted '
        title_str += 'Values for Continuous Variables at '
        title_str += 'Plot Locations</strong>'
        story.append(self._make_title(title_str))
        story.append(p.Spacer(0, 0.2 * u.inch))

        # Scatter explanation
        scatter_str = '''
            These scatterplots compare the observed plot values against
            predicted (modeled) values for each plot used in the GNN model.
            We use a modified leave-one-out (LOO) approach.  In traditional
            LOO accuracy assessment, a model is run with <i>n</i>-1
            plots and then accuracy is determined at the plot left out of
            modeling, for all plots used in modeling.  Because of computing
            limitations, we use a 'second-nearest-neighbor' approach.  We
            develop our models with all plots, but in determining accuracy, we
            don't allow a plot to assign itself as a neighbor at the plot
            location.  This yields similar accuracy assessment results as
            a true cross-validation approach, but probably slightly
            underestimates the true accuracy of the distributed
            (first-nearest-neighbor) map.<br/><br/>
            The observed value comes directly from the plot data,
            whereas the predicted value comes from the GNN prediction
            for the plot location.  The GNN prediction is the mean of
            pixel values for a window that approximates the
            field plot configuration.<br/><br/>
            The correlation coefficients, normalized Root Mean Squared
            Errors (RMSE), and coefficients of determination (R-square) are
            given. The RMSE is normalized by dividing the RMSE by the
            observed mean value.
        '''
        story.append(p.Paragraph(scatter_str, styles['body_style']))
        story.append(p.Spacer(0, 0.1 * u.inch))

        # Create a table of scatterplots and add to story
        story.append(self._make_figure_table(scatter_files))

        # Return this story
        return story
