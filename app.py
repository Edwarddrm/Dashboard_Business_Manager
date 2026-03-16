import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuración de página ---
st.set_page_config(page_title="Dashboard Empresarial", page_icon="📈", layout="wide")

# --- Funciones de Carga de Datos ---
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"El archivo de datos no se encuentra en la ruta: {file_path}. Por favor, generá los datos de prueba primero.")
        st.stop()
        
    excel_file = pd.ExcelFile(file_path)
    
    # Cargar todas las hojas
    df_finanzas = excel_file.parse('Finanzas')
    df_procedimientos = excel_file.parse('Procedimientos')
    df_marketing = excel_file.parse('Marketing_General')
    df_campanas = excel_file.parse('Campanas')
    df_tareas = excel_file.parse('Tareas')
    
    return df_finanzas, df_procedimientos, df_marketing, df_campanas, df_tareas

# Ruta al archivo de datos
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'dummy_data.xlsx')

# Cargar los datos
df_finanzas, df_procedimientos, df_marketing, df_campanas, df_tareas = load_data(DATA_PATH)

# --- Título y Estilos ---
st.title("📊 Panel de Control Empresarial")
st.markdown("Bienvenido a tu dashboard interactivo. Navega entre las pestañas para ver las diferentes métricas.")

# Estilos CSS personalizados para las métricas
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #f0f2f6;
    border: 1px solid #e0e0e0;
    padding: 5% 5% 5% 10%;
    border-radius: 10px;
    color: #31333F;
    overflow-wrap: break-word;
}
/* Estilo modo oscuro (ajusta automáticamente) */
@media (prefers-color-scheme: dark) {
    div[data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #4d4d4d;
        color: white;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Definición de Pestañas ---
tab_finanzas, tab_marketing = st.tabs(["💰 Finanzas y Operaciones", "🚀 Marketing y Gestión"])

# ==============================================================================
# PESTAÑA 1: FINANZAS Y OPERACIONES
# ==============================================================================
with tab_finanzas:
    st.header("Resumen Financiero y Clientes")
    
    # Para el ejemplo, tomaremos el 'mes actual' como el último en el dataframe para mostrar KPIs puntuales
    # En un caso real, esto vendría filtrado o seleccionado por el usuario.
    # Asumamos que el mes actual de interés es 'Marzo' (índice 2)
    current_month_data = df_finanzas.iloc[2]
    
    # 1. KPIs Principales
    st.subheader("Métricas de Clientes (Mes Actual: Marzo)")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        label="Clientes Diarios Promedio", 
        value=f"{current_month_data['Promedio Clientes Diarios']:.1f}"
    )
    kpi2.metric(
        label="Clientes Semanales Promedio", 
        value=f"{current_month_data['Promedio Clientes Semanales']:.1f}"
    )
    kpi3.metric(
        label="Clientes Mensuales Totales", 
        value=f"{int(current_month_data['Clientes Mensuales'])}"
    )
    
    st.markdown("---")
    
    # 2. Gráficos de Ventas y Clientes Mensuales lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolución de Ventas Mensuales")
        fig_ventas = px.bar(
            df_finanzas, 
            x='Mes', 
            y='Ventas ($)',
            text='Ventas ($)',
            color_discrete_sequence=['#1f77b4'],
            template='plotly_white'
        )
        fig_ventas.update_traces(texttemplate='$%{text:.2s}', textposition='outside')
        st.plotly_chart(fig_ventas, use_container_width=True)
        
    with col2:
        st.subheader("Evolución de Clientes Mensuales")
        fig_clientes = px.line(
            df_finanzas, 
            x='Mes', 
            y='Clientes Mensuales',
            markers=True,
            color_discrete_sequence=['#ff7f0e'],
            template='plotly_white'
        )
        st.plotly_chart(fig_clientes, use_container_width=True)
        
    st.markdown("---")
    
    # 3. Procedimientos Más Pedidos
    st.subheader("Top Procedimientos Solicitados")
    col_proc_chart, col_proc_table = st.columns([2, 1])
    
    with col_proc_chart:
        fig_procedimientos = px.pie(
            df_procedimientos.head(5), # Top 5
            names='Procedimiento', 
            values='Cantidad Solicitadas',
            hole=0.4,
            template='plotly_white'
        )
        st.plotly_chart(fig_procedimientos, use_container_width=True)
        
    with col_proc_table:
        st.dataframe(
            df_procedimientos, 
            hide_index=True, 
            use_container_width=True,
            height=300
        )


# ==============================================================================
# PESTAÑA 2: MARKETING Y GESTIÓN
# ==============================================================================
with tab_marketing:
    st.header("Métricas de Marketing y Tareas")
    
    # 1. KPIs de Redes Sociales y Correos
    st.subheader("Alcance e Interacción")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    # Extrayendo valores específicos del dataframe de marketing general
    seguidores_ig = df_marketing.loc[df_marketing['Métrica'] == 'Seguidores Instagram', 'Valor'].values[0]
    seguidores_fb = df_marketing.loc[df_marketing['Métrica'] == 'Seguidores Facebook', 'Valor'].values[0]
    correos_enviados = df_marketing.loc[df_marketing['Métrica'] == 'Correos Enviados (Mes)', 'Valor'].values[0]
    tasa_apertura = df_marketing.loc[df_marketing['Métrica'] == 'Tasa de Apertura Correos (%)', 'Valor'].values[0]
    
    col_kpi1.metric(label="Seguidores Instagram 📸", value=f"{int(seguidores_ig):,}")
    col_kpi2.metric(label="Correos Enviados ✉️", value=f"{int(correos_enviados):,}")
    col_kpi3.metric(label="Tasa de Apertura Correos 📈", value=f"{tasa_apertura:.1f}%")
    
    st.markdown("---")
    
    # 2. Campañas Vigentes
    st.subheader("Campañas de Marketing Activas")
    
    # Definir colores para los estados
    def color_status(val):
        color = 'green' if val == 'Activa' else 'orange' if val == 'En Progreso' else 'red'
        return f'color: {color}'
        
    st.dataframe(
        df_campanas.style.applymap(color_status, subset=['Estado']),
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("---")
    
    # 3. Lista de Tareas (To-Do List)
    st.subheader("Lista de Tareas Pendientes (To-Do List) ✅")
    
    col_tareas1, col_tareas2 = st.columns([2, 1])
    
    with col_tareas1:
        st.dataframe(
            df_tareas,
            hide_index=True,
            use_container_width=True
        )
        
    with col_tareas2:
        st.info("💡 **Tip de Productividad:** Puedes actualizar estas tareas directamente editando la pestaña 'Tareas' en tu archivo Excel. El dashboard reflejará los cambios automáticamente cuando refresques la página.")
        
        tareas_completadas = len(df_tareas[df_tareas['Estado'] == 'Completada'])
        total_tareas = len(df_tareas)
        st.progress(tareas_completadas / total_tareas, text=f"Progreso de Tareas ({tareas_completadas}/{total_tareas})")
