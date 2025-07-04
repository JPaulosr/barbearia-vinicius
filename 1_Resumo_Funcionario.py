import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da página
st.set_page_config(page_title="Resumo do Funcionário", page_icon="🧾", layout="wide")
st.title("🧾 Resumo do Funcionário - Vinicius")

# Carregando dados do secrets
info = st.secrets["GCP_SERVICE_ACCOUNT"]
planilha_url = st.secrets["PLANILHA_URL"]["url"]

# Autenticando com Google Sheets
escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    credenciais = ServiceAccountCredentials.from_json_keyfile_dict(info, escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_url(planilha_url)
    aba_dados = planilha.worksheet("Base de Dados")
    dados = pd.DataFrame(aba_dados.get_all_records())
    st.success("✅ Planilha carregada com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar dados da planilha: {e}")
    st.stop()

# Diagnóstico básico
st.write("📋 Colunas:", dados.columns.tolist())

# Filtra por Vinicius
if "Funcionário" in dados.columns:
    dados["Funcionário"] = dados["Funcionário"].astype(str).str.strip()
    df_vini = dados[dados["Funcionário"] == "Vinicius"]

    if df_vini.empty:
        st.warning("⚠️ Nenhum atendimento encontrado para Vinicius.")
    else:
        total_receita = df_vini["Valor"].sum()
        total_atendimentos = df_vini.shape[0]

        col1, col2 = st.columns(2)
        col1.metric("💰 Receita Total", f"R$ {total_receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("🎯 Total de Atendimentos", total_atendimentos)

        st.subheader("📊 Detalhamento")
        st.dataframe(df_vini[['Data', 'Cliente', 'Serviço', 'Valor']], use_container_width=True)
else:
    st.error("❌ A coluna 'Funcionário' não foi encontrada.")
