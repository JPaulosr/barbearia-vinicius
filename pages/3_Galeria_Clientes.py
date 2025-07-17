
import streamlit as st
from PIL import Image as PILImage
import requests
from io import BytesIO

# Simulação dos dados
clientes = [
    {"nome": "abel", "foto": "https://res.cloudinary.com/db8ipmete/image/upload/v1752455594/Fotos%20clientes/abel.png"},
    {"nome": "cliente sem foto", "foto": ""},
    {"nome": "cliente com erro", "foto": "https://url_invalida.com/foto.png"},
]

# Carrega imagem padrão
IMAGEM_PADRAO = PILImage.open("logo_salao_padrao.png")  # Altere o caminho conforme necessário

# Layout
st.title("🧑‍🎨 Galeria de Clientes")
colunas = st.columns(4)

for idx, cliente in enumerate(clientes):
    nome = cliente["nome"]
    url_foto = cliente["foto"]

    imagem_cliente = None
    if url_foto:
        try:
            response = requests.get(url_foto, timeout=5)
            if response.status_code == 200:
                imagem_cliente = PILImage.open(BytesIO(response.content))
        except Exception as e:
            st.error(f"Erro ao baixar imagem de {nome}: {e}")

    # Garantia: se não for imagem válida, usa a padrão
    if not isinstance(imagem_cliente, PILImage.Image):
        imagem_cliente = IMAGEM_PADRAO

    # Mostra imagem se ainda for válida
    if isinstance(imagem_cliente, PILImage.Image):
        with colunas[idx % 4]:
            st.image(imagem_cliente, caption=nome, use_container_width=True)
    else:
        st.warning(f"Erro ao carregar imagem de {nome}")
