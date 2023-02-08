from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ImageAndFlowables,
    Paragraph,
    Spacer,
    Table,
)

from .report_formatter import ReportFormatter, page_break
from .. import (
    PLOT_DIAGRAM,
    LOCAL_SCATTER,
    ERROR_MATRIX,
    REGIONAL_HISTOGRAM,
    HEX_10_SCATTER,
    HEX_30_SCATTER,
    HEX_50_SCATTER,
)


class AccuracyIntroductionFormatter(ReportFormatter):
    def __init__(self):
        super().__init__()

    def run_formatter(self):
        """
        Create an introduction to the AttributeAccuracy section
        """
        flowables = page_break(self.PORTRAIT)

        # Section title
        title = "Continuous Attribute Accuracy Assessment"
        flowables.extend(self.create_section_title(title))

        intro = """
            On the following pages, we present accuracy assessment for
            each of the core GNN continuous attributes.  Core attributes
            include those most commonly requested by users and represent a
            broad cross section of forest stand attributes.  We assess accuracy
            at a variety of spatial scales, from the scale of the FIA plots
            that serve as neighbors in GNN modeling to the scale of the full
            modeling region. We have also included accuracy information at
            three intermediate scales based on the assessment protocol
            detailed in Riemann et al. (2010). This introduction serves as a
            key to understanding the diagnostics on the following pages.
        """
        flowables.append(Paragraph(intro, self.styles["body_style"]))
        flowables.append(Spacer(0, 0.15 * inch))

        local_str = """
            For local scale accuracy assessment, we present a scatterplot of
            paired observed (Y) and predicted (X) values for all plots that were
            included in model development.  Observed values come directly from
            the FIA plot data and are calculated across all forested conditions
            on a plot.  Predicted values are calculated from a modified
            leave-one-out technique.  Using a 90-m x 90-m area centered
            on the plot location (see right), we calculate predictions for each
            of the nine 30-m pixels.  Although all plots are used in model
            development, we restrict the prediction to come only from
            independent neighbors - that is a plot may not use itself (nor any
            co-located plot measured at a different time) in prediction.  For
            each pixel, we extract the first seven independent candidate
            neighbors, weight each neighbor based on values that approximate
            a bootstrapped sample (see Bell et al. (2015) for more information),
            and calculate the weighted average.  The plot predicted value is
            calculated as the unweighted average across all nine pixels.
            <br/><br/>
            We include three statistical measures of agreement: the correlation
            coefficient, root mean squared error normalized by the observed
            values' mean, and the coefficient of determination (R-square).  
            We also display the 1:1 line between observed and predicted values
            and color the dots based on a kernel density estimator to
            highlight frequent values in the distribution.  Lower densities
            of points are displayed in blue and higher densities are displayed
            in yellow.
            <br/><br/>
            In addition, we present a confusion matrix based on binning the 
            observed-predicted pairs using a natural breaks classification.
            Both strict and fuzzy class accuracy are displayed, with fuzzy
            classes defined as +/- one class from the actual class.  Strict
            classes are shaded as darker gray and fuzzy classes as shaded as
            lighter gray.
        """
        flowables.extend(
            [
                Paragraph(
                    "Local (Plot) Scale Accuracy", self.styles["heading_style"]
                ),
                Spacer(0, 0.15 * inch),
                ImageAndFlowables(
                    Image(PLOT_DIAGRAM, 2.0 * inch, 1.96 * inch, mask="auto"),
                    [Paragraph(local_str, self.styles["body_style"])],
                    imageSide="right",
                    imageLeftPadding=12,
                ),
                Spacer(0, 0.15 * inch),
                Table(
                    [
                        [
                            Image(
                                LOCAL_SCATTER,
                                width=3.2 * inch,
                                height=3.2 * inch,
                            ),
                            Image(
                                ERROR_MATRIX,
                                width=4.107 * inch,
                                height=3.2 * inch,
                            ),
                        ]
                    ],
                    style=self.table_styles["default"],
                    hAlign="LEFT",
                ),
            ]
        )
        flowables.extend(page_break(self.PORTRAIT))

        regional_str = """
            For regional scale accuracy assessment, we compare forest area
            using three different methods.  First, a design-based sample from
            the FIA plots is used to estimate nonforest area and forested
            area of the attribute split into six classes.  Area
            expansion factors are associated with each plot based on the
            relative proportion of each condition on a plot.  Note that the
            plot estimate typically includes unsampled areas that were
            inaccessible due to hazardous conditions or denied access.  
            <br/><br/>
            The plots that comprise the FIA estimate are those nearest in time
            to the model year.  Because the FIA data is collected on a 10-year
            annual cycle, plot assessment dates may be up to ten years
            different than the current GNN model year.  There may arise
            discrepancies between the plot sample and mapped (GNN) estimate
            due to this temporal inconsistency, especially in disturbance 
            impacted landscapes.  It is also important to note that plots that
            are included in the design-based estimate may or may not be used
            as model plots for GNN - for example, plots that straddle two or
            more distinct forested conditions will not be included in GNN 
            model building but are used in design-based area estimation.
            <br/><br/>
            The second series shows GNN model predictions based on grouping
            pixel areas into the classes defined by natural breaks
            classification of the plot data.  Because GNN is predicted across
            all forested pixels, there will be no corresponding unsampled
            area.  As such, the sum of area across forest and nonforest
            classes will be greater in the GNN estimate than in the FIA
            estimate.
            <br/><br/>
            Lastly, the third series is based on an area estimation technique
            introduced by Olofsson et al. (2013).  In this approach, an
            error matrix is constructed for all plots that were used in the
            design-based sample using the same bin endpoints.  We further
            subset this population to include only plots that were at least
            50% forested.  The error matrix is used to adjust the
            mapped (GNN) based estimates to more closely approximate the
            relative distribution of this design-based sample.  In addition,
            confidence intervals are constructed which vary as a function
            of the agreement in the error matrix.  Note that GNN and this
            error-adjusted series sum to exactly the same area and, as such,
            the error-adjusted series can be a useful tool in estimating how
            the unsampled area may be distributed.  Error-corrected estimates
            are not provided for nonforest and unsampled classes as denoted
            by asterisks in the histogram.  
        """
        flowables.extend(
            [
                Paragraph(
                    "Regional Scale Accuracy", self.styles["heading_style"]
                ),
                Spacer(0, 0.15 * inch),
                Paragraph(regional_str, self.styles["body_style"]),
                Spacer(0, 0.15 * inch),
                Image(REGIONAL_HISTOGRAM, width=7.5 * inch, height=2.5 * inch),
                Spacer(0, 0.15 * inch),
            ]
        )
        flowables.extend(page_break(self.PORTRAIT))

        riemann_str = """
            Finally, to assess intermediate scales of GNN model performance,
            we rely on the assessment protocol introduced by Riemann et al.
            (2010).  We constructed three spatial scales of hexagon
            tessellations across our model region: 10-km spacing between
            hexagon centers (8,660 ha), 30-km spacing (78,100 ha), and 50-km
            spacing (216,500 ha).  We first calculate paired observed-predicted
            values as in the local accuracy assessment for every FIA plot
            (again using the FIA plot at each location temporally closest to
            the GNN model year).
            <br/><br/>
            For every hexagon, both the observed and predicted means are
            calculated across all plots within that hexagon. As the spatial
            scale of the hexagons increase, more plots are included in the
            calculation of mean observed and predicted values. The paired
            means for each hexagon are then displayed as scatterplots.  The
            average number of plots in each hexagon as well as the number of
            hexagons in the modeling region are reported on the scatterplot.  
            <br/><br/>
            Generally, as spatial scale increases, there is a tighter
            correspondence between hexagon observed and predicted mean values.
            When this behavior is observed in the scatterplot (and decreasing
            normalized RMSE), it suggests that the correspondence between
            design-based estimates (plots) and model-based estimates (GNN) 
            converge reliably as a function of spatial scale. While hexagons
            themselves are a specific spatial scale, the area of forest being
            used for comparison is far less. For example, for the 8,660 ha
            hexagons, only about 5 ha are being compared for the average
            hexagon (i.e., at the plot footprints). Thus, interpretation of
            reported accuracies as a direct measure of GNN accuracy at the
            designated hexagon scale may not be appropriate.
        """
        subheading_style = self.styles["subheading"]
        flowables.extend(
            [
                Paragraph(
                    "Accuracy Across Scales", self.styles["heading_style"]
                ),
                Spacer(0, 0.15 * inch),
                Paragraph(riemann_str, self.styles["body_style"]),
                Spacer(0, 0.15 * inch),
                Table(
                    [
                        [
                            Image(
                                HEX_10_SCATTER,
                                width=2.4 * inch,
                                height=2.4 * inch,
                            ),
                            Image(
                                HEX_30_SCATTER,
                                width=2.4 * inch,
                                height=2.4 * inch,
                            ),
                            Image(
                                HEX_50_SCATTER,
                                width=2.4 * inch,
                                height=2.4 * inch,
                            ),
                        ],
                        [
                            Spacer(1, 0.05 * inch),
                            Spacer(1, 0.05 * inch),
                            Spacer(1, 0.05 * inch),
                        ],
                        [
                            Paragraph("8,660 ha hexagons", subheading_style),
                            Paragraph("78,100 ha hexagons", subheading_style),
                            Paragraph("216,5000 ha hexagons", subheading_style),
                        ],
                    ],
                    style=self.table_styles["no_padding"],
                ),
            ]
        )

        return flowables
