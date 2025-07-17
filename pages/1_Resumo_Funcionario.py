import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("👨‍💼 Detalhes do Funcionário - Vinicius")

# Função corrigida para carregar dados do Google Sheets via CSV (sem credenciais)
@st.cache_data
def carregar_dados_google_sheets(sheet_url, aba_nome):
    base_url = sheet_url.replace("/edit?usp=sharing", "")
    url_csv = f"{base_url}/gviz/tq?tqx=out:csv&sheet={aba_nome}"
    df = pd.read_csv(url_csv)
    return df

# URL da planilha principal (conectada diretamente)
sheet_url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/edit?usp=sharing"
df = carregar_dados_google_sheets(sheet_url, "Base de Dados")

# Filtra somente os dados do funcionário Vinicius
df = df[df['Profissional'] == 'Vinicius']

# Conversão de datas e extração de partes
if 'Data' in df.columns:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])
    df['Ano'] = df['Data'].dt.year
    df['Mes'] = df['Data'].dt.month
    df['Dia'] = df['Data'].dt.day
    df['DiaSemana'] = df['Data'].dt.day_name().str[:3]

# Filtros interativos
col1, col2, col3, col4 = st.columns(4)
ano = col1.selectbox("📅 Filtrar por ano", options=sorted(df['Ano'].unique(), reverse=True))
mes = col2.selectbox("📅 Filtrar por mês", options=['Todos'] + sorted(df['Mes'].unique()))
dia = col3.selectbox("📅 Filtrar por dia", options=['Todos'] + sorted(df['Dia'].unique()))
semana = col4.selectbox("📅 Filtrar por dia da semana", options=['Todas'] + sorted(df['DiaSemana'].unique()))

# Aplicação de filtros
filtro = df[df['Ano'] == ano]
if mes != 'Todos':
    filtro = filtro[filtro['Mes'] == mes]
if dia != 'Todos':
    filtro = filtro[filtro['Dia'] == dia]
if semana != 'Todas':
    filtro = filtro[filtro['DiaSemana'] == semana]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("🧾 Total de atendimentos", len(filtro))
col2.metric("👥 Clientes únicos", filtro['Cliente'].nunique())
col3.metric("💰 Receita total", f"R$ {filtro['Valor'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
media = filtro['Valor'].mean() if not filtro.empty else 0
col4.metric("💳 Ticket médio", f"R$ {media:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

# Dia com mais atendimentos
if not filtro.empty:
    dia_top = filtro['Data'].value_counts().idxmax().strftime("%d/%m/%Y")
    qtd_top = filtro['Data'].value_counts().max()
    st.info(f"📅 Dia com mais atendimentos: **{dia_top}** com **{qtd_top} atendimentos**")

# Atendimentos por dia da semana
atend_semana = filtro['DiaSemana'].value_counts().reindex(['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'])
st.subheader("📅 Atendimentos por Dia da Semana")
fig1 = px.bar(x=atend_semana.index, y=atend_semana.values,
              labels={'x': 'Dia da Semana', 'y': 'Quantidade'},
              text=atend_semana.values, height=400)
fig1.update_layout(yaxis_title='Atendimentos', xaxis_title='Dia da Semana')
st.plotly_chart(fig1, use_container_width=True)

# Receita mensal
st.subheader("📊 Receita Mensal por Mês e Ano")
df_receita = filtro.groupby(['Ano', 'Mes'])['Valor'].sum().reset_index()
df_receita['DataLabel'] = pd.to_datetime(df_receita[['Ano', 'Mes']].assign(DAY=1)).dt.strftime('%B %Y')
fig2 = px.bar(df_receita, x='DataLabel', y='Valor', text='Valor', labels={'Valor': 'Receita (R$)'})
fig2.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig2, use_container_width=True)
