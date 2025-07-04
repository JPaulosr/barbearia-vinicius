import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Resumo do Funcionário", page_icon="🧾", layout="wide")
st.title("🧾 Resumo do Funcionário - Vinicius")

# Autenticando com Google Sheets
escopo = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credenciais = ServiceAccountCredentials.from_json_keyfile_name('config.toml', escopo)
cliente = gspread.authorize(credenciais)

# Lendo a planilha
planilha = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/edit")
aba_dados = planilha.worksheet("RELATORIO_TRANSACOES")
dados = pd.DataFrame(aba_dados.get_all_records())

# Filtrando apenas Vinicius
df_vini = dados[dados["Funcionário"] == "Vinicius"]

# Calculando totais
total_receita = df_vini["Valor (R$)"].sum()
total_atendimentos = df_vini.shape[0]

col1, col2 = st.columns(2)
col1.metric("💰 Receita Total", f"R$ {total_receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("✂️ Total de Atendimentos", total_atendimentos)

st.dataframe(df_vini[['Data', 'Cliente', 'Serviço', 'Valor (R$)']], use_container_width=True)
