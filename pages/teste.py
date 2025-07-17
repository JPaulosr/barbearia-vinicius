import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials
import gspread

st.set_page_config(page_title="Comissões Recebidas - Vinicius", layout="wide")
st.title("💸 Comissões Recebidas - Vinicius")

# Função para carregar a aba 'Despesas'
@st.cache_data

def carregar_despesas():
    escopos = ["https://www.googleapis.com/auth/spreadsheets"]
    credenciais = Credentials.from_service_account_info(
        st.secrets["GCP_SERVICE_ACCOUNT"], scopes=escopos
    )
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_url(st.secrets["PLANILHA_URL"])
    aba = planilha.worksheet("Despesas")
    dados = aba.get_all_records()
    return pd.DataFrame(dados)

# Carregar dados da planilha
df_despesas = carregar_despesas()

# Verificação de coluna correta
coluna_desc = None
for col in df_despesas.columns:
    if col.lower().strip() in ["descricao", "descrição"]:
        coluna_desc = col
        break

if not coluna_desc:
    st.error("Coluna de descrição não encontrada. Verifique se existe 'Descrição' ou 'Descricao'.")
    st.write("Colunas disponíveis:", df_despesas.columns.tolist())
else:
    # Filtrar apenas comissões recebidas por Vinicius
    df_vinicius = df_despesas[
        df_despesas[coluna_desc].str.contains("vinicius", case=False, na=False)
    ].copy()

    if df_vinicius.empty:
        st.warning("Nenhuma comissão encontrada para Vinicius.")
    else:
        # Converter coluna de data
        if "Data" in df_vinicius.columns:
            df_vinicius["Data"] = pd.to_datetime(df_vinicius["Data"], errors="coerce")
            df_vinicius = df_vinicius.dropna(subset=["Data"])
            df_vinicius["Ano-Mês"] = df_vinicius["Data"].dt.to_period("M").astype(str)

        # Gráfico mensal
        if "Valor" in df_vinicius.columns:
            df_vinicius["Valor"] = pd.to_numeric(df_vinicius["Valor"], errors="coerce")
            df_mensal = df_vinicius.groupby("Ano-Mês")["Valor"].sum().reset_index()

            st.subheader("📊 Gráfico de Comissões por Mês")
            fig = px.bar(df_mensal, x="Ano-Mês", y="Valor", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📋 Tabela Detalhada")
            st.dataframe(df_vinicius[["Data", coluna_desc, "Valor"]].sort_values("Data", ascending=False), use_container_width=True)

            total_pago = df_vinicius["Valor"].sum()
            st.success(f"💰 Total de comissões recebidas: R$ {total_pago:,.2f}".replace(",", ".").replace(".", ",", 1))
        else:
            st.warning("Coluna 'Valor' não encontrada na planilha de despesas.")
