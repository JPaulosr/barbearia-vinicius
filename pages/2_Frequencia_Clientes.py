import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da página
st.set_page_config(page_title="Frequência Clientes", layout="wide")
st.title("👥 Frequência de Clientes do Vinicius")

# Autenticação com Google Sheets
@st.cache_resource
def carregar_dados_google_sheets():
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", escopo)
    cliente = gspread.authorize(creds)

    planilha = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/edit?usp=sharing")
    base = planilha.worksheet("Base de Dados")
    df = pd.DataFrame(base.get_all_records())
    return df

df = carregar_dados_google_sheets()

# Filtrar apenas atendimentos do Vinicius
df = df[df["Funcionário"] == "Vinicius"]

# Agrupar por cliente
frequencia = df["Cliente"].value_counts().reset_index()
frequencia.columns = ["Cliente", "Qtd_Atendimentos"]

# Remover nomes genéricos
nomes_invalidos = ["brasileiro", "boliviano", "menino", "cliente"]
frequencia = frequencia[~frequencia["Cliente"].str.lower().isin(nomes_invalidos)]

# Mostrar tabela
st.subheader("📋 Ranking de Clientes por Frequência")
st.dataframe(frequencia, use_container_width=True)

# Gráfico de barras
st.subheader("📊 Gráfico de Frequência")
st.bar_chart(frequencia.set_index("Cliente"))
