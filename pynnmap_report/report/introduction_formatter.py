import itertools
import locale
from datetime import datetime

from reportlab import platypus as p
from reportlab.lib import colors
from reportlab.lib import units as u

from pynnmap_report import LEMMA_LOGO
from pynnmap_report.report.report_formatter import ReportFormatter, page_break
from pynnmap_report.report import report_styles
from pynnmap.parser import xml_report_metadata_parser as xrmp


class IntroductionFormatter(ReportFormatter):
    _required = ["report_metadata_file"]

    # Constants
    ACRES_PER_HECTARE = 2.471

    def __init__(self, parameter_parser):
        super().__init__()
        self.report_metadata_file = parameter_parser.report_metadata_file
        self.model_region = parameter_parser.model_region
        self.model_type = parameter_parser.model_type
        self.model_year = parameter_parser.model_year
        self.styles = report_styles.get_report_styles()

        self.check_missing_files()

    def report_heading(self, rmp):
        model_type_dict = {
            "sppsz": "Basal-Area by Species-Size Combinations",
            "trecov": "Tree Percent Cover by Species",
            "wdycov": "Woody Percent Cover by Species",
            "sppba": "Basal-Area by Species",
        }
        return [
            p.ImageAndFlowables(
                p.Image(
                    LEMMA_LOGO, 2.0 * u.inch, 1.96 * u.inch, mask="auto"
                ),
                [
                    p.Spacer(1, 0.2 * u.inch),
                    p.Paragraph(
                        "GNN Accuracy Assessment Report",
                        self.styles["title_style"]
                    ),
                    p.Paragraph(
                        "{} (Modeling Region {})".format(
                            rmp.model_region_name, self.model_region
                        ),
                        self.styles["sub_title_style"],
                    ),
                    p.Paragraph(
                        "Model Type: {}".format(
                            model_type_dict[self.model_type]),
                        self.styles["sub_title_style"],
                    ),
                ],
                imageSide="left",
                imageRightPadding=12,
            ),
            p.Spacer(0.0, 0.3 * u.inch),
        ]

    def model_region_description(self, rmp):
        return [
            p.ImageAndFlowables(
                p.Image(
                    rmp.image_path, 3.0 * u.inch, 3.86 * u.inch, mask="auto"
                ),
                [
                    p.Paragraph("Overview", self.styles["heading_style"]),
                    p.Paragraph(
                        rmp.model_region_overview, self.styles["body_style"]
                    ),
                ],
                imageSide="left",
                imageRightPadding=6,
            ),
            p.Spacer(0.0, 0.2 * u.inch),
        ]

    def contact_information(self, rmp):
        def _contact_cell(_contact):
            contact_str = """
                <b>{name}</b><br/>
                {position}<br/>
                {affiliation}><br/>
                Phone: {phone}<br/>
                Email: {email}"
            """
            return p.Paragraph(
                contact_str.format(
                    name=_contact.name,
                    position=_contact.position_title,
                    affiliation=_contact.affiliation,
                    phone=_contact.phone_number,
                    email=_contact.email_address,
                ),
                self.styles["body_style_9"],
            )

        contact_table = []
        contact_row = []
        table_cols = min(3, len(rmp.contacts))
        for i, contact in enumerate(rmp.contacts):
            contact_row.append(_contact_cell(contact))
            if i % table_cols == table_cols - 1:
                contact_table.append(contact_row)
                contact_row = []
        table = p.Table(contact_table)
        table.setStyle(
            p.TableStyle(
                [
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("BACKGROUND", (0, 0), (-1, -1), "#f1efe4"),
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 1.0, colors.white),
                ]
            )
        )
        return [
            p.Paragraph("Contact Information:", self.styles["heading_style"]),
            p.Spacer(0.0, 0.1 * u.inch),
            table,
            p.Spacer(0, 0.15 * u.inch),
        ]

    def website_information(self):
        return [
            p.Paragraph(
                (
                    "<strong>LEMMA Website:</strong> "
                    '<link color="#0000ff" '
                    'href="https://lemma.forestry.oregonstate.edu/">'
                    "https://lemma.forestry.oregonstate.edu</link>"
                ),
                self.styles["body_style"],
            )
        ]

    def model_information(self, rmp):
        time_str = "<strong>Report Date:</strong> {}".format(
            datetime.now().strftime("%Y.%m.%d")
        )

        # Model region area
        locale.setlocale(locale.LC_ALL, "")
        mr_area_ha = rmp.model_region_area
        mr_area_ac = mr_area_ha * self.ACRES_PER_HECTARE
        area_str = (
            "<strong>Model Region Area:</strong> {} hectares ({} acres)"
        ).format(
            locale.format("%d", mr_area_ha, True),
            locale.format("%d", mr_area_ac, True),
        )

        # Model imagery date
        mr_imagery_str = "<strong>Model Imagery Date:</strong> {}".format(
            self.model_year
        )

        return [
            p.Paragraph("General Information", self.styles["heading_style"]),
            p.Spacer(0, 0.1 * u.inch),
            p.Paragraph(time_str, self.styles["body_style"]),
            p.Spacer(0, 0.1 * u.inch),
            p.Paragraph(area_str, self.styles["body_style"]),
            p.Spacer(0, 0.1 * u.inch),
            p.Paragraph(mr_imagery_str, self.styles["body_style"]),
            p.Spacer(0, 0.1 * u.inch),
        ]

    def plot_matching(self):
        plot_title = """
            <strong>Matching Plots to Imagery for Model Development:</strong>
        """
        imagery_str = """
            The current versions of the GNN maps were developed using
            data from inventory plots that span a range of dates, and
            from a yearly time-series of Landsat imagery mosaics from
            1984 to 2012 developed with the LandTrendr algorithms
            (Kennedy et al., 2010). For model development, plots were
            matched to spectral data for the same year as plot
            measurement. In addition, because as many as four plots were
            measured at a given plot location, we constrained the
            imputation for a given map year to only one plot from each
            location -- the plot nearest in date to the imagery (map)
            year. See Ohmann et al. (in press) for more detailed
            information about the GNN modeling process.
        """
        return [
            p.Paragraph(plot_title, self.styles["body_style"]),
            p.Spacer(0, 0.1 * u.inch),
            p.Paragraph(imagery_str, self.styles["body_style"]),
            p.Spacer(0, 0.10 * u.inch),
        ]

    def mask_information(self):
        mask_str = """
            An important limitation of the GNN map products is the separation
            of forest and nonforest lands. The GNN modeling applies to forest
            areas only, where we have detailed field plot data. Nonforest
            areas are 'masked' as such using an ancillary map. In California,
            Oregon, Washington and parts of adjacent states, we are using
            maps of Ecological Systems developed for the Gap Analysis
            Program (GAP) as our nonforest mask. There are 'unmasked'
            versions of our GNN maps available upon request,
            in case you have an alternative map of nonforest for your area
            of interest that you would like to apply to the GNN maps.
        """
        return [
            p.Paragraph(
                "<strong>Nonforest Mask Information:</strong>",
                self.styles["body_style"],
            ),
            p.Spacer(0, 0.1 * u.inch),
            p.Paragraph(mask_str, self.styles["body_style"]),
            p.Spacer(0, 0.1 * u.inch),
        ]

    def _build_year_count_row(self, year):
        return (
            year.plot_count,
            [
                p.Paragraph(
                    year.assessment_year, self.styles["contact_style_right"]
                ),
                p.Paragraph(
                    str(year.plot_count), self.styles["contact_style_right"]
                ),
            ],
        )

    def _build_data_source_row(self, source):
        plot_count_table = []
        plot_count = 0
        for year in source.assessment_years:
            count, flowable = self._build_year_count_row(year)
            plot_count += count
            plot_count_table.append(flowable)

        table = p.Table(plot_count_table)
        table.setStyle(self.styles["default_table_style"])

        return (
            plot_count,
            [
                p.Paragraph(source.data_source, self.styles["contact_style"]),
                p.Paragraph(source.description, self.styles["contact_style"]),
                table,
            ],
        )

    def _build_long_data_source_row(self, source):
        years = (x.assessment_year for x in source.assessment_years)
        count = sum(x.plot_count for x in source.assessment_years)
        return (
            count,
            [
                p.Paragraph(source.data_source, self.styles["contact_style"]),
                p.Paragraph(source.description, self.styles["contact_style"]),
                p.Paragraph(
                    "{}-{}: {}".format(min(years), max(years), count),
                    self.styles["contact_style_right"],
                ),
            ],
        )

    def plots_by_date(self, rmp):
        # Header row
        plot_table = [
            [
                p.Paragraph(
                    "<strong>Data Source</strong>", self.styles["contact_style"]
                ),
                p.Paragraph(
                    "<strong>Description</strong>", self.styles["contact_style"]
                ),
                p.Paragraph(
                    "<strong>Plot Count by Year</strong>",
                    self.styles["contact_style"],
                ),
            ]
        ]

        # Data source rows
        total_plots = 0
        for source in rmp.plot_data_sources:
            if len(source.assessment_years) > 30:
                ds_count, flowable = self._build_long_data_source_row(source)
            else:
                ds_count, flowable = self._build_data_source_row(source)
            total_plots += ds_count
            plot_table.append(flowable)

        # Summary row
        plot_table.append(
            [
                "",
                p.Paragraph(
                    "Total Plots", self.styles["contact_style_right_bold"]
                ),
                p.Paragraph(
                    str(total_plots), self.styles["contact_style_right_bold"]
                ),
            ]
        )

        table = p.Table(
            plot_table, colWidths=[1.3 * u.inch, 4.2 * u.inch, 1.3 * u.inch]
        )
        table.hAlign = "LEFT"
        table.setStyle(
            p.TableStyle(
                [
                    ("GRID", (0, 0), (-1, -2), 1.5, colors.white),
                    ("BOX", (0, -1), (-1, -1), 1.5, colors.white),
                    ("LINEAFTER", (1, -1), (1, -1), 1.5, colors.white),
                    ("BACKGROUND", (0, 0), (-1, -1), "#f1efe4"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (1, -2), 2),
                    ("BOTTOMPADDING", (0, 0), (1, -2), 2),
                    ("LEFTPADDING", (0, 0), (1, -2), 6),
                    ("RIGHTPADDING", (0, 0), (1, -2), 6),
                    ("ALIGNMENT", (0, 0), (1, -2), "LEFT"),
                    ("TOPPADDING", (2, 0), (2, 0), 2),
                    ("BOTTOMPADDING", (2, 0), (2, 0), 2),
                    ("LEFTPADDING", (2, 0), (2, 0), 6),
                    ("RIGHTPADDING", (2, 0), (2, 0), 6),
                    ("ALIGNMENT", (2, 0), (2, 0), "LEFT"),
                    ("TOPPADDING", (2, 1), (2, -2), 0),
                    ("BOTTOMPADDING", (2, 1), (2, -2), 0),
                    ("LEFTPADDING", (2, 1), (2, -2), 0),
                    ("RIGHTPADDING", (2, 1), (2, -2), 0),
                    ("ALIGNMENT", (2, 1), (2, -2), "LEFT"),
                    ("TOPPADDING", (0, -1), (2, -1), 4),
                    ("BOTTOMPADDING", (0, -1), (2, -1), 4),
                    ("LEFTPADDING", (0, -1), (2, -1), 6),
                    ("RIGHTPADDING", (0, -1), (2, -1), 6),
                    ("ALIGNMENT", (0, -1), (2, -1), "RIGHT"),
                ]
            )
        )

        return [
            p.Paragraph(
                "<strong>Inventory Plots in Model Development</strong>",
                self.styles["heading_style"],
            ),
            p.Spacer(0, 0.10 * u.inch),
            table,
        ]

    def _build_spatial_predictor_row(self, predictor):
        return [
            p.Paragraph(predictor.field_name, self.styles["contact_style"]),
            p.Paragraph(predictor.description, self.styles["contact_style"]),
            p.Paragraph(predictor.source, self.styles["contact_style"]),
        ]

    def spatial_predictors(self, rmp):
        ord_var_str = """
            The list below represents the spatial predictor
            (GIS/remote sensing) variables that were used in creating
            this model.
        """

        # Header row
        ordination_table = [
            [
                p.Paragraph(
                    "<strong>Variable</strong>", self.styles["contact_style"]
                ),
                p.Paragraph(
                    "<strong>Description</strong>", self.styles["contact_style"]
                ),
                p.Paragraph(
                    "<strong>Data Source</strong>", self.styles["contact_style"]
                ),
            ],
        ]

        # Data rows
        for predictor in rmp.ordination_variables:
            flowable = self._build_spatial_predictor_row(predictor)
            ordination_table.append(flowable)

        table = p.Table(
            ordination_table,
            colWidths=[1.0 * u.inch, 2.3 * u.inch, 3.5 * u.inch],
        )
        table.hAlign = "LEFT"
        table.setStyle(
            p.TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 1.5, colors.white),
                    ("BACKGROUND", (0, 0), (-1, -1), "#f1efe4"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        return [
            p.Paragraph(
                "Spatial Predictor Variables in Model Development",
                self.styles["heading_style"],
            ),
            p.Spacer(0, 0.10 * u.inch),
            p.Paragraph(ord_var_str, self.styles["body_style"]),
            p.Spacer(0, 0.1 * u.inch),
            table,
        ]

    def run_formatter(self):
        # Report metadata
        rmp = xrmp.XMLReportMetadataParser(self.report_metadata_file)

        # Only run self.plot_matching when sppsz
        if self.model_type == "sppsz":
            pass

        story = [
            self.report_heading(rmp),
            self.model_region_description(rmp),
            self.contact_information(rmp),
            self.website_information(),
            page_break(self.PORTRAIT),
            self.model_information(rmp),
            self.plot_matching(),
            self.mask_information(),
            page_break(self.PORTRAIT),
            self.plots_by_date(rmp),
            page_break(self.PORTRAIT),
            self.spatial_predictors(rmp),
        ]
        return list(itertools.chain.from_iterable(story))
