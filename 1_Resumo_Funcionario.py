import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da página
st.set_page_config(page_title="Resumo do Funcionário", page_icon="🧾", layout="wide")
st.title("🧾 Resumo do Funcionário - Vinicius")

# Autenticando com Google Sheets
escopo = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credenciais = ServiceAccountCredentials.from_json_keyfile_name('config.toml', escopo)
cliente = gspread.authorize(credenciais)

# Lendo a planilha
planilha = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qtOF1I7pA4By2388ySThoVlZHbI3rAJv_haEcil0IUE/edit")
aba_dados = planilha.worksheet("RELATORIO_TRANSACOES")
dados = pd.DataFrame(aba_dados.get_all_records())

# Exibe as colunas disponíveis para verificar se 'Funcionário' está correto
st.write("📋 Colunas disponíveis:", dados.columns.tolist())

# Remove espaços extras da coluna de funcionários
if "Funcionário" in dados.columns:
    dados["Funcionário"] = dados["Funcionário"].str.strip()
    st.write("👤 Funcionários únicos na base:", dados["Funcionário"].unique())

    # Filtra apenas dados do Vinicius
    df_vini = dados[dados["Funcionário"] == "Vinicius"]

    if df_vini.empty:
        st.warning("⚠️ Nenhum atendimento encontrado para Vinicius.")
    else:
        # Calcula totais
        total_receita = df_vini["Valor (R$)"].sum()
        total_atendimentos = df_vini.shape[0]

        col1, col2 = st.columns(2)
        col1.metric("💰 Receita Total", f"R$ {total_receita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("🎯 Total de Atendimentos", total_atendimentos)

        st.subheader("📊 Detalhamento")
        st.dataframe(df_vini[['Data', 'Cliente', 'Serviço', 'Valor (R$)']], use_container_width=True)

else:
    st.error("❌ Coluna 'Funcionário' não encontrada na planilha.")
