# [...] (manter todo o código anterior até a seção "# Dia mais cheio")

# === Dia mais cheio + receita do dia ===
dia_mais_cheio = df_func.groupby(df_func["Data"].dt.date).agg({
    "Valor": ["count", "sum"]
}).reset_index()
dia_mais_cheio.columns = ["Data", "Qtd Atendimentos", "Receita"]
dia_mais_cheio = dia_mais_cheio.sort_values("Qtd Atendimentos", ascending=False).head(1)

if not dia_mais_cheio.empty:
    data_cheia = pd.to_datetime(dia_mais_cheio.iloc[0, 0]).strftime("%d/%m/%Y")
    qtd_atend = int(dia_mais_cheio.iloc[0, 1])
    receita_dia = dia_mais_cheio.iloc[0, 2] * 0.5
    receita_formatada = f"R$ {receita_dia:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

    st.info(f"📅 Dia com mais atendimentos: **{data_cheia}** com **{qtd_atend} atendimentos**\n\n💰 Receita recebida no dia: **{receita_formatada}**")

# === Receita Mensal - exibindo apenas 50% ===
st.subheader("📊 Receita Mensal por Mês e Ano")
df_func["MesNum"] = df_func["Data"].dt.month
df_func["MesNome"] = df_func["MesNum"].map(meses_pt) + df_func["Data"].dt.strftime(" %Y")
receita_mensal = df_func.groupby(["MesNum", "MesNome"])["Valor"].sum().reset_index(name="Bruto")
receita_mensal["Recebido"] = receita_mensal["Bruto"] * 0.5
receita_mensal = receita_mensal.sort_values("MesNum")

receita_mensal["Recebido Formatado"] = receita_mensal["Recebido"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

fig_receita = px.bar(
    receita_mensal,
    x="MesNome",
    y="Recebido",
    text="Recebido Formatado",
    labels={"Recebido": "Receita Recebida (R$)", "MesNome": "Mês"},
    template="plotly_white",
)
fig_receita.update_layout(height=450, margin=dict(t=40, b=20))
fig_receita.update_traces(textposition="outside", cliponaxis=False)
st.plotly_chart(fig_receita, use_container_width=True)
