"""
Sistema de logging para SafeHex MX
"""
import logging
import os
from datetime import datetime


class SafeHexLogger:
    """Clase para manejar logs de la aplicación"""
    
    def __init__(self, name="safehex", log_level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """Configura el sistema de logging"""
        # Crear directorio de logs si no existe
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Nombre del archivo con fecha
        log_file = os.path.join(log_dir, f"safehex_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Agregar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """Log de nivel DEBUG"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log de nivel INFO"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log de nivel WARNING"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log de nivel ERROR"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log de nivel CRITICAL"""
        self.logger.critical(message)
    
    def log_operacion(self, operacion, detalles="", duracion=None):
        """Registra operaciones importantes"""
        mensaje = f"OPERACIÓN: {operacion}"
        if detalles:
            mensaje += f" | {detalles}"
        if duracion:
            mensaje += f" | Duración: {duracion:.2f}s"
        
        self.info(mensaje)
    
    def log_filtro_aplicado(self, año, estado, municipio, delito, resultados):
        """Registra aplicación de filtros"""
        mensaje = "FILTRO APLICADO: "
        filtros = []
        
        if año: filtros.append(f"Año={año}")
        if estado: filtros.append(f"Estado={estado}")
        if municipio: filtros.append(f"Municipio={municipio}")
        if delito: filtros.append(f"Delito={delito}")
        
        mensaje += ", ".join(filtros) if filtros else "Sin filtros"
        mensaje += f" | Resultados: {resultados.get('total_registros', 0)} registros, {resultados.get('total_delitos', 0)} delitos"
        
        self.info(mensaje)
    
    def log_error_usuario(self, accion, error, contexto=""):
        """Registra errores de usuario"""
        mensaje = f"ERROR USUARIO: {accion} | {str(error)}"
        if contexto:
            mensaje += f" | Contexto: {contexto}"
        
        self.error(mensaje)


# Logger global
logger = SafeHexLogger()
