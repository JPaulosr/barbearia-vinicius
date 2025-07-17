import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials
import gspread

st.set_page_config(page_title="Comissões Recebidas - Vinicius", layout="wide")
st.title("💸 Comissões Recebidas - Vinicius")

# Função para carregar a aba 'Base de Dados'
@st.cache_data
def carregar_base():
    escopos = ["https://www.googleapis.com/auth/spreadsheets"]
    credenciais = Credentials.from_service_account_info(
        st.secrets["GCP_SERVICE_ACCOUNT"], scopes=escopos
    )
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_url(st.secrets["PLANILHA_URL"])
    aba = planilha.worksheet("Base de Dados")
    dados = aba.get_all_records()
    return pd.DataFrame(dados)

# Carregar dados da planilha
base = carregar_base()

# Padronizar nome das colunas
colunas_renomeadas = {col: col.strip().capitalize() for col in base.columns}
base.rename(columns=colunas_renomeadas, inplace=True)

# Verificar nome correto da coluna de profissional
coluna_prof = [col for col in base.columns if col.strip().lower() in ["profissional", "funcionário"]]
if not coluna_prof:
    st.error("❌ Coluna de profissional não encontrada na planilha.")
    st.stop()
coluna_prof = coluna_prof[0]

# Filtrar somente atendimentos de Vinicius
base_vini = base[base[coluna_prof] == "Vinicius"].copy()

# Converter valores
base_vini["Valor"] = pd.to_numeric(base_vini["Valor"], errors="coerce")
base_vini["Data"] = pd.to_datetime(base_vini["Data"], errors="coerce")
base_vini = base_vini.dropna(subset=["Data", "Valor"])

# Estimar comissão real recebida
if "Comissão" in base_vini.columns:
    base_vini["ComissaoRecebida"] = pd.to_numeric(base_vini["Comissão"], errors="coerce")
else:
    def calcular_comissao(valor):
        if pd.isna(valor):
            return 0
        if round(valor, 2) % 5 != 0 and not float(valor).is_integer():
            return valor / 2  # valor já com desconto maquininha
        else:
            return valor * 0.5
    base_vini["ComissaoRecebida"] = base_vini["Valor"].apply(calcular_comissao)

base_vini["Ano-Mês"] = base_vini["Data"].dt.to_period("M").astype(str)

# Gráfico
df_mensal = base_vini.groupby("Ano-Mês")["ComissaoRecebida"].sum().reset_index()
st.subheader("📊 Gráfico de Comissões por Mês")
fig = px.bar(df_mensal, x="Ano-Mês", y="ComissaoRecebida", text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# Tabela
st.subheader("📋 Tabela Detalhada")
st.dataframe(base_vini[["Data", "Cliente", "Serviço", "Valor", "ComissaoRecebida"]].sort_values("Data", ascending=False), use_container_width=True)

total_pago = base_vini["ComissaoRecebida"].sum()
st.success(f"💰 Total de comissões recebidas: R$ {total_pago:,.2f}".replace(",", ".").replace(".", ",", 1))
