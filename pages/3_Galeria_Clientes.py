
import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Galeria de Clientes", layout="wide")

# Imagem padrão
LOGO_PADRAO = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"

# Simulando carregamento de dados (você pode substituir pela planilha do Google)
df = pd.DataFrame({
    'Cliente': ['3'],
    'Link_Foto': [None]
})

st.title("🧑‍🦱 Galeria de Clientes")
clientes = df['Cliente'].dropna().unique()
cliente_selecionado = st.selectbox("Filtrar por cliente:", options=['Todos'] + sorted(clientes.tolist()))

# Filtro de cliente
if cliente_selecionado != 'Todos':
    df = df[df['Cliente'] == cliente_selecionado]

# Agrupando por inicial
df['Inicial'] = df['Cliente'].str[0].str.upper()
letras = sorted(df['Inicial'].unique())
st.markdown("### 🔤 Navegação por letra")
st.markdown(" | ".join(f"[{letra}](#{letra})" for letra in letras))

# Expandir tudo
if st.button("🟢 Expandir tudo"):
    st.session_state['expandir_tudo'] = True
if st.button("🔴 Recolher tudo"):
    st.session_state['expandir_tudo'] = False

for letra in letras:
    grupo = df[df['Inicial'] == letra]
    with st.expander(f"{letra} ({len(grupo)} cliente{'s' if len(grupo) > 1 else ''})", expanded=st.session_state.get('expandir_tudo', False)):
        for _, row in grupo.iterrows():
            nome_cliente = row['Cliente']
            url_imagem = row['Link_Foto']

            try:
                response = requests.get(url_imagem)
                img = Image.open(BytesIO(response.content))
                st.image(img, caption=str(nome_cliente), use_container_width=True)
            except:
                st.image(LOGO_PADRAO, caption=f"{str(nome_cliente)} (imagem padrão)", use_container_width=True)
