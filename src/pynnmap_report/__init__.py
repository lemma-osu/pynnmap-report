"""
Automatic report generation for pynnmap
"""
import os

__version__ = "0.2.0"

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Report assets
LEMMA_LOGO = os.path.join(BASEDIR, "resources/lemma_logo.png")
PLOT_DIAGRAM = os.path.join(BASEDIR, "resources/report/plot_diagram.png")
LOCAL_SCATTER = os.path.join(BASEDIR, "resources/report/local_scatter.png")
ERROR_MATRIX = os.path.join(BASEDIR, "resources/report/error_matrix.png")
REGIONAL_HISTOGRAM = os.path.join(
    BASEDIR, "resources/report/regional_histogram.png"
)
HEX_10_SCATTER = os.path.join(BASEDIR, "resources/report/hex_10_scatter.png")
HEX_30_SCATTER = os.path.join(BASEDIR, "resources/report/hex_30_scatter.png")
HEX_50_SCATTER = os.path.join(BASEDIR, "resources/report/hex_50_scatter.png")
