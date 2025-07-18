import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe
from google.oauth2.service_account import Credentials
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🏆 Premiação Especial - Destaques do Ano")

SHEET_ID = "1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE"

@st.cache_resource
def conectar_sheets():
    info = st.secrets["GCP_SERVICE_ACCOUNT"]
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = Credentials.from_service_account_info(info, scopes=escopo)
    cliente = gspread.authorize(credenciais)
    return cliente.open_by_key(SHEET_ID)

@st.cache_data
def carregar_dados():
    planilha = conectar_sheets()
    aba = planilha.worksheet("Base de Dados")
    df = get_as_dataframe(aba).dropna(how="all")
    df.columns = [str(col).strip() for col in df.columns]
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    return df

@st.cache_data
def carregar_status():
    planilha = conectar_sheets()
    aba = planilha.worksheet("clientes_status")
    df = get_as_dataframe(aba).dropna(how="all")
    df.columns = [str(col).strip() for col in df.columns]
    return df

def limpar_nomes(nome):
    nome = str(nome).strip().lower()
    nomes_excluir = ["boliviano", "brasileiro", "menino", "sem nome", "cliente", "sem preferência", "sem preferencia"]
    return not any(gen in nome for gen in nomes_excluir)

def mostrar_cliente(nome, legenda):
    foto = df_status[df_status["Cliente"] == nome]["Foto"].dropna().values
    col1, col2 = st.columns([1, 5])
    with col1:
        if len(foto) > 0:
            try:
                response = requests.get(foto[0])
                img = Image.open(BytesIO(response.content))
                st.image(img, width=100)
            except:
                st.image("https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png", width=100)
        else:
            st.image("https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png", width=100)
    with col2:
        st.markdown(f"### 🏅 {nome.title()}")
        st.markdown(legenda)

df = carregar_dados()
df_status = carregar_status()
df = df[df["Cliente"].notna() & df["Cliente"].apply(limpar_nomes)]
df = df[df["Valor"] > 0]

# 👨‍👩‍👧‍👦 Cliente Família — Todas as Famílias
st.subheader("👨‍👩‍👧‍👦 Cliente Família — Todas as Famílias")

df_familia = df.merge(df_status[["Cliente", "Família"]], on="Cliente", how="left")
df_familia = df_familia[df_familia["Família"].notna() & (df_familia["Família"] != "")]

# Agrupa por Família, Cliente e Data para contar 1 atendimento por cliente/dia
familia_contagem = df_familia.groupby(["Família", "Cliente", df_familia["Data"].dt.date]).size().reset_index(name="Qtd")

# Soma por Família
total_atendimentos = familia_contagem.groupby("Família").size()
dias_distintos = df_familia.drop_duplicates(subset=["Família", "Data"]).groupby("Família").size()

# Junta os dados em um DataFrame
familias_df = pd.DataFrame({
    "Atendimentos": total_atendimentos,
    "Dias Diferentes": dias_distintos
}).reset_index().sort_values("Atendimentos", ascending=False)

for _, row in familias_df.iterrows():
    familia = row["Família"]
    qtd_atendimentos = row["Atendimentos"]
    qtd_dias = row["Dias Diferentes"]

    st.markdown(f"### 🏅 Família {familia.title()}")
    st.markdown(
        f"A família **{familia.lower()}** teve atendimentos em **{qtd_dias} dias diferentes**, "
        f"somando **{qtd_atendimentos} atendimentos individuais** entre todos os membros."
    )

    membros_df = df_status[df_status["Família"] == familia]
    for _, membro in membros_df.iterrows():
        col1, col2 = st.columns([1, 5])
        with col1:
            try:
                if pd.notna(membro["Foto"]):
                    response = requests.get(membro["Foto"])
                    img = Image.open(BytesIO(response.content))
                    st.image(img, width=100)
                else:
                    raise Exception("sem imagem")
            except:
                st.image("https://res.cloudinary.com/db8ipmete/image/upload/v1752463905/Logo_sal%C3%A3o_kz9y9c.png", width=100)
        with col2:
            st.markdown(f"**{membro['Cliente']}**")
