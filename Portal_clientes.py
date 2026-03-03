import streamlit as st
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal de Clientes | Biomedia", page_icon="🚀", layout="centered")

# --- ESTILOS VISUALES (Branding Biomedia) ---
# Modificado para forzar un fondo blanco y textos negros según la restricción del usuario.
st.markdown("""
<style>
/* 1. Forzar fondo blanco en el contenedor principal */
[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
}

/* 2. Forzar todos los textos, etiquetas y métricas a NEGRO */
/* Usamos !important para sobrescribir cualquier tema oscuro que el usuario tenga por defecto */
[data-testid="stAppViewContainer"] *,
[data-testid="stHeader"] *,
[data-testid="stSidebar"] *,
p, span, label, h1, h2, h3, h4, h5, h6,
.stMetric, .stSubheader, .stAlert, .stWrite, .stMarkdown {
    color: #000000 !important;
}

/* 3. Título principal (H1) */
/* He oscurecido el azul original (#4A90E2) a un azul marino (#1E4D8A) 
   para garantizar contraste en fondo blanco. */
h1 {
    color: #1E4D8A !important;
}

/* 4. Botón principal */
/* Mantener fondo azul marino pero asegurar texto accesible */
.stButton>button {
    width: 100%;
    border-radius: 5px;
    background-color: #1E4D8A !important; /* Azul marino oscuro */
    color: #FFFFFF !important; /* Texto blanco DENTRO del botón azul */
    border: 1px solid #1E4D8A !important;
}

.stButton>button:hover {
    background-color: #153A6A !important; /* Azul más oscuro al pasar el mouse */
}

/* 5. Asegurar contraste en Metrics y Alertas (Info, Warning, Error) */
.stMetric * {
    color: #000000 !important;
}

.stAlert * {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Portal de Clientes Biomedia")
st.write("Bienvenido a tu espacio de proyecto. Ingresa tu código de rastreo para ver el estatus en tiempo real.")

# --- CREDENCIALES (Bóveda de Streamlit) ---
# Asegúrate de tener estas variables en tus 'Secrets' de Streamlit.
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

# --- CAJA DE BÚSQUEDA ---
# El label "🔑 Código de Proyecto" ahora será negro gracias al CSS inyectado.
codigo_input = st.text_input("🔑 Código de Proyecto (Ej. r_abc123...):")

if st.button("Buscar mi Proyecto"):
    if codigo_input:
        with st.spinner("Conectando con la bóveda de Biomedia..."):
            
            # Preparamos la conexión con Notion
            headers = {
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            
            # FILTRO FLEXIBLE: Buscando por la columna "Codigo_Cliente"
            # Cambiamos "equals" por "contains" para mayor flexibilidad.
            payload = {
                "filter": {
                    "property": "Codigo_Cliente",
                    "rich_text": {
                        "contains": codigo_input.strip() 
                    }
                }
            }
            
            url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    resultados = data.get("results", [])
                    
                    if len(resultados) > 0:
                        st.success("¡Proyecto encontrado!")
                        
                        proyecto = resultados[0]["properties"]
                        
                        # --- MAPEO EXACTO DE COLUMNAS DE NOTION ---
                        
                        # 1. Extraer Nombre (La API de Notion cambia si es la columna principal 'title' o 'rich_text')
                        try:
                            if "title" in proyecto["Nombre"]:
                                nombre_cliente = proyecto["Nombre"]["title"][0]["text"]["content"]
                            else:
                                nombre_cliente = proyecto["Nombre"]["rich_text"][0]["text"]["content"]
                        except Exception:
                            nombre_cliente = "Cliente VIP"

                        # 2. Extraer Empresa
                        try:
                            if "title" in proyecto["Empresa"]:
                                empresa_cliente = proyecto["Empresa"]["title"][0]["text"]["content"]
                            else:
                                empresa_cliente = proyecto["Empresa"]["rich_text"][0]["text"]["content"]
                        except Exception:
                            empresa_cliente = "Tu Proyecto"
                            
                        # 3. Extraer Status (Asegúrate de tener una columna llamada 'Estado' en Notion)
                        try:
                            estatus = proyecto["Estado"]["status"]["name"] 
                        except Exception:
                            try:
                                # Por si lo tienes como Select en lugar de Status
                                estatus = proyecto["Estado"]["select"]["name"]
                            except Exception:
                                estatus = "En proceso / Por definir"
                            
                        # 4. Extraer Fecha (Esta es la que entra desde Tally)
                        try:
                            fecha_ingreso = proyecto["Fecha"]["date"]["start"]
                        except Exception:
                            fecha_ingreso = "Fecha no registrada"
                            
                        # 5. Extraer link de Drive (Asegúrate de crear una columna tipo URL llamada 'Link Drive' en Notion)
                        try:
                            link_drive = proyecto["Link Drive"]["url"]
                        except Exception:
                            link_drive = None
                        
                        # --- INTERFAZ DE RESULTADOS ---
                        st.divider()
                        st.subheader(f"👤 {nombre_cliente} | 🏢 {empresa_cliente}")
                        
                        col1, col2 = st.columns(2)
                        # Metric y Metric Value ahora serán negros.
                        col1.metric("📌 Estatus Actual", estatus)
                        col2.metric("📅 Ingresado el", fecha_ingreso)
                        
                        # Info/Warning/Error boxes también tendrán texto negro.
                        st.info("Tus avances se actualizan en tiempo real conforme nuestro equipo avanza en las etapas de tu proyecto.")
                            
                        if link_drive:
                            st.markdown(f"### 📂 [Clic aquí para acceder a tu carpeta de Google Drive]({link_drive})")
                        else:
                            st.warning("⏳ Tu carpeta de archivos seguros se habilitará en la siguiente etapa operativa.")
                            
                    else:
                        st.error("❌ Código no encontrado. Por favor, verifica que no haya espacios extra.")
                else:
                    # Diagnóstico detallado si la API falla
                    st.error(f"Error {response.status_code}: Notion dice -> {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Fallo de conexión con el servidor: {e}")
    else:
        st.warning("⚠️ Por favor ingresa tu código.")
