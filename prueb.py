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

@st.cache_data
def cargar_Ara_MacaoAmbiguus():
    try:
        # Cargar el archivo CSV con tabulaciones como delimitador
        MacaoAmbiguus = pd.read_csv(Ara_MacaoAmbiguus, delimiter="\t")
        
        # Eliminar espacios adicionales de los nombres de las columnas
        MacaoAmbiguus.columns = MacaoAmbiguus.columns.str.strip()
        
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
    st.write("Columnas disponibles en los datos:", MacaoAmbiguus_CR.columns.tolist())
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
# Datos de Ara Macao y Ara Ambiguus
carga_MacaoAmbiguus = st.text('Datos de Ara Macao y Ara Ambiguus')
MacaoAmbiguus_CR = cargar_Ara_MacaoAmbiguus()
carga_MacaoAmbiguus.text('Los datos de Ara Macao y Ara Ambiguus han sido cargados.')

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

# Selectbox
provincia_seleccionada = st.sidebar.selectbox(
    'Elige una provincia',
    opciones_provincias
)

# Filtrar datos para no tener nulos
if provincia_seleccionada != 'Todas':
    MacaoAmbiguus_filtrados = MacaoAmbiguus_CR[MacaoAmbiguus_CR['Provincia'] == provincia_seleccionada]
    if 'cod_provin' in MacaoAmbiguus_filtrados.columns:
        Ara_seleccion = MacaoAmbiguus_filtrados['cod_provin'].iloc[0]
    else:
        st.warning("La columna 'cod_provin' no existe en los datos filtrados.")
        Ara_seleccion = None
else:
    MacaoAmbiguus_filtrados = MacaoAmbiguus_CR.copy()
    Ara_seleccion = None

# %%
# Unión de los datos de Ara Macao y Ara Ambiguus con las provincias
try:
    MacaoAmbiguus_gdf = provinciasCR.copy()
    MacaoAmbiguus_merged = MacaoAmbiguus_gdf.merge(
        MacaoAmbiguus_filtrados, 
        how='inner', 
        left_on='provincia', 
        right_on='Provincia'
    )

    # Filtración de las columnas relevantes del conjunto de datos
    columnas_bf = ['provincia', 'geometry', 'Nombre']
    MacaoAmbiguus_merged = MacaoAmbiguus_merged[columnas_bf]
    MacaoAmbiguus_merged = MacaoAmbiguus_merged.rename(columns={'Nombre': 'Especie'})

    # Convertir la columna 'geometry' a texto (WKT) para compatibilidad con Streamlit
    if 'geometry' in MacaoAmbiguus_merged.columns:
        MacaoAmbiguus_merged['geometry'] = MacaoAmbiguus_merged['geometry'].apply(lambda geom: geom.wkt if geom else None)

    # Mostrar la tabla sin la columna 'geometry'
    st.subheader('Datos seleccionables por provincia para Ara Macao y Ara Ambiguus')
    st.dataframe(MacaoAmbiguus_merged.drop(columns=['geometry']), hide_index=True)
except Exception as e:
    st.error(f"Error al procesar los datos para la visualización: {e}")

# %%
# Crear el mapa interactivo con las áreas de conservación
try:
    m = provinciasCR.explore(
        column='Conteo',
        name='Cantidad de Lapas por provincia',
        cmap='OrRd',
        tooltip=['provincia'],
        legend=True,
        legend_kwds={
            'caption': "Distribución de los lapas en Provincias",
            'orientation': "horizontal"
        }
    )

    # Mostrar el mapa interactivo
    st.subheader('Distribución de Ara Macao y Ara Ambiguus en Costa Rica')
    st_folium(m, width=700, height=600)
except Exception as e:
    st.error(f"Error al generar el mapa interactivo: {e}")
