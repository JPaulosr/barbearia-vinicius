st.subheader("🔍 Diagnóstico rápido")

# Mostra as colunas
st.write("📋 Colunas da planilha:", dados.columns.tolist())

# Mostra os primeiros registros
st.write("🔎 Prévia da base:")
st.dataframe(dados.head(), use_container_width=True)

# Mostra os valores únicos da coluna Funcionário
if "Funcionário" in dados.columns:
    dados["Funcionário"] = dados["Funcionário"].astype(str).str.strip()
    st.write("👤 Funcionários únicos:", dados["Funcionário"].unique())
else:
    st.error("❌ Coluna 'Funcionário' não encontrada.")
