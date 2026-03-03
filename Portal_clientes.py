import streamlit as st
import requests
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal de Clientes | Biomedia", page_icon="logo_png.png", layout="centered")

# --- CREDENCIALES (Bóveda de Streamlit) ---
# Asegúrate de tener estas variables en tus 'Secrets' de Streamlit.
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

# --- INYECCIÓN DE IMAGEN DE FONDO Y ESTILOS ---
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        st.markdown(
            f"""
            <style>
            /* 1. Inyectar la imagen de fondo en toda la app */
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            
            /* 2. Quitar el fondo blanco sólido para que la imagen se vea */
            [data-testid="stAppViewContainer"] {{
                background-color: transparent !important;
            }}
            
            /* 3. Forzar todos los textos principales a NEGRO para contraste en fondo claro */
            [data-testid="stAppViewContainer"] *,
            [data-testid="stHeader"] *,
            [data-testid="stSidebar"] *,
            p, span, label, h1, h2, h3, h4, h5, h6,
            .stMetric, .stSubheader, .stAlert, .stWrite, .stMarkdown {{
                color: #000000 !important;
            }}
            
            /* 4. Título Principal (Azul Marino Profundo para fondo blanco) */
            h1 {{
                color: #1E4D8A !important;
            }}
            
            /* 5. Botón Azul con texto blanco */
            .stButton>button {{
                width: 100%;
                border-radius: 5px;
                background-color: #1E4D8A !important;
                color: #FFFFFF !important;
                border: 1px solid #1E4D8A !important;
            }}
            .stButton>button:hover {{
                background-color: #153A6A !important;
            }}
            
            /* 6. Cristal ahumado sutil detrás del contenido para asegurar lectura */
            .main .block-container {{
                background-color: rgba(255, 255, 255, 0.85); /* Blanco al 85% de transparencia */
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                
                /* 🚀 NUEVO: Empujar el contenido principal hacia abajo 🚀 */
                /* Esto crea espacio para el logo centrado en la imagen de fondo original */
                margin-top: 250px; 
            }}
            
            /* 7. ARREGLAR LA CAJA DE TEXTO (INPUT) */
            /* Forzar fondo blanco y texto negro para el campo de entrada */
            div[data-testid="stTextInput"] input {
                background-color: #FFFFFF !important;
                color: #000000 !important;
                border: 1px solid #1E4D8A !important;
                border-radius: 5px !important;
            }
            
            /* Asegurar que el placeholder sea legible */
            div[data-testid="stTextInput"] input::placeholder {
                color: rgba(0, 0, 0, 0.5) !important;
            }
            
            /* Asegurar que el icono de búsqueda o emoji sea legible (si existe) */
            div[data-testid="stTextInput"] div[data-baseweb="input"] svg {
                color: #000000 !important;
            }

            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("⚠️ No se encontró la imagen de fondo. Asegúrate de subirla a GitHub con el nombre correcto.")

# 🔴 ATENCIÓN: Cambia "fondo_portal.png" por el nombre exacto de tu imagen en GitHub
# Dado que es una plantilla blanca con el logo centrado, moveré el contenido hacia abajo.
set_background("fondo_portal.png") 

# --- INTERFAZ DEL PORTAL ---
# El título principal H1, ahora será azul marino y el texto de abajo será negro.
st.title("🚀 Portal de Clientes Biomedia")
st.write("Bienvenido a tu espacio de proyecto. Ingresa tu código de rastreo para ver el estatus en tiempo real.")

# --- CAJA DE BÚSQUEDA ---
# El label "🔑 Código de Proyecto" ahora será negro gracias al CSS inyectado.
# El input box tendrá fondo blanco y texto negro.
codigo_input = st.text_input("🔑 Código de Proyecto (Ej. r_abc123...):")

if st.button("Buscar mi Proyecto"):
    if codigo_input:
        with st.spinner("Conectando con la bóveda de Biomedia..."):
            
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
                        # Subheader (👤 Frida...) y Texto Informativo serán negros.
                        st.subheader(f"👤 {nombre_cliente} | 🏢 {empresa_cliente}")
                        
                        col1, col2 = st.columns(2)
                        # Metric y Metric Value ahora serán negros.
                        col1.metric("📌 Estatus Actual", estatus)
                        col2.metric("📅 Ingresado el", fecha_ingreso)
                        
                        # Info box tendrá texto negro.
                        st.info("Tus avances se actualizan en tiempo real conforme nuestro equipo avanza en las etapas de tu proyecto.")
                            
                        # El link de Google Drive tendrá icono y texto negro.
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
