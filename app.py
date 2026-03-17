import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time

# --- Configuración de página ---
st.set_page_config(page_title="Clínica Dental Premium", page_icon="🦷", layout="wide")

# ID por defecto para nuevos usuarios
DEFAULT_SHEET_ID = "1m7st9kE61vHlLMNFGxSiR1IKkRzmhkJ482x17Rsmg20"

# --- CONFIGURACIÓN DE USUARIOS (Simulada para este ejemplo) ---
# En una app real, esto iría a una base de datos (Supabase/Firebase)
if 'user_db' not in st.session_state:
    st.session_state['user_db'] = {
        'usernames': {
            'admin': {
                'email': 'admin@clinica.com',
                'name': 'Administrador',
                'password': 'js$12$Hk.vO6ZfXvO6ZfXvO6ZfX.vO6ZfXvO6ZfXvO6ZfXvO6ZfX', # '123' hashed (ejemplo)
                'sheet_id': '1m7st9kE61vHlLMNFGxSiR1IKkRzmhkJ482x17Rsmg20',
                'first_login': False
            }
        }
    }

# --- LÓGICA DE AUTENTICACIÓN ---
authenticator = stauth.Authenticate(
    st.session_state['user_db'],
    'dental_dashboard_cookie',
    'auth_key',
    cookie_expiry_days=30
)

def send_email(to_email, subject, body):
    """Envía un correo real usando SMTP y Streamlit Secrets."""
    import smtplib
    from email.mime.text import MIMEText
    
    try:
        # Validar si existen los secretos antes de intentar enviar
        if "emails" not in st.secrets:
            st.info("💡 **Configuración requerida:** Para que los correos lleguen, debes añadir tus claves de SMTP en los 'Secrets' de Streamlit Cloud.")
            return False
            
        smtp_user = st.secrets["emails"]["smtp_user"]
        smtp_pass = st.secrets["emails"]["smtp_pass"]
        smtp_server = st.secrets.get("emails", {}).get("smtp_server", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("emails", {}).get("smtp_port", 587))

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        st.warning(f"No se pudo enviar el correo real: {e}")
        st.info("💡 Para activar correos reales, configura 'emails.smtp_user' y 'emails.smtp_pass' en los Secrets de Streamlit.")
        return False

if not st.session_state.get("authentication_status"):
    # Mostrar Login / Registro en el cuerpo principal si no está autenticado
    login_tab, register_tab = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
    
    with login_tab:
        authenticator.login(location='main')
        st.markdown("---")
        if st.button("🔵 Entrar con Google (Demo)"):
            st.info("Configura 'auth.google' en Secrets para habilitar Google Login real.")

    with register_tab:
        try:
            # register_user devuelve True si los datos son válidos y se añadieron al dict
            if authenticator.register_user(location='main', pre_authorized=None):
                st.success('¡Registro exitoso! 📧 Intentando enviar correo de bienvenida...')
                
                # Obtener el último usuario registrado (el que acabamos de crear)
                # st-authenticator lo añade automáticamente a st.session_state['user_db']
                new_username = list(st.session_state['user_db']['usernames'].keys())[-1]
                user_info = st.session_state['user_db']['usernames'][new_username]
                
                # Personalizar los campos extra para nuestro dashboard
                user_info['sheet_id'] = DEFAULT_SHEET_ID
                user_info['first_login'] = True
                
                # Enviar correo real si hay secretos configurados
                enviado = send_email(
                    user_info['email'],
                    "Bienvenido a tu Dashboard Dental Premium",
                    f"Hola {user_info['name']},\n\nTu cuenta ha sido creada con éxito. Ya puedes entrar y configurar tu Google Sheet.\n\nSaludos,\nEquipo Antigravity"
                )
                if enviado:
                    st.success("Correo de confirmación enviado. ¡Ya puedes iniciar sesión!")
                else:
                    st.info("Usuario creado, pero los correos reales están desactivados (falta configurar SMTP en Secrets).")
                    
        except Exception as e:
            st.error(f"Error en el registro: {e}")

if not st.session_state.get("authentication_status"):
    st.stop()

# --- ID del Google Sheet del Usuario ---
user_data = st.session_state['user_db']['usernames'].get(st.session_state['username'], {})
SHEET_ID = user_data.get('sheet_id', "1m7st9kE61vHlLMNFGxSiR1IKkRzmhkJ482x17Rsmg20")
is_first_login = user_data.get('first_login', True)

# --- Tutorial Inicial ---
if is_first_login:
    st.balloons()
    st.success(f"¡Bienvenido {st.session_state['name']}! 👋")
    with st.expander("🚀 Tutorial Rápido: Cómo configurar tus Dashboard", expanded=True):
        st.markdown("""
        ### ¡Bienvenido a tu plataforma de gestión! 🦷
        Sigue estos pasos para ver tus propios datos:
        
        1. **Prepara tu Google Sheet**: Si no tienes una, [haz clic aquí para copiar nuestra plantilla](https://docs.google.com/spreadsheets/d/1m7st9kE61vHlLMNFGxSiR1IKkRzmhkJ482x17Rsmg20/copy).
        2. **Comparte la Hoja**: En Google, ve a 'Compartir' > 'Cualquier persona con el enlace' > 'Lector'.
        3. **Configura el Dash**: Ve a la pestaña **⚙️ Configuración** a la izquierda y pega tu enlace.
        4. **¡Listo!**: Los gráficos se generarán automáticamente con tu información.
        """)
        if st.button("Entendido, ¡empecemos!"):
            st.session_state['user_db']['usernames'][st.session_state['username']]['first_login'] = False
            st.rerun()

# --- Configuración en Sidebar ---
st.sidebar.title("⚙️ Configuración")
st.sidebar.markdown("Personaliza tu fuente de datos.")

sheet_input = st.sidebar.text_input(
    "Enlace de Google Sheet:",
    value=f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
    help="Asegúrate que la hoja sea pública"
)

# Función para extraer el ID del enlace
def extract_sheet_id(url):
    if not url or "spreadsheets/d/" not in url:
        return SHEET_ID
    try:
        return url.split("/d/")[1].split("/")[0]
    except:
        return SHEET_ID

NEW_SHEET_ID = extract_sheet_id(sheet_input)
if NEW_SHEET_ID != SHEET_ID:
    st.session_state['user_db']['usernames'][st.session_state['username']]['sheet_id'] = NEW_SHEET_ID
    st.rerun() # Recargar con los nuevos datos

def sheet_url(sheet_name, sheet_id):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

def to_float(series):
    """Convierte una serie a float manejando formatos regionales (miles con punto, decimal con coma)."""
    # 1. Convertir a string y limpiar espacios
    s = series.astype(str).str.strip()
    
    # 2. Si hay múltiples puntos y una coma, o puntos en posiciones de miles:
    # Una técnica común es quitar TODOS los puntos y convertir la coma en punto.
    # Pero para ser más robustos: solo quitamos el punto si hay coma O si hay más de un punto.
    def clean_number(val):
        if not val or val.lower() == 'nan':
            return '0'
        # Si tiene comas y puntos, el punto es miles
        if ',' in val and '.' in val:
            val = val.replace('.', '')
        # Si tiene múltiples puntos, son miles
        elif val.count('.') > 1:
            val = val.replace('.', '')
        # Finalmente, la coma siempre es decimal en este contexto
        return val.replace(',', '.')

    s = s.apply(clean_number)
    return pd.to_numeric(s, errors='coerce')

def safe_int(val, default=0):
    """Convierte a int de forma segura, retorna default si es NaN o inválido."""
    try:
        import math
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return default
        return int(val)
    except (ValueError, TypeError):
        return default

def safe_float(val, default=0.0):
    """Convierte a float de forma segura, retorna default si es NaN o inválido."""
    try:
        import math
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return default
        return float(val)
    except (ValueError, TypeError):
        return default

@st.cache_data(ttl=300)
def load_data(sid):
    try:
        df_finanzas       = pd.read_csv(sheet_url("Finanzas", sid))
        df_procedimientos = pd.read_csv(sheet_url("Procedimientos", sid))
        df_marketing      = pd.read_csv(sheet_url("Marketing_General", sid))
        df_campanas       = pd.read_csv(sheet_url("Campanas", sid))
        df_tareas         = pd.read_csv(sheet_url("Tareas", sid))
        df_personal       = pd.read_csv(sheet_url("Personal", sid))

        for col in ['Ventas ($)', 'Clientes Mensuales', 'Promedio Clientes Semanales', 'Promedio Clientes Diarios']:
            if col in df_finanzas.columns:
                df_finanzas[col] = to_float(df_finanzas[col])
        
        # Limpiar espacios en la columna Mes para evitar errores de filtrado
        if 'Mes' in df_finanzas.columns:
            df_finanzas['Mes'] = df_finanzas['Mes'].astype(str).str.strip()

        return df_finanzas, df_procedimientos, df_marketing, df_campanas, df_tareas, df_personal
    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        st.info("💡 Asegúrate de que las hojas tengan los nombres correctos y que el enlace sea público.")
        st.stop()

df_finanzas, df_procedimientos, df_marketing, df_campanas, df_tareas, df_personal = load_data(SHEET_ID)

# Ayuda en el sidebar
st.sidebar.markdown("---")
with st.sidebar.expander("❓ ¿Cómo usar mi propia hoja?"):
    st.markdown("""
    1. Crea un **Copia** de la plantilla.
    2. En Google Sheets, ve a **Compartir** > **Cualquier persona con el enlace** > **Lector**.
    3. Copia el enlace de la barra de direcciones.
    4. Pégalo arriba en el campo de configuración.
    """)

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
    
    fila = df_finanzas[df_finanzas['Mes'] == mes_sel]
    if fila.empty:
        st.warning(f"No se encontraron datos para el mes: '{mes_sel}'. Verifica el Google Sheet.")
    else:
        current = fila.iloc[0]

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("💵 Ventas del Mes", f"${safe_int(current['Ventas ($)']):,}")
        kpi2.metric("👥 Clientes Mensuales", safe_int(current['Clientes Mensuales']))
        kpi3.metric("📅 Prom. Clientes / Semana", f"{safe_float(current['Promedio Clientes Semanales']):.1f}")
        kpi4.metric("📆 Prom. Clientes / Día", f"{safe_float(current['Promedio Clientes Diarios']):.1f}")

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
        # Mostramos como float si tiene decimales significativos, sino como entero seguro
        if pd.notnull(val) and val % 1 != 0:
            col.metric(f"{icon} {k}", f"{safe_float(val):,.1f}")
        else:
            col.metric(f"{icon} {k}", f"{safe_int(val):,}")

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
        total = len(df_tareas)
        
        if total > 0:
            st.progress(completadas / total, text=f"✅ {completadas}/{total} tareas completadas")

            fig_tareas = px.pie(
                values=[completadas, en_progreso, pendientes],
                names=['Completadas', 'En Progreso', 'Pendientes'],
                color_discrete_sequence=['#28a745', '#fd7e14', '#dc3545'],
                hole=0.45, template='plotly_white'
            )
            st.plotly_chart(fig_tareas, use_container_width=True)
        else:
            st.info("No hay tareas registradas en la lista.")
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

        # Construir el grafo en notación DOT usando índices numéricos como IDs
        # Esto evita problemas con tildes, puntos y espacios en los nombres.
        dot_lines = [
            'digraph orgchart {',
            '  graph [rankdir=TB, bgcolor="#FAFAFA", ranksep=1.0, nodesep=0.7];',
            '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, '
            '        margin="0.3,0.2", penwidth=1.5];',
            '  edge [color="#AAAAAA", penwidth=1.5, arrowsize=0.7];',
        ]

        # Crear lookup nombre (tal como está en la hoja) -> índice numérico
        nombre_to_id = {
            str(r['Nombre']).strip(): idx
            for idx, r in df_personal.iterrows()
        }

        # Añadir nodos usando n{idx} como ID interno seguro
        for idx, row in df_personal.iterrows():
            nombre = str(row['Nombre']).strip().replace('"', "'")
            cargo  = str(row['Cargo']).strip().replace('"', "'")
            area   = str(row['Área']).strip()
            color  = colores_area.get(area, '#CCCCCC')
            label  = f"{nombre}\\n{cargo}"
            dot_lines.append(
                f'  n{idx} [label="{label}", fillcolor="{color}", fontcolor="white", color="{color}"];'
            )

        # Añadir aristas usando los índices numéricos (robustos a cualquier nombre)
        for idx, row in df_personal.iterrows():
            jefe = str(row['Reporta a']).strip()
            if jefe and jefe.lower() not in ('nan', ''):
                id_jefe = nombre_to_id.get(jefe)
                if id_jefe is not None:
                    dot_lines.append(f'  n{id_jefe} -> n{idx};')

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


