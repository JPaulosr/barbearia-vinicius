import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Galeria de Clientes", layout="wide")

LOGO_PADRAO = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"

# Exemplo de dados simulados
df = pd.DataFrame({
    'Cliente': ['3'],
    'Link_Foto': [None]  # ou tente com 'https://...' para testar com imagem real
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

for letra in letras:
    grupo = df[df['Inicial'] == letra]
    with st.expander(f"{letra} ({len(grupo)} cliente{'s' if len(grupo) > 1 else ''})", expanded=st.session_state.get('expandir_tudo', False)):
        for _, row in grupo.iterrows():
            nome_cliente = row['Cliente']
            url_imagem = row.get('Link_Foto', '')

            # DEBUG
            st.write(f"Cliente: {nome_cliente} | URL: {url_imagem}")

            if isinstance(url_imagem, str) and url_imagem.startswith("http"):
                try:
                    response = requests.get(url_imagem, timeout=5)
                    img = Image.open(BytesIO(response.content))
                    st.image(img, caption=str(nome_cliente), use_container_width=True)
                except Exception as e:
                    st.warning(f"Erro ao carregar imagem de {nome_cliente}. Usando imagem padrão.")
                    st.image(LOGO_PADRAO, caption=f"{str(nome_cliente)} (imagem padrão)", use_container_width=True)
            else:
                st.image(LOGO_PADRAO, caption=f"{str(nome_cliente)} (imagem padrão)", use_container_width=True)
