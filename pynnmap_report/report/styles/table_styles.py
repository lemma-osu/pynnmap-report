from reportlab.platypus import TableStyle
from reportlab.lib import colors


def get_table_styles():
    return {
        "default_table_style": TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1, colors.white),
                ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    }
