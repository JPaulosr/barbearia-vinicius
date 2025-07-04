import streamlit as st
import pandas as pd
import gspread
import toml
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da página
st.set_page_config(page_title="Resumo do Funcionário", page_icon="🧾", layout="wide")
st.title("🧾 Resumo do Funcionário - Vinicius")

# Carrega o arquivo de configuração
try:
    config = toml.load("config.toml")
    info = config["GCP_SERVICE_ACCOUNT"]
    planilha_url = config["PLANILHA_URL"]["url"]
except Exception as e:
    st.error(f"Erro ao carregar o arquivo config.toml: {e}")
    st.stop()

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

# Mostra preview dos dados carregados
st.write("📋 Colunas disponíveis:", dados.columns.tolist())
st.write("👀 Prévia dos dados:")
st.dataframe(dados.head(), use_container_width=True)

# Verifica se a coluna 'Funcionário' existe
if "Funcionário" in dados.columns:
    dados["Funcionário"] = dados["Funcionário"].astype(str).str.strip()
    st.write("👥 Funcionários únicos na base:", dados["Funcionário"].unique())

    # Filtra os dados de Vinicius
    df_vini = dados[dados["Funcionário"] == "Vinicius"]

    if df_vini.empty:
        st.warning("⚠️ Nenhum atendimento encontrado para Vinicius.")
    else:
        total_receita = df_vini["Valor (R$)"].sum()
        total_atendimentos = df_vini.shape[0]

        col1, col2 = st.columns(2)
        col1.metric("💰 Receita Total", f"R$ {total_receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("🎯 Total de Atendimentos", total_atendimentos)

        st.subheader("📊 Detalhamento")
        st.dataframe(df_vini[['Data', 'Cliente', 'Serviço', 'Valor (R$)']], use_container_width=True)
else:
    st.error("❌ A coluna 'Funcionário' não foi encontrada na aba 'Base de Dados'.")
