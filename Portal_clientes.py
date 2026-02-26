import streamlit as st
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Portal de Clientes | Biomedia", page_icon="🚀", layout="centered")

# --- ESTILOS VISUALES (Branding Biomedia) ---
st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    h1 {color: #4A90E2;}
    .stButton>button {width: 100%; border-radius: 5px; background-color: #4A90E2; color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title("Portal de Clientes Biomedia")
st.write("Bienvenido a tu espacio de proyecto. Ingresa tu código de rastreo para ver el estatus en tiempo real.")

# --- CREDENCIALES (Bóveda de Streamlit) ---
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

# --- CAJA DE BÚSQUEDA ---
codigo_input = st.text_input("Código de Proyecto (Ej. r_abc123...):")

if st.button("Buscar mi Proyecto"):
    if codigo_input:
        with st.spinner("Conectando con la bóveda de Biomedia..."):
            
            headers = {
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            
# FILTRO FLEXIBLE: Buscando por la columna "Codigo_Cliente"
            payload = {
                "filter": {
                    "property": "Codigo_Cliente",
                    "rich_text": {
                        "contains": codigo_input.strip() # <--- ¡Cambiamos equals por contains!
                    }
                }
            }
                    }
                }
            }
            
            url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                resultados = data.get("results", [])
                
                if len(resultados) > 0:
                    st.success("¡Proyecto encontrado!")
                    
                    proyecto = resultados[0]["properties"]
                    
                    # --- MAPEO EXACTO DE COLUMNAS SEGÚN TU CAPTURA ---
                    
                    # 1. Extraer Nombre (La API de Notion cambia si es la columna principal 'title' o 'rich_text')
                    try:
                        if "title" in proyecto["Nombre"]:
                            nombre_cliente = proyecto["Nombre"]["title"][0]["text"]["content"]
                        else:
                            nombre_cliente = proyecto["Nombre"]["rich_text"][0]["text"]["content"]
                    except:
                        nombre_cliente = "Cliente VIP"

                    # 2. Extraer Empresa
                    try:
                        if "title" in proyecto["Empresa"]:
                            empresa_cliente = proyecto["Empresa"]["title"][0]["text"]["content"]
                        else:
                            empresa_cliente = proyecto["Empresa"]["rich_text"][0]["text"]["content"]
                    except:
                        empresa_cliente = "Tu Proyecto"
                        
                    # 3. Extraer Status (Asegúrate de tener una columna llamada 'Estado' en Notion)
                    try:
                        estatus = proyecto["Estado"]["status"]["name"] 
                    except:
                        try:
                            # Por si lo tienes como Select en lugar de Status
                            estatus = proyecto["Estado"]["select"]["name"]
                        except:
                            estatus = "En proceso / Por definir"
                        
                    # 4. Extraer Fecha (Esta es la que entra desde Tally)
                    try:
                        fecha_ingreso = proyecto["Fecha"]["date"]["start"]
                    except:
                        fecha_ingreso = "Fecha no registrada"
                        
                    # 5. Extraer link de Drive (Asegúrate de crear una columna tipo URL llamada 'Link Drive' en Notion)
                    try:
                        link_drive = proyecto["Link Drive"]["url"]
                    except:
                        link_drive = None
                    
                    # --- INTERFAZ DE RESULTADOS ---
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
    else:

        st.warning("⚠️ Por favor ingresa tu código.")

