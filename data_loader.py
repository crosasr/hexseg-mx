"""
Data Loader optimizado con SQLite para SafeHex MX
"""
import pandas as pd
from database import DatabaseManager
from config import MAPA_CONFIG


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
        
        return self.db.obtener_estadisticas_rapidas(año, estado, municipio, delito)
    
    def obtener_top_focos_rojos(self, año=None, estado=None, municipio=None, delito=None, limite=5):
        """Obtiene top focos rojos usando SQL"""
        if not self.db_inicializada:
            self.cargar_todos_los_datos()
        
        return self.db.obtener_top_focos_rojos(año, estado, municipio, delito, limite)
    
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
                AVG(indice_delincuencia) as indice_delincuencia
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
        
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
