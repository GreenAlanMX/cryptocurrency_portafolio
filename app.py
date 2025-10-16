import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import sys

# Agregar el directorio padre al path para acceder a los datos
sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(page_title='Streaming Dashboard', layout='wide')
st.title('🌍 Streaming Executive Dashboard - Spatiotemporal Analysis')

# Configuración de datos
crypto_to_content = {
    'Bitcoin': 'Drama',
    'Ethereum': 'Comedy', 
    'BNB': 'Action',
    'Solana': 'Documentary',
    'Tether': 'Romance'
}

country_to_region = {
    'US': 'North America',
    'CN': 'Asia',
    'JP': 'Asia',
    'DE': 'Europe',
    'GB': 'Europe',
    'IN': 'Asia',
    'BR': 'South America',
    'CA': 'North America',
    'AU': 'Oceania',
    'KR': 'Asia'
}

@st.cache_data
def load_data():
    """Cargar datos desde la carpeta analyst"""
    try:
        # Cargar datos integrados
        integrated_path = Path('../analyst/integrated_data.csv')
        if integrated_path.exists():
            df_integrated = pd.read_csv(integrated_path)
            df_integrated['content_category'] = df_integrated['crypto'].map(crypto_to_content)
            df_integrated['region'] = df_integrated['country_code'].map(country_to_region)
        else:
            df_integrated = pd.DataFrame()
        
        # Cargar datos agregados por país
        country_path = Path('../analyst/country_aggregated.csv')
        if country_path.exists():
            df_country = pd.read_csv(country_path)
            df_country['content_category'] = df_country['crypto'].map(crypto_to_content)
            df_country['region'] = df_country['country_code'].map(country_to_region)
        else:
            df_country = pd.DataFrame()
        
        return df_integrated, df_country
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Cargar datos
df_integrated, df_country = load_data()

if df_integrated.empty or df_country.empty:
    st.error("❌ No se pudieron cargar los datos. Verifica que los archivos estén en la carpeta analyst/")
    st.stop()

# Sidebar con filtros
st.sidebar.header("🔧 Filtros")

# Filtro por categoría de contenido
content_categories = df_integrated['content_category'].unique()
selected_categories = st.sidebar.multiselect(
    "Categorías de Contenido",
    content_categories,
    default=content_categories
)

# Filtro por región
regions = df_integrated['region'].unique()
selected_regions = st.sidebar.multiselect(
    "Regiones",
    regions,
    default=regions
)

# Aplicar filtros
df_filtered = df_integrated[
    (df_integrated['content_category'].isin(selected_categories)) &
    (df_integrated['region'].isin(selected_regions))
]

df_country_filtered = df_country[
    (df_country['content_category'].isin(selected_categories)) &
    (df_country['region'].isin(selected_regions))
]

# Tabs principales
tab1, tab2, tab3 = st.tabs(['🌍 Geographic', '📈 Temporal', '📊 Analytics'])

with tab1:
    st.subheader('🌍 Análisis Geográfico')
    
    # Selector de visualización
    viz_type = st.selectbox(
        "Seleccionar tipo de visualización:",
        ["Gráfico de Barras por Región", "Gráfico de Barras por País", "Gráfico de Donut por Categoría", "Todos los Gráficos"]
    )
    
    if viz_type in ["Gráfico de Barras por Región", "Gráfico de Barras por País", "Gráfico de Donut por Categoría"]:
        col1, col2 = st.columns(2)
    else:
        col1, col2 = st.columns(2)
    
    if viz_type in ["Gráfico de Barras por Región", "Todos los Gráficos"]:
        with col1:
            # Gráfico de Barras por Región
            st.write("**Interés por Región**")
            if not df_country_filtered.empty:
                region_interest = df_country_filtered.groupby('region')['interest_mean'].mean().reset_index()
                region_interest = region_interest.sort_values('interest_mean', ascending=True)
                
                fig_region = px.bar(
                    region_interest,
                    x='interest_mean',
                    y='region',
                    orientation='h',
                    title="Interés Promedio por Región",
                    color='interest_mean',
                    color_continuous_scale="Blues",
                    text='interest_mean'
                )
                fig_region.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_region.update_layout(
                    height=400,
                    xaxis_title="Interés Promedio",
                    yaxis_title="Región",
                    showlegend=False
                )
                st.plotly_chart(fig_region, use_container_width=True)
            else:
                st.info("No hay datos para mostrar el gráfico")
    
    if viz_type in ["Gráfico de Barras por País", "Todos los Gráficos"]:
        col_for_country = col2 if viz_type == "Todos los Gráficos" else col1
        with col_for_country:
            # Gráfico de Barras por País
            st.write("**Interés por País**")
            if not df_country_filtered.empty:
                country_interest = df_country_filtered.groupby(['name', 'region'])['interest_mean'].mean().reset_index()
                country_interest = country_interest.sort_values('interest_mean', ascending=True)
                
                fig_country = px.bar(
                    country_interest,
                    x='interest_mean',
                    y='name',
                    orientation='h',
                    title="Interés Promedio por País",
                    color='interest_mean',
                    color_continuous_scale="Blues",
                    text='interest_mean',
                    hover_data=['region']
                )
                fig_country.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_country.update_layout(
                    height=500,
                    xaxis_title="Interés Promedio",
                    yaxis_title="País",
                    showlegend=False
                )
                st.plotly_chart(fig_country, use_container_width=True)
            else:
                st.info("No hay datos para mostrar el gráfico")
    
    if viz_type in ["Gráfico de Donut por Categoría", "Todos los Gráficos"]:
        col_for_donut = col2 if viz_type == "Todos los Gráficos" else col1
        with col_for_donut:
            # Gráfico de Donut por Categoría
            st.write("**Distribución por Categoría**")
            if not df_country_filtered.empty:
                category_interest = df_country_filtered.groupby('content_category')['interest_mean'].sum().reset_index()
                
                fig_donut = px.pie(
                    category_interest,
                    values='interest_mean',
                    names='content_category',
                    title="Distribución del Interés por Categoría",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4
                )
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                fig_donut.update_layout(height=400)
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("No hay datos para mostrar el gráfico")
    
    # Agregar tabla de datos y estadísticas
    if not df_country_filtered.empty:
        st.write("---")
        st.write("**📊 Datos Detallados y Estadísticas**")
        
        # Mostrar datos en tabla
        col_table, col_stats = st.columns([2, 1])
        
        with col_table:
            st.write("**Datos por País:**")
            display_data = df_country_filtered[['name', 'region', 'content_category', 'interest_mean', 'interest_max', 'volatility_7d_mean']].round(2)
            st.dataframe(display_data, use_container_width=True, height=300)
        
        with col_stats:
            st.write("**Estadísticas Clave:**")
            st.metric("País con Mayor Interés", 
                     df_country_filtered.loc[df_country_filtered['interest_mean'].idxmax(), 'name'],
                     f"{df_country_filtered['interest_mean'].max():.1f}")
            st.metric("País con Menor Interés", 
                     df_country_filtered.loc[df_country_filtered['interest_mean'].idxmin(), 'name'],
                     f"{df_country_filtered['interest_mean'].min():.1f}")
            st.metric("Interés Promedio Global", 
                     f"{df_country_filtered['interest_mean'].mean():.1f}")
            st.metric("Total de Países", 
                     df_country_filtered['name'].nunique())
    else:
        st.info("No hay datos para mostrar")

with tab2:
    st.subheader('📈 Análisis Temporal')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Serie temporal de interés
        st.write("**Evolución del Interés en el Tiempo**")
        if not df_filtered.empty:
            # Convertir fecha y agrupar por fecha
            df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
            daily_interest = df_filtered.groupby(['Date', 'content_category'])['interest'].mean().reset_index()
            
            # Paleta de azules personalizada
            blue_palette = ['#1f77b4', '#aec7e8', '#6ba3d6', '#4a90c2', '#2e5c8a']
            
            fig_temporal = px.line(
                daily_interest,
                x='Date',
                y='interest',
                color='content_category',
                title="Interés Promedio por Categoría",
                markers=True,
                color_discrete_sequence=blue_palette
            )
            fig_temporal.update_layout(
                height=500,
                xaxis_title="Fecha",
                yaxis_title="Interés Promedio",
                hovermode='x unified'
            )
            fig_temporal.update_traces(
                hovertemplate="<b>%{fullData.name}</b><br>" +
                             "Fecha: %{x}<br>" +
                             "Interés: %{y:.1f}<extra></extra>"
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
        else:
            st.info("No hay datos para mostrar la serie temporal")
    
    with col2:
        # Gráfico de volatilidad
        st.write("**Volatilidad por Categoría**")
        if not df_country_filtered.empty:
            volatility_data = df_country_filtered.groupby('content_category')['volatility_7d_mean'].mean().reset_index()
            fig_volatility = px.bar(
                volatility_data,
                x='content_category',
                y='volatility_7d_mean',
                title="Volatilidad Promedio por Categoría",
                color='volatility_7d_mean',
                color_continuous_scale="Blues"
            )
            fig_volatility.update_layout(
                height=500,
                xaxis_title="Categoría de Contenido",
                yaxis_title="Volatilidad Promedio",
                showlegend=False
            )
            fig_volatility.update_traces(
                hovertemplate="<b>%{x}</b><br>" +
                             "Volatilidad Promedio: %{y:.3f}<extra></extra>"
            )
            st.plotly_chart(fig_volatility, use_container_width=True)
        else:
            st.info("No hay datos para mostrar la volatilidad")

with tab3:
    st.subheader('📊 Analytics y KPIs')
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_countries = df_country_filtered['country_code'].nunique()
        st.metric("Países Analizados", total_countries)
    
    with col2:
        total_categories = df_country_filtered['content_category'].nunique()
        st.metric("Categorías de Contenido", total_categories)
    
    with col3:
        avg_interest = df_country_filtered['interest_mean'].mean()
        st.metric("Interés Promedio", f"{avg_interest:.1f}")
    
    with col4:
        max_interest = df_country_filtered['interest_max'].max()
        st.metric("Interés Máximo", f"{max_interest:.1f}")
    
    # Tabla de datos
    st.write("**Datos Detallados por País**")
    if not df_country_filtered.empty:
        display_columns = ['name', 'content_category', 'region', 'interest_mean', 'interest_max', 'volatility_7d_mean']
        st.dataframe(
            df_country_filtered[display_columns].round(2),
            use_container_width=True,
            height=300
        )
    else:
        st.info("No hay datos para mostrar en la tabla")

# Footer
st.markdown("---")
st.markdown("**Dashboard creado con Streamlit** | Datos de la carpeta analyst/")
