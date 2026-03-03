import streamlit as st
import requests
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal de Clientes | Biomedia", page_icon="logo_png.png", layout="centered")

# --- CREDENCIALES (Bóveda de Streamlit) ---
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
            
            /* 4. Título Principal */
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
                
                /* 🚀 Empujar el contenido principal hacia abajo para no tapar tu logo 🚀 */
                margin-top: 250px; 
            }}
            
            /* 7. ARREGLAR LA CAJA DE TEXTO (INPUT) */
            /* ¡CORREGIDO: LLAVES DOBLES PARA EVITAR EL NAMEERROR! */
            div[data-testid="stTextInput"] input {{
                background-color: #FFFFFF !important;
                color: #000000 !important;
                border: 1px solid #1E4D8A !important;
                border-radius: 5px !important;
            }}
            
            /* Asegurar que el placeholder sea legible */
            div[data-testid="stTextInput"] input::placeholder {{
                color: rgba(0, 0, 0, 0.5) !important;
            }}
            
            /* Asegurar que el icono de búsqueda o emoji sea legible (si existe) */
            div[data-testid="stTextInput"] div[data-baseweb="input"] svg {{
                color: #000000 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("⚠️ No se encontró la imagen de fondo. Asegúrate de subirla a GitHub con el nombre correcto.")

# 🔴 ATENCIÓN: Asegúrate de que el nombre coincida con tu imagen
set_background("fondo_portal.png") 

# --- INTERFAZ DEL PORTAL ---
st.title("🚀 Portal de Clientes Biomedia")
st.write("Bienvenido a tu espacio de proyecto. Ingresa tu código de rastreo para ver el estatus en tiempo real.")

# --- CAJA DE BÚSQUEDA ---
codigo_input = st.text_input("🔑 Código de Proyecto (Ej. r_abc123...):")

if st.button("Buscar mi Proyecto"):
    if codigo_input:
        with st.spinner("Conectando con la bóveda de Biomedia..."):
            
            headers = {
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            
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
                        
                        try:
                            if "title" in proyecto["Nombre"]:
                                nombre_cliente = proyecto["Nombre"]["title"][0]["text"]["content"]
                            else:
                                nombre_cliente = proyecto["Nombre"]["rich_text"][0]["text"]["content"]
                        except Exception:
                            nombre_cliente = "Cliente VIP"

                        try:
                            if "title" in proyecto["Empresa"]:
                                empresa_cliente = proyecto["Empresa"]["title"][0]["text"]["content"]
                            else:
                                empresa_cliente = proyecto["Empresa"]["rich_text"][0]["text"]["content"]
                        except Exception:
                            empresa_cliente = "Tu Proyecto"
                            
                        try:
                            estatus = proyecto["Estado"]["status"]["name"] 
                        except Exception:
                            try:
                                estatus = proyecto["Estado"]["select"]["name"]
                            except Exception:
                                estatus = "En proceso / Por definir"
                            
                        try:
                            fecha_ingreso = proyecto["Fecha"]["date"]["start"]
                        except Exception:
                            fecha_ingreso = "Fecha no registrada"
                            
                        try:
                            link_drive = proyecto["Link Drive"]["url"]
                        except Exception:
                            link_drive = None
                        
                        st.divider()
                        st.subheader(f"👤 {nombre_cliente} | 🏢 {empresa_cliente}")
                        
                        col1, col2 = st.columns(2)
                        col1.metric("📌 Estatus Actual", estatus)
                        col2.metric("📅 Ingresado el", fecha_ingreso)
                        
                        st.info("Tus avances se actualizan en tiempo real conforme nuestro equipo avanza en las etapas de tu proyecto.")
                            
                        if link_drive:
                            st.markdown(f"### 📂 [Clic aquí para acceder a tu carpeta de Google Drive]({link_drive})")
                        else:
                            st.warning("⏳ Tu carpeta de archivos seguros se habilitará en la siguiente etapa operativa.")
                            
                    else:
                        st.error("❌ Código no encontrado. Por favor, verifica que no haya espacios extra.")
                else:
                    st.error(f"Error {response.status_code}: Notion dice -> {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Fallo de conexión con el servidor: {e}")
    else:
        st.warning("⚠️ Por favor ingresa tu código.")
