import pandas as pd
import folium
import h3
import flet as ft
import unicodedata
import io
import webbrowser
import os
import tempfile
import urllib.parse
from math import isnan

# ======================
# 1. Función para quitar acentos
# ======================
def quitar_acentos(texto):
    if isinstance(texto, str):
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto

# ======================
# 2. Cargar y Preparar Datos
# ======================
print("📍 Cargando coordenadas...")
# --- Intenta cargar archivos de datos ---
try:
    coords = pd.read_csv("data.csv", encoding="utf-8", low_memory=False)
except FileNotFoundError:
    print("❌ Error: No se encontró 'data.csv'. Asegúrate de que el archivo esté en la misma carpeta.")
    exit()

coords.rename(columns={
    'NOM_ENT': 'Entidad',
    'NOM_MUN': 'Municipio',
    'NOM_LOC': 'Localidad',
    'LAT_DEC': 'Lat',
    'LON_DEC': 'Lon'
}, inplace=True)
coords['Entidad'] = coords['Entidad'].str.strip().str.upper().apply(quitar_acentos)
coords['Municipio'] = coords['Municipio'].str.strip().str.upper().apply(quitar_acentos)
coords['Localidad'] = coords['Localidad'].str.strip().str.upper().apply(quitar_acentos)
cabeceras = coords[coords['Localidad'] == coords['Municipio']].drop_duplicates(subset=['Entidad', 'Municipio'])

print("📚 Cargando población...")
try:
    pob = pd.read_csv("poblacion_municipios.csv", encoding="latin1")
except FileNotFoundError:
    print("❌ Error: No se encontró 'poblacion_municipios.csv'. Asegúrate de que el archivo esté en la misma carpeta.")
    exit()

pob.rename(columns={
    'NOM_ENT': 'Entidad',
    'NOM_MUN': 'Municipio',
    'POB_TOTAL': 'Habitantes'
}, inplace=True)
pob['Entidad'] = pob['Entidad'].str.strip().str.upper().apply(quitar_acentos)
pob['Municipio'] = pob['Municipio'].str.strip().str.upper().apply(quitar_acentos)
pob['Habitantes'] = pd.to_numeric(pob['Habitantes'], errors='coerce')

print("📥 Cargando delitos...")
try:
    delitos_df = pd.read_csv("Municipal-Delitos - Junio 2025 (2015-2025).csv", encoding="latin1")
except FileNotFoundError:
    print("❌ Error: No se encontró 'Municipal-Delitos - Junio 2025 (2015-2025).csv'. Asegúrate de que el archivo esté en la misma carpeta.")
    exit()


if 'Tipo de delito' not in delitos_df.columns:
    print("⚠️ Advertencia: La columna 'Tipo de delito' no fue encontrada. Usando valor por defecto.")
    delitos_df['Tipo de delito'] = 'Todos los delitos'

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
delitos_long['Entidad'] = delitos_long['Entidad'].str.strip().str.upper().apply(quitar_acentos)
delitos_long['Municipio'] = delitos_long['Municipio'].str.strip().str.upper().apply(quitar_acentos)

print("🔗 Uniendo datos...")
data = pd.merge(cabeceras, delitos_long, on=['Entidad', 'Municipio'], how='left')
data = pd.merge(data, pob[['Entidad', 'Municipio', 'Habitantes']], on=['Entidad', 'Municipio'], how='left')
data['Delitos'] = data['Delitos'].fillna(0)
data['Habitantes'] = data['Habitantes'].fillna(1)
data = data[data['Habitantes'] >= 100]
data['Indice_Delincuencia'] = (data['Delitos'] / data['Habitantes']) * 100

data_original = data.copy()
print("✅ Datos cargados y preparados.")

# Variable global para guardar la ruta del mapa actual
mapa_actual = None

# ======================
# Función para generar hexágonos y mapa (con Pop-up de Enlace Compartible)
# ======================
def generar_mapa(datos_filtrados):
    global mapa_actual
    
    if datos_filtrados.empty:
        return None

    print("📍 Generando hexágonos...")
    datos_mun = datos_filtrados.groupby(['Entidad', 'Municipio']).agg({
        'Delitos': 'sum',
        'Habitantes': 'mean',
        'Lat': 'mean',
        'Lon': 'mean'
    }).reset_index()
    datos_mun['Indice_Delincuencia'] = (datos_mun['Delitos'] / datos_mun['Habitantes']) * 100
    
    def get_hex(row):
        try:
            # Resolución 8 es un buen equilibrio para el análisis municipal
            return h3.latlng_to_cell(row['Lat'], row['Lon'], 8)
        except Exception:
            return None

    datos_mun['hex_id'] = datos_mun.apply(get_hex, axis=1)
    datos_mun.dropna(subset=['hex_id'], inplace=True)

    hex_summary = datos_mun.groupby('hex_id').agg({
        'Delitos': 'sum',
        'Habitantes': 'sum',
        'Lat': 'mean',
        'Lon': 'mean'
    }).reset_index()
    hex_summary['Indice_Hex'] = (hex_summary['Delitos'] / hex_summary['Habitantes']) * 100

    print("🌍 Generando mapa...")
    # Centrar el mapa en México, ajustando el zoom si se filtra a un solo estado
    if len(datos_mun['Entidad'].unique()) == 1:
        centro_lat = datos_mun['Lat'].mean() if not isnan(datos_mun['Lat'].mean()) else 23.6345
        centro_lon = datos_mun['Lon'].mean() if not isnan(datos_mun['Lon'].mean()) else -102.5528
        zoom = 8
    else:
        centro_lat = 23.6345
        centro_lon = -102.5528
        zoom = 5

    m = folium.Map(location=[centro_lat, centro_lon], zoom_start=zoom, tiles="OpenStreetMap")
    
    for _, row in hex_summary.iterrows():
        lat_centro = row['Lat']
        lon_centro = row['Lon']
        indice = row['Indice_Hex']
        delitos_count = int(row['Delitos'])
        
        # 1. Definir color y generar el polígono
        color = 'red' if indice > 1.0 else 'orange' if indice > 0.5 else 'green'
        
        vertices = h3.cell_to_boundary(row['hex_id'])
        coords_poly = [(lat, lng) for lat, lng in vertices]
        
        folium.Polygon(
            locations=coords_poly,
            color=color,
            fill=True,
            fill_opacity=0.6,
            weight=1,
            tooltip=f"Índice: {indice:.2f} | Delitos: {delitos_count}"
        ).add_to(m)

        # 2. GENERACIÓN DEL ENLACE COMPARTIBLE
        # Usamos el formato de búsqueda directa de coordenadas para el link de Maps
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat_centro},{lon_centro}"
        
        popup_html = f"""
        <b>Índice de Riesgo:</b> {indice:.2f}<br>
        <b>Delitos Agregados:</b> {delitos_count:,}<br><br>
        <a href='{google_maps_url}' target='_blank'>
            <button style='background-color: #4CAF50; color: white; padding: 5px 10px; border: none; cursor: pointer; border-radius: 4px;'>
                📍 Abrir en Google Maps
            </button>
        </a>
        <br><br>
        <small>Link para compartir:<br><code>{google_maps_url}</code></small>
        """

        # 3. Añadir un círculo/marcador en el centro del hexágono con Pop-up (solo focos de riesgo)
        if indice > 0.5:
            folium.CircleMarker(
                location=[lat_centro, lon_centro],
                radius=6 if indice > 1.0 else 4,
                color=color,
                fill=True,
                fill_color=color,
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)
    
    # Guardar el mapa en un archivo temporal
    mapa_actual = os.path.join(tempfile.gettempdir(), "mapa_safehex.html")
    m.save(mapa_actual)
    return mapa_actual

# ======================
# Dashboard Flet con filtros
# ======================
def main(page: ft.Page):
    page.title = "🔐 SafeHex MX - BI para Seguridad"
    page.theme_mode = "dark"
    page.scroll = "auto"
    page.window.width = 1600
    page.window.height = 900

    data_filtrada = data_original.copy()
    
    años_series = pd.to_numeric(data_original['Año'], errors='coerce').dropna()
    años = sorted(años_series.unique().astype(int))
    
    tipos_delito_series = data_original['Tipo de delito'].dropna().unique()
    tipos_delito = sorted([str(t) for t in tipos_delito_series])
    
    entidades_series = data_original['Entidad'].dropna().unique()
    entidades = sorted([str(e) for e in entidades_series])
    
    municipios_series = data_original['Municipio'].dropna().unique()
    municipios = sorted([str(m) for m in municipios_series])
    
    # Filtros
    filtro_estado = ft.Dropdown(
        label="Estado/Entidad",
        options=[ft.dropdown.Option(e, text=e) for e in entidades],
        width=250,
        hint_text="Selecciona un estado"
    )

    filtro_año = ft.Dropdown(
        label="Año",
        options=[ft.dropdown.Option(str(a), text=str(a)) for a in años],
        width=150,
        hint_text="Selecciona un año"
    )
    
    filtro_delito = ft.Dropdown(
        label="Tipo de delito",
        options=[ft.dropdown.Option(d, text=d) for d in tipos_delito],
        width=250,
        hint_text="Selecciona un delito"
    )
    
    filtro_municipio = ft.Dropdown(
        label="Municipio",
        options=[ft.dropdown.Option(m, text=m) for m in municipios],
        width=250,
        disabled=True,
        hint_text="Selecciona un municipio"
    )
    
    # Componentes de la Interfaz
    info_mapa = ft.Text(
        "🗺️ El mapa se abrirá en tu navegador cuando presiones 'Ver Mapa'",
        size=16,
        text_align=ft.TextAlign.CENTER,
        color=ft.Colors.BLUE_400
    )
    
    tarjeta_delitos = ft.Card(ft.Container(
        content=ft.Column([
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOCAL_POLICE, color=ft.Colors.BLUE_400),
                title=ft.Text("0", size=24, weight="bold"),
                subtitle=ft.Text("Delitos Agregados")
            )
        ]),
        padding=10
    ))
    
    tarjeta_focos = ft.Card(ft.Container(
        content=ft.Column([
            ft.ListTile(
                leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED_500),
                title=ft.Text("0", size=24, weight="bold"),
                subtitle=ft.Text("Focos Rojos (Índice > 1.0)")
            )
        ]),
        padding=10
    ))
    
    tabla_con_scroll = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Municipio")),
            ft.DataColumn(ft.Text("Entidad")),
            ft.DataColumn(ft.Text("Delitos")),
            ft.DataColumn(ft.Text("Índice")),
        ],
        rows=[],
    )
    
    contenedor_tabla = ft.Container(
        content=ft.Column(
            controls=[tabla_con_scroll],
            height=300,
            scroll=ft.ScrollMode.AUTO,
        ),
        border=ft.border.all(1, ft.Colors.GREY_400),
        padding=10,
    )
    
    top_column = ft.Column([], spacing=5)

    def abrir_mapa(e):
        if mapa_actual and os.path.exists(mapa_actual):
            webbrowser.open(f"file://{mapa_actual}")
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("🗺️ Mapa abierto en el navegador"), duration=2000)
            )
        else:
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("⚠️ Aplica los filtros para generar el mapa"), duration=2000)
            )

    boton_ver_mapa = ft.ElevatedButton(
        "🗺️ Ver Mapa y Enlaces Compartibles",
        icon=ft.Icons.MAP,
        on_click=abrir_mapa,
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
        height=50
    )

    def actualizar_municipios(e):
        if filtro_estado.value:
            data_temp = data_original[data_original['Entidad'] == filtro_estado.value]
            filtro_municipio.disabled = False
        else:
            data_temp = data_original
            filtro_municipio.disabled = True
            
        nuevos_municipios_series = data_temp['Municipio'].dropna().unique()
        nuevos_municipios = sorted([str(m) for m in nuevos_municipios_series])
        
        filtro_municipio.value = None
        filtro_municipio.options = [ft.dropdown.Option(m, text=m) for m in nuevos_municipios]
        filtro_municipio.hint_text = f"Selecciona un municipio ({len(nuevos_municipios)})"
        
        page.update()
        actualizar_vista()

    # Función principal de actualización (CORREGIDA)
    def actualizar_vista(e=None):
        nonlocal data_filtrada
        
        data_filtrada = data_original.copy()
        
        # 1. Aplicar filtros
        if filtro_estado.value:
            data_filtrada = data_filtrada[data_filtrada['Entidad'] == filtro_estado.value]
        
        if filtro_año.value:
            data_filtrada = data_filtrada[data_filtrada['Año'] == int(filtro_año.value)]
        
        if filtro_delito.value:
            data_filtrada = data_filtrada[data_filtrada['Tipo de delito'] == filtro_delito.value]
        
        if filtro_municipio.value:
            data_filtrada = data_filtrada[data_filtrada['Municipio'] == filtro_municipio.value]
        
        # Inicializar valores
        total_delitos = 0
        focos_rojos = 0
        datos_mun = pd.DataFrame()
        top5 = pd.DataFrame()
        focos_df = pd.DataFrame()
        
        if not data_filtrada.empty:
            
            total_delitos = int(data_filtrada['Delitos'].sum())
            
            datos_mun = data_filtrada.groupby(['Entidad', 'Municipio']).agg({
                'Delitos': 'sum',
                'Habitantes': 'mean',
                'Indice_Delincuencia': 'mean'
            }).reset_index()
            
            # --- CORRECCIÓN: Ordenar por índice descendente ---
            datos_mun.sort_values('Indice_Delincuencia', ascending=False, inplace=True)
            
            # --- CORRECCIÓN: Filtrar solo focos rojos (Indice > 1.0) ---
            focos_rojos_df = datos_mun[datos_mun['Indice_Delincuencia'] > 1.0]
            
            focos_rojos = len(focos_rojos_df)
            
            # El Top 5 son los 5 con mayor índice (ya están ordenados)
            top5 = datos_mun.head(5) 
            
            # La tabla muestra SOLO los focos rojos
            focos_df = focos_rojos_df[['Municipio', 'Entidad', 'Delitos', 'Indice_Delincuencia']]
        
        # 2. Actualizar la Interfaz
        top_list = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED_ACCENT_400),
                title=ft.Text(f"{row['Municipio']}"),
                subtitle=ft.Text(f"{row['Entidad']} | Índice: {row['Indice_Delincuencia']:.2f}")
            )
            for _, row in top5.iterrows()
        ]
        
        table_rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row['Municipio']))),
                ft.DataCell(ft.Text(str(row['Entidad']))),
                ft.DataCell(ft.Text(f"{int(row['Delitos']):,}")),
                ft.DataCell(ft.Text(f"{row['Indice_Delincuencia']:.2f}")),
            ])
            for _, row in focos_df.iterrows()
        ]
        
        tabla_con_scroll.rows = table_rows
        
        tarjeta_delitos.content.content.controls[0].title.value = f"{total_delitos:,}"
        tarjeta_focos.content.content.controls[0].title.value = f"{focos_rojos}"
        
        top_column.controls = top_list
        
        # 3. Generar el mapa
        mapa_path = generar_mapa(data_filtrada)
        if mapa_path:
            info_mapa.value = f"✅ Mapa generado con {len(datos_mun)} municipios. Presiona el botón para abrirlo."
        else:
             info_mapa.value = "⚠️ No hay datos para los filtros seleccionados. Mapa no generado."


        page.update()
    
    # Conexión de Eventos
    filtro_estado.on_change = actualizar_municipios
    filtro_año.on_change = actualizar_vista
    filtro_delito.on_change = actualizar_vista
    filtro_municipio.on_change = actualizar_vista
    
    # Diseño de la Interfaz
    contenedor_principal = ft.Column([
        ft.Text("📊 SafeHex MX", size=30, weight="bold"),
        ft.Text("Análisis de delitos por células hexagonales", size=14),
        ft.Divider(),
        # Fila de filtros
        ft.Row([
            filtro_año,
            filtro_delito,
            filtro_estado,
            filtro_municipio,
        ], wrap=True),
        ft.Divider(),
        # Fila de tarjetas de indicadores
        ft.ResponsiveRow([
            ft.Container(
                tarjeta_delitos,
                col={"sm": 12, "md": 6}
            ),
            ft.Container(
                tarjeta_focos,
                col={"sm": 12, "md": 6}
            ),
        ]),
        ft.Divider(),
        # Sección de Mapa
        ft.Text("Mapa de Focos Rojos", size=20, weight="bold"),
        ft.Container(
            content=ft.Column([
                info_mapa,
                boton_ver_mapa,
                ft.Text("⚠️ Dentro del mapa, haz clic en los círculos rojos/naranjas para obtener el enlace de Google Maps.", size=12, color=ft.Colors.YELLOW_ACCENT_400)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            height=250,
            bgcolor=ft.Colors.GREY_800,
            border_radius=10,
            padding=20,
            alignment=ft.alignment.center
        ),
        ft.Divider(),
        # Fila de Tablas
        ft.ResponsiveRow([
            ft.Container(
                ft.Column([
                    ft.Text("Top 5 Focos Rojos:", weight="bold", size=18),
                    top_column,
                ]),
                col={"sm": 12, "md": 4}
            ),
            ft.Container(
                ft.Column([
                    ft.Text("Lista completa de focos rojos:", weight="bold", size=18),
                    contenedor_tabla,
                ]),
                col={"sm": 12, "md": 8}
            ),
        ], alignment=ft.MainAxisAlignment.START),
    ], scroll="auto")
    
    page.add(contenedor_principal)
    
    actualizar_vista()

# Inicializar la aplicación Flet
ft.app(target=main)