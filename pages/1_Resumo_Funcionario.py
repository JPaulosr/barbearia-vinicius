import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from google.oauth2 import service_account
import gspread

st.set_page_config(layout="wide")

# --- CONFIGURAÇÕES ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/edit?usp=sharing"

# --- CONEXÃO COM GOOGLE SHEETS ---
@st.cache_data(ttl=600)
def carregar_dados():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["GCP_SERVICE_ACCOUNT"], scopes=SCOPE
    )
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_url(SPREADSHEET_URL)
    worksheet = spreadsheet.worksheet("Base de Dados")
    df = pd.DataFrame(worksheet.get_all_records())

    # Padroniza nomes de colunas
    df.columns = [col.strip() for col in df.columns]

    # Garante que a coluna 'Funcionário' seja usada corretamente
    col_funcionario = [col for col in df.columns if "funcion" in col.lower()][0]
    df = df[df[col_funcionario] == "Vinicius"]

    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["Dia da Semana"] = df["Data"].dt.day_name()

    return df

df = carregar_dados()

# --- TÍTULO ---
st.title("📊 Resumo Funcionário - Vinicius")

# --- RESUMO MENSAL ---
st.subheader("📅 Receita Mensal por Mês e Ano")
df_receita = df.copy()
df_receita['DataLabel'] = pd.to_datetime(df_receita[['Ano', 'Mes']].assign(DAY=1)).dt.strftime('%b %Y')
resumo = df_receita.groupby('DataLabel')['Valor'].sum().reset_index()
resumo = resumo.sort_values('DataLabel', key=lambda x: pd.to_datetime(x, format='%b %Y'))

fig = px.bar(resumo, x='DataLabel', y='Valor', text_auto=True, title="Receita por Mês")
st.plotly_chart(fig, use_container_width=True)

# --- ATENDIMENTOS POR DIA DA SEMANA ---
st.subheader("📈 Atendimentos por Dia da Semana")
dias = df['Dia da Semana'].value_counts().reindex(
    ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
).dropna()

fig2 = px.bar(dias, x=dias.index, y=dias.values, text_auto=True, title="Distribuição dos Atendimentos")
fig2.update_layout(xaxis_title="Dia", yaxis_title="Quantidade", showlegend=False)
st.plotly_chart(fig2, use_container_width=True)

# --- TABELA DETALHADA ---
st.subheader("📋 Detalhamento dos Atendimentos")
st.dataframe(
    df[['Data', 'Cliente', 'Serviço', 'Valor', 'Combo']].sort_values('Data', ascending=False),
    use_container_width=True
)
