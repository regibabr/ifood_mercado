# ifood_mercado
Insigths produtos Atakarejo Paripe vs Atacadão Pirajá

Comparador de Compras

Este é um aplicativo web desenvolvido com Streamlit que compara preços de produtos entre dois mercados: Atakarejo e Atacadão. O objetivo é ajudar os usuários a encontrar os melhores preços para suas compras.

Funcionalidades

- Lista Inteligente de Compra: o aplicativo lê uma lista de produtos e encontra o preço mais barato para cada produto nos dois mercados.
- Tabela de Compra Ideal: o aplicativo gera uma tabela com os produtos e seus preços mais baratos, além do total da compra e do valor economizado.
- Comparação Direta de Preços: o aplicativo compara os preços dos produtos nos dois mercados e gera uma tabela com as diferenças de preços.
- Resumo Comparativo: o aplicativo gera um resumo com o total de produtos, produtos em ambos os mercados e produtos somente em um mercado.

Arquivos necessários

- lista2.xlsx: arquivo Excel com a lista de produtos
- precos_ifood_comparado.csv: arquivo CSV com os preços dos produtos nos dois mercados. Esses dados foi extraido com robô scraping.

Tecnologias utilizadas

- Streamlit: framework para desenvolvimento de aplicativos web
- Pandas: biblioteca para manipulação de dados
- FuzzyWuzzy: biblioteca para comparação de strings

Como usar

1. Clone o repositório e instale as dependências necessárias.
2. Prepare os arquivos lista2.xlsx e precos_ifood_comparado.csv com os dados necessários.
3. Execute o aplicativo com streamlit run app.py.
4. Acesse o aplicativo no navegador e siga as instruções.


