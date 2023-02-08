from reportlab.platypus import TableStyle
from reportlab.lib import colors


def get_table_styles():
    styles = dict()
    styles["default"] = TableStyle(
        [
            ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]
    )

    styles["default_shaded"] = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), "#efefef"),
            ("GRID", (0, 0), (-1, -1), 0.25, "#cccccc"),
        ],
        parent=styles["default"],
    )

    styles["dark_shaded"] = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), "#444444"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ],
        parent=styles["default"],
    )

    styles["title"] = TableStyle(
        [
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ],
        parent=styles["default"],
    )

    styles["contacts"] = TableStyle(
        [
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ],
        parent=styles["default_shaded"],
    )

    styles["plot_listing"] = TableStyle(
        [
            ("TOPPADDING", (2, 1), (2, -2), 0),
            ("BOTTOMPADDING", (2, 1), (2, -2), 0),
            ("LEFTPADDING", (2, 1), (2, -2), 0),
            ("RIGHTPADDING", (2, 1), (2, -2), 0),
            ("TOPPADDING", (0, -1), (2, -1), 4),
            ("BOTTOMPADDING", (0, -1), (2, -1), 4),
            ("ALIGNMENT", (0, -1), (2, -1), "RIGHT"),
        ],
        parent=styles["default_shaded"],
    )

    styles["no_padding"] = TableStyle(
        [
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ],
        parent=styles["default"],
    )

    styles["error_matrix"] = TableStyle(
        [
            ("SPAN", (0, 0), (1, 1)),
            ("SPAN", (0, 2), (0, -1)),
            ("SPAN", (2, 0), (-1, 0)),
            ("GRID", (0, 0), (-1, -1), 0.25, "#cccccc"),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOX", (0, 0), (-1, -1), 1.25, colors.black),
            ("ALIGNMENT", (1, 0), (-1, 0), "CENTER"),
            ("ALIGNMENT", (2, 1), (-1, 1), "CENTER"),
            ("VALIGN", (0, 2), (-1, -1), "CENTER"),
            ("VALIGN", (2, 1), (-1, 1), "BOTTOM"),
            ("BOTTOMPADDING", (0, 0), (-1, 1), 4),
        ],
        parent=styles["default"],
    )

    styles["species_accuracy"] = TableStyle(
        [
            ("VALIGN", (0, 1), (0, -1), "MIDDLE"),
            ("ALIGNMENT", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (1, 1), (1, -1), "MIDDLE"),
            ("TOPPADDING", (2, 0), (2, -1), 0),
            ("BOTTOMPADDING", (2, 0), (2, -1), 0),
            ("LEFTPADDING", (2, 0), (2, -1), 0),
            ("RIGHTPADDING", (2, 0), (2, -1), 0),
            ("ALIGNMENT", (3, 0), (3, -1), "RIGHT"),
            ("VALIGN", (3, 1), (3, -1), "MIDDLE"),
        ],
        parent=styles["default_shaded"],
    )

    styles["data_dictionary"] = TableStyle(
        [
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ],
        parent=styles["default_shaded"],
    )

    styles["description_table"] = TableStyle(
        [
            ("TOPPADDING", (0, 0), (-1, 0), 0),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -2), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ],
        parent=styles["default"],
    )

    styles["code_table"] = TableStyle(
        [
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("BACKGROUND", (0, 0), (-1, -1), "#f8f8f8"),
        ],
        parent=styles["default_shaded"],
    )

    return styles
