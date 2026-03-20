"""
Funciones de utilidad para SafeHex MX
"""
import unicodedata
import pandas as pd
import os
from typing import List


def quitar_acentos(texto):
    """Elimina acentos de una cadena de texto"""
    if not texto:
        return ""
    
    # Normalizar a forma NFD (separa caracteres diacríticos)
    texto_normalizado = unicodedata.normalize('NFD', texto)
    
    # Eliminar caracteres diacríticos (combinación de acentos)
    texto_sin_acentos = ''.join(
        char for char in texto_normalizado 
        if unicodedata.category(char) != 'Mn'
    )
    
    return texto_sin_acentos


def limpiar_texto_columna(df, columna):
    """Limpia una columna de texto de un DataFrame"""
    if columna in df.columns:
        # Convertir a string si no lo es
        df[columna] = df[columna].astype(str)
        
        # Eliminar espacios extra
        df[columna] = df[columna].str.strip()
        
        # Quitar acentos y convertir a mayúsculas
        df[columna] = df[columna].apply(quitar_acentos)
        df[columna] = df[columna].str.upper()
        
        # Reemplazar valores nulos con cadena vacía
        df[columna] = df[columna].fillna('')
    
    return df


def validar_archivos():
    """Valida que todos los archivos de datos existan"""
    from config import ARCHIVOS
    
    faltantes = []
    for nombre, ruta in ARCHIVOS.items():
        if not os.path.exists(ruta):
            faltantes.append(f"{nombre}: {ruta}")
    
    if faltantes:
        print("❌ Archivos faltantes:")
        for archivo in faltantes:
            print(f"   - {archivo}")
        return False
    else:
        print("✅ Todos los archivos de datos existen")
        return True


def formatear_numero(numero):
    """Formatea un número con separadores de miles"""
    if pd.isna(numero) or numero == 0:
        return "0"
    
    try:
        # Convertir a entero si es posible
        if isinstance(numero, (int, float)):
            return f"{int(numero):,}"
        else:
            return f"{int(float(numero)):,}"
    except (ValueError, TypeError):
        return str(numero)


def limpiar_nombre_municipio(nombre):
    """Limpia y normaliza el nombre de un municipio"""
    if not isinstance(nombre, str):
        return ""
    
    # Eliminar espacios extra
    nombre = nombre.strip()
    
    # Quitar acentos
    nombre = quitar_acentos(nombre)
    
    # Convertir a mayúsculas
    nombre = nombre.upper()
    
    # Eliminar caracteres especiales excepto espacios y guiones
    import re
    nombre = re.sub(r'[^\w\s-]', '', nombre)
    
    return nombre


def validar_coordenadas(lat, lon):
    """Valida que las coordenadas sean válidas para México"""
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        
        # México aproximadamente: 14° - 33° N, 86° - 118° O
        if (14 <= lat_float <= 33) and (-118 <= lon_float <= -86):
            return True
        return False
    except (ValueError, TypeError):
        return False


def calcular_indice_delincuencia(delitos, habitantes):
    """Calcula el índice de delincuencia (delitos por 100 habitantes)"""
    try:
        if habitantes <= 0:
            return 0.0
        
        return (delitos / habitantes) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def normalizar_texto(texto):
    """Normaliza texto para comparaciones"""
    if not isinstance(texto, str):
        return ""
    
    # Eliminar acentos, convertir a mayúsculas, eliminar espacios extra
    texto = quitar_acentos(texto)
    texto = texto.upper().strip()
    
    # Eliminar caracteres especiales
    import re
    texto = re.sub(r'[^\w\s]', '', texto)
    
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto


def obtener_colores_riesgo(indice):
    """Asigna colores según el nivel de riesgo"""
    if indice > 0.3:
        return '#D32F2F'  # Rojo - Alto riesgo
    elif indice > 0.15:
        return '#F57C00'  # Naranja - Medio riesgo
    elif indice > 0.05:
        return '#FFC107'  # Amarillo - Bajo riesgo
    else:
        return '#4CAF50'  # Verde - Muy bajo riesgo


def crear_directorio_si_no_existe(ruta):
    """Crea un directorio si no existe"""
    if not os.path.exists(ruta):
        os.makedirs(ruta)
        print(f"📁 Directorio creado: {ruta}")
    return ruta


def obtener_estadisticas_descriptivas(serie):
    """Obtiene estadísticas descriptivas básicas de una serie"""
    try:
        if len(serie) == 0:
            return {
                'count': 0,
                'mean': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'median': 0
            }
        
        return {
            'count': len(serie),
            'mean': serie.mean(),
            'std': serie.std(),
            'min': serie.min(),
            'max': serie.max(),
            'median': serie.median()
        }
    except Exception:
        return {
            'count': 0,
            'mean': 0,
            'std': 0,
            'min': 0,
            'max': 0,
            'median': 0
        }


def formatear_fecha(fecha):
    """Formatea una fecha para mostrarla"""
    if pd.isna(fecha):
        return ""
    
    try:
        if hasattr(fecha, 'strftime'):
            return fecha.strftime('%Y-%m-%d')
        else:
            return str(fecha)
    except:
        return str(fecha)


def es_dia_habil(fecha):
    """Determina si una fecha es día hábil (lunes-viernes)"""
    try:
        if hasattr(fecha, 'weekday'):
            return fecha.weekday() < 5  # 0-4 = lunes-viernes
        return True
    except:
        return True
