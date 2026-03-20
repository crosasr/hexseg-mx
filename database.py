"""
Módulo para manejar base de datos SQLite para SafeHex MX
"""
import sqlite3
import pandas as pd
from contextlib import contextmanager
from config import ARCHIVOS, COLUMNAS
from utils import limpiar_texto_columna


class DatabaseManager:
    """Clase para manejar operaciones de base de datos SQLite"""
    
    def __init__(self, db_path="safehex.db"):
        self.db_path = db_path
        self.conn = None
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        try:
            yield conn
        finally:
            conn.close()
    
    def crear_tablas(self):
        """Crea las tablas necesarias en la base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de coordenadas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS coordenadas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entidad TEXT NOT NULL,
                    municipio TEXT NOT NULL,
                    localidad TEXT NOT NULL,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    UNIQUE(entidad, municipio, localidad)
                )
            ''')
            
            # Tabla de población
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS poblacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entidad TEXT NOT NULL,
                    municipio TEXT NOT NULL,
                    habitantes INTEGER NOT NULL,
                    UNIQUE(entidad, municipio)
                )
            ''')
            
            # Tabla de delitos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS delitos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    año INTEGER NOT NULL,
                    entidad TEXT NOT NULL,
                    municipio TEXT NOT NULL,
                    tipo_delito TEXT NOT NULL,
                    mes TEXT NOT NULL,
                    delitos INTEGER NOT NULL
                )
            ''')
            
            # Tabla principal (vista materializada)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_principales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entidad TEXT NOT NULL,
                    municipio TEXT NOT NULL,
                    localidad TEXT NOT NULL,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    habitantes INTEGER NOT NULL,
                    año INTEGER NOT NULL,
                    tipo_delito TEXT NOT NULL,
                    mes TEXT NOT NULL,
                    delitos INTEGER NOT NULL,
                    indice_delincuencia REAL NOT NULL
                )
            ''')
            
            # Crear índices para rendimiento
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_entidad ON datos_principales(entidad)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_municipio ON datos_principales(municipio)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_año ON datos_principales(año)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_tipo_delito ON datos_principales(tipo_delito)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_datos_indice ON datos_principales(indice_delincuencia)')
            
            conn.commit()
            print("✅ Tablas e índices creados")
    
    def cargar_datos_csv(self):
        """Carga datos desde archivos CSV a la base de datos"""
        print("📥 Cargando datos a SQLite...")
        
        # Cargar coordenadas
        print("📍 Coordenadas...")
        coords = pd.read_csv(ARCHIVOS['coordenadas'], encoding="utf-8", low_memory=False)
        coords.rename(columns=COLUMNAS['coordenadas'], inplace=True)
        
        for col in ['Entidad', 'Municipio', 'Localidad']:
            coords = limpiar_texto_columna(coords, col)
        
        # Obtener cabeceras municipales
        cabeceras = coords[coords['Localidad'] == coords['Municipio']].drop_duplicates(subset=['Entidad', 'Municipio'])
        
        # Cargar población
        print("📚 Población...")
        pob = pd.read_csv(ARCHIVOS['poblacion'], encoding="latin1")
        pob.rename(columns=COLUMNAS['poblacion'], inplace=True)
        
        for col in ['Entidad', 'Municipio']:
            pob = limpiar_texto_columna(pob, col)
        
        pob['Habitantes'] = pd.to_numeric(pob['Habitantes'], errors='coerce')
        
        # Cargar delitos
        print("📥 Delitos...")
        delitos_df = pd.read_csv(ARCHIVOS['delitos'], encoding="latin1")
        
        if 'Tipo de delito' not in delitos_df.columns:
            delitos_df['Tipo de delito'] = 'Todos los delitos'
        
        # Convertir a formato largo
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        delitos_long = pd.melt(
            delitos_df,
            id_vars=['Año', 'Clave_Ent', 'Entidad', 'Cve. Municipio', 'Municipio', 'Tipo de delito'],
            value_vars=meses,
            var_name='Mes',
            value_name='Delitos'
        )
        
        delitos_long = delitos_long[delitos_long['Año'] >= 2023]
        delitos_long.dropna(subset=['Delitos'], inplace=True)
        delitos_long = delitos_long[delitos_long['Delitos'] > 0]
        delitos_long['Delitos'] = delitos_long['Delitos'].astype(int)
        
        for col in ['Entidad', 'Municipio']:
            delitos_long = limpiar_texto_columna(delitos_long, col)
        
        # Insertar datos en lotes
        self._insertar_coordenadas(cabeceras)
        self._insertar_poblacion(pob)
        self._insertar_delitos(delitos_long, 'Tipo de delito')
        self._generar_vista_principal()
        
        print("✅ Datos cargados en SQLite")
    
    def _insertar_coordenadas(self, df):
        """Inserta coordenadas en la base de datos"""
        with self.get_connection() as conn:
            df.to_sql('coordenadas_temp', conn, if_exists='replace', index=False)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO coordenadas (entidad, municipio, localidad, lat, lon)
                SELECT entidad, municipio, localidad, lat, lon FROM coordenadas_temp
            ''')
            cursor.execute('DROP TABLE IF EXISTS coordenadas_temp')
            conn.commit()
    
    def _insertar_poblacion(self, df):
        """Inserta población en la base de datos"""
        with self.get_connection() as conn:
            df.to_sql('poblacion_temp', conn, if_exists='replace', index=False)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO poblacion (entidad, municipio, habitantes)
                SELECT entidad, municipio, habitantes FROM poblacion_temp
            ''')
            cursor.execute('DROP TABLE IF EXISTS poblacion_temp')
            conn.commit()
    
    def _insertar_delitos(self, df, columna_tipo):
        """Inserta delitos en la base de datos"""
        with self.get_connection() as conn:
            df.to_sql('delitos_temp', conn, if_exists='replace', index=False)
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT OR IGNORE INTO delitos (año, entidad, municipio, tipo_delito, mes, delitos)
                SELECT año, entidad, municipio, "{columna_tipo}", mes, delitos FROM delitos_temp
            ''')
            cursor.execute('DROP TABLE IF EXISTS delitos_temp')
            conn.commit()
    
    def _generar_vista_principal(self):
        """Genera la tabla principal con índices calculados"""
        print("🔗 Generando vista principal...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Limpiar tabla principal
            cursor.execute('DELETE FROM datos_principales')
            
            # Insertar datos combinados con índice calculado
            cursor.execute('''
                INSERT INTO datos_principales (
                    entidad, municipio, localidad, lat, lon, habitantes,
                    año, tipo_delito, mes, delitos, indice_delincuencia
                )
                SELECT 
                    c.entidad, c.municipio, c.localidad, c.lat, c.lon, 
                    COALESCE(p.habitantes, 1) as habitantes,
                    d.año, d.tipo_delito, d.mes, d.delitos,
                    ROUND((CAST(d.delitos AS FLOAT) / COALESCE(p.habitantes, 1)) * 100, 4) as indice_delincuencia
                FROM coordenadas c
                JOIN delitos d ON c.entidad = d.entidad AND c.municipio = d.municipio
                LEFT JOIN poblacion p ON c.entidad = p.entidad AND c.municipio = p.municipio
                WHERE COALESCE(p.habitantes, 1) >= 100
            ''')
            
            conn.commit()
            print("✅ Vista principal generada")
    
    def obtener_filtros_disponibles(self):
        """Obtiene los valores únicos para los filtros usando SQL"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Años disponibles
            cursor.execute('SELECT DISTINCT año FROM datos_principales ORDER BY año')
            años = [row[0] for row in cursor.fetchall()]
            
            # Tipos de delito
            cursor.execute('SELECT DISTINCT tipo_delito FROM datos_principales ORDER BY tipo_delito')
            tipos_delito = [row[0] for row in cursor.fetchall()]
            
            # Entidades
            cursor.execute('SELECT DISTINCT entidad FROM datos_principales ORDER BY entidad')
            entidades = [row[0] for row in cursor.fetchall()]
            
            # Municipios
            cursor.execute('SELECT DISTINCT municipio FROM datos_principales ORDER BY municipio')
            municipios = [row[0] for row in cursor.fetchall()]
            
            return años, tipos_delito, entidades, municipios
    
    def filtrar_datos(self, año=None, estado=None, municipio=None, delito=None):
        """Filtra datos usando SQL optimizado"""
        query = "SELECT * FROM datos_principales WHERE 1=1"
        params = []
        
        if año:
            query += " AND año = ?"
            params.append(año)
        
        if estado:
            query += " AND entidad = ?"
            params.append(estado)
        
        if municipio:
            query += " AND municipio = ?"
            params.append(municipio)
        
        if delito:
            query += " AND tipo_delito = ?"
            params.append(delito)
        
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def obtener_estadisticas_rapidas(self, año=None, estado=None, municipio=None, delito=None):
        """Obtiene estadísticas agregadas usando SQL"""
        query = '''
            SELECT 
                COUNT(*) as total_registros,
                SUM(delitos) as total_delitos,
                COUNT(DISTINCT municipio) as municipios_unicos,
                AVG(indice_delincencia) as indice_promedio,
                MAX(indice_delincencia) as indice_maximo,
                COUNT(CASE WHEN indice_delincencia > 0.3 THEN 1 END) as focos_rojos
            FROM datos_principales 
            WHERE 1=1
        '''
        params = []
        
        if año:
            query += " AND año = ?"
            params.append(año)
        
        if estado:
            query += " AND entidad = ?"
            params.append(estado)
        
        if municipio:
            query += " AND municipio = ?"
            params.append(municipio)
        
        if delito:
            query += " AND tipo_delito = ?"
            params.append(delito)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else {}
    
    def obtener_top_focos_rojos(self, año=None, estado=None, municipio=None, delito=None, limite=5):
        """Obtiene los principales focos rojos usando SQL"""
        query = '''
            SELECT 
                municipio, entidad, 
                SUM(delitos) as total_delitos,
                AVG(indice_delincencia) as indice_promedio,
                COUNT(*) as registros
            FROM datos_principales 
            WHERE indice_delincencia > 0.3
        '''
        params = []
        
        if año:
            query += " AND año = ?"
            params.append(año)
        
        if estado:
            query += " AND entidad = ?"
            params.append(estado)
        
        if municipio:
            query += " AND municipio = ?"
            params.append(municipio)
        
        if delito:
            query += " AND tipo_delito = ?"
            params.append(delito)
        
        query += " GROUP BY municipio, entidad ORDER BY indice_promedio DESC LIMIT ?"
        params.append(limite)
        
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def obtener_municipios_por_estado(self, estado):
        """Obtiene municipios para un estado específico"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT DISTINCT municipio FROM datos_principales WHERE entidad = ? ORDER BY municipio',
                (estado,)
            )
            return [row[0] for row in cursor.fetchall()]
    
    def inicializar_bd(self):
        """Inicializa la base de datos completa"""
        print("🗄️ Inicializando base de datos SQLite...")
        self.crear_tablas()
        self.cargar_datos_csv()
        print("✅ Base de datos lista para usar")
