import streamlit as st
import pandas as pd
import requests
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Validação de Imagens", layout="wide")

# Dados da planilha
SHEET_ID = "1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE"
NOME_ABA = "clientes_status"

@st.cache_data
def carregar_dados():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = dict(st.secrets["GCP_SERVICE_ACCOUNT"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    aba = client.open_by_key(SHEET_ID).worksheet(NOME_ABA)
    data = aba.get_all_records()
    df = pd.DataFrame(data)
    df['Foto'] = df['Foto'].astype(str)
    df['Cliente'] = df['Cliente'].astype(str)
    return df

def verificar_imagem(url):
    if not url or url.strip() == "" or url.lower() == "nan":
        return "⚠️ Vazio"
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return "✅ OK"
        else:
            return f"❌ {response.status_code}"
    except:
        return "❌ Erro"

df = carregar_dados()
df = df[df['Status'].str.lower() == 'ativo']

st.title("🔍 Verificação de Links de Imagem (Cloudinary)")

# Verifica as imagens
st.info("Verificando status das imagens, aguarde...")
df['Status da Imagem'] = df['Foto'].apply(verificar_imagem)

# Exibe resultado
st.dataframe(df[['Cliente', 'Foto', 'Status da Imagem']], use_container_width=True)
