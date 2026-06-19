"""
Definición de campos y layout por defecto para cada tipo de constancia.
Coordenadas en puntos PDF (72 pt = 1 pulgada). Página carta: 612 x 792 pt.
"""

# Cada campo: { "label": str, "field": str, "x": float, "y": float, "font_size": int }
DEFAULT_LAYOUTS = {
    "matrimonios": {
        "titulo": {
            "label": "CONSTANCIA DE MATRIMONIO",
            "field": None,
            "x": 306, "y": 720, "font_size": 16, "bold": True, "center": True,
        },
        "pareja": {
            "label": "Contrayentes:",
            "field": "pareja",
            "x": 80, "y": 660, "font_size": 12,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 80, "y": 630, "font_size": 12,
        },
        "presbitero": {
            "label": "Celebrante:",
            "field": "presbitero",
            "x": 80, "y": 600, "font_size": 12,
        },
        "testigos": {
            "label": "Testigos:",
            "field": "_testigos",
            "x": 80, "y": 570, "font_size": 12,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 80, "y": 540, "font_size": 12,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro",
            "x": 80, "y": 510, "font_size": 12,
        },
    },
    "primera_comunion": {
        "titulo": {
            "label": "CONSTANCIA DE PRIMERA COMUNIÓN",
            "field": None,
            "x": 306, "y": 720, "font_size": 16, "bold": True, "center": True,
        },
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 80, "y": 660, "font_size": 12,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 80, "y": 630, "font_size": 12,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres_comunion",
            "x": 80, "y": 600, "font_size": 12,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 80, "y": 570, "font_size": 12,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 80, "y": 540, "font_size": 12,
        },
    },
    "confirmacion": {
        "titulo": {
            "label": "CONSTANCIA DE CONFIRMACIÓN",
            "field": None,
            "x": 306, "y": 720, "font_size": 16, "bold": True, "center": True,
        },
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 80, "y": 660, "font_size": 12,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 80, "y": 630, "font_size": 12,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres",
            "x": 80, "y": 600, "font_size": 12,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 80, "y": 570, "font_size": 12,
        },
        "arzobispo": {
            "label": "Arzobispo:",
            "field": "arzobispo",
            "x": 80, "y": 540, "font_size": 12,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 80, "y": 510, "font_size": 12,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro",
            "x": 80, "y": 480, "font_size": 12,
        },
    },
    "bautismos": {
        "titulo": {
            "label": "CONSTANCIA DE BAUTISMO",
            "field": None,
            "x": 306, "y": 720, "font_size": 16, "bold": True, "center": True,
        },
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 80, "y": 660, "font_size": 12,
        },
        "nacimiento": {
            "label": "Nacimiento:",
            "field": "_fecha_nacimiento",
            "x": 80, "y": 630, "font_size": 12,
        },
        "lugar_nacimiento": {
            "label": "Lugar de nacimiento:",
            "field": "lugar_nacimiento",
            "x": 80, "y": 600, "font_size": 12,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres",
            "x": 80, "y": 570, "font_size": 12,
        },
        "bautismo": {
            "label": "Fecha de bautismo:",
            "field": "_fecha_bautismo",
            "x": 80, "y": 540, "font_size": 12,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "_padrinos_bautismo",
            "x": 80, "y": 510, "font_size": 12,
        },
        "ministro": {
            "label": "Ministro:",
            "field": "ministro",
            "x": 80, "y": 480, "font_size": 12,
        },
        "parroco": {
            "label": "Párroco:",
            "field": "parroco",
            "x": 80, "y": 450, "font_size": 12,
        },
        "registro": {
            "label": "Registro:",
            "field": "_registro_bautismo",
            "x": 80, "y": 420, "font_size": 12,
        },
    },
    "catecumenos": {
        "titulo": {
            "label": "CONSTANCIA DE CATECÚMENO",
            "field": None,
            "x": 306, "y": 720, "font_size": 16, "bold": True, "center": True,
        },
        "nombre": {
            "label": "Nombre:",
            "field": "nombre",
            "x": 80, "y": 660, "font_size": 12,
        },
        "fecha": {
            "label": "Fecha:",
            "field": "_fecha",
            "x": 80, "y": 630, "font_size": 12,
        },
        "padres": {
            "label": "Padres:",
            "field": "_padres_catecumeno",
            "x": 80, "y": 600, "font_size": 12,
        },
        "padrinos": {
            "label": "Padrinos:",
            "field": "padrinos",
            "x": 80, "y": 570, "font_size": 12,
        },
    },
}
