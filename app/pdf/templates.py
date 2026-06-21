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
        # Canvas carta (612×792). Imagen del formulario se muestra sin distorsión dentro del canvas.
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
        # Canvas carta (612×792). Imagen del formulario se muestra sin distorsión dentro del canvas.
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
        # Canvas carta (612×792). Imagen del formulario se muestra sin distorsión dentro del canvas.
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
        # Canvas carta (612×792). Imagen del formulario se muestra sin distorsión dentro del canvas.
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
