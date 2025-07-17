import streamlit as st

# Senha definida
SENHA_CORRETA = "vinicius2025"

# Verifica se usuário já autenticou
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Se ainda não autenticado, exibe campo de senha
if not st.session_state["autenticado"]:
    senha = st.text_input("🔐 Digite a senha para acessar:", type="password")
    if senha == SENHA_CORRETA:
        st.session_state["autenticado"] = True
        st.experimental_rerun()
    else:
        st.warning("Acesso restrito. Insira a senha correta.")
        st.stop()


# ========== CABEÇALHO ========== #
st.markdown("""
<div style="background-color:#003049;padding:10px;border-radius:5px">
    <span style="color:white;">Navegue pelas páginas ao lado para acessar os dados da sua performance e dos seus clientes.</span>
</div>
""", unsafe_allow_html=True)

# ========== FUNÇÃO DE CARREGAMENTO ========== #
@st.cache_data
def carregar_base_vinicius():
    url = "https://docs.google.com/spreadsheets/d/1qtOF1I7Ap4By2388ySThoVlZHbI3rAJv_haEcil0IUE/gviz/tq?tqx=out:csv&sheet=Base%20de%20Dados"
    df = pd.read_csv(url, encoding="utf-8")

    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    col_valor = next((col for col in df.columns if "valor" in col.lower()), None)
    if not col_valor:
        raise ValueError("❌ Coluna 'Valor' não encontrada.")
    df.rename(columns={col_valor: "Valor"}, inplace=True)

    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)
    df["Funcionario"] = df["Funcionario"].astype(str).str.strip().str.title()
    df = df[df["Funcionario"] == "Vinicius"]

    df["Valor"] = (
        df["Valor"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(" ", "")
        .str.replace(",", ".")
    )
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    return df

# ========== LÓGICA PRINCIPAL ========== #
try:
    df = carregar_base_vinicius()

    st.subheader("📅 Selecione o Mês e o Ano")
    meses_dict = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    anos = sorted(df["Data"].dt.year.dropna().unique())
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year

    col1, col2 = st.columns(2)
    mes = col1.selectbox("📆 Mês", options=meses_dict.keys(), format_func=lambda x: meses_dict[x], index=mes_atual - 1)
    ano = col2.selectbox("🗓️ Ano", options=anos, index=anos.index(ano_atual))

    df_mes = df[(df["Data"].dt.month == mes) & (df["Data"].dt.year == ano)]
    mes_ant = 12 if mes == 1 else mes - 1
    ano_ant = ano - 1 if mes == 1 else ano
    df_ant = df[(df["Data"].dt.month == mes_ant) & (df["Data"].dt.year == ano_ant)]

    receita = df_mes["Valor"].sum()
    receita_ant = df_ant["Valor"].sum()
    variacao = ((receita - receita_ant) / receita_ant * 100) if receita_ant > 0 else 0

    col1, col2 = st.columns(2)
    col1.metric("💰 Receita no Mês", f"R$ {receita:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","), f"{variacao:.1f}% vs anterior")
    col2.metric("📅 Atendimentos", len(df_mes))

    st.markdown("---")

    st.subheader(f"📊 Evolução Diária - {meses_dict[mes]}/{ano}")
    df_dia = df_mes.groupby(df_mes["Data"].dt.date)["Valor"].sum().reset_index()
    fig = px.bar(df_dia, x="Data", y="Valor", text_auto=True, labels={"Data": "Dia", "Valor": "Receita (R$)"})
    fig.update_layout(xaxis_title="Data", yaxis_title="Receita (R$)", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("👤 Top 5 Clientes do Mês")
    top = df_mes.groupby("Cliente")["Valor"].sum().sort_values(ascending=False).head(5).reset_index()
    st.table(top.rename(columns={"Cliente": "Cliente", "Valor": "Receita (R$)"}))

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
