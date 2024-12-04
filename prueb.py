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
# # Carga de datos

@st.cache_data
def cargar_Ara_MacaoAmbiguus():
    try:
        # Cargar el archivo CSV con tabulaciones como delimitador
        MacaoAmbiguus = pd.read_csv(Macao_Ambiguus, delimiter="\t")
        
        # Eliminar espacios adicionales de los nombres de las columnas
        MacaoAmbiguus.columns = MacaoAmbiguus.columns.str.strip()
                
        return MacaoAmbiguus
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return None

# Cargar los datos
MacaoAmbiguus_CR = cargar_Ara_MacaoAmbiguus()

# Verificar si los datos se cargaron correctamente
if MacaoAmbiguus_CR is not None:
    st.write("Datos cargados con éxito.")
    # Continuar con el procesamiento normal
    MacAmb_prov = MacaoAmbiguus_CR['Provincia'].unique().tolist()
else:
    st.error("No se pudieron cargar los datos.")
    st.stop()

@st.cache_data
def cargar_lim_provincias():
    provincias = gpd.read_file(lim_provincias)
    return provincias

# %%
st.title('Ara Macao y Ara Ambiguus: Costa Rica')
st.subheader('Geog. Santiago Brenes Salas (B81292)')

# %%
# Datos de Ara Macao y Ara Ambiguus
carga_MacaoAmbiguus = st.text('Datos de Ara Macao y Ara Ambiguus')
MacaoAmbiguus_CR = cargar_Ara_MacaoAmbiguus()
carga_MacaoAmbiguus.text('Los datos de Ara Macao y Ara Ambiguus han sido cargados.')

# Cargar datos geoespaciales de las provincias
carga_provinciasCR = st.text('Cargando datos de los límites de las provincias...')
provinciasCR = cargar_lim_provincias()
carga_provinciasCR.text('Los límites de las provincias han sido cargados.')

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
    Ara_seleccion = MacaoAmbiguus_filtrados['cod_provin'].iloc[0]
else:
    MacaoAmbiguus_filtrados = MacaoAmbiguus_CR.copy()
    Ara_seleccion = None

# %%
# Crear un GeoDataFrame para las provincias
provinciasCR = provinciasCR.to_crs("EPSG:4326")

# Unión de los datos de Ara Macao y Ara Ambiguus con las provincias
MacaoAmbiguus_gdf = provinciasCR.copy()
MacaoAmbiguus_merged = MacaoAmbiguus_gdf.merge(
    MacaoAmbiguus_filtrados, 
    how='inner', 
    left_on='provincia', 
    right_on='Provincia'
)

# Filtración de las columnas relevantes del conjunto de datos
columnas_bf = [
    'provincia',
    'geometry',
    'Nombre'
]
MacaoAmbiguus_merged = MacaoAmbiguus_merged[columnas_bf]
MacaoAmbiguus_merged = MacaoAmbiguus_merged.rename(columns={'Nombre': 'Especie'})

# Mostrar la tabla
st.subheader('Datos seleccionables por provincia para Ara Macao y Ara Ambiguus')
st.dataframe(MacaoAmbiguus_merged, hide_index=True)

# %% [markdown]
# # Frecuencia de observaciones registradas de Ara Macao y Ara Ambiguus por mes

# %%
# Crear una columna con los nombres de los meses
MacaoAmbiguus_CR['Mes'] = MacaoAmbiguus_CR['month'].replace({
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
})

# Crear un histograma para la frecuencia de observaciones registradas por mes, separado por especie
fig = px.histogram(
    MacaoAmbiguus_CR,
    x='Mes',
    color='Nombre',
    title='Frecuencia de observaciones registradas de Ara Macao y Ara Ambiguus por mes',
    labels={
        'Mes': 'Mes',
        'Cantidad de observaciones registradas': 'Cantidad de observaciones registradas'
    },
    color_discrete_map={
        'Ara macao': '#E60000',
        'Ara ambiguus': '#38A800'
    }
)

fig.update_xaxes(categoryorder='array', categoryarray=[
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
])

fig.update_layout(
    xaxis_title='Mes',
    yaxis_title='Cantidad de observaciones registradas',
    barmode='group',
    width=1000,
    height=600
)

fig.update_yaxes(tickformat=",d")
fig.update_layout(legend_title_text='Especie')
st.plotly_chart(fig)

# %% [markdown]
# # Cantidad de observaciones registradas de Ara Macao y Ara Ambiguus por provincia

# %%
# Crear el mapa interactivo con las áreas de conservación
m = provinciasCR.explore(
    column='Conteo',
    name='Cantidad de Lapas por provincia',
    cmap='OrRd',
    tooltip=['provincia', 'geometry'],
    legend=True,
    legend_kwds={
        'caption': "Distribución de los lapas en Provincias",
        'orientation': "horizontal"
    }
)

# Mostrar el mapa interactivo
st.subheader('Distribución de Ara Macao y Ara Ambiguus en Costa Rica')
st_folium(m, width=700, height=600)
