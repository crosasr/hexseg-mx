"""
Generador de mapas interactivos con Folium para SafeHex MX
"""
import folium
import pandas as pd
import h3
import webbrowser
import os
from datetime import datetime
from config import MAPA_CONFIG


class MapGenerator:
    """Clase para generar mapas interactivos con hexágonos"""
    
    def __init__(self):
        self.mapa_actual = None
        self.directorio_mapas = "mapas"
        os.makedirs(self.directorio_mapas, exist_ok=True)
    
    def generar_hexagonos(self, datos):
        """Genera hexágonos H3 para los datos"""
        print("📍 Generando hexágonos...")
        
        # Convertir coordenadas a hexágonos
        datos['hex_id'] = datos.apply(
            lambda row: h3.latlng_to_cell(row['lat'], row['lon'], MAPA_CONFIG['resolucion_hex']),
            axis=1
        )
        
        # Agrupar por hexágonos
        hex_agrupado = datos.groupby('hex_id').agg({
            'delitos': 'sum',
            'habitantes': 'sum',
            'lat': 'mean',
            'lon': 'mean',
            'municipio': 'first',
            'entidad': 'first'
        }).reset_index()
        
        # Calcular índice de delincuencia
        hex_agrupado['indice_delincuencia'] = (hex_agrupado['delitos'] / hex_agrupado['habitantes']) * 100
        
        # Filtrar hexágonos con datos significativos
        hex_agrupado = hex_agrupado[hex_agrupado['habitantes'] >= 100]
        
        print(f"✅ Se generaron {len(hex_agrupado)} hexágonos")
        return hex_agrupado
    
    def obtener_color_riesgo(self, indice):
        """Asigna color según el nivel de riesgo"""
        if indice > MAPA_CONFIG['umbrales_riesgo']['alto']:
            return '#D32F2F'  # Rojo - Alto riesgo
        elif indice > MAPA_CONFIG['umbrales_riesgo']['medio']:
            return '#F57C00'  # Naranja - Medio riesgo
        elif indice > MAPA_CONFIG['umbrales_riesgo']['bajo']:
            return '#FFC107'  # Amarillo - Bajo riesgo
        else:
            return '#4CAF50'  # Verde - Muy bajo riesgo
    
    def generar_mapa(self, datos):
        """Genera un mapa interactivo con hexágonos"""
        print("🌍 Generando mapa...")
        
        if datos.empty:
            print("⚠️ No hay datos para generar el mapa")
            return None
        
        # Generar hexágonos
        hex_datos = self.generar_hexagonos(datos)
        
        if hex_datos.empty:
            print("⚠️ No se pudieron generar hexágonos")
            return None
        
        # Crear mapa base
        if len(hex_datos) == 1:
            # Si solo hay un municipio, centrar en ese punto
            centro = [hex_datos.iloc[0]['lat'], hex_datos.iloc[0]['lon']]
            zoom = MAPA_CONFIG['zoom_estado']
        else:
            # Si hay múltiples municipios, usar centro de México
            centro = MAPA_CONFIG['centro_mexico']
            zoom = MAPA_CONFIG['zoom_default']
        
        mapa = folium.Map(
            location=centro,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # Agregar hexágonos al mapa
        for _, row in hex_datos.iterrows():
            color = self.obtener_color_riesgo(row['indice_delincuencia'])
            
            # Obtener coordenadas del hexágono
            hex_coords = h3.cell_to_boundary(row['hex_id'])
            
            # Crear popup con información
            popup_text = f"""
            <b>{row['municipio']}</b><br>
            <b>Entidad:</b> {row['entidad']}<br>
            <b>Delitos:</b> {int(row['delitos']):,}<br>
            <b>Habitantes:</b> {int(row['habitantes']):,}<br>
            <b>Índice:</b> {row['indice_delincuencia']:.2f}<br>
            <br>
            <a href="https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lon']}" 
               target="_blank">Ver en Google Maps</a>
            """
            
            # Agregar polígono del hexágono
            folium.Polygon(
                locations=hex_coords,
                color=color,
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(mapa)
        
        # Agregar marcadores para los municipios con mayor índice
        top_municipios = hex_datos.nlargest(5, 'indice_delincuencia')
        for _, row in top_municipios.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"<b>{row['municipio']}</b><br>Índice: {row['indice_delincuencia']:.2f}",
                icon=folium.Icon(color='red', icon='warning-sign')
            ).add_to(mapa)
        
        # Agregar leyenda
        self._agregar_leyenda(mapa)
        
        # Guardar mapa
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"mapa_safehex_{timestamp}.html"
        ruta_mapa = os.path.join(self.directorio_mapas, nombre_archivo)
        
        mapa.save(ruta_mapa)
        self.mapa_actual = ruta_mapa
        
        print(f"✅ Mapa guardado: {ruta_mapa}")
        return ruta_mapa
    
    def _agregar_leyenda(self, mapa):
        """Agrega una leyenda de colores al mapa"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Nivel de Riesgo</b></p>
        <p><i class="fa fa-circle" style="color:#D32F2F"></i> Alto (>0.30)</p>
        <p><i class="fa fa-circle" style="color:#F57C00"></i> Medio (0.15-0.30)</p>
        <p><i class="fa fa-circle" style="color:#FFC107"></i> Bajo (0.05-0.15)</p>
        <p><i class="fa fa-circle" style="color:#4CAF50"></i> Muy Bajo (<0.05)</p>
        </div>
        '''
        mapa.get_root().html.add_child(folium.Element(legend_html))
    
    def mapa_existe(self):
        """Verifica si hay un mapa generado"""
        return self.mapa_actual is not None and os.path.exists(self.mapa_actual)
    
    def obtener_mapa_actual(self):
        """Retorna la ruta del mapa actual"""
        return self.mapa_actual
    
    def abrir_mapa(self):
        """Abre el mapa en el navegador"""
        if self.mapa_existe():
            webbrowser.open(f"file://{os.path.abspath(self.mapa_actual)}")
            return True
        return False
    
    def limpiar_mapas_antiguos(self, dias=7):
        """Elimina mapas más antiguos que N días"""
        import time
        from pathlib import Path
        
        tiempo_actual = time.time()
        limite_tiempo = tiempo_actual - (dias * 24 * 60 * 60)
        
        directorio = Path(self.directorio_mapas)
        for archivo in directorio.glob("mapa_safehex_*.html"):
            if archivo.stat().st_mtime < limite_tiempo:
                archivo.unlink()
                print(f"🗑️ Mapa antiguo eliminado: {archivo}")
    
    def obtener_estadisticas_mapa(self):
        """Obtiene estadísticas del último mapa generado"""
        if not self.mapa_existe():
            return None
        
        # Aquí podrías agregar lógica para analizar el archivo HTML
        # y extraer estadísticas del mapa
        return {
            'archivo': self.mapa_actual,
            'fecha': datetime.fromtimestamp(os.path.getmtime(self.mapa_actual)),
            'tamaño': os.path.getsize(self.mapa_actual)
        }
