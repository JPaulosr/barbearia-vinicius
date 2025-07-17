import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🧬 Gestão de Clientes - Vinicius")

# === CONFIGURAÇÃO GOOGLE SHEETS ===
SHEET_ID = "1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE"
BASE_ABA = "Base de Dados"
STATUS_ABA = "clientes_status"
STATUS_OPTIONS = ["Ativo", "Ignorado", "Inativo"]

@st.cache_resource
def conectar_sheets():
    info = st.secrets["GCP_SERVICE_ACCOUNT"]
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = Credentials.from_service_account_info(info, scopes=escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(SHEET_ID)
    return planilha

def carregar_base(planilha):
    aba = planilha.worksheet(BASE_ABA)
    df = get_as_dataframe(aba, dtype=str).dropna(how="all")
    df.columns = [col.strip() for col in df.columns]
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Data"])
    return df

def carregar_status(planilha):
    try:
        aba = planilha.worksheet(STATUS_ABA)
        df_status = get_as_dataframe(aba).dropna(how="all")
        return df_status
    except:
        return pd.DataFrame(columns=["Cliente", "Status"])

def salvar_status(planilha, df_status_atualizado):
    aba = planilha.worksheet(STATUS_ABA)
    df_status_existente = get_as_dataframe(aba).dropna(how="all")
    df_status_existente.columns = [str(c).strip() for c in df_status_existente.columns]

    if "Cliente" not in df_status_existente.columns or "Status" not in df_status_existente.columns:
        st.error("A aba de status precisa conter colunas 'Cliente' e 'Status'.")
        return

    df_status_existente.set_index("Cliente", inplace=True)
    df_status_atualizado.set_index("Cliente", inplace=True)
    df_status_existente.update(df_status_atualizado)
    df_status_existente.reset_index(inplace=True)

    aba.clear()
    set_with_dataframe(aba, df_status_existente)

# === CARGA DE DADOS
planilha = conectar_sheets()
df = carregar_base(planilha)

# ✅ FILTRAR APENAS CLIENTES ATENDIDOS POR VINICIUS
df = df[df["Funcionário"] == "Vinicius"]

df_clientes = pd.DataFrame({"Cliente": sorted(df["Cliente"].dropna().unique())})
df_status = carregar_status(planilha)

clientes_com_status = df_clientes.merge(df_status[["Cliente", "Status"]], on="Cliente", how="left")
clientes_com_status["Status"] = clientes_com_status["Status"].fillna("Ativo")

st.subheader("📋 Lista de Clientes com Status")
st.markdown("Você pode alterar o status de clientes inativos ou que não devem aparecer nos relatórios.")

busca = st.text_input("🔍 Buscar cliente por nome").strip().lower()
clientes_filtrados = clientes_com_status[clientes_com_status["Cliente"].str.lower().str.contains(busca)] if busca else clientes_com_status

status_order = {"Ignorado": 0, "Inativo": 1, "Ativo": 2}
clientes_filtrados["Ordem"] = clientes_filtrados["Status"].map(status_order)
clientes_filtrados = clientes_filtrados.sort_values("Ordem")

novo_status = []
for i, row in clientes_filtrados.iterrows():
    cor = "#ffcccc" if row["Status"] == "Ignorado" else "#fff2b2" if row["Status"] == "Inativo" else "#d8f8d8"
    texto_cor = "#000000"
    with st.container():
        st.markdown(
            f"""
            <div style="background-color:{cor}; padding:15px; border-radius:10px; margin-bottom:10px">
                <div style="font-size:17px; font-weight:bold; color:{texto_cor}; margin-bottom:5px">👤 {row['Cliente']}</div>
                <div style="font-size:14px; color:{texto_cor}; margin-bottom:8px">Status de {row['Cliente']}:</div>
            </div>
            """, unsafe_allow_html=True
        )
        status = st.selectbox(
            f"Status de {row['Cliente']}",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(row["Status"]),
            key=f"status_{i}"
        )
        novo_status.append(status)

if st.button("📂 Salvar alterações"):
    clientes_filtrados["Status"] = novo_status
    atualizados = clientes_filtrados.set_index("Cliente")[["Status"]]
    clientes_com_status.set_index("Cliente", inplace=True)
    clientes_com_status.update(atualizados)
    clientes_com_status.reset_index(inplace=True)

    df_para_salvar = clientes_com_status[["Cliente", "Status"]]
    salvar_status(planilha, df_para_salvar)
    st.success("Status atualizado com sucesso!")

st.subheader("📈 Resumo por Status")
resumo = clientes_com_status["Status"].value_counts().reset_index()
resumo.columns = ["Status", "Qtd Clientes"]
st.dataframe(resumo, use_container_width=True)

fig = px.pie(clientes_com_status, names="Status", title="Distribuição de Clientes por Status")
st.plotly_chart(fig, use_container_width=True)
