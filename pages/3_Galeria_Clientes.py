
import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🧑‍🎨 Galeria de Clientes")

# Imagem padrão (logo)
url_logo_padrao = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"
IMAGEM_PADRAO = Image.open(requests.get(url_logo_padrao, stream=True).raw)

# URL da planilha clientes_status exportada como CSV
url_planilha = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/gviz/tq?tqx=out:csv&sheet=clientes_status"

@st.cache_data
def carregar_dados():
    return pd.read_csv(url_planilha)

df = carregar_dados()

# Preencher nulos
df['nome'] = df['nome'].fillna("Sem Nome")
df['link_foto'] = df['link_foto'].fillna("")

# Filtro por cliente
clientes_unicos = ["Todos"] + sorted(df['nome'].unique().tolist())
cliente_selecionado = st.selectbox("Filtrar por cliente:", clientes_unicos)

if cliente_selecionado != "Todos":
    df = df[df['nome'] == cliente_selecionado]

# Navegação por letra
st.markdown("### 🔤 Navegação por letra")
letras = sorted(set(nome[0].upper() for nome in df['nome'] if nome))
letras_links = [f"[{letra}](#{letra})" for letra in letras]
st.markdown(" | ".join(letras_links))

# Expandir tudo
expandir = st.toggle("📗 Expandir tudo", value=False)

for letra in letras:
    clientes_letra = df[df['nome'].str.upper().str.startswith(letra)]

    if not expandir:
        with st.expander(letra):
            cols = st.columns(4)
            for i, (_, row) in enumerate(clientes_letra.iterrows()):
                with cols[i % 4]:
                    nome_cliente = row['nome']
                    link_foto = row['link_foto']
                    try:
                        if link_foto:
                            imagem = Image.open(requests.get(link_foto, stream=True).raw)
                        else:
                            imagem = IMAGEM_PADRAO
                    except:
                        imagem = IMAGEM_PADRAO
                    st.image(imagem, caption=nome_cliente, use_container_width=True)
    else:
        st.markdown(f"### {letra}")
        cols = st.columns(4)
        for i, (_, row) in enumerate(clientes_letra.iterrows()):
            with cols[i % 4]:
                nome_cliente = row['nome']
                link_foto = row['link_foto']
                try:
                    if link_foto:
                        imagem = Image.open(requests.get(link_foto, stream=True).raw)
                    else:
                        imagem = IMAGEM_PADRAO
                except:
                    imagem = IMAGEM_PADRAO
                st.image(imagem, caption=nome_cliente, use_container_width=True)
