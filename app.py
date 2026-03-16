import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de página ---
st.set_page_config(page_title="Clínica Premium Dashboard", page_icon="💎", layout="wide")

# --- ID del Google Sheet ---
SHEET_ID = "1m7st9kE61vHlLMNFGxSiR1IKkRzmhkJ482x17Rsmg20"

def sheet_url(sheet_name):
    """Genera la URL de exportación CSV para cada hoja por nombre."""
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=300)  # Actualiza cada 5 minutos
def load_data():
    try:
        df_finanzas       = pd.read_csv(sheet_url("Finanzas"))
        df_procedimientos = pd.read_csv(sheet_url("Procedimientos"))
        df_marketing      = pd.read_csv(sheet_url("Marketing_General"))
        df_campanas       = pd.read_csv(sheet_url("Campanas"))
        df_tareas         = pd.read_csv(sheet_url("Tareas"))
        return df_finanzas, df_procedimientos, df_marketing, df_campanas, df_tareas
    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        st.stop()

df_finanzas, df_procedimientos, df_marketing, df_campanas, df_tareas = load_data()

# --- Estilos CSS personalizados ---
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    padding: 5% 5% 5% 10%;
    border-radius: 12px;
    color: #31333F;
    overflow-wrap: break-word;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --- Título ---
st.title("💎 Dashboard Clínica Premium")
st.markdown("*Panel de control en tiempo real — datos actualizados desde Google Sheets*")
st.markdown("---")

# --- Tabs ---
tab_finanzas, tab_marketing = st.tabs(["💰 Finanzas y Operaciones", "🚀 Marketing y Gestión"])

# ==============================================================================
# PESTAÑA 1: FINANZAS Y OPERACIONES
# ==============================================================================
with tab_finanzas:
    st.header("📊 Resumen Financiero")

    # Asegurar tipos correctos
    df_finanzas['Ventas ($)'] = pd.to_numeric(df_finanzas['Ventas ($)'], errors='coerce')
    df_finanzas['Clientes Mensuales'] = pd.to_numeric(df_finanzas['Clientes Mensuales'], errors='coerce')

    # Selección de mes actual (usamos Marzo como referencia)
    meses = df_finanzas['Mes'].tolist()
    mes_sel = st.selectbox("Selecciona el mes a detallar:", meses, index=2)
    current = df_finanzas[df_finanzas['Mes'] == mes_sel].iloc[0]

    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💵 Ventas del Mes", f"${int(current['Ventas ($)']):,}")
    kpi2.metric("👥 Clientes Mensuales", int(current['Clientes Mensuales']))
    kpi3.metric("📅 Prom. Clientes / Semana", f"{current['Promedio Clientes Semanales']:.1f}")
    kpi4.metric("📆 Prom. Clientes / Día", f"{current['Promedio Clientes Diarios']:.1f}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Ventas Mensuales")
        fig_v = px.bar(
            df_finanzas, x='Mes', y='Ventas ($)',
            text='Ventas ($)',
            color_discrete_sequence=['#6C63FF'],
            template='plotly_white'
        )
        fig_v.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_v.update_layout(yaxis_title="Ventas ($)", xaxis_title="")
        st.plotly_chart(fig_v, use_container_width=True)

    with col2:
        st.subheader("👤 Evolución de Clientes")
        fig_c = px.line(
            df_finanzas, x='Mes', y='Clientes Mensuales',
            markers=True,
            color_discrete_sequence=['#FF6584'],
            template='plotly_white'
        )
        st.plotly_chart(fig_c, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Procedimientos Más Solicitados")

    df_procedimientos['Cantidad Solicitadas'] = pd.to_numeric(df_procedimientos['Cantidad Solicitadas'], errors='coerce')
    if 'Precio Promedio ($)' in df_procedimientos.columns:
        df_procedimientos['Precio Promedio ($)'] = pd.to_numeric(df_procedimientos['Precio Promedio ($)'], errors='coerce')

    col_pie, col_tbl = st.columns([2, 1])
    with col_pie:
        fig_p = px.pie(
            df_procedimientos.head(5),
            names='Procedimiento', values='Cantidad Solicitadas',
            hole=0.4, template='plotly_white'
        )
        st.plotly_chart(fig_p, use_container_width=True)
    with col_tbl:
        st.dataframe(df_procedimientos, hide_index=True, use_container_width=True, height=350)


# ==============================================================================
# PESTAÑA 2: MARKETING Y GESTIÓN
# ==============================================================================
with tab_marketing:
    st.header("📣 Marketing y Gestión")

    # KPIs Marketing
    df_marketing['Valor'] = pd.to_numeric(df_marketing['Valor'], errors='coerce')
    metricas = df_marketing.set_index('Métrica')['Valor'].to_dict()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    keys = list(metricas.keys())
    cols = [col_m1, col_m2, col_m3, col_m4]
    icons = ["📸", "👑", "✉️", "📈"]
    for i, (k, col) in enumerate(zip(keys, cols)):
        val = metricas[k]
        icon = icons[i] if i < len(icons) else "📊"
        col.metric(f"{icon} {k}", f"{val:,.1f}" if isinstance(val, float) else f"{int(val):,}")

    st.markdown("---")

    col_camp, col_todo = st.columns(2)

    with col_camp:
        st.subheader("🎯 Campañas Activas")
        df_campanas['Inversión ($)'] = pd.to_numeric(df_campanas['Inversión ($)'], errors='coerce')
        df_campanas['Clics/Interacciones'] = pd.to_numeric(df_campanas['Clics/Interacciones'], errors='coerce')

        def color_estado(val):
            if val == 'Activa':
                return 'color: green; font-weight: bold'
            elif val == 'En Preparación':
                return 'color: orange; font-weight: bold'
            return 'color: red'
        st.dataframe(
            df_campanas.style.map(color_estado, subset=['Estado']),
            hide_index=True, use_container_width=True
        )

    with col_todo:
        st.subheader("✅ Lista de Tareas")

        def color_tarea(val):
            if val == 'Completada':
                return 'color: green'
            elif val == 'En Progreso':
                return 'color: orange'
            return 'color: red'

        st.dataframe(
            df_tareas.style.map(color_tarea, subset=['Estado']),
            hide_index=True, use_container_width=True
        )
        completadas = len(df_tareas[df_tareas['Estado'] == 'Completada'])
        total = len(df_tareas)
        st.progress(completadas / total, text=f"Progreso global: {completadas}/{total} tareas completadas")
