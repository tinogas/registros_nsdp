from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Matrimonio:
    id: Optional[int] = None
    numero: Optional[str] = None
    pareja: Optional[str] = None
    dia: Optional[str] = None
    mes: Optional[str] = None
    anio: Optional[str] = None
    presbitero: Optional[str] = None
    testigo1: Optional[str] = None
    testigo2: Optional[str] = None
    testigo3: Optional[str] = None
    testigo4: Optional[str] = None
    parroco: Optional[str] = None
    libro: Optional[str] = None
    pagina: Optional[str] = None
    acta: Optional[str] = None
    dias_extra: Optional[str] = None
    mes_extra: Optional[str] = None
    fuente_archivo: Optional[str] = None


@dataclass
class PrimeraComunion:
    id: Optional[int] = None
    nombre: Optional[str] = None
    dia: Optional[str] = None
    mes: Optional[str] = None
    anio: Optional[str] = None
    mama: Optional[str] = None
    papa: Optional[str] = None
    padrinos: Optional[str] = None
    parroco: Optional[str] = None
    fuente_archivo: Optional[str] = None


@dataclass
class Confirmacion:
    id: Optional[int] = None
    numero: Optional[str] = None
    nombre: Optional[str] = None
    dia: Optional[str] = None
    mes: Optional[str] = None
    anio: Optional[str] = None
    papa: Optional[str] = None
    mama: Optional[str] = None
    padrinos: Optional[str] = None
    arzobispo: Optional[str] = None
    parroco: Optional[str] = None
    libro: Optional[str] = None
    pagina: Optional[str] = None
    acta: Optional[str] = None
    fuente_archivo: Optional[str] = None


@dataclass
class Bautismo:
    id: Optional[int] = None
    nombre: Optional[str] = None
    dia_nacimiento: Optional[str] = None
    mes_nacimiento: Optional[str] = None
    anio_nacimiento: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    papa: Optional[str] = None
    mama: Optional[str] = None
    dia_bautismo: Optional[str] = None
    mes_bautismo: Optional[str] = None
    anio_bautismo: Optional[str] = None
    ministro: Optional[str] = None
    padrinos1: Optional[str] = None
    padrinos2: Optional[str] = None
    parroco: Optional[str] = None
    registro_no: Optional[str] = None
    libro: Optional[str] = None
    pagina: Optional[str] = None
    acta: Optional[str] = None
    fuente_archivo: Optional[str] = None


@dataclass
class Catecumeno:
    id: Optional[int] = None
    nombre: Optional[str] = None
    dia: Optional[str] = None
    mes: Optional[str] = None
    anio: Optional[str] = None
    padre: Optional[str] = None
    madre: Optional[str] = None
    padrinos: Optional[str] = None
    fuente_archivo: Optional[str] = None
