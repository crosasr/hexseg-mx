"""
SafeHex MX - Aplicación Principal Moderna con todas las mejoras
"""
import flet as ft
from data_loader import OptimizedDataLoader
from map_generator import MapGenerator
from ui import ModernSafeHexUI
from logger import logger
from validator import performance_monitor
import time
import sys


def main(page: ft.Page):
    """Función principal de la aplicación modernizada"""
    
    try:
        # Inicializar componentes
        logger.info("🚀 Iniciando SafeHex MX Moderno...")
        start_time = time.time()
        
        # Monitorear rendimiento de carga
        with performance_monitor:
            performance_monitor.iniciar_operacion("carga_aplicacion")
            
            data_loader = OptimizedDataLoader()
            map_generator = MapGenerator()
            ui = ModernSafeHexUI(data_loader, map_generator)
            
            # Cargar datos con monitoreo
            performance_monitor.iniciar_operacion("carga_datos")
            if not data_loader.cargar_todos_los_datos():
                logger.error("❌ No se pudieron cargar los datos. Verifica que los archivos existan.")
                page.dialog = ft.AlertDialog(
                    title=ft.Text("Error de Carga"),
                    content=ft.Text("No se pudieron cargar los datos. Por favor verifica que los archivos CSV existan en el directorio."),
                    actions=[ft.TextButton("OK", on_click=lambda _: page.window.close())]
                )
                page.dialog.open = True
                page.update()
                return
            
            performance_monitor.finalizar_operacion("carga_datos")
            
            # Crear interfaz
            performance_monitor.iniciar_operacion("creacion_interfaz")
            ui.crear_interfaz(page)
            performance_monitor.finalizar_operacion("creacion_interfaz")
            
            performance_monitor.finalizar_operacion("carga_aplicacion")
        
        total_time = time.time() - start_time
        logger.info(f"✅ SafeHex MX Moderno iniciado exitosamente en {total_time:.2f} segundos")
        
        # Mostrar mensaje de bienvenida
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"🎉 SafeHex MX listo en {total_time:.2f}s", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()
        
    except Exception as e:
        logger.critical(f"Error crítico iniciando aplicación: {str(e)}")
        
        # Mostrar diálogo de error
        page.dialog = ft.AlertDialog(
            title=ft.Text("Error Crítico"),
            content=ft.Text(f"Ocurrió un error crítico al iniciar la aplicación:\n\n{str(e)}\n\nPor favor contacta al soporte técnico."),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: page.window.close())
            ]
        )
        page.dialog.open = True
        page.update()


if __name__ == "__main__":
    try:
        ft.run(main, view=ft.AppView.WEB_BROWSER)
    except KeyboardInterrupt:
        logger.info("👋 Aplicación cerrada por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Error no controlado: {str(e)}")
        sys.exit(1)
