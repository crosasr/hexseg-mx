"""
Configuración y constantes para SafeHex MX
"""

# Archivos de datos
ARCHIVOS = {
    'coordenadas': 'data.csv',
    'poblacion': 'poblacion_municipios.csv',
    'delitos': 'Municipal-Delitos-2015-2025_dic2025.csv'
}

# Columnas de los archivos CSV
COLUMNAS = {
    'coordenadas': {
        'Entidad': 'NOM_ENT',
        'Municipio': 'NOM_MUN', 
        'Localidad': 'NOM_LOC',
        'Lat': 'LAT_DEC',
        'Lon': 'LON_DEC'
    },
    'poblacion': {
        'Entidad': 'NOM_ENT',
        'Municipio': 'NOM_MUN',
        'Habitantes': 'POB_TOTAL'
    }
}

# Configuración de mapas
MAPA_CONFIG = {
    'resolucion_hex': 8,
    'centro_mexico': [23.6345, -102.5528],
    'zoom_default': 5,
    'zoom_estado': 8,
    'umbrales_riesgo': {
        'alto': 0.3,      # Percentil ~99
        'medio': 0.15,    # Percentil ~95
        'bajo': 0.05      # Umbral mínimo
    }
}

# Configuración interfaz
UI_CONFIG = {
    'ventana': {
        'ancho': 1600,
        'alto': 900
    },
    'colores': {
        'primario': '#1976D2',
        'secundario': '#424242',
        'accent': '#FF5722',
        'fondo': '#FAFAFA'
    }
}
