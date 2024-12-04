# %% [markdown]
# # Ara Macao y Ara Ambiguus: Costa Rica

# %%
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium import TileLayer

# %% [markdown]
# Configuración inicial y carga de datos

# CSV Ara Macao y Ara Ambiguus
Ara_MacaoAmbiguus = 'Aras/Macao_Ambiguus.csv' 

# Provincias
lim_provincias = 'Aras/provincias.gpkg'

st.title('Ara Macao y Ara Ambiguus: Costa Rica')
st.subheader('Geog. Santiago Brenes Salas (B81292)')

# Función para cargar y corregir los datos del CSV
@st.cache_data
def cargar_Ara_MacaoAmbiguus():
    try:
        MacaoAmbiguus = pd.read_csv(Ara_MacaoAmbiguus, delimiter="\t")
        MacaoAmbiguus.columns = MacaoAmbiguus.columns.str.strip()
        MacaoAmbiguus['Provincia'] = MacaoAmbiguus['Provincia'].replace({
            "Limon": "Limón",
            "San Jose": "San José"
        })
        return MacaoAmbiguus
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return None

@st.cache_data
def cargar_lim_provincias():
    try:
        provincias = gpd.read_file(lim_provincias)
        if provincias.crs is None:
            provincias.set_crs("EPSG:4326", inplace=True)
        return provincias
    except Exception as e:
        st.error(f"Error al cargar los datos geoespaciales: {e}")
        return None

# Carga de datos
MacaoAmbiguus_CR = cargar_Ara_MacaoAmbiguus()
provinciasCR = cargar_lim_provincias()

if MacaoAmbiguus_CR is None or provinciasCR is None:
    st.stop()

# %% [markdown]
# Filtro para todas las visualizaciones

# Obtener las opciones de filtro
provincias_unicas = MacaoAmbiguus_CR['Provincia'].unique().tolist()
provincias_unicas.sort()
opciones_provincias = ['Todas'] + provincias_unicas

# Filtro de selección de provincia
provincia_seleccionada = st.sidebar.selectbox("Elige una provincia:", opciones_provincias)

# Aplicar filtro a los datos
if provincia_seleccionada != 'Todas':
    datos_filtrados = MacaoAmbiguus_CR[MacaoAmbiguus_CR['Provincia'] == provincia_seleccionada]
    provinciasCR['Conteo'] = provinciasCR['provincia'].map(
        datos_filtrados['Provincia'].value_counts()
    ).fillna(0)
else:
    datos_filtrados = MacaoAmbiguus_CR.copy()
    provinciasCR['Conteo'] = provinciasCR['provincia'].map(
        MacaoAmbiguus_CR['Provincia'].value_counts()
    ).fillna(0)

# Mostrar los datos filtrados en una tabla
st.subheader('Datos Filtrados de Ara Ambiguus')
st.dataframe(datos_filtrados)

# %% [markdown]
# Gráfico de frecuencia mensual
if 'month' in datos_filtrados.columns:
    datos_filtrados['Mes'] = datos_filtrados['month'].replace({
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    })

    fig = px.histogram(
        datos_filtrados,
        x='Mes',
        color='Nombre',
        title='Frecuencia de observaciones por mes',
        labels={'Mes': 'Mes', 'Cantidad de observaciones': 'Cantidad de observaciones'}
    )
    fig.update_xaxes(categoryorder='array', categoryarray=[
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ])
    st.plotly_chart(fig)

# %% [markdown]
# Mapa interactivo

# Crear un mapa base
mapa = folium.Map(location=[9.8, -84], zoom_start=8, tiles=None)  # Sin mapa base inicial

# Agregar capas de mapas base
folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(mapa)
folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(mapa)
folium.TileLayer('Stamen Terrain', name='Stamen Terrain').add_to(mapa)

# Agregar capa de ráster remoto
raster_url = 'https://github.com/gf0657-programacionsig/2024-ii/raw/refs/heads/main/datos/worldclim/altitud.tif'
folium.raster_layers.ImageOverlay(
    name="Altitud",
    image=raster_url,
    bounds=[[8, -87], [11, -82]],  # Ajusta los límites a tu área de interés
    opacity=0.6
).add_to(mapa)

# Agregar capa de cloropletas
folium.Choropleth(
    geo_data=provinciasCR,
    name='Cantidad de Lapas por provincia',
    data=provinciasCR,
    columns=['provincia', 'Conteo'],
    key_on='feature.properties.provincia',
    fill_color='OrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Conteo por Provincia'
).add_to(mapa)

# Agregar control de capas
folium.LayerControl(collapsed=False).add_to(mapa)

# Mostrar el mapa interactivo
st.subheader('Mapa Interactivo')
st_folium(mapa, width=700, height=600)
