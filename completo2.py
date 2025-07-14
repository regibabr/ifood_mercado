import streamlit as st 
import pandas as pd
import re
from fuzzywuzzy import fuzz

st.set_page_config(page_title="Comparador de Compras", layout="wide")

# ========== FUNÇÕES ==========

def extrair_peso(texto):
    match = re.search(r'(\d+\.?\d*)\s*(g|kg|ml|l)', texto.lower())
    return match.group(0).replace(" ", "") if match else ""

def encontrar_produto_mais_barato(produto_lista, peso, categoria_lista, df_precos, limiar_similaridade=80):
    peso = peso.lower()

    df_filtrado = df_precos[df_precos['produto'].str.contains(peso, case=False, na=False)].copy()
    if df_filtrado.empty:
        return pd.Series(["", "", "", "", "", ""])

    df_filtrado['preco'] = df_filtrado['preco'].astype(str).str.replace("R\$", "", regex=True)
    df_filtrado['preco'] = df_filtrado['preco'].str.replace(".", "", regex=False).str.replace(",", ".")
    df_filtrado['preco'] = pd.to_numeric(df_filtrado['preco'], errors='coerce')
    df_filtrado = df_filtrado[df_filtrado['preco'].notnull()]
    if df_filtrado.empty:
        return pd.Series(["", "", "", "", "", ""])

    if categoria_lista and isinstance(categoria_lista, str):
        df_filtrado = df_filtrado[df_filtrado['categoria'].str.lower() == categoria_lista.lower()]
        if df_filtrado.empty:
            return pd.Series(["", "", "", "", "", ""])

    df_filtrado["similaridade"] = df_filtrado["produto"].apply(
        lambda x: fuzz.token_sort_ratio(produto_lista.lower(), x.lower())
    )
    df_similares = df_filtrado[df_filtrado["similaridade"] >= limiar_similaridade]
    df_considerados = df_similares if not df_similares.empty else df_filtrado

    produto_barato = df_considerados.sort_values(by="preco").iloc[0]
    preco_barato = produto_barato["preco"]
    preco_caro = df_considerados["preco"].max()
    diferenca = preco_caro - preco_barato

    return pd.Series([
        produto_barato["produto"],
        produto_barato.get("mercado", ""),
        preco_barato,
        produto_barato.get("categoria", ""),
        preco_caro,
        diferenca
    ])

# ========== APP ==========

st.title("🛍️ Comparação Atacadão x Atakarejo")

try:
    df_lista = pd.read_excel("lista2.xlsx")
    df_precos = pd.read_csv("precos_ifood_comparado.csv", sep=";")

    df_lista.columns = df_lista.columns.str.lower().str.strip()
    df_precos.columns = df_precos.columns.str.lower().str.strip()

    if 'produtos' not in df_lista.columns or 'produto' not in df_precos.columns:
        st.error("❌ Arquivo inválido: falta 'produtos' na lista ou 'produto' nos preços.")
    else:
        # ========== BLOCO 1 – Comparador Inteligente ==========

        st.header("🔎 Lista Inteligente de Compra")

        df_lista['peso'] = df_lista['produtos'].apply(extrair_peso)

        resultado = df_lista.apply(
            lambda row: encontrar_produto_mais_barato(
                row['produtos'],
                row['peso'],
                row.get('categoria', ""),
                df_precos
            ),
            axis=1
        )
        resultado.columns = [
            'produto_mais_barato', 'mercado', 'preco_unitario',
            'categoria_encontrada', 'preco_mais_caro', 'diferenca_preco'
        ]

        df_final = pd.concat([df_lista, resultado], axis=1)
        df_final['quantidade'] = pd.to_numeric(df_final['quantidade'], errors='coerce').fillna(0)
        df_final['preco_unitario'] = pd.to_numeric(df_final['preco_unitario'], errors='coerce')
        df_final['total'] = df_final['quantidade'] * df_final['preco_unitario']

        st.subheader("🧾 Tabela de Compra Ideal")
        st.dataframe(df_final.drop(columns=["categoria_encontrada"]), use_container_width=True)


        total_geral = df_final['total'].sum()
        total_qtd = df_final['quantidade'].sum()
        st.markdown(f"**Total de Itens:** {total_qtd}")
        st.markdown(f"**Valor Total da Compra:** R$ {total_geral:,.2f}")

        total_atakarejo = df_final.loc[df_final['mercado'].str.lower() == 'atakarejo', 'total'].sum()
        total_atacadao = df_final.loc[df_final['mercado'].str.lower() == 'atacadão', 'total'].sum()
        st.markdown(f"**Total no Atakarejo:** R$ {total_atakarejo:,.2f}")
        st.markdown(f"**Total no Atacadão:** R$ {total_atacadao:,.2f}")

        valor_economizado = pd.to_numeric(df_final['diferenca_preco'], errors='coerce').sum()
        total_preco_caro = pd.to_numeric(df_final['preco_mais_caro'], errors='coerce').sum()
        percentual_economizado = (valor_economizado / total_preco_caro) * 100 if total_preco_caro > 0 else 0
        st.markdown(f"**Valor Economizado:** R$ {valor_economizado:,.2f}")
        st.markdown(f"**Percentual Economizado:** {percentual_economizado:.2f}%")

        # ========== BLOCO 2 – Comparador Clássico ==========

        st.header("📊 Comparação Direta de Preços")

        df_precos["preco"] = df_precos["preco"].replace("R\$", "", regex=True).str.replace(",", ".").str.strip()
        df_precos["preco"] = pd.to_numeric(df_precos["preco"], errors="coerce")

        df_pivot = df_precos.pivot_table(index=["produto", "categoria"], columns="mercado", values="preco").reset_index()
        df_pivot["produto_nos_dois"] = ~df_pivot["Atakarejo"].isna() & ~df_pivot["Atacadão"].isna()
        df_pivot["diferença"] = df_pivot["Atakarejo"] - df_pivot["Atacadão"]
        df_pivot["mais_barato"] = df_pivot["diferença"].apply(
            lambda x: "Atakarejo" if x < 0 else "Atacadão" if x > 0 else "Mesmo preço"
        )

        st.subheader("📌 Resumo Comparativo")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Produtos", len(df_pivot))
        col2.metric("Produtos em ambos", df_pivot["produto_nos_dois"].sum())
        col3.metric("Somente em 1 mercado", len(df_pivot) - df_pivot["produto_nos_dois"].sum())

        st.subheader("📉 Diferença de Preços (Top 15)")
        top_dif = df_pivot[df_pivot["produto_nos_dois"]].copy()
        top_dif = top_dif.sort_values(by="diferença", key=abs, ascending=False).head(15)
        st.bar_chart(top_dif.set_index("produto")["diferença"])

        st.subheader("📋 Tabela Comparativa")
        st.dataframe(df_pivot[
            ["produto", "categoria", "Atakarejo", "Atacadão", "diferença", "mais_barato", "produto_nos_dois"]
        ], use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ Os arquivos 'lista.xlsx' e 'precos_ifood_comparado.csv' não foram encontrados no diretório.")
except Exception as e:
    st.exception(e)
