import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Galeria de Clientes", layout="wide")

# URL imagem padrão
LOGO_PADRAO = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"

# URL da planilha oficial
url_planilha = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/export?format=csv&gid=1218942877"  # aba clientes_status

@st.cache_data
def carregar_dados():
    df = pd.read_csv(url_planilha)
    df['Foto'] = df['Foto'].astype(str)  # força tudo para string
    df['Cliente'] = df['Cliente'].astype(str)
    return df

def carregar_imagem(url):
    try:
        response = requests.get(url, timeout=5)
        return Image.open(BytesIO(response.content))
    except:
        return None

df = carregar_dados()
df = df[df['Status'] == 'Ativo']  # exibe só clientes ativos

st.title("🧑‍🦱 Galeria de Clientes")
clientes = df['Cliente'].dropna().unique()
cliente_selecionado = st.selectbox("Filtrar por cliente:", options=['Todos'] + sorted(clientes.tolist()))

if cliente_selecionado != 'Todos':
    df = df[df['Cliente'] == cliente_selecionado]

df['Inicial'] = df['Cliente'].str[0].str.upper()
letras = sorted(df['Inicial'].unique())
st.markdown("### 🔤 Navegação por letra")
st.markdown(" | ".join(f"[{letra}](#{letra})" for letra in letras))

if st.button("🟢 Expandir tudo"):
    st.session_state['expandir_tudo'] = True
if st.button("🔴 Recolher tudo"):
    st.session_state['expandir_tudo'] = False

for letra in letras:
    grupo = df[df['Inicial'] == letra]
    with st.expander(f"{letra} ({len(grupo)} cliente{'s' if len(grupo) > 1 else ''})", expanded=st.session_state.get('expandir_tudo', False)):
        for _, row in grupo.iterrows():
            nome_cliente = row['Cliente']
            url_foto = row['Foto'].strip()

            # Validação do link
            imagem = carregar_imagem(url_foto) if url_foto.startswith("http") else None
            if imagem:
                st.image(imagem, caption=nome_cliente, use_container_width=True)
            else:
                imagem_padrao = carregar_imagem(LOGO_PADRAO)
                st.image(imagem_padrao, caption=f"{nome_cliente} (imagem padrão)", use_container_width=True)
