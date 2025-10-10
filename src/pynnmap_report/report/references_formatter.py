"""
Formatter to add citations to report
"""
from reportlab import platypus as p
from reportlab.lib import units as u

from . import report_formatter
from .report_formatter import page_break


class ReferencesFormatter(report_formatter.ReportFormatter):
    """
    Formatter to add citations to report
    """

    def __init__(self):
        super(ReferencesFormatter, self).__init__()

    def run_formatter(self):
        """Run the formatter"""
        # Set up an empty list to hold the story
        story = []

        # Create a page break
        story.extend(page_break(self.PORTRAIT))

        # Section title
        title = "References"
        story.extend(self.create_section_title(title))

        # List of references used
        references = [
            """
            Bell, DM, MJ Gregory, and JL Ohmann. 2015. "Imputed forest
            structure uncertainty varies across elevational and longitudinal
            gradients in the western Cascade Mountains, Oregon, USA."
            Forest Ecology and Management 358: 154-164.
            """,
            """
            Cohen, J. 1960. "A coefficient of agreement for
            nominal scales." Educational and Psychological Measurement
            20: 37-46.
            """,
            """
            Olofsson, P, GM Foody, SV Stehman, and CE Woodcock. 2013.
            "Making better use of accuracy data in land change studies:
            Estimating accuracy and area and quantifying uncertainty using
            stratified estimation." Remote Sensing of Environment 129: 122-131.
            """,
            """
            Ohmann, JL, MJ Gregory, and HM Roberts. 2014. "Scale
            considerations for integrating forest inventory plot data and
            satellite image data for regional forest mapping." Remote
            Sensing of Environment 151: 3-15.
            """,
            """
            O'Neil, TA, KA Bettinger, M Vander Heyden, BG Marcot, C Barrett,
            TK Mellen, WM Vanderhaegen, DH Johnson, PJ Doran, L Wunder, and
            KM Boula. 2001. "Structural conditions and habitat elements of
            Oregon and Washington. Pages 115-139 in: Johnson, DH and TA
            O'Neil, editors. 2001. "Wildlife-habitat relationships in Oregon
            and Washington." Oregon State University Press, Corvallis, OR.
            """,
            """
            Riemann, R, BT Wilson, A Lister, and S Parks. 2010. "An effective
            assessment protocol for continuous geospatial datasets of
            forest characteristics using USFS Forest Inventory and
            Analysis (FIA) data." Remote Sensing of Environment 114: 2337-2352.
            """,
            """
            Zhu, Z and CE Woodcock. 2014. "Continuous change detection and
            classification of land cover using all available Landsat data."
            Remote Sensing of Environment 144: 152-171.
            """,
        ]

        # Print all references
        for reference in references:
            story.extend(
                [
                    p.Paragraph(reference, self.styles["body_style"]),
                    p.Spacer(0, 0.15 * u.inch),
                ]
            )

        # Return this story
        return story

    def clean_up(self):
        pass
