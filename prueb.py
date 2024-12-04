# %% [markdown]
# # Ara Macao y Ara Ambiguus: Costa Rica

# %%
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
from streamlit_folium import folium_static, st_folium

# %%
# Rutas de los datos
Ara_MacaoAmbiguus = 'Aras/Macao_Ambiguus.csv'  # CSV de Ara Macao y Ara Ambiguus
lim_provincias = 'Aras/provincias.gpkg'  # Archivo de límites provinciales

# %% [markdown]
st.title('Ara Macao y Ara Ambiguus: Costa Rica')
st.subheader('Geog. Santiago Brenes Salas (B81292)')

# %% [markdown]
# ## Función para cargar y procesar datos

@st.cache_data
def cargar_Ara_MacaoAmbiguus():
    try:
        # Cargar el archivo CSV con tabulaciones como delimitador
        MacaoAmbiguus = pd.read_csv(Ara_MacaoAmbiguus, delimiter="\t")
        
        # Eliminar espacios adicionales de los nombres de las columnas
        MacaoAmbiguus.columns = MacaoAmbiguus.columns.str.strip()
        
        # Reemplazar nombres de provincias para corregir inconsistencias
        if 'Provincia' in MacaoAmbiguus.columns:
            MacaoAmbiguus['Provincia'] = MacaoAmbiguus['Provincia'].replace({
                "Limon": "Limón",
                "San Jose": "San José"
            })
        
        # Filtrar registros de Ara ambiguus
        MacaoAmbiguus = MacaoAmbiguus[MacaoAmbiguus['Nombre'] == 'Ara ambiguus']
                
        return MacaoAmbiguus
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return None

# %% [markdown]
# ## Función para cargar datos geoespaciales

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

# %% [markdown]
# ## Cargar los datos

# Cargar datos de Ara ambiguus
MacaoAmbiguus_CR = cargar_Ara_MacaoAmbiguus()

if MacaoAmbiguus_CR is not None:
    st.write("Datos filtrados (Ara ambiguus) cargados con éxito.")
    st.dataframe(MacaoAmbiguus_CR.head())  # Mostrar primeras filas
else:
    st.error("No se pudieron cargar los datos.")
    st.stop()

# Cargar datos geoespaciales de las provincias
carga_provinciasCR = st.text('Cargando datos de los límites de las provincias...')
provinciasCR = cargar_lim_provincias()
carga_provinciasCR.text('Los límites de las provincias han sido cargados.')

if provinciasCR is not None:
    st.write("Columnas disponibles en provinciasCR:", provinciasCR.columns.tolist())
else:
    st.error("No se pudieron cargar las provincias.")
    st.stop()

# %% [markdown]
# ## Agrupamiento por provincia

@st.cache_data
def agrupar_por_provincia(MacaoAmbiguus_CR):
    agrupado = MacaoAmbiguus_CR.groupby('Provincia')['Cuenta Individual'].sum().reset_index()
    agrupado.rename(columns={'Cuenta Individual': 'Total Cuenta Individual'}, inplace=True)
    return agrupado

# Agrupamiento por provincia
agrupado_MacaoAmbiguus_CR = agrupar_por_provincia(MacaoAmbiguus_CR)

# Mostrar los totales por provincia
st.subheader('Totales por provincia (Ara ambiguus)')
st.dataframe(agrupado_MacaoAmbiguus_CR)

# %% [markdown]
# ## Gráfico de Totales por Provincia

fig_totales = px.bar(
    agrupado_MacaoAmbiguus_CR,
    x='Provincia',
    y='Total Cuenta Individual',
    title='Totales de Ara ambiguus por provincia',
    labels={'Provincia': 'Provincia', 'Total Cuenta Individual': 'Total Cuenta Individual'},
    color='Provincia'
)
st.plotly_chart(fig_totales)

# %% [markdown]
# ## Mapa de Totales por Provincia

if provinciasCR is not None:
    # Asignar totales por provincia al GeoDataFrame
    provinciasCR['Total Cuenta Individual'] = provinciasCR['provincia'].map(
        agrupado_MacaoAmbiguus_CR.set_index('Provincia')['Total Cuenta Individual']
    ).fillna(0)  # Rellenar con 0 si no hay datos

    try:
        # Crear el mapa cloroplético
        m_totales = provinciasCR.explore(
            column='Total Cuenta Individual',
            name='Total Cuenta Individual',
            cmap='YlGn',
            tooltip=['provincia', 'Total Cuenta Individual'],
            legend=True,
            legend_kwds={
                'caption': "Totales de Ara ambiguus por provincia",
                'orientation': "horizontal"
            }
        )

        # Mostrar el mapa interactivo
        st.subheader('Totales de Ara ambiguus en Costa Rica')
        st_folium(m_totales, width=700, height=600)
    except Exception as e:
        st.error(f"Error al generar el mapa interactivo: {e}")
else:
    st.error("No se pudieron cargar los datos de provincias.")

