import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>🧑‍🎨 Galeria de Clientes</h1>", unsafe_allow_html=True)

# Função robusta para carregar imagem
def carregar_imagem(url):
    try:
        if not url or pd.isna(url):
            return None
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        return None
    return None

# URL da imagem padrão do salão
URL_IMAGEM_PADRAO = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"
IMAGEM_PADRAO = carregar_imagem(URL_IMAGEM_PADRAO)

# Carregamento da planilha
@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/gviz/tq?tqx=out:csv&sheet=clientes_status"
    return pd.read_csv(url)

df = carregar_dados()

# Filtro de cliente
clientes_unicos = sorted(df["Cliente"].dropna().unique())
cliente_filtro = st.selectbox("Filtrar por cliente:", ["Todos"] + clientes_unicos)

if cliente_filtro != "Todos":
    df = df[df["Cliente"] == cliente_filtro]

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

# Exibição das imagens agrupadas por letra
df = df.sort_values("Cliente")
for letra in letras:
    grupo = df[df["Cliente"].str.upper().str.startswith(letra)]
    if grupo.empty:
        continue

    st.markdown(f"<h3 id='{letra}'>{letra}</h3>", unsafe_allow_html=True)
    colunas = st.columns(4)
    idx = 0

    for _, row in grupo.iterrows():
        nome = row["Cliente"]
        link_imagem = str(row.get("Foto", "")).strip()
        imagem_cliente = carregar_imagem(link_imagem)

        # Proteção final — sempre exibe algo
        if imagem_cliente is None:
            imagem_cliente = IMAGEM_PADRAO

        with colunas[idx % 4]:
            st.image(imagem_cliente, caption=nome, use_container_width=True)

        idx += 1
