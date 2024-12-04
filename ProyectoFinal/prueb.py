# %% [markdown]
# # Ara Macao y Ara Ambiguus: Costa Rica

# %%
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
import mapclassify
import numpy as np
import folium
import branca
import plotly.graph_objects as go
import leafmap
import rasterio
import io
import ee
import geemap

# %%
from io import BytesIO
from os import name
from matplotlib import colors
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from folium.raster_layers import ImageOverlay
from rasterio.plot import show
from folium import Choropleth, Popup, Tooltip, GeoJson, GeoJsonTooltip
from streamlit_folium import folium_static, st_folium
from folium.raster_layers import ImageOverlay
from branca.colormap import LinearColormap, linear

# %%
#CSV Ara Macao y Ara Ambiguus
Ara_MacaoAmbiguus = 'Aras/Macao_Ambiguus.csv' 

#Provincias
lim_provincias= 'Aras/provincias.gpkg'


# %% [markdown]
# # Carga de datos

# %%
#carga datos CSV

@st.cache_data
def cargar_Ara_MacaoAmbiguus():
    MacaoAmbiguus = pd.read_csv(Ara_MacaoAmbiguus)
    return MacaoAmbiguus

# Función para cargar el límite de provincias

@st.cache_data
def cargar_lim_provincias():
    provincias= gpd.read_file(lim_provincias)
    return provincias




# %%
st.title('Ara Macao y Ara Ambiguus: Costa Rica')
st.subheader ('Geog. Santiago Brenes Salas (B81292)')

# %%
#Datos de Ara Macao y Ara Ambiguus
carga_MacaoAmbiguus = st.text('Datos de Ara Macao y Ara Ambiguus')
MacaoAmbiguus_CR = cargar_MacaoAmbiguus()
carga_MacaoAmbiguus.text('Los datos de Ara Macao y Ara Ambiguus.')


# Cargar datos geoespcailes de las provicnias
carga_provinciasCR = st.text('Cargando datos de los límites de las provincias...')
provinciasCR = cargar_provincias()
carga_provinciasCR.text('Los límites de las provincias fueron cargadas.')



# %%
MacAmb_prov = MacaoAmbiguus_CR['Provincia'].unique().tolist()
MacAmb_prov.sort()

#  "Todas" al inicio de la lista
opciones_provincias = ['Todas'] + MacAmb_prov

# Selectbox
provincia_seleccionado = st.sidebar.selectbox(
    'Elige una provincia',
    opciones_provincias
)

# %%
# Filtrar datos para no tener nulos

if provincia_seleccionado != 'Todas':
    # Filtrar los datos para el provincia seleccionado
    MacaoAmbiguus_filtrados = MacaoAmbiguus_CR[MacaoAmbiguus_CR['Provincia'] == provincia_seleccionado]
    
    # Obtener el Código de la provincia seleccionada
    Ara_seleccion = MacaoAmbiguus_filtrados['cod_provin'].iloc[0]
else:
    # No aplicar filtro
    MacaoAmbiguus_filtrados = MacaoAmbiguus_CR.copy()
    Ara_seleccion= None

# %%
#Unión de los datos de Ara Macao y Ara Ambiguus con las provincias
MacaoAmbiguus_merged = MacaoAmbiguus_gdf.merge(
    MacaoAmbiguus_filtrados, 
    how='inner', 
    left_on='provincia', 
    right_on='Provincia'
)


# Filtración de las columnas relevantes del conjunto de los datos 
 #   columnas_bf = [
  #  'provincia',
   # 'geometry',
    #'Nombre'
#]
#MacaoAmbiguus_merged= MacaoAmbiguus_merged[columnas_bf]
#MacaoAmbiguus_merged = MacaoAmbiguus_merged.rename(columns={'Nombre': 'Especie'})

# %%
# ----- Sección interactiva -----

# Mostrar la tabla
st.subheader('Datos seleccionables por provincia para Ara Macao y Ara Ambiguus')
st.dataframe(MacaoAmbiguus_merged, hide_index=True)

# %% [markdown]
# # Frecuencia de observaciones registradas de Ara Macao y Ara Ambiguus por mes

# %%
# Crear una columna con los nombres de los meses
data['Mes'] = data['month'].replace({
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
})

# Crear un histograma para la frecuencia de observaciones registradas por mes, separado por especie
fig = px.histogram(
    data,
    x='Mes',
    color='Nombre',  # Diferenciar las observaciones por especie
    title='Frecuencia de observaciones registradas de Ara Macao y Ara Ambiguus por mes',
    labels={
        'Mes': 'Mes',
        'Cantidad de observaciones registradas': 'Cantidad de observaciones registradas'
    },
    color_discrete_map={
        'Ara macao': '#E60000',     # Color rojo para Ara macao
        'Ara ambiguus': '#38A800'    # Color verde para Ara ambiguus
    }
)

# Ordenar los meses en el orden cronológico correcto
fig.update_xaxes(categoryorder='array', categoryarray=[
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
])

# Personalizar el diseño del histograma
fig.update_layout(
    xaxis_title='Mes',
    yaxis_title='Cantidad de observaciones registradas',
    barmode='group',  # Mostrar las barras de cada especie una al lado de la otra
    width=1000,       # Ancho del gráfico en píxeles
    height=600        # Alto del gráfico en píxeles
)

# Actualizar el formato del eje y evitar notación científica
fig.update_yaxes(tickformat=",d")

# Atributos globales de la figura
fig.update_layout(
    legend_title_text='Especie'
)

# Mostrar el gráfico
fig.show()

# %% [markdown]
# # Cantidad de observaciones registradas de Ara Macao y Ara Ambiguus por provincia

# %%
# # # ----- Mapa interactivo: Cantones con presencia de botaderos y su relación con el IDHD -----

MacaoAmbiguus_merged = MacaoAmbiguus_merged.to_crs("EPSG:4326")
provincias = provincias.to_crs("EPSG:4326")

# Crear el mapa interactivo con las áreas de conservación
m = polygons_wgs84_gdf.explore(
    column='Conteo',
    name='Cantidad de Lapas por provincia',
    cmap='OrRd',
    tooltip=['PROVINCIA', 'Conteo'],
    legend=True,
    legend_kwds={
        'caption': "Distribución de los lapas en Provincias",
        'orientation': "horizontal"
    },
)

# Ruta del ráster remoto
raster_url = 'https://github.com/gf0657-programacionsig/2024-ii/raw/refs/heads/main/datos/worldclim/altitud.tif'

# Crear una capa de ráster con folium
raster_layer = folium.raster_layers.TileLayer(
    tiles=raster_url,
    attr="WorldClim Altitud",
    name="Altitud",
    overlay=True,
    control=True
)

# Agregar la capa ráster al mapa
raster_layer.add_to(m)

# Agregar un control de capas al mapa
folium.LayerControl().add_to(m)

# Mostrar el mapa interactivo
m


# ----- Agregar control de capas -----
folium.LayerControl().add_to(mapa)

# ----- Mostrar el mapa en Streamlit -----
st.subheader('Relación entre los cantones con presencia de botaderos y su promedio del IDHD entre 2010 y 2020 según provincia')
st_folium(mapa, width=700, height=600)


