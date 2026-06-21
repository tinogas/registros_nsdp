"""
Definición de campos y layout por defecto para cada tipo de constancia.
Coordenadas en puntos PDF (72 pt = 1 pulgada). Carta vertical: 612 x 792 pt.
"""

# Cada campo: { "label": str, "field": str, "x": float, "y": float, "font_size": int }
# Centro horizontal: 306. Margen izquierdo: 60. Espacio entre filas: ~42 pt.
DEFAULT_LAYOUTS = {
    # Matrimonios: más espacio tras "pareja" (nombres largos de contrayentes)
    "matrimonios": {
        "pareja": {
            "label": "Contrayentes:",
            "field": "pareja",
            "x": 60, "y": 650, "font_size": 12,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 60, "y": 588, "font_size": 12,
        },
        "presbitero": {
            "label": "Celebrante:",
            "field": "presbitero",
            "x": 60, "y": 542, "font_size": 12,
        },
        "testigos": {
            "label": "Testigos:",
            "field": "_testigos",
            "x": 60, "y": 496, "font_size": 12,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 60, "y": 450, "font_size": 12,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro",
            "x": 60, "y": 404, "font_size": 12,
        },
    },
    # Primera comunión: espaciado 46 pt
    "primera_comunion": {
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 60, "y": 650, "font_size": 12,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 60, "y": 604, "font_size": 12,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres_comunion",
            "x": 60, "y": 558, "font_size": 12,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 60, "y": 512, "font_size": 12,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 60, "y": 466, "font_size": 12,
        },
    },
    # Confirmación: espaciado 52 pt para evitar encimamiento en campos largos
    "confirmacion": {
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 60, "y": 650, "font_size": 12,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 60, "y": 598, "font_size": 12,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres",
            "x": 60, "y": 546, "font_size": 12,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 60, "y": 494, "font_size": 12,
        },
        "arzobispo": {
            "label": "Arzobispo:",
            "field": "arzobispo",
            "x": 60, "y": 442, "font_size": 12,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 60, "y": 390, "font_size": 12,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro",
            "x": 60, "y": 338, "font_size": 12,
        },
    },
    # Bautismos: fuente reducida a 11 pt, espaciado 38 pt
    "bautismos": {
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 60, "y": 650, "font_size": 11,
        },
        "nacimiento": {
            "label": "Nacimiento:",
            "field": "_fecha_nacimiento",
            "x": 60, "y": 612, "font_size": 11,
        },
        "lugar_nacimiento": {
            "label": "Lugar de nacimiento:",
            "field": "lugar_nacimiento",
            "x": 60, "y": 574, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres",
            "x": 60, "y": 536, "font_size": 11,
        },
        "bautismo": {
            "label": "Fecha de bautismo:",
            "field": "_fecha_bautismo",
            "x": 60, "y": 498, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "_padrinos_bautismo",
            "x": 60, "y": 460, "font_size": 11,
        },
        "ministro": {
            "label": "Ministro:",
            "field": "ministro",
            "x": 60, "y": 422, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 60, "y": 384, "font_size": 11,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro_bautismo",
            "x": 60, "y": 346, "font_size": 11,
        },
    },
    # Catecúmenos: espaciado 46 pt
    "catecumenos": {
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 60, "y": 650, "font_size": 12,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 60, "y": 604, "font_size": 12,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres_catecumeno",
            "x": 60, "y": 558, "font_size": 12,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 60, "y": 512, "font_size": 12,
        },
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# Layouts para imprimir SOLO datos sobre formularios pre-impresos físicos.
# page_size en puntos PDF (72 pt = 1 pulgada). Ajustar con medidas reales.
# Coordenadas son estimaciones iniciales; calibrar con el editor drag-and-drop.
# ──────────────────────────────────────────────────────────────────────────────
FORM_LAYOUTS = {
    "bautismos": {
        # Carta vertical — formulario en mitad superior (y 420–700). Calibrar con drag-and-drop.
        "page_size": [612, 792],
        "fields": {
            "nombre":           {"field": "nombre",             "x": 150, "y": 680, "font_size": 11},
            "fecha_nacimiento": {"field": "_fecha_nacimiento",  "x": 160, "y": 655, "font_size": 11},
            "registro_no":      {"field": "registro_no",        "x": 430, "y": 655, "font_size": 11},
            "lugar_nacimiento": {"field": "lugar_nacimiento",   "x": 100, "y": 628, "font_size": 11},
            "padres":           {"field": "_padres",            "x": 150, "y": 600, "font_size": 11},
            "padrinos":         {"field": "_padrinos_bautismo", "x": 150, "y": 572, "font_size": 11},
            "fecha_bautismo":   {"field": "_fecha_bautismo",    "x": 210, "y": 540, "font_size": 11},
            "libro":            {"field": "libro",              "x": 115, "y": 508, "font_size": 11},
            "acta":             {"field": "acta",               "x": 370, "y": 508, "font_size": 11},
            "ministro":         {"field": "ministro",           "x": 185, "y": 476, "font_size": 11},
            "parroco":          {"field": "parroco",            "x": 420, "y": 476, "font_size": 11},
        },
    },
    "primera_comunion": {
        # Carta vertical — formulario en mitad superior (y 430–680). Calibrar con drag-and-drop.
        "page_size": [612, 792],
        "fields": {
            "nombre":   {"field": "nombre",           "x": 306, "y": 660, "font_size": 12, "center": True},
            "padres":   {"field": "_padres_comunion", "x": 120, "y": 620, "font_size": 11},
            "dia":      {"field": "dia",              "x": 160, "y": 585, "font_size": 11},
            "mes":      {"field": "mes",              "x": 260, "y": 585, "font_size": 11},
            "anio":     {"field": "anio",             "x": 420, "y": 585, "font_size": 11},
            "padrinos": {"field": "padrinos",         "x": 120, "y": 550, "font_size": 11},
            "parroco":  {"field": "parroco",          "x": 120, "y": 515, "font_size": 11},
        },
    },
    "confirmacion": {
        # Carta vertical — formulario en mitad superior (y 440–680). Calibrar con drag-and-drop.
        "page_size": [612, 792],
        "fields": {
            "nombre":    {"field": "nombre",     "x": 306, "y": 660, "font_size": 12, "center": True},
            "padres":    {"field": "_padres",    "x": 120, "y": 625, "font_size": 11},
            "arzobispo": {"field": "arzobispo",  "x": 300, "y": 590, "font_size": 11},
            "dia":       {"field": "dia",        "x": 140, "y": 558, "font_size": 11},
            "mes":       {"field": "mes",        "x": 240, "y": 558, "font_size": 11},
            "anio":      {"field": "anio",       "x": 400, "y": 558, "font_size": 11},
            "padrinos":  {"field": "padrinos",   "x": 120, "y": 524, "font_size": 11},
            "parroco":   {"field": "parroco",    "x": 120, "y": 490, "font_size": 11},
            "libro":     {"field": "libro",      "x": 120, "y": 458, "font_size": 11},
            "pagina":    {"field": "pagina",     "x": 240, "y": 458, "font_size": 11},
            "partida":   {"field": "partida",    "x": 360, "y": 458, "font_size": 11},
        },
    },
    "matrimonios": {
        # Carta vertical — formulario en mitad superior (y 450–680). Calibrar con drag-and-drop.
        "page_size": [612, 792],
        "fields": {
            "pareja":     {"field": "pareja",     "x": 306, "y": 660, "font_size": 12, "center": True},
            "dia":        {"field": "dia",        "x": 100, "y": 620, "font_size": 11},
            "mes":        {"field": "mes",        "x": 200, "y": 620, "font_size": 11},
            "anio":       {"field": "anio",       "x": 360, "y": 620, "font_size": 11},
            "presbitero": {"field": "presbitero", "x": 100, "y": 585, "font_size": 11},
            "testigo1":   {"field": "testigo1",   "x": 100, "y": 550, "font_size": 11},
            "testigo2":   {"field": "testigo2",   "x": 340, "y": 550, "font_size": 11},
            "parroco":    {"field": "parroco",    "x": 120, "y": 515, "font_size": 11},
            "libro":      {"field": "libro",      "x": 120, "y": 475, "font_size": 11},
            "pagina":     {"field": "pagina",     "x": 260, "y": 475, "font_size": 11},
            "partida":    {"field": "partida",    "x": 100, "y": 450, "font_size": 11},
        },
    },
}
