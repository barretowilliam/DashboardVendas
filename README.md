# Dashboard de Vendas 🛒

Este projeto é um Dashboard de Vendas interativo utilizando Streamlit, Pandas, Plotly e conexão com um banco de dados SQL Server. Ele permite filtrar dados de vendas por períodos, regiões e produtos, exibindo gráficos interativos e insights sobre o desempenho das vendas.

## Funcionalidades

- Visualização das vendas por produto e ao longo do tempo.
- Filtros interativos por datas, regiões e produtos.
- Insights dinâmicos com informações sobre o produto mais vendido, data com maior volume de vendas, e vendas médias.
- Conexão com um banco de dados SQL Server para carregar dados em tempo real.

## Tecnologias Utilizadas

- Streamlit
- Pandas
- Plotly
- SQLAlchemy
- PyODBC

## Pré-requisitos

Certifique-se de ter os seguintes componentes instalados em sua máquina:

- Python 3.x
- SQL Server (com a base de dados AdventureWorks)
- Pip (gerenciador de pacotes do Python)

## Instalação

Clone o repositório para sua máquina local:

```bash
git clone https://github.com/usuario/dashboard-vendas.git
cd dashboard-vendas
Instale as dependências necessárias:

pip install -r requirements.txt
Se o arquivo requirements.txt ainda não estiver criado, adicione as seguintes linhas ao arquivo:

streamlit
pandas
plotly
sqlalchemy
pyodbc
Configure a conexão com o banco de dados:

Edite a URL de conexão no arquivo dashboard_vendas.py para apontar para o seu servidor SQL e banco de dados:

python

connection_url = 'mssql+pyodbc://SEU_SERVIDOR/AdventureWorks?driver=SQL+Server&trusted_connection=yes'
Substitua SEU_SERVIDOR pelo nome do seu servidor SQL.

Executando o Projeto
Para rodar o projeto localmente, execute o comando abaixo no terminal:

streamlit run Dashboard.py
Abra o navegador no endereço exibido no terminal (http://localhost:8501) para acessar o Dashboard de Vendas.

```

## Estrutura do Projeto

├── Dashboard.py Código principal do dashboard

├── requirements.txt Dependências do projeto

└── README.md Instruções e documentação

## Filtros Disponíveis

Período: Selecione o intervalo de datas para visualizar as vendas.

Regiões: Filtre as vendas por regiões específicas.

Produtos: Filtre as vendas por produtos específicos.

## Customização

O layout e os temas podem ser ajustados diretamente no código dashboard_vendas.py, na seção de gráficos Plotly. O cache dos dados tem duração de 10 minutos, o que pode ser ajustado na função @st.cache_data(ttl=1800).

## Problemas Conhecidos

Caso haja problemas na conexão com o banco de dados, revise a URL de conexão e verifique as permissões no SQL Server.
Se os gráficos não estiverem aparecendo, verifique a instalação da biblioteca Plotly.
