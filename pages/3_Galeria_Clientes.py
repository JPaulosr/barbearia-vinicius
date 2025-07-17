import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Galeria de Clientes", layout="wide")

# URL da imagem padrão (logo do salão)
LOGO_PADRAO = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"

# Dados simulados
df = pd.DataFrame({
    'Cliente': ['3'],
    'Link_Foto': [None]
})

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

# Função para carregar imagem a partir da URL
def carregar_imagem(url):
    try:
        response = requests.get(url, timeout=5)
        return Image.open(BytesIO(response.content))
    except Exception as e:
        return None

for letra in letras:
    grupo = df[df['Inicial'] == letra]
    with st.expander(f"{letra} ({len(grupo)} cliente{'s' if len(grupo) > 1 else ''})", expanded=st.session_state.get('expandir_tudo', False)):
        for _, row in grupo.iterrows():
            nome_cliente = row['Cliente']
            url_imagem = str(row.get('Link_Foto', '') or '')

            # Tenta carregar imagem do cliente
            imagem = carregar_imagem(url_imagem) if url_imagem.startswith("http") else None

            if imagem:
                st.image(imagem, caption=str(nome_cliente), use_container_width=True)
            else:
                imagem_padrao = carregar_imagem(LOGO_PADRAO)
                st.image(imagem_padrao, caption=f"{str(nome_cliente)} (imagem padrão)", use_container_width=True)
