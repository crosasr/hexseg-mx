"""
Data Loader optimizado con SQLite para SafeHex MX
"""
import pandas as pd
from database import DatabaseManager
from config import MAPA_CONFIG
from logger import logger


class OptimizedDataLoader:
    """Clase para manejar datos usando SQLite para mejor rendimiento"""
    
    def __init__(self, db_path="safehex.db"):
        self.db = DatabaseManager(db_path)
        self.db_inicializada = False
    
    def validar_archivos_datos(self):
        """Verifica que los archivos CSV existan"""
        import os
        from config import ARCHIVOS
        
        faltantes = []
        for nombre, ruta in ARCHIVOS.items():
            if not os.path.exists(ruta):
                faltantes.append(nombre)
        
        if faltantes:
            print(f"❌ Error: Archivos faltantes: {', '.join(faltantes)}")
            return False
        return True
    
    def cargar_todos_los_datos(self):
        """Carga datos a SQLite (solo la primera vez)"""
        if not self.validar_archivos_datos():
            return False
        
        # Verificar si la BD ya existe y tiene datos
        try:
            años, _, _, _ = self.db.obtener_filtros_disponibles()
            if años:  # Si hay datos, no recargar
                print("✅ Base de datos ya contiene datos")
                self.db_inicializada = True
                return True
        except Exception as e:
            print(f"🔍 Verificando BD: {e}")
            pass  # La BD no existe o está vacía
        
        # Inicializar BD desde cero
        resultado = self.db.inicializar_bd()
        if resultado:
            self.db_inicializada = True
        return resultado
    
    def obtener_filtros_disponibles(self):
        """Obtiene los valores únicos para los filtros"""
        if not self.db_inicializada:
            self.cargar_todos_los_datos()
        
        return self.db.obtener_filtros_disponibles()
    
    def filtrar_datos(self, año=None, estado=None, municipio=None, delito=None):
        """Filtra datos usando SQL optimizado"""
        if not self.db_inicializada:
            self.cargar_todos_los_datos()
        
        return self.db.filtrar_datos(año, estado, municipio, delito)
    
    def obtener_estadisticas_rapidas(self, año=None, estado=None, municipio=None, delito=None):
        """Obtiene estadísticas agregadas rápidamente"""
        if not self.db_inicializada:
            self.cargar_todos_los_datos()
        
        try:
            # Consulta simple para estadísticas
            query = '''
                SELECT 
                    COUNT(*) as total_registros,
                    SUM(delitos) as total_delitos,
                    COUNT(DISTINCT municipio) as municipios_unicos,
                    0.0 as indice_promedio,
                    0.0 as indice_maximo,
                    0 as focos_rojos
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
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                # Calcular focos rojos por separado
                stats = dict(result) if result else {}
                stats['focos_rojos'] = self._contar_focos_rojos(año, estado, municipio, delito)
                
                return stats
        except Exception as e:
            logger.error(f"Error en estadísticas: {e}")
            # Retornar valores por defecto
            return {
                'total_registros': 0,
                'total_delitos': 0,
                'municipios_unicos': 0,
                'focos_rojos': 0
            }
    
    def _contar_focos_rojos(self, año=None, estado=None, municipio=None, delito=None):
        """Cuenta focos rojos con índice > 0.3"""
        try:
            query = '''
                SELECT COUNT(*) as focos_rojos
                FROM (
                    SELECT municipio, 
                           (SUM(delitos) * 100.0 / AVG(habitantes)) as indice
                    FROM datos_principales 
                    WHERE habitantes > 0
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
            
            query += " GROUP BY municipio HAVING indice > 0.3) as focos"
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error contando focos rojos: {e}")
            return 0
    
    def obtener_top_focos_rojos(self, año=None, estado=None, municipio=None, delito=None, limite=5):
        """Obtiene top focos rojos usando SQL"""
        if not self.db_inicializada:
            self.cargar_todos_los_datos()
        
        try:
            # Calcular focos rojos directamente desde los datos
            query = '''
                SELECT 
                    municipio, entidad, 
                    SUM(delitos) as total_delitos,
                    AVG(habitantes) as habitantes,
                    (SUM(delitos) * 100.0 / AVG(habitantes)) as indice_promedio,
                    COUNT(*) as registros
                FROM datos_principales 
                WHERE habitantes > 0
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
            
            query += " GROUP BY municipio, entidad HAVING (SUM(delitos) * 100.0 / AVG(habitantes)) > 0.3 ORDER BY indice_promedio DESC LIMIT ?"
            params.append(limite)
            
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except Exception as e:
            logger.error(f"Error en top focos: {e}")
            # Retornar DataFrame vacío
            return pd.DataFrame()
    
    def obtener_municipios_por_estado(self, estado):
        """Obtiene municipios para un estado específico"""
        if not self.db_inicializada:
            self.cargar_todos_los_datos()
        
        return self.db.obtener_municipios_por_estado(estado)
    
    def obtener_datos_para_mapa(self, año=None, estado=None, municipio=None, delito=None):
        """Obtiene datos agregados para el mapa"""
        if not self.db_inicializada:
            self.cargar_todos_los_datos()
        
        query = '''
            SELECT 
                municipio, entidad,
                AVG(lat) as lat,
                AVG(lon) as lon,
                SUM(delitos) as delitos,
                AVG(habitantes) as habitantes,
                (SUM(delitos) * 100.0 / AVG(habitantes)) as indice_delincuencia
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
        
        query += " GROUP BY municipio, entidad"
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except Exception as e:
            logger.error(f"Error en obtener_datos_para_mapa: {e}")
            # Retornar DataFrame vacío
            return pd.DataFrame()
