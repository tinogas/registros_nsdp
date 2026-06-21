"""
Definición de campos y layout por defecto para cada tipo de constancia.
Coordenadas en puntos PDF (72 pt = 1 pulgada). Media carta vertical: 396 x 612 pt.
"""

# Cada campo: { "label": str, "field": str, "x": float, "y": float, "font_size": int }
# Centro horizontal: 198. Margen izquierdo: 50. Espacio entre filas: ~32-36 pt.
# Encabezado ocupa aprox. y=486..612 (126 pt). Contenido: y=80..470.
DEFAULT_LAYOUTS = {
    # Matrimonios: más espacio tras "pareja" (nombres largos de contrayentes)
    "matrimonios": {
        "pareja": {
            "label": "Contrayentes:",
            "field": "pareja",
            "x": 50, "y": 470, "font_size": 11,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 50, "y": 434, "font_size": 11,
        },
        "presbitero": {
            "label": "Celebrante:",
            "field": "presbitero",
            "x": 50, "y": 398, "font_size": 11,
        },
        "testigos": {
            "label": "Testigos:",
            "field": "_testigos",
            "x": 50, "y": 362, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 50, "y": 326, "font_size": 11,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro",
            "x": 50, "y": 290, "font_size": 11,
        },
    },
    # Primera comunión: espaciado 36 pt
    "primera_comunion": {
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 50, "y": 470, "font_size": 11,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 50, "y": 434, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres_comunion",
            "x": 50, "y": 398, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 50, "y": 362, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 50, "y": 326, "font_size": 11,
        },
    },
    # Confirmación: espaciado 32 pt
    "confirmacion": {
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 50, "y": 470, "font_size": 11,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 50, "y": 438, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres",
            "x": 50, "y": 406, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 50, "y": 374, "font_size": 11,
        },
        "arzobispo": {
            "label": "Arzobispo:",
            "field": "arzobispo",
            "x": 50, "y": 342, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 50, "y": 310, "font_size": 11,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro",
            "x": 50, "y": 278, "font_size": 11,
        },
    },
    # Bautismos: 9 campos, espaciado 32 pt
    "bautismos": {
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 50, "y": 470, "font_size": 11,
        },
        "nacimiento": {
            "label": "Nacimiento:",
            "field": "_fecha_nacimiento",
            "x": 50, "y": 438, "font_size": 11,
        },
        "lugar_nacimiento": {
            "label": "Lugar de nacimiento:",
            "field": "lugar_nacimiento",
            "x": 50, "y": 406, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres",
            "x": 50, "y": 374, "font_size": 11,
        },
        "bautismo": {
            "label": "Fecha de bautismo:",
            "field": "_fecha_bautismo",
            "x": 50, "y": 342, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "_padrinos_bautismo",
            "x": 50, "y": 310, "font_size": 11,
        },
        "ministro": {
            "label": "Ministro:",
            "field": "ministro",
            "x": 50, "y": 278, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 50, "y": 246, "font_size": 11,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro_bautismo",
            "x": 50, "y": 214, "font_size": 11,
        },
    },
    # Catecúmenos: espaciado 36 pt
    "catecumenos": {
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 50, "y": 470, "font_size": 11,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 50, "y": 434, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres_catecumeno",
            "x": 50, "y": 398, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 50, "y": 362, "font_size": 11,
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
        # 15×15 cm = 425×425 pt. Coords escaladas proporcionalmente desde carta (612×792).
        "page_size": [425, 425],
        "fields": {
            "nombre":           {"field": "nombre",             "x": 104, "y": 365, "font_size": 11},
            "fecha_nacimiento": {"field": "_fecha_nacimiento",  "x": 111, "y": 351, "font_size": 11},
            "registro_no":      {"field": "registro_no",        "x": 298, "y": 351, "font_size": 11},
            "lugar_nacimiento": {"field": "lugar_nacimiento",   "x":  69, "y": 337, "font_size": 11},
            "padres":           {"field": "_padres",            "x": 104, "y": 322, "font_size": 11},
            "padrinos":         {"field": "_padrinos_bautismo", "x": 104, "y": 307, "font_size": 11},
            "fecha_bautismo":   {"field": "_fecha_bautismo",    "x": 146, "y": 290, "font_size": 11},
            "libro":            {"field": "libro",              "x":  80, "y": 273, "font_size": 11},
            "acta":             {"field": "acta",               "x": 257, "y": 273, "font_size": 11},
            "ministro":         {"field": "ministro",           "x": 128, "y": 255, "font_size": 11},
            "parroco":          {"field": "parroco",            "x": 291, "y": 255, "font_size": 11},
        },
    },
    "primera_comunion": {
        # Media carta vertical 396×612 pt. Coords escaladas proporcionalmente desde carta (612×792).
        "page_size": [396, 612],
        "fields": {
            "nombre":   {"field": "nombre",           "x": 198, "y": 510, "font_size": 12, "center": True},
            "padres":   {"field": "_padres_comunion", "x":  78, "y": 480, "font_size": 11},
            "dia":      {"field": "dia",              "x": 104, "y": 452, "font_size": 11},
            "mes":      {"field": "mes",              "x": 168, "y": 452, "font_size": 11},
            "anio":     {"field": "anio",             "x": 272, "y": 452, "font_size": 11},
            "padrinos": {"field": "padrinos",         "x":  78, "y": 425, "font_size": 11},
            "parroco":  {"field": "parroco",          "x":  78, "y": 398, "font_size": 11},
        },
    },
    "confirmacion": {
        # Media carta vertical 396×612 pt. Coords escaladas proporcionalmente desde carta (612×792).
        "page_size": [396, 612],
        "fields": {
            "nombre":    {"field": "nombre",     "x": 198, "y": 510, "font_size": 12, "center": True},
            "padres":    {"field": "_padres",    "x":  78, "y": 483, "font_size": 11},
            "arzobispo": {"field": "arzobispo",  "x": 194, "y": 456, "font_size": 11},
            "dia":       {"field": "dia",        "x":  91, "y": 431, "font_size": 11},
            "mes":       {"field": "mes",        "x": 155, "y": 431, "font_size": 11},
            "anio":      {"field": "anio",       "x": 259, "y": 431, "font_size": 11},
            "padrinos":  {"field": "padrinos",   "x":  78, "y": 405, "font_size": 11},
            "parroco":   {"field": "parroco",    "x":  78, "y": 379, "font_size": 11},
            "libro":     {"field": "libro",      "x":  78, "y": 354, "font_size": 11},
            "pagina":    {"field": "pagina",     "x": 155, "y": 354, "font_size": 11},
            "partida":   {"field": "partida",    "x": 233, "y": 354, "font_size": 11},
        },
    },
    "matrimonios": {
        # Media carta vertical 396×612 pt. Coords escaladas proporcionalmente desde carta (612×792).
        "page_size": [396, 612],
        "fields": {
            "pareja":     {"field": "pareja",     "x": 198, "y": 510, "font_size": 12, "center": True},
            "dia":        {"field": "dia",        "x":  65, "y": 480, "font_size": 11},
            "mes":        {"field": "mes",        "x": 129, "y": 480, "font_size": 11},
            "anio":       {"field": "anio",       "x": 233, "y": 480, "font_size": 11},
            "presbitero": {"field": "presbitero", "x":  65, "y": 452, "font_size": 11},
            "testigo1":   {"field": "testigo1",   "x":  65, "y": 425, "font_size": 11},
            "testigo2":   {"field": "testigo2",   "x": 220, "y": 425, "font_size": 11},
            "parroco":    {"field": "parroco",    "x":  78, "y": 398, "font_size": 11},
            "libro":      {"field": "libro",      "x":  78, "y": 367, "font_size": 11},
            "pagina":     {"field": "pagina",     "x": 168, "y": 367, "font_size": 11},
            "partida":    {"field": "partida",    "x":  65, "y": 348, "font_size": 11},
        },
    },
}
