import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>🧑‍🎨 Galeria de Clientes</h1>", unsafe_allow_html=True)

# Função para carregar imagem via URL
def carregar_imagem(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        return None

# Função para verificar se a URL é válida
def imagem_valida(url):
    if not url or str(url).strip().lower() in ["", "nan"]:
        return False
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

# URL da imagem padrão do salão
imagem_padrao_url = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"
imagem_padrao = carregar_imagem(imagem_padrao_url)

# Carregar planilha
@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/gviz/tq?tqx=out:csv&sheet=clientes_status"
    return pd.read_csv(url)

df = carregar_dados()

# Filtro de clientes
clientes = sorted(df["Cliente"].dropna().unique())
filtro_cliente = st.selectbox("Filtrar por cliente:", ["Todos"] + clientes)

if filtro_cliente != "Todos":
    df = df[df["Cliente"] == filtro_cliente]

# Navegação por letra
letras = sorted(set(str(nome)[0].upper() for nome in df["Cliente"] if isinstance(nome, str)))
letras_html = " ".join(f"<a href='#{letra}'>{letra}</a>" for letra in letras)
st.markdown("### 🔤 Navegação por letra", unsafe_allow_html=True)
st.markdown(letras_html, unsafe_allow_html=True)

# Botões de controle
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 Expandir tudo"):
        st.session_state.expandir = True
with col2:
    if st.button("🔴 Recolher tudo"):
        st.session_state.expandir = False

st.markdown("---")

# Agrupamento por letra
clientes_ordenados = df.sort_values("Cliente")

for letra in letras:
    grupo = clientes_ordenados[clientes_ordenados["Cliente"].str.upper().str.startswith(letra)]

    if grupo.empty:
        continue

    with st.container():
        st.markdown(f"<h3 id='{letra}'>{letra}</h3>", unsafe_allow_html=True)

        colunas = st.columns(4)
        idx = 0

        for _, row in grupo.iterrows():
            nome_cliente = row["Cliente"]
            url_foto = str(row.get("Foto", "")).strip()

            # Carrega imagem válida ou padrão
            imagem = carregar_imagem(url_foto) if imagem_valida(url_foto) else imagem_padrao

            with colunas[idx % 4]:
                st.image(imagem, caption=nome_cliente, use_container_width=True)

            idx += 1
