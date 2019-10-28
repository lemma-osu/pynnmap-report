from reportlab import platypus as p
from reportlab.lib import units as u

from pynnmap_report.report import report_formatter
from pynnmap_report.report import report_styles


class ReferencesFormatter(report_formatter.ReportFormatter):

    def __init__(self):
        super(ReferencesFormatter, self).__init__()

    def run_formatter(self):
        return self._create_story()

    def clean_up(self):
        pass

    def _create_story(self):

        # Set up an empty list to hold the story
        story = []

        # Import the report styles
        styles = report_styles.get_report_styles()

        # Create a page break
        story = self._make_page_break(story, self.PORTRAIT)

        # Section title
        title_str = '<strong>References</strong>'
        story.append(self._make_title(title_str))
        story.append(p.Spacer(0, 0.1 * u.inch))

        # List of references used
        references = [
            '''
            Cohen, J. 1960. "A coefficient of agreement for
            nominal scales." Educational and Psychological Measurement
            20: 37-46.
            ''',
            '''
            Kennedy, RE, Z Yang and WB Cohen. 2010. "Detecting trends
            in forest disturbance and recovery using yearly Landsat
            time series: 1. Landtrendr -- Temporal segmentation
            algorithms." Remote Sensing of Environment 114(2010):
            2897-2910.
            ''',
            '''
            Ohmann, JL, MJ Gregory and HM Roberts. 2014 (in press). "Scale
            considerations for integrating forest inventory plot data and
            satellite image data for regional forest mapping." Remote
            Sensing of Environment.
            ''',
            '''
            O'Neil, TA, KA Bettinger, M Vander Heyden, BG Marcot, C Barrett,
            TK Mellen, WM Vanderhaegen, DH Johnson, PJ Doran, L Wunder, and
            KM Boula. 2001. "Structural conditions and habitat elements of
            Oregon and Washington. Pages 115-139 in: Johnson, DH and TA
            O'Neil, editors. 2001. "Wildlife-habitat relationships in Oregon
            and Washington." Oregon State University Press, Corvallis, OR.
            ''',
        ]

        # Print all references
        for reference in references:
            para = p.Paragraph(reference, styles['body_style'])
            story.append(para)
            story.append(p.Spacer(0, 0.10 * u.inch))

        # Return this story
        return story
