import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image
import unicodedata

# ========== CONFIGURAÇÕES ==========
LOGO_PADRAO = "https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png"

# ====== ACESSO GOOGLE SHEETS ======
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["GCP_SERVICE_ACCOUNT"], scopes=SCOPE)
client = gspread.authorize(credentials)

# Carregar a aba 'clientes_status'
sheet = client.open_by_url(st.secrets["PLANILHA_URL"])
aba_status = sheet.worksheet("clientes_status")
df_fotos = pd.DataFrame(aba_status.get_all_records())

# ======== TRATAMENTO DE NOMES ========
def remover_acentos(texto):
    if isinstance(texto, str):
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()
    return ""

df_fotos['nome_tratado'] = df_fotos['Cliente'].apply(remover_acentos)
df_fotos['Foto'] = df_fotos['Foto'].replace('', np.nan)

# ========== DADOS ÚNICOS ==========
clientes_unicos = df_fotos[df_fotos['Status'] == "Ativo"].copy()
clientes_unicos.sort_values(by='Cliente', inplace=True)

# ========== MENU ==========
st.title("🔡 Navegação por letra")
letras = list("ABCDEFGHIJKLMNOPQRSTUVWXYZÁ")
letra = st.selectbox("Escolha uma letra", options=["Todos"] + letras)

# ====== AGRUPAMENTO POR LETRA =======
clientes_unicos['primeira_letra'] = clientes_unicos['Cliente'].str.upper().str[0]
if letra != "Todos":
    clientes_exibidos = clientes_unicos[clientes_unicos['primeira_letra'] == letra]
else:
    clientes_exibidos = clientes_unicos

# ====== EXIBIR CLIENTES EM COLUNAS =======
st.markdown("### 📁 Galeria")
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

if clientes_exibidos.empty:
    st.warning("Nenhum cliente encontrado.")
else:
    for idx, (_, row) in enumerate(clientes_exibidos.iterrows()):
        nome_cliente = row['Cliente']
        nome_tratado = remover_acentos(nome_cliente)

        # Buscar link da foto
        imagem_url = row['Foto']
        if pd.isna(imagem_url):
            imagem_url = LOGO_PADRAO
            caption = f"{nome_cliente} (imagem padrão)"
        else:
            caption = nome_cliente

        with cols[idx % 3]:
            st.image(imagem_url, caption=caption, use_column_width=True)
