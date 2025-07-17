# --------------------- FILTRO DINÂMICO DE MÊS E ANO ---------------------
st.subheader("📅 Selecione o Mês e o Ano")

# Opções disponíveis na base
meses_dict = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

anos_disponiveis = sorted(df["Data"].dt.year.dropna().unique())
mes_atual = datetime.now().month
ano_atual = datetime.now().year

col1, col2 = st.columns(2)
mes_selecionado = col1.selectbox("📆 Mês", options=meses_dict.keys(), format_func=lambda x: meses_dict[x], index=mes_atual-1)
ano_selecionado = col2.selectbox("🗓️ Ano", options=anos_disponiveis, index=anos_disponiveis.index(ano_atual))

# Filtro principal
df_selecionado = df[(df["Data"].dt.month == mes_selecionado) & (df["Data"].dt.year == ano_selecionado)]
df_anterior = df[(df["Data"].dt.month == (mes_selecionado - 1) if mes_selecionado > 1 else 12) &
                 (df["Data"].dt.year == (ano_selecionado if mes_selecionado > 1 else ano_selecionado - 1))]

# --------------------- MÉTRICAS ---------------------
receita = df_selecionado["Valor"].sum()
receita_ant = df_anterior["Valor"].sum()
variacao = ((receita - receita_ant) / receita_ant * 100) if receita_ant > 0 else 0

col1, col2 = st.columns(2)
col1.metric("💰 Receita no Mês", f"R$ {receita:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","), f"{variacao:.1f}% vs anterior")
col2.metric("📅 Atendimentos", len(df_selecionado))

# --------------------- GRÁFICO ---------------------
st.markdown("---")
st.subheader(f"📊 Evolução Diária da Receita ({meses_dict[mes_selecionado]}/{ano_selecionado})")

df_dia = df_selecionado.groupby(df_selecionado["Data"].dt.date)["Valor"].sum().reset_index()
fig = px.bar(df_dia, x="Data", y="Valor", text_auto=True, labels={"Data": "Dia", "Valor": "Receita (R$)"})
fig.update_layout(xaxis_title="Data", yaxis_title="Receita (R$)", height=400)
st.plotly_chart(fig, use_container_width=True)

# --------------------- TOP CLIENTES ---------------------
st.subheader("👤 Top 5 Clientes do Mês")
top_clientes = df_selecionado.groupby("Cliente")["Valor"].sum().sort_values(ascending=False).head(5).reset_index()
st.table(top_clientes.rename(columns={"Cliente": "Cliente", "Valor": "Receita (R$)"}))
