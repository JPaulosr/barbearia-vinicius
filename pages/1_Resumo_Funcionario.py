import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
import gspread

st.set_page_config(layout="wide", page_title="Resumo Funcionário", page_icon="💼")

# Carrega dados do Google Sheets com service account
@st.cache_data
def carregar_dados():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["GCP_SERVICE_ACCOUNT"],
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(st.secrets["PLANILHA_URL"])
    worksheet = sh.worksheet("Base de Dados")
    df = pd.DataFrame(worksheet.get_all_records())
    return df

df = carregar_dados()

# Filtra apenas atendimentos do Vinicius
df = df[df["Profissional"] == "Vinicius"]

# Formata data
df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["Data"])

# Extrai ano e mês
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month
df["DiaSemana"] = df["Data"].dt.day_name(locale='pt_BR')

# 🔹 Gráfico: Atendimentos por Dia da Semana (Total)
st.markdown("### 📅 Atendimentos por dia da semana")
dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
df["DiaSemana"] = pd.Categorical(df["DiaSemana"], categories=dias_semana, ordered=True)

df_dia = df["DiaSemana"].value_counts().sort_index().reset_index()
df_dia.columns = ["DiaSemana", "Qtd Atendimentos"]

fig = px.bar(df_dia, x="DiaSemana", y="Qtd Atendimentos", text="Qtd Atendimentos",
             color_discrete_sequence=["#636EFA"])
fig.update_layout(xaxis_title="Dia da Semana", yaxis_title="Qtd Atendimentos")
st.plotly_chart(fig, use_container_width=True)

# 🔹 Receita mensal por mês e ano (exibindo 50% apenas)
st.markdown("### 📊 Receita Mensal por Mês e Ano (comissão 50%)")
df_receita = df.copy()
df_receita["Valor"] = pd.to_numeric(df_receita["Valor"], errors="coerce").fillna(0)
df_receita["Valor50"] = df_receita["Valor"] * 0.5

df_agrupado = df_receita.groupby(["Ano", "Mes"], as_index=False)["Valor50"].sum()
df_agrupado["DataLabel"] = pd.to_datetime(df_agrupado[["Ano", "Mes"]].assign(DAY=1), errors="coerce")
df_agrupado = df_agrupado.sort_values("DataLabel")

fig2 = px.bar(df_agrupado, x="DataLabel", y="Valor50", text_auto='.2s',
              labels={"DataLabel": "Mês", "Valor50": "Receita (50%)"},
              color_discrete_sequence=["#82C0FF"])
fig2.update_layout(xaxis_title="Mês", yaxis_title="R$", showlegend=False)
fig2.update_traces(texttemplate="R$ %{y:.2f}")
st.plotly_chart(fig2, use_container_width=True)
