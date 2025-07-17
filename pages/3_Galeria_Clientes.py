
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🧑‍🎨 Galeria de Clientes")

# Função de carregamento dos dados (exemplo simplificado)
@st.cache_data
def carregar_dados():
    url_planilha = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/export?format=csv&id=1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE&gid=2133461841"
    return pd.read_csv(url_planilha)

df = carregar_dados()

# URL da imagem padrão no Cloudinary
IMAGEM_PADRAO_URL = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"

# Filtro por nome
nome_filtro = st.selectbox("Filtrar por cliente:", options=["Todos"] + sorted(df["Cliente"].dropna().unique().tolist()))
df_filtrado = df if nome_filtro == "Todos" else df[df["Cliente"] == nome_filtro]

# Navegação por letra inicial
st.markdown("#### 🔤 Navegação por letra")
import string
letras = list("3" + string.ascii_uppercase + "Á")
selecionada = st.selectbox("Letra", letras)
st.markdown("---")
st.markdown(f"### {selecionada}")

# Filtrar por letra
df_letra = df_filtrado[df_filtrado["Cliente"].str.upper().str.startswith(selecionada)]

# Mostrar galeria
cols = st.columns(4)
for i, (_, row) in enumerate(df_letra.iterrows()):
    with cols[i % 4]:
        nome = row["Cliente"]
        imagem = row["Foto"]
        try:
            st.image(imagem, caption=nome, use_container_width=True)
        except:
            st.image(IMAGEM_PADRAO_URL, caption=nome, use_container_width=True)
