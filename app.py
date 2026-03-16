import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de página ---
st.set_page_config(page_title="Clínica Dental Premium", page_icon="🦷", layout="wide")

# --- ID del Google Sheet ---
SHEET_ID = "1m7st9kE61vHlLMNFGxSiR1IKkRzmhkJ482x17Rsmg20"

def sheet_url(sheet_name):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

def to_float(series):
    return pd.to_numeric(
        series.astype(str).str.replace(',', '.', regex=False).str.strip(),
        errors='coerce'
    )

@st.cache_data(ttl=300)
def load_data():
    try:
        df_finanzas       = pd.read_csv(sheet_url("Finanzas"))
        df_procedimientos = pd.read_csv(sheet_url("Procedimientos"))
        df_marketing      = pd.read_csv(sheet_url("Marketing_General"))
        df_campanas       = pd.read_csv(sheet_url("Campanas"))
        df_tareas         = pd.read_csv(sheet_url("Tareas"))
        df_personal       = pd.read_csv(sheet_url("Personal"))

        for col in ['Ventas ($)', 'Clientes Mensuales', 'Promedio Clientes Semanales', 'Promedio Clientes Diarios']:
            if col in df_finanzas.columns:
                df_finanzas[col] = to_float(df_finanzas[col])

        return df_finanzas, df_procedimientos, df_marketing, df_campanas, df_tareas, df_personal
    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        st.stop()

df_finanzas, df_procedimientos, df_marketing, df_campanas, df_tareas, df_personal = load_data()

# --- Estilos CSS ---
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    padding: 5% 5% 5% 10%;
    border-radius: 12px;
    overflow-wrap: break-word;
}
.stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- Título ---
st.title("🦷 Dashboard · Clínica Dental Premium")
st.markdown("*Panel de control en tiempo real — actualizado desde Google Sheets cada 5 minutos*")
st.markdown("---")

# ---- 4 Tabs ----
tab_fin, tab_mkt, tab_gest, tab_personal = st.tabs([
    "💰 Finanzas", "📣 Marketing", "📋 Gestión", "👥 Personal"
])

# ==============================================================================
# PESTAÑA 1: FINANZAS
# ==============================================================================
with tab_fin:
    st.header("📊 Resumen Financiero y Operativo")

    meses = df_finanzas['Mes'].tolist()
    mes_sel = st.selectbox("Selecciona el mes a detallar:", meses, index=2)
    current = df_finanzas[df_finanzas['Mes'] == mes_sel].iloc[0]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💵 Ventas del Mes", f"${int(current['Ventas ($)']):,}")
    kpi2.metric("👥 Clientes Mensuales", int(current['Clientes Mensuales']))
    kpi3.metric("📅 Prom. Clientes / Semana", f"{float(current['Promedio Clientes Semanales']):.1f}")
    kpi4.metric("📆 Prom. Clientes / Día", f"{float(current['Promedio Clientes Diarios']):.1f}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Ventas Mensuales")
        fig_v = px.bar(df_finanzas, x='Mes', y='Ventas ($)', text='Ventas ($)',
                       color_discrete_sequence=['#6C63FF'], template='plotly_white')
        fig_v.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_v.update_layout(yaxis_title="Ventas ($)", xaxis_title="")
        st.plotly_chart(fig_v, use_container_width=True)

    with col2:
        st.subheader("👤 Evolución de Clientes")
        fig_c = px.line(df_finanzas, x='Mes', y='Clientes Mensuales', markers=True,
                        color_discrete_sequence=['#FF6584'], template='plotly_white')
        st.plotly_chart(fig_c, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Procedimientos Más Solicitados")
    df_procedimientos['Cantidad Solicitadas'] = to_float(df_procedimientos['Cantidad Solicitadas'])
    if 'Precio Promedio ($)' in df_procedimientos.columns:
        df_procedimientos['Precio Promedio ($)'] = to_float(df_procedimientos['Precio Promedio ($)'])

    col_pie, col_tbl = st.columns([2, 1])
    with col_pie:
        fig_p = px.pie(df_procedimientos.head(5), names='Procedimiento', values='Cantidad Solicitadas',
                       hole=0.4, template='plotly_white')
        st.plotly_chart(fig_p, use_container_width=True)
    with col_tbl:
        st.dataframe(df_procedimientos, hide_index=True, use_container_width=True, height=350)


# ==============================================================================
# PESTAÑA 2: MARKETING
# ==============================================================================
with tab_mkt:
    st.header("📣 Marketing y Redes Sociales")

    df_marketing['Valor'] = to_float(df_marketing['Valor'])
    metricas = df_marketing.set_index('Métrica')['Valor'].to_dict()
    keys = list(metricas.keys())
    icons = ["📸", "👑", "✉️", "📈"]
    cols = st.columns(len(keys))
    for i, (k, col) in enumerate(zip(keys, cols)):
        val = metricas[k]
        icon = icons[i] if i < len(icons) else "📊"
        col.metric(f"{icon} {k}", f"{val:,.1f}" if str(val).replace('.', '', 1).isdigit() and '.' in str(val) else f"{int(val):,}")

    st.markdown("---")
    st.subheader("🎯 Campañas de Marketing Activas")
    df_campanas['Inversión ($)'] = to_float(df_campanas['Inversión ($)'])
    df_campanas['Clics/Interacciones'] = to_float(df_campanas['Clics/Interacciones'])

    def color_estado(val):
        if val == 'Activa': return 'color: green; font-weight: bold'
        if val == 'En Preparación': return 'color: orange; font-weight: bold'
        return 'color: red'

    st.dataframe(df_campanas.style.map(color_estado, subset=['Estado']),
                 hide_index=True, use_container_width=True)

    st.markdown("---")
    col_inv, col_clics = st.columns(2)
    with col_inv:
        fig_inv = px.bar(df_campanas, x='Campaña', y='Inversión ($)', color='Plataforma',
                         template='plotly_white', title='Inversión por Campaña')
        st.plotly_chart(fig_inv, use_container_width=True)
    with col_clics:
        fig_clics = px.bar(df_campanas, x='Campaña', y='Clics/Interacciones', color='Estado',
                           template='plotly_white', title='Interacciones por Campaña')
        st.plotly_chart(fig_clics, use_container_width=True)


# ==============================================================================
# PESTAÑA 3: GESTIÓN (TAREAS)
# ==============================================================================
with tab_gest:
    st.header("📋 Lista de Tareas y Gestión Interna")

    col_filtro, _ = st.columns([1, 3])
    with col_filtro:
        estados_disponibles = ['Todos'] + df_tareas['Estado'].unique().tolist()
        filtro = st.selectbox("Filtrar por estado:", estados_disponibles)

    df_tareas_filtrado = df_tareas if filtro == 'Todos' else df_tareas[df_tareas['Estado'] == filtro]

    def color_tarea(val):
        if val == 'Completada': return 'color: green; font-weight: bold'
        if val == 'En Progreso': return 'color: orange; font-weight: bold'
        return 'color: crimson; font-weight: bold'

    st.dataframe(df_tareas_filtrado.style.map(color_tarea, subset=['Estado']),
                 hide_index=True, use_container_width=True, height=400)

    st.markdown("---")
    col_prog, col_info = st.columns([1, 1])
    with col_prog:
        completadas = len(df_tareas[df_tareas['Estado'] == 'Completada'])
        en_progreso = len(df_tareas[df_tareas['Estado'] == 'En Progreso'])
        pendientes  = len(df_tareas[df_tareas['Estado'] == 'Pendiente'])
        total       = len(df_tareas)
        st.progress(completadas / total, text=f"✅ {completadas}/{total} tareas completadas")

        fig_tareas = px.pie(
            values=[completadas, en_progreso, pendientes],
            names=['Completadas', 'En Progreso', 'Pendientes'],
            color_discrete_sequence=['#28a745', '#fd7e14', '#dc3545'],
            hole=0.45, template='plotly_white'
        )
        st.plotly_chart(fig_tareas, use_container_width=True)
    with col_info:
        st.metric("✅ Completadas", completadas)
        st.metric("🔄 En Progreso", en_progreso)
        st.metric("🕐 Pendientes", pendientes)


# ==============================================================================
# PESTAÑA 4: PERSONAL (ORGANIGRAMA)
# ==============================================================================
with tab_personal:
    st.header("👥 Equipo y Organigrama")

    # --- KPIs del equipo ---
    num_dueños    = len(df_personal[df_personal['Área'] == 'Dirección'])
    num_dentistas = len(df_personal[df_personal['Área'] == 'Médica'])
    num_admin     = len(df_personal[df_personal['Área'] == 'Administración'])
    num_recep     = len(df_personal[df_personal['Cargo'].str.contains('Recepcion', case=False, na=False)])

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👑 Dueñas / Directoras", num_dueños)
    k2.metric("🦷 Dentistas", num_dentistas)
    k3.metric("🗂️ Administración", num_admin)
    k4.metric("📞 Recepcionistas", num_recep)

    st.markdown("---")

    col_org, col_tabla = st.columns([3, 2])

    with col_org:
        st.subheader("🏛️ Organigrama de la Clínica")

        # Colores por área para el organigrama Graphviz
        colores_area = {
            'Dirección':           '#6C63FF',
            'Médica':              '#4CAF50',
            'Administración':      '#2196F3',
            'Atención al Cliente': '#FF9800',
            'Operaciones':         '#9E9E9E',
        }

        # Construir el grafo en notación DOT de forma dinámica desde el dataframe
        dot_lines = [
            'digraph orgchart {',
            '  graph [rankdir=TB, bgcolor="#FAFAFA", ranksep=0.9, nodesep=0.6];',
            '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, '
            '        margin="0.25,0.15", penwidth=1.5];',
            '  edge [color="#AAAAAA", penwidth=1.5, arrowsize=0.7];',
        ]

        # Añadir nodos
        for _, row in df_personal.iterrows():
            nombre = row['Nombre'].replace('"', "'")
            cargo  = row['Cargo'].replace('"', "'")
            area   = row['Área']
            color  = colores_area.get(area, '#CCCCCC')
            label  = f"{nombre}\\n{cargo}"
            node_id = nombre.replace(' ', '_').replace('.', '')
            dot_lines.append(
                f'  {node_id} [label="{label}", fillcolor="{color}", fontcolor="white", color="{color}"];'
            )

        # Añadir aristas (relaciones jerárquicas)
        for _, row in df_personal.iterrows():
            jefe = str(row['Reporta a']).strip()
            if jefe and jefe != 'nan':
                id_jefe = jefe.replace(' ', '_').replace('.', '')
                id_hijo = row['Nombre'].replace(' ', '_').replace('.', '')
                dot_lines.append(f'  {id_jefe} -> {id_hijo};')

        dot_lines.append('}')
        dot_source = '\n'.join(dot_lines)

        st.graphviz_chart(dot_source, use_container_width=True)

        # Leyenda de colores por área
        st.markdown("**Leyenda de áreas:**")
        leyenda_cols = st.columns(len(colores_area))
        for i, (area, color) in enumerate(colores_area.items()):
            leyenda_cols[i].markdown(
                f'<span style="background:{color};color:white;padding:3px 10px;border-radius:8px;font-size:12px">{area}</span>',
                unsafe_allow_html=True
            )

    with col_tabla:
        st.subheader("📋 Detalle del Equipo")
        st.dataframe(
            df_personal[['Nombre', 'Cargo', 'Área', 'Función Principal']],
            hide_index=True,
            use_container_width=True,
            height=500
        )


