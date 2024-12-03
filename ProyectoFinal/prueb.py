# %% [markdown]
# # Ara Macao y Ara Ambiguus: Costa Rica

# %%
pip install streamlit-folium

# %%
pip show streamlit-folium

# %%
from streamlit_folium import st_folium
print("streamlit_folium importado correctamente")

# %%
csv_data = pd.read_csv(
    r"C:\Users\nparra\ProyectoFinal\Aras - Proyecto Final\Ara Macao_Ara Ambiguus.csv",
    delimiter="\t",
    engine="python"
)

# %%
with open(r"C:\Users\nparra\ProyectoFinal\Aras - Proyecto Final\Ara Macao_Ara Ambiguus.csv", "r", encoding="utf-8") as file:
    for i, line in enumerate(file):
        print(f"Línea {i+1}: {line.strip()}")
        if i >= 10:  # Muestra solo las primeras 10 líneas
            break

# %%
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Cargar datos
@st.cache_data
def load_data():
    csv_path = r"C:\Users\nparra\ProyectoFinal\Aras - Proyecto Final\Ara Macao_Ara Ambiguus.csv"
    geojson_path = r"C:\Users\nparra\ProyectoFinal\Aras - Proyecto Final\provinciasCR.geojson"
    csv_data = pd.read_csv(csv_path, delimiter="\t")  # Cambia el delimitador si es necesario
    geojson_data = gpd.read_file(geojson_path)
    return csv_data, geojson_data

csv_data, geojson_data = load_data()

# Título de la aplicación
st.title("Proyecto Final: Visualización Interactiva con Streamlit")

# Lista de selección
field_to_filter = st.selectbox("Selecciona el campo para filtrar:", csv_data.columns)
unique_values = csv_data[field_to_filter].unique()
selected_value = st.selectbox(f"Selecciona un valor de '{field_to_filter}':", unique_values)

# Filtrar datos
filtered_data = csv_data[csv_data[field_to_filter] == selected_value]

# Tabla de datos
st.subheader("Tabla de Datos Filtrados")
st.write(filtered_data)

# Gráfico interactivo
st.subheader("Gráfico Interactivo")
chart = px.bar(filtered_data, x=filtered_data.columns[0], y=filtered_data.columns[1])  # Ajusta las columnas
st.plotly_chart(chart)

# Mapa interactivo
st.subheader("Mapa Interactivo")

try:
    # Combinar datos filtrados con el GeoJSON
    # Asegúrate de que los nombres de las columnas coincidan
    map_data = geojson_data.merge(filtered_data, how="inner", left_on="nombre_provincia", right_on="Provincia")
    
    # Crear el mapa
    m = folium.Map(location=[9.8, -83.8], zoom_start=8)  # Ajusta la ubicación inicial según corresponda
    for _, row in map_data.iterrows():
        folium.Marker(
            location=[row['geometry'].centroid.y, row['geometry'].centroid.x],
            popup=row['nombre_provincia']  # O ajusta según las columnas disponibles
        ).add_to(m)
    
    # Mostrar el mapa en Streamlit
    st_folium(m, width=700, height=500)

except Exception as e:
    st.write(f"Error al generar el mapa: {e}")




