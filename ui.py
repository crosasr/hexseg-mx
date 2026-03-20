"""
Interfaz de usuario Flet mejorada y moderna para SafeHex MX
"""
import flet as ft
import pandas as pd
import webbrowser
import os
from config import MAPA_CONFIG, UI_CONFIG
from utils import formatear_numero
from validator import validator, error_handler, sanitizer, performance_monitor
from logger import logger


class ModernSafeHexUI:
    """Clase para manejar la interfaz de usuario moderna"""
    
    def __init__(self, data_loader, map_generator):
        self.data_loader = data_loader
        self.map_generator = map_generator
        self.page = None
        
        # Componentes de la interfaz
        self.filtro_estado = None
        self.filtro_año = None
        self.filtro_delito = None
        self.filtro_municipio = None
        
        # Componentes de información
        self.tarjeta_delitos = None
        self.tarjeta_focos = None
        self.tarjeta_tiempo = None
        self.tabla_focos = None
        self.lista_top5 = None
        self.info_mapa = None
        
        # Indicadores de carga
        self.progress_ring = None
        self.carga_overlay = None
    
    def crear_tarjeta_moderna(self, titulo, valor, icono, color, subtitulo=""):
        """Crea una tarjeta moderna con mejor diseño"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icono, color=color, size=24),
                        ft.Column([
                            ft.Text(
                                valor, 
                                size=28, 
                                weight="bold", 
                                color=color
                            ),
                            ft.Text(
                                subtitulo or titulo,
                                size=12,
                                color=ft.Colors.GREY_400
                            )
                        ], expand=True)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                padding=20
            ),
            elevation=2
        )
    
    def crear_filtros_mejorados(self, años, tipos_delito, entidades, municipios):
        """Crea filtros con mejor diseño y validación"""
        
        # Estilo común para dropdowns
        dropdown_style = ft.BoxDecoration(
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=ft.border_radius.all(8)
        )
        
        self.filtro_año = ft.Dropdown(
            label="📅 Año",
            options=[ft.dropdown.Option(str(a), text=str(a)) for a in años],
            width=140,
            height=50,
            text_style=ft.TextStyle(size=14),
            filled=True
        )
        
        self.filtro_estado = ft.Dropdown(
            label="📍 Estado",
            options=[ft.dropdown.Option(e, text=e) for e in entidades],
            width=200,
            height=50,
            text_style=ft.TextStyle(size=14),
            filled=True
        )
        
        self.filtro_municipio = ft.Dropdown(
            label="🏛️ Municipio",
            options=[ft.dropdown.Option(m, text=m) for m in municipios],
            width=200,
            height=50,
            text_style=ft.TextStyle(size=14),
            filled=True,
            disabled=True
        )
        
        self.filtro_delito = ft.Dropdown(
            label="⚖️ Tipo de Delito",
            options=[ft.dropdown.Option(d, text=d) for d in tipos_delito],
            width=200,
            height=50,
            text_style=ft.TextStyle(size=14),
            filled=True
        )
        
        # Botón de aplicar filtros con mejor diseño
        self.boton_filtrar = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.FILTER_ALT, size=16),
                ft.Text("Aplicar Filtros", weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                elevation=3,
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            height=50,
            on_click=self.actualizar_vista_con_validacion,
            width=180
        )
        
        # Botón de limpiar filtros
        self.boton_limpiar = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CLEAR, size=16),
                ft.Text("Limpiar")
            ], alignment=ft.MainAxisAlignment.CENTER),
            style=ft.ButtonStyle(
                color=ft.Colors.GREY_600,
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            height=50,
            on_click=self.limpiar_filtros,
            width=120
        )
    
    def crear_indicadores_carga(self):
        """Crea indicadores de carga modernos"""
        self.progress_ring = ft.ProgressRing(
            color=ft.Colors.BLUE_600,
            width=20,
            height=20,
            visible=False
        )
        
        self.carga_overlay = ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=ft.Colors.BLUE_600, width=40, height=40),
                ft.Text("Procesando...", size=14, color=ft.Colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLACK_26,
            border_radius=10,
            padding=20,
            visible=False
        )
    
    def crear_tabla_moderna(self):
        """Crea una tabla más moderna"""
        self.tabla_focos = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text("Municipio", size=12, weight="bold"),
                    numeric=False
                ),
                ft.DataColumn(
                    ft.Text("Entidad", size=12, weight="bold"),
                    numeric=False
                ),
                ft.DataColumn(
                    ft.Text("Delitos", size=12, weight="bold"),
                    numeric=True
                ),
                ft.DataColumn(
                    ft.Text("Índice", size=12, weight="bold"),
                    numeric=True
                ),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=8,
            data_row_max_height=35,
            heading_row_height=40
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "🔥 Focos Rojos Detectados",
                    size=16,
                    weight="bold",
                    color=ft.Colors.RED_600
                ),
                ft.Container(
                    content=self.tabla_focos,
                    height=300,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=10
                )
            ], spacing=10),
            margin=ft.margin.only(top=20)
        )
    
    def crear_lista_top5_moderna(self):
        """Crea una lista top 5 más visual"""
        self.lista_top5 = ft.Column([], spacing=8)
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "🏆 Top 5 Municipios Críticos",
                    size=16,
                    weight="bold",
                    color=ft.Colors.ORANGE_600
                ),
                ft.Container(
                    content=self.lista_top5,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=15,
                    height=280
                )
            ], spacing=10),
            margin=ft.margin.only(top=20)
        )
    
    def mostrar_carga(self, mostrar=True):
        """Muestra u oculta indicadores de carga"""
        if self.carga_overlay:
            self.carga_overlay.visible = mostrar
        if self.progress_ring:
            self.progress_ring.visible = mostrar
        self.page.update()
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error elegante"""
        self.mostrar_snackbar(mensaje, ft.Colors.RED_600)
        logger.error(f"Error en UI: {mensaje}")
    
    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito"""
        self.mostrar_snackbar(mensaje, ft.Colors.GREEN_600)
        logger.info(f"Operación exitosa: {mensaje}")
    
    def mostrar_snackbar(self, mensaje, color=ft.Colors.BLUE_600):
        """Muestra snackbar personalizado"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(mensaje, color=ft.Colors.WHITE),
                bgcolor=color,
                duration=3000
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def limpiar_filtros(self, e):
        """Limpia todos los filtros"""
        self.filtro_año.value = None
        self.filtro_estado.value = None
        self.filtro_municipio.value = None
        self.filtro_municipio.disabled = True
        self.filtro_delito.value = None
        
        self.page.update()
        self.actualizar_vista_con_validacion(e)
    
    def actualizar_municipios(self, e):
        """Actualiza municipios con validación"""
        try:
            if self.filtro_estado.value:
                municipios = self.data_loader.obtener_municipios_por_estado(self.filtro_estado.value)
                self.filtro_municipio.disabled = False
            else:
                municipios = self.data_loader.obtener_filtros_disponibles()[3]
                self.filtro_municipio.disabled = True
            
            self.filtro_municipio.value = None
            self.filtro_municipio.options = [ft.dropdown.Option(m, text=m) for m in municipios]
            self.filtro_municipio.hint_text = f"Selecciona un municipio ({len(municipios)})"
            
            self.page.update()
        except Exception as error:
            self.mostrar_error(error_handler.manejar_error_general(error, "actualizar municipios"))
    
    def actualizar_vista_con_validacion(self, e):
        """Actualiza vista con validación completa"""
        try:
            performance_monitor.iniciar_operacion("aplicar_filtros")
            self.mostrar_carga(True)
            
            # Obtener y sanitizar filtros
            filtros = {
                'año': self.filtro_año.value,
                'estado': self.filtro_estado.value,
                'municipio': self.filtro_municipio.value,
                'delito': self.filtro_delito.value
            }
            
            filtros_limpios = sanitizer.sanitizar_filtros(filtros)
            
            # Validar filtros
            es_valido, errores = validator.validar_filtros(filtros_limpios)
            
            if not es_valido:
                self.mostrar_error(error_handler.manejar_error_validacion(errores, "aplicar filtros"))
                self.mostrar_carga(False)
                return
            
            # Aplicar filtros
            self._aplicar_filtros_interno(filtros_limpios)
            
        except Exception as error:
            self.mostrar_error(error_handler.manejar_error_general(error, "aplicar filtros"))
        finally:
            self.mostrar_carga(False)
            performance_monitor.finalizar_operacion("aplicar_filtros")
    
    def _aplicar_filtros_interno(self, filtros):
        """Aplica filtros de forma segura"""
        # Obtener estadísticas rápidas
        stats = self.data_loader.obtener_estadisticas_rapidas(
            filtros.get('año'), 
            filtros.get('estado'), 
            filtros.get('municipio'), 
            filtros.get('delito')
        )
        
        total_delitos = int(stats.get('total_delitos', 0))
        focos_rojos = stats.get('focos_rojos', 0)
        
        # Validar resultados
        if total_delitos == 0:
            self.mostrar_snackbar("No hay datos con los filtros seleccionados", ft.Colors.ORANGE_600)
        
        # Obtener datos adicionales
        top_focos = self.data_loader.obtener_top_focos_rojos(
            filtros.get('año'), 
            filtros.get('estado'), 
            filtros.get('municipio'), 
            filtros.get('delito'), 
            5
        )
        
        datos_mapa = self.data_loader.obtener_datos_para_mapa(
            filtros.get('año'), 
            filtros.get('estado'), 
            filtros.get('municipio'), 
            filtros.get('delito')
        )
        
        # Actualizar componentes
        self._actualizar_tarjetas(total_delitos, focos_rojos, stats)
        self._actualizar_tablas(top_focos)
        self._actualizar_mapa(datos_mapa)
        
        # Mostrar mensaje de éxito
        self.mostrar_exito(f"Filtros aplicados: {formatear_numero(total_delitos)} delitos, {focos_rojos} focos rojos")
        
        # Registrar en log
        logger.log_filtro_aplicado(
            filtros.get('año'), 
            filtros.get('estado'), 
            filtros.get('municipio'), 
            filtros.get('delito'), 
            stats
        )
    
    def _actualizar_tarjetas(self, total_delitos, focos_rojos, stats):
        """Actualiza tarjetas con datos"""
        if self.tarjeta_delitos:
            self.tarjeta_delitos.content.content.controls[0].controls[1].controls[0].value = formatear_numero(total_delitos)
        
        if self.tarjeta_focos:
            self.tarjeta_focos.content.content.controls[0].controls[1].controls[0].value = str(focos_rojos)
        
        if self.tarjeta_tiempo:
            municipios = stats.get('municipios_unicos', 0)
            self.tarjeta_tiempo.content.content.controls[0].controls[1].controls[0].value = str(municipios)
    
    def _actualizar_tablas(self, top_focos):
        """Actualiza tablas y listas"""
        # Actualizar top 5
        if isinstance(top_focos, pd.DataFrame) and not top_focos.empty:
            items_top5 = []
            for _, row in top_focos.iterrows():
                items_top5.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED_500, size=16),
                            ft.Column([
                                ft.Text(
                                    row['municipio'], 
                                    size=14, 
                                    weight="bold",
                                    color=ft.Colors.WHITE
                                ),
                                ft.Text(
                                    f"{row['entidad']} | Índice: {row['indice_promedio']:.2f}",
                                    size=11,
                                    color=ft.Colors.GREY_300
                                )
                            ], expand=True),
                            ft.Text(
                                f"{row['indice_promedio']:.2f}",
                                size=16,
                                weight="bold",
                                color=ft.Colors.RED_400
                            )
                        ]),
                        bgcolor=ft.Colors.GREY_800,
                        border_radius=8,
                        padding=12,
                        margin=ft.margin.only(bottom=8)
                    )
                )
            self.lista_top5.controls = items_top5
        else:
            self.lista_top5.controls = [
                ft.Text(
                    "No hay focos rojos con los filtros actuales",
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                )
            ]
        
        # Actualizar tabla
        if isinstance(top_focos, pd.DataFrame) and not top_focos.empty:
            table_rows = []
            for _, row in top_focos.iterrows():
                color_indice = ft.Colors.RED_600 if row['indice_promedio'] > 0.4 else ft.Colors.ORANGE_600
                
                table_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(row['municipio'], size=12)),
                            ft.DataCell(ft.Text(row['entidad'], size=12)),
                            ft.DataCell(
                                ft.Text(
                                    formatear_numero(row['total_delitos']), 
                                    size=12,
                                    weight="bold"
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    f"{row['indice_promedio']:.2f}", 
                                    size=12,
                                    weight="bold",
                                    color=color_indice
                                )
                            ),
                        ]
                    )
                )
            self.tabla_focos.rows = table_rows
        else:
            self.tabla_focos.rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                "No hay datos disponibles",
                                color=ft.Colors.GREY_500,
                                text_align=ft.TextAlign.CENTER
                            )
                        ),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text(""))
                    ]
                )
            ]
    
    def _actualizar_mapa(self, datos_mapa):
        """Actualiza la información del mapa y lo genera"""
        try:
            if datos_mapa is not None and not datos_mapa.empty:
                # Generar el mapa
                mapa_path = self.map_generator.generar_mapa(datos_mapa)
                if mapa_path:
                    self.info_mapa.value = f"✅ Mapa generado con {len(datos_mapa)} municipios. ¡Listo para abrir!"
                    self.info_mapa.color = ft.Colors.GREEN_600
                    logger.info(f"Mapa generado exitosamente: {len(datos_mapa)} municipios")
                else:
                    self.info_mapa.value = "⚠️ Error al generar el mapa."
                    self.info_mapa.color = ft.Colors.RED_600
                    logger.error("Error generando el mapa")
            else:
                self.info_mapa.value = "⚠️ No hay datos para generar el mapa con los filtros seleccionados."
                self.info_mapa.color = ft.Colors.ORANGE_600
                logger.warning("No hay datos para generar mapa")
        except Exception as error:
            self.info_mapa.value = "⚠️ Error crítico generando el mapa."
            self.info_mapa.color = ft.Colors.RED_600
            logger.error(f"Error crítico generando mapa: {str(error)}")
            raise error
    
    def crear_interfaz(self, page: ft.Page):
        """Crea la interfaz completa moderna"""
        self.page = page
        
        # Configuración de página
        page.title = "🔐 SafeHex MX - Análisis de Seguridad Moderno"
        page.theme_mode = "dark"
        page.scroll = "auto"
        page.window.width = 1400
        page.window.height = 900
        page.bgcolor = ft.Colors.GREY_50
        
        # Obtener filtros disponibles
        años, tipos_delito, entidades, municipios = self.data_loader.obtener_filtros_disponibles()
        
        # Crear componentes
        self.crear_filtros_mejorados(años, tipos_delito, entidades, municipios)
        self.crear_indicadores_carga()
        
        # Tarjetas de indicadores
        self.tarjeta_delitos = self.crear_tarjeta_moderna(
            "Delitos Totales", "0", ft.Icons.GROUP_WORK, ft.Colors.BLUE_600
        )
        
        self.tarjeta_focos = self.crear_tarjeta_moderna(
            "Focos Rojos", "0", ft.Icons.WARNING, ft.Colors.RED_600, 
            f"Índice > {MAPA_CONFIG['umbrales_riesgo']['alto']}"
        )
        
        self.tarjeta_tiempo = self.crear_tarjeta_moderna(
            "Municipios", "0", ft.Icons.LOCATION_CITY, ft.Colors.GREEN_600
        )
        
        # Sección de mapa
        self.info_mapa = ft.Text(
            "🗺️ El mapa se generará al aplicar filtros",
            size=14,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER
        )
        
        boton_ver_mapa = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.MAP, size=16),
                ft.Text("Ver Mapa Interactivo", weight="bold")
            ]),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
                elevation=3,
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            height=45,
            on_click=self.abrir_mapa
        )
        
        # Diseño principal
        contenido_principal = ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.SECURITY, color=ft.Colors.BLUE_600, size=32),
                            ft.Column([
                                ft.Text("SafeHex MX", size=28, weight="bold", color=ft.Colors.BLUE_800),
                                ft.Text("Sistema de Análisis de Delitos por Células Hexagonales", 
                                       size=14, color=ft.Colors.GREY_600)
                            ])
                        ]),
                        ft.Divider(height=1, thickness=1)
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=ft.border_radius.only(top_left=12, top_right=12)
                ),
                
                # Filtros
                ft.Container(
                    content=ft.Column([
                        ft.Text("🔍 Filtros de Búsqueda", size=18, weight="bold", color=ft.Colors.BLUE_800),
                        ft.Row([
                            self.filtro_año, self.filtro_estado, self.filtro_municipio,
                            self.filtro_delito, self.boton_filtrar, self.boton_limpiar
                        ], wrap=True, alignment=ft.MainAxisAlignment.SPACE_AROUND)
                    ], spacing=15),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.margin.symmetric(vertical=10),
                    border_radius=12
                ),
                
                # Indicadores
                ft.Container(
                    content=ft.Row([
                        self.tarjeta_delitos, self.tarjeta_focos, self.tarjeta_tiempo
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12
                ),
                
                # Contenido inferior
                ft.Row([
                    # Top 5
                    ft.Container(
                        content=self.crear_lista_top5_moderna(),
                        expand=True,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        padding=20
                    ),
                    # Tabla y mapa
                    ft.Container(
                        content=ft.Column([
                            self.crear_tabla_moderna(),
                            ft.Container(
                                content=ft.Container(
                                    content=ft.Column([
                                        self.info_mapa,
                                        boton_ver_mapa
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                                    padding=20,
                                    bgcolor=ft.Colors.BLUE_50,
                                    border_radius=12,
                                    margin=ft.margin.only(top=20)
                                )
                            )
                        ]),
                        expand=2,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        padding=20
                    )
                ], expand=True),
                
                # Overlay de carga
                self.carga_overlay
                
            ], scroll="auto", expand=True),
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
            padding=10
        )
        
        # Conectar eventos
        self.filtro_estado.on_change = self.actualizar_municipios
        
        page.add(contenido_principal)
        
        # Carga inicial
        self.actualizar_vista_con_validacion(None)
    
    def abrir_mapa(self, e):
        """Abre el mapa en el navegador"""
        try:
            logger.info("🔍 Intentando abrir mapa...")
            
            if self.map_generator.mapa_existe():
                mapa_path = self.map_generator.obtener_mapa_actual()
                logger.info(f"📁 Ruta del mapa: {mapa_path}")
                
                # Verificar que el archivo exista
                if os.path.exists(mapa_path):
                    file_url = f"file://{os.path.abspath(mapa_path)}"
                    logger.info(f"🌐 Abriendo URL: {file_url}")
                    webbrowser.open(file_url)
                    self.mostrar_exito("Mapa abierto en tu navegador")
                else:
                    logger.error(f"❌ Archivo de mapa no encontrado: {mapa_path}")
                    self.mostrar_error("Archivo de mapa no encontrado")
            else:
                logger.warning("⚠️ No hay mapa generado")
                self.mostrar_error("Primero aplica los filtros para generar el mapa")
        except Exception as error:
            logger.error(f"❌ Error abriendo mapa: {str(error)}")
            self.mostrar_error(error_handler.manejar_error_general(error, "abrir mapa"))
