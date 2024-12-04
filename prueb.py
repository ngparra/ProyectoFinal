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
import ee
import geemap
import matplotlib.pyplot as plt

from io import BytesIO
from matplotlib import colors
from matplotlib.colors import LinearSegmentedColormap
from folium.raster_layers import ImageOverlay
from streamlit_folium import folium_static, st_folium
from branca.colormap import LinearColormap, linear
from folium import TileLayer

# %%
# CSV Ara Macao y Ara Ambiguus
Ara_MacaoAmbiguus = 'Aras/Macao_Ambiguus.csv' 

# Provincias
lim_provincias = 'Aras/provincias.gpkg'

# %% [markdown]
# %%
st.title('Ara Macao y Ara Ambiguus: Costa Rica')
st.subheader('Geog. Santiago Brenes Salas (B81292)')

# # Carga de datos
# Función para cargar y corregir los datos del CSV
@st.cache_data
def cargar_Ara_MacaoAmbiguus():
    try:
        # Cargar el archivo CSV con tabulaciones como delimitador
        MacaoAmbiguus = pd.read_csv(Ara_MacaoAmbiguus, delimiter="\t")
        
        # Eliminar espacios adicionales de los nombres de las columnas
        MacaoAmbiguus.columns = MacaoAmbiguus.columns.str.strip()
        
        # Reemplazar "Limon" por "Limón" y "San Jose" por "San José" en la columna correspondiente
        if 'Provincia' in MacaoAmbiguus.columns:
            MacaoAmbiguus['Provincia'] = MacaoAmbiguus['Provincia'].replace({
                "Limon": "Limón",
                "San Jose": "San José"
            })
        
        # Filtrar solo los registros de Ara ambiguus
        MacaoAmbiguus = MacaoAmbiguus[MacaoAmbiguus['Nombre'] == 'Ara ambiguus']
                
        return MacaoAmbiguus
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return None

# Cargar los datos filtrados
MacaoAmbiguus_CR = cargar_Ara_MacaoAmbiguus()

if MacaoAmbiguus_CR is not None:
    st.write("Datos filtrados (Ara ambiguus) cargados con éxito.")
    st.dataframe(MacaoAmbiguus_CR.head())  # Muestra los primeros registros para verificar
else:
    st.error("No se pudieron cargar los datos.")
    st.stop()

@st.cache_data
def cargar_lim_provincias():
    try:
        provincias = gpd.read_file(lim_provincias)
        # Verificar y configurar CRS si es necesario
        if provincias.crs is None:
            provincias.set_crs("EPSG:4326", inplace=True)
        return provincias
    except Exception as e:
        st.error(f"Error al cargar los datos geoespaciales: {e}")
        return None


# %%
# Cargar datos geoespaciales de las provincias
carga_provinciasCR = st.text('Cargando datos de los límites de las provincias...')
provinciasCR = cargar_lim_provincias()
carga_provinciasCR.text('Los límites de las provincias han sido cargados.')

# Verificar columnas en provinciasCR
if provinciasCR is not None:
    st.write("Columnas disponibles en provinciasCR:", provinciasCR.columns.tolist())

    # Crear la columna 'Conteo' si no existe
    if 'Conteo' not in provinciasCR.columns:
        provinciasCR['Conteo'] = 0  # Valor por defecto
else:
    st.error("No se pudieron cargar las provincias.")
    st.stop()

# %%
MacAmb_prov = MacaoAmbiguus_CR['Provincia'].unique().tolist()
MacAmb_prov.sort()

# "Todas" al inicio de la lista
opciones_provincias = ['Todas'] + MacAmb_prov

# Selección de provincia para filtrar solo la tabla
st.sidebar.title('Filtros')
provincia_seleccionada = st.sidebar.selectbox(
    'Elige una provincia para ver los datos en la tabla:',
    opciones_provincias
)

# Filtrar datos para la tabla según la selección
if provincia_seleccionada != 'Todas':
    MacaoAmbiguus_filtrados = MacaoAmbiguus_CR[MacaoAmbiguus_CR['Provincia'] == provincia_seleccionada]
else:
    MacaoAmbiguus_filtrados = MacaoAmbiguus_CR.copy()

# Mostrar la tabla filtrada
st.subheader('Datos filtrados de Ara ambiguus')
st.dataframe(MacaoAmbiguus_filtrados)

# %%
# Crear el gráfico de frecuencia mensual
if 'month' in MacaoAmbiguus_filtrados.columns:
    MacaoAmbiguus_filtrados['Mes'] = MacaoAmbiguus_filtrados['month'].replace({
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    })

    fig = px.histogram(
        MacaoAmbiguus_filtrados,
        x='Mes',
        color='Nombre',
        title='Frecuencia de observaciones registradas de Ara ambiguus por mes',
        labels={'Mes': 'Mes', 'Cantidad de observaciones': 'Cantidad de observaciones'},
        color_discrete_map={'Ara ambiguus': '#38A800'}
    )
    fig.update_xaxes(categoryorder='array', categoryarray=[
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ])
    st.plotly_chart(fig)
else:
    st.warning("La columna 'month' no está presente en los datos filtrados.")

# %% [markdown]
# Mapa interactivo con capas de mapas base

# Crear un mapa base
mapa = folium.Map(location=[9.8, -84], zoom_start=8, tiles=None)  # Sin mapa base inicial

# Agregar capas de mapas base
TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(mapa)
TileLayer('CartoDB positron', name='CartoDB Positron').add_to(mapa)
TileLayer('Stamen Terrain', name='Stamen Terrain').add_to(mapa)

# Agregar capa de datos (cloropletas)
folium.Choropleth(
    geo_data=provinciasCR,
    name='Conteo de Ara ambiguus',
    data=provinciasCR,
    columns=['provincia', 'Conteo'],
    legend_name='Observaciones de Ara ambiguus'
).add_to(mapa)

# Agregar control de capas
folium.LayerControl().add_to(mapa)

# Mostrar mapa
st.subheader('Mapa interactivo con opciones de mapas base')
st_folium(mapa, width=700, height=600)
