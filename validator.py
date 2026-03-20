"""
Validación de datos y manejo de errores para SafeHex MX
"""
import re
from typing import Dict, List, Optional, Tuple
from logger import logger


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


class DataValidator:
    """Clase para validar datos de entrada y salidas"""
    
    @staticmethod
    def validar_año(año: str) -> bool:
        """Valida que el año sea un valor válido"""
        if not año:
            return True  # Año opcional
        
        try:
            año_int = int(año)
            return 2020 <= año_int <= 2030  # Rango razonable
        except ValueError:
            return False
    
    @staticmethod
    def validar_nombre_entidad(nombre: str) -> bool:
        """Valida nombre de entidad (solo letras, espacios y acentos)"""
        if not nombre:
            return True  # Opcional
        
        # Permitir letras, espacios, acentos y ñ
        patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$'
        return bool(re.match(patron, nombre)) and len(nombre.strip()) >= 3
    
    @staticmethod
    def validar_filtros(filtros: Dict) -> Tuple[bool, List[str]]:
        """Valida todos los filtros y devuelve errores si los hay"""
        errores = []
        
        # Validar año
        if filtros.get('año') and not DataValidator.validar_año(filtros['año']):
            errores.append("El año debe ser un número entre 2020 y 2030")
        
        # Validar estado
        if filtros.get('estado') and not DataValidator.validar_nombre_entidad(filtros['estado']):
            errores.append("El estado debe contener solo letras y tener al menos 3 caracteres")
        
        # Validar municipio
        if filtros.get('municipio') and not DataValidator.validar_nombre_entidad(filtros['municipio']):
            errores.append("El municipio debe contener solo letras y tener al menos 3 caracteres")
        
        # Validar delito
        if filtros.get('delito') and len(filtros['delito'].strip()) < 3:
            errores.append("El tipo de delito debe tener al menos 3 caracteres")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validar_resultados_datos(datos) -> Tuple[bool, List[str]]:
        """Valida que los resultados de datos sean coherentes"""
        errores = []
        
        if datos is None:
            errores.append("No se pudieron cargar los datos")
            return False, errores
        
        if hasattr(datos, 'empty') and datos.empty:
            errores.append("No hay datos con los filtros seleccionados")
            return False, errores
        
        # Validar columnas necesarias
        columnas_requeridas = ['entidad', 'municipio', 'delitos', 'indice_delincuencia']
        if hasattr(datos, 'columns'):
            columnas_faltantes = [col for col in columnas_requeridas if col not in datos.columns]
            if columnas_faltantes:
                errores.append(f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}")
        
        return len(errores) == 0, errores


class ErrorHandler:
    """Clase para manejar errores de manera consistente"""
    
    @staticmethod
    def manejar_error_validacion(errores: List[str], contexto: str = ""):
        """Maneja errores de validación de forma consistente"""
        mensaje_error = f"Error de validación: {', '.join(errores)}"
        logger.log_error_usuario(contexto, errores, "Validación de datos")
        return mensaje_error
    
    @staticmethod
    def manejar_error_datos(error: Exception, contexto: str = ""):
        """Maneja errores relacionados con datos"""
        mensaje_error = f"Error en datos: {str(error)}"
        logger.log_error_usuario(contexto, error, "Procesamiento de datos")
        return mensaje_error
    
    @staticmethod
    def manejar_error_general(error: Exception, contexto: str = ""):
        """Maneja errores generales"""
        mensaje_error = f"Error inesperado: {str(error)}"
        logger.error(f"ERROR GENERAL en {contexto}: {str(error)}")
        return "Ocurrió un error inesperado. Por favor intenta nuevamente."


class InputSanitizer:
    """Clase para limpiar y sanitizar entradas de usuario"""
    
    @staticmethod
    def limpiar_texto(texto: str) -> str:
        """Limpia texto de caracteres peligrosos"""
        if not texto:
            return ""
        
        # Eliminar caracteres especiales peligrosos
        texto_limpio = re.sub(r'[<>"\'\%;]', '', texto)
        
        # Eliminar espacios extra
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        
        return texto_limpio
    
    @staticmethod
    def sanitizar_filtros(filtros: Dict) -> Dict:
        """Sanitiza todos los filtros"""
        filtros_limpios = {}
        
        for clave, valor in filtros.items():
            if valor and isinstance(valor, str):
                filtros_limpios[clave] = InputSanitizer.limpiar_texto(valor)
            else:
                filtros_limpios[clave] = valor
        
        return filtros_limpios


class PerformanceMonitor:
    """Clase para monitorear rendimiento de operaciones"""
    
    def __init__(self):
        self.operaciones = {}
    
    def iniciar_operacion(self, nombre: str):
        """Inicia el monitoreo de una operación"""
        import time
        self.operaciones[nombre] = {'inicio': time.time()}
    
    def finalizar_operacion(self, nombre: str) -> float:
        """Finaliza el monitoreo y retorna la duración"""
        import time
        if nombre in self.operaciones:
            duracion = time.time() - self.operaciones[nombre]['inicio']
            logger.log_operacion(nombre, f"Completada exitosamente", duracion)
            del self.operaciones[nombre]
            return duracion
        return 0.0
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Finalizar todas las operaciones pendientes
        for nombre in list(self.operaciones.keys()):
            self.finalizar_operacion(nombre)


# Instancias globales
validator = DataValidator()
error_handler = ErrorHandler()
sanitizer = InputSanitizer()
performance_monitor = PerformanceMonitor()
