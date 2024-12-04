# %% [markdown]
# # Ara Macao y Ara Ambiguus: Costa Rica

# %%
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px

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
        # Agregar columna con centroides para el zoom dinámico
        provincias['centroid'] = provincias.geometry.centroid
        return provincias
    except Exception as e:
        st.error(f"Error al cargar los datos geoespaciales: {e}")
        return None

# Carga de datos
MacaoAmbiguus_CR = cargar_Ara_MacaoAmbiguus()
provinciasCR = cargar_lim_provincias()

if MacaoAmbiguus_CR is None or provinciasCR is None:
    st.stop()

# Agrupación de datos por Provincia y Cuenta Individual
datos_agrupados = MacaoAmbiguus_CR.groupby(['Provincia', 'Cuenta Individual']).size().reset_index(name='Conteo')

# Filtro por Provincia
provincias_filtradas = datos_agrupados['Provincia'].unique().tolist()
provincias_filtradas.sort()
opciones_provincias = ['Todas'] + provincias_filtradas

provincia_seleccionada = st.sidebar.selectbox("Elige una Provincia:", opciones_provincias)

# Aplicar filtro por Provincia
if provincia_seleccionada != 'Todas':
    datos_filtrados = datos_agrupados[datos_agrupados['Provincia'] == provincia_seleccionada]
    provinciasCR['Conteo'] = provinciasCR['provincia'].map(
        datos_filtrados.groupby('Provincia')['Conteo'].sum()
    ).fillna(0)

    # Obtener coordenadas para centrar el mapa en la provincia seleccionada
    provincia_geom = provinciasCR[provinciasCR['provincia'] == provincia_seleccionada]
    centro = [provincia_geom['centroid'].iloc[0].y, provincia_geom['centroid'].iloc[0].x]
    zoom = 10  # Zoom más cercano para provincias
else:
    datos_filtrados = datos_agrupados.copy()
    provinciasCR['Conteo'] = provinciasCR['provincia'].map(
        datos_filtrados.groupby('Provincia')['Conteo'].sum()
    ).fillna(0)

    # Coordenadas predeterminadas para Costa Rica
    centro = [9.8, -84]
    zoom = 8

# Mostrar los datos filtrados en una tabla
st.subheader('Datos Filtrados')
st.dataframe(datos_filtrados)

# Gráfico de cuentas individuales por provincia
fig = px.bar(
    datos_filtrados,
    x='Cuenta Individual',
    y='Conteo',
    color='Provincia',
    title=f'Cantidad de observaciones por Cuenta Individual en {"todas las provincias" if provincia_seleccionada == "Todas" else provincia_seleccionada}',
    labels={'Cuenta Individual': 'Cuenta Individual', 'Conteo': 'Cantidad de observaciones'},
)
st.plotly_chart(fig)

# Mapa interactivo

# Crear un mapa base con ubicación y zoom dinámico
mapa = folium.Map(location=centro, zoom_start=zoom, tiles=None)  # Vista inicial

# Agregar capas de mapas base
folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(mapa)
folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(mapa)
folium.TileLayer('Stamen Terrain', name='Stamen Terrain').add_to(mapa)

# Agregar capa de cloropletas basada en la columna 'Conteo'
folium.Choropleth(
    geo_data=provinciasCR,
    name='Conteo de observaciones por provincia',
    data=provinciasCR,
    columns=['provincia', 'Conteo'],  # Usamos la columna de conteo
    key_on='feature.properties.provincia',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Conteo por Provincia'
).add_to(mapa)

# Agregar etiquetas para cada provincia
for _, row in provinciasCR.iterrows():
    folium.Marker(
        location=[row['centroid'].y, row['centroid'].x],
        icon=None,
        popup=f"{row['provincia']}: {int(row['Conteo'])} observaciones"
    ).add_to(mapa)

# Agregar control de capas
folium.LayerControl(collapsed=False).add_to(mapa)

# Mostrar el mapa interactivo
st.subheader('Mapa Interactivo')
st_folium(mapa, width=700, height=600)

st.subheader('Mapa Interactivo')
st_folium(mapa, width=700, height=600)

