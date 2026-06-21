"""
Definición de campos y layout por defecto para cada tipo de constancia.
Coordenadas en puntos PDF (72 pt = 1 pulgada). Media carta vertical: 396 x 612 pt.
"""

# Cada campo: { "label": str, "field": str, "x": float, "y": float, "font_size": int }
# Centro horizontal: 198. Margen izquierdo: 50. Espacio entre filas: ~33 pt.
DEFAULT_LAYOUTS = {
    "matrimonios": {
        "titulo": {
            "label": "CONSTANCIA DE MATRIMONIO",
            "field": None,
            "x": 198, "y": 558, "font_size": 14, "bold": True, "center": True,
        },
        "pareja": {
            "label": "Contrayentes:",
            "field": "pareja",
            "x": 50, "y": 490, "font_size": 11,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 50, "y": 456, "font_size": 11,
        },
        "presbitero": {
            "label": "Celebrante:",
            "field": "presbitero",
            "x": 50, "y": 422, "font_size": 11,
        },
        "testigos": {
            "label": "Testigos:",
            "field": "_testigos",
            "x": 50, "y": 388, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 50, "y": 354, "font_size": 11,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro",
            "x": 50, "y": 320, "font_size": 11,
        },
    },
    "primera_comunion": {
        "titulo": {
            "label": "CONSTANCIA DE PRIMERA COMUNIÓN",
            "field": None,
            "x": 198, "y": 558, "font_size": 14, "bold": True, "center": True,
        },
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 50, "y": 490, "font_size": 11,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 50, "y": 456, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres_comunion",
            "x": 50, "y": 422, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 50, "y": 388, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 50, "y": 354, "font_size": 11,
        },
    },
    "confirmacion": {
        "titulo": {
            "label": "CONSTANCIA DE CONFIRMACIÓN",
            "field": None,
            "x": 198, "y": 558, "font_size": 14, "bold": True, "center": True,
        },
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 50, "y": 490, "font_size": 11,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 50, "y": 458, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres",
            "x": 50, "y": 426, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 50, "y": 394, "font_size": 11,
        },
        "arzobispo": {
            "label": "Arzobispo:",
            "field": "arzobispo",
            "x": 50, "y": 362, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 50, "y": 330, "font_size": 11,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro",
            "x": 50, "y": 298, "font_size": 11,
        },
    },
    "bautismos": {
        "titulo": {
            "label": "CONSTANCIA DE BAUTISMO",
            "field": None,
            "x": 198, "y": 558, "font_size": 14, "bold": True, "center": True,
        },
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 50, "y": 488, "font_size": 11,
        },
        "nacimiento": {
            "label": "Nacimiento:",
            "field": "_fecha_nacimiento",
            "x": 50, "y": 458, "font_size": 11,
        },
        "lugar_nacimiento": {
            "label": "Lugar de nacimiento:",
            "field": "lugar_nacimiento",
            "x": 50, "y": 428, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres",
            "x": 50, "y": 398, "font_size": 11,
        },
        "bautismo": {
            "label": "Fecha de bautismo:",
            "field": "_fecha_bautismo",
            "x": 50, "y": 368, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "_padrinos_bautismo",
            "x": 50, "y": 338, "font_size": 11,
        },
        "ministro": {
            "label": "Ministro:",
            "field": "ministro",
            "x": 50, "y": 308, "font_size": 11,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 50, "y": 278, "font_size": 11,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro_bautismo",
            "x": 50, "y": 248, "font_size": 11,
        },
    },
    "catecumenos": {
        "titulo": {
            "label": "CONSTANCIA DE CATECÚMENO",
            "field": None,
            "x": 198, "y": 558, "font_size": 14, "bold": True, "center": True,
        },
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 50, "y": 490, "font_size": 11,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 50, "y": 456, "font_size": 11,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres_catecumeno",
            "x": 50, "y": 422, "font_size": 11,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 50, "y": 388, "font_size": 11,
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
        # Boleta cuadrada — medir y actualizar: pt = cm / 2.54 * 72
        "page_size": [612, 612],
        "fields": {
            "nombre":           {"field": "nombre",             "x": 150, "y": 490, "font_size": 11},
            "fecha_nacimiento": {"field": "_fecha_nacimiento",  "x": 160, "y": 462, "font_size": 11},
            "registro_no":      {"field": "registro_no",        "x": 450, "y": 462, "font_size": 11},
            "lugar_nacimiento": {"field": "lugar_nacimiento",   "x": 100, "y": 432, "font_size": 11},
            "padres":           {"field": "_padres",            "x": 150, "y": 402, "font_size": 11},
            "padrinos":         {"field": "_padrinos_bautismo", "x": 150, "y": 372, "font_size": 11},
            "fecha_bautismo":   {"field": "_fecha_bautismo",    "x": 210, "y": 312, "font_size": 11},
            "libro":            {"field": "libro",              "x": 115, "y": 258, "font_size": 11},
            "acta":             {"field": "acta",               "x": 370, "y": 258, "font_size": 11},
            "ministro":         {"field": "ministro",           "x": 185, "y": 222, "font_size": 11},
            "parroco":          {"field": "parroco",            "x": 440, "y": 222, "font_size": 11},
        },
    },
    "primera_comunion": {
        # Certificado apaisado — placeholder carta landscape
        "page_size": [792, 612],
        "fields": {
            "nombre":   {"field": "nombre",           "x": 396, "y": 440, "font_size": 12, "center": True},
            "padres":   {"field": "_padres_comunion", "x": 260, "y": 390, "font_size": 11},
            "dia":      {"field": "dia",              "x": 315, "y": 355, "font_size": 11},
            "mes":      {"field": "mes",              "x": 380, "y": 355, "font_size": 11},
            "anio":     {"field": "anio",             "x": 560, "y": 355, "font_size": 11},
            "padrinos": {"field": "padrinos",         "x": 250, "y": 318, "font_size": 11},
            "parroco":  {"field": "parroco",          "x": 250, "y": 282, "font_size": 11},
        },
    },
    "confirmacion": {
        # Certificado apaisado — placeholder carta landscape
        "page_size": [792, 612],
        "fields": {
            "nombre":    {"field": "nombre",     "x": 396, "y": 460, "font_size": 12, "center": True},
            "padres":    {"field": "_padres",    "x": 240, "y": 415, "font_size": 11},
            "arzobispo": {"field": "arzobispo",  "x": 420, "y": 382, "font_size": 11},
            "dia":       {"field": "dia",        "x": 180, "y": 352, "font_size": 11},
            "mes":       {"field": "mes",        "x": 250, "y": 352, "font_size": 11},
            "anio":      {"field": "anio",       "x": 480, "y": 352, "font_size": 11},
            "padrinos":  {"field": "padrinos",   "x": 250, "y": 318, "font_size": 11},
            "parroco":   {"field": "parroco",    "x": 250, "y": 282, "font_size": 11},
            "libro":     {"field": "libro",      "x": 160, "y": 238, "font_size": 11},
            "pagina":    {"field": "pagina",     "x": 280, "y": 238, "font_size": 11},
            "partida":   {"field": "partida",    "x": 390, "y": 238, "font_size": 11},
        },
    },
    "matrimonios": {
        # Certificado apaisado — placeholder carta landscape
        "page_size": [792, 612],
        "fields": {
            "pareja":     {"field": "pareja",     "x": 396, "y": 470, "font_size": 12, "center": True},
            "dia":        {"field": "dia",         "x": 130, "y": 415, "font_size": 11},
            "mes":        {"field": "mes",         "x": 195, "y": 415, "font_size": 11},
            "anio":       {"field": "anio",        "x": 410, "y": 415, "font_size": 11},
            "presbitero": {"field": "presbitero",  "x": 490, "y": 415, "font_size": 11},
            "testigo1":   {"field": "testigo1",    "x": 185, "y": 372, "font_size": 11},
            "testigo2":   {"field": "testigo2",    "x": 450, "y": 372, "font_size": 11},
            "parroco":    {"field": "parroco",     "x": 250, "y": 330, "font_size": 11},
            "libro":      {"field": "libro",       "x": 150, "y": 252, "font_size": 11},
            "pagina":     {"field": "pagina",      "x": 310, "y": 252, "font_size": 11},
            "partida":    {"field": "partida",     "x": 140, "y": 232, "font_size": 11},
        },
    },
}
