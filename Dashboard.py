# Importação de bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, exc
from datetime import datetime

# Configuração da página
st.set_page_config(page_title='Dashboard de Vendas', layout='wide')
st.title('DASHBOARD DE VENDAS 🛒')

# URL de conexão
connection_url = 'mssql+pyodbc://ELLAS/AdventureWorks?driver=SQL+Server&trusted_connection=yes'

# Função para conectar ao banco de dados e carregar os dados
@st.cache_data(ttl=1800)
def load_data():
    try:
        engine = create_engine(connection_url)
        with engine.connect() as conn:
            query = """
            SELECT soh.OrderDate, soh.TotalDue, a.StateProvinceID, sp.Name AS StateName, p.Name AS ProductName
            FROM Sales.SalesOrderHeader AS soh
            JOIN Sales.SalesOrderDetail AS sod ON soh.SalesOrderID = sod.SalesOrderID
            JOIN Production.Product AS p ON sod.ProductID = p.ProductID
            JOIN Person.Address AS a ON soh.ShipToAddressID = a.AddressID
            JOIN Person.StateProvince AS sp ON a.StateProvinceID = sp.StateProvinceID
            JOIN Person.CountryRegion AS cr ON sp.CountryRegionCode = cr.CountryRegionCode
            """
            df = pd.read_sql(query, conn)
            df['OrderDate'] = pd.to_datetime(df['OrderDate'])
            return df
    except exc.SQLAlchemyError as e:
        st.error("Erro ao conectar ou ler dados do banco de dados: " + str(e))
        st.stop()

# Função para formatar números grandes
def format_large_numbers(value):
    if value >= 1e12:
        return f'{value / 1e12:.2f}T'
    elif value >= 1e9:
        return f'{value / 1e9:.2f}Bi'
    elif value >= 1e6:
        return f'{value / 1e6:.2f}M'
    elif value >= 1e3:
        return f'{value / 1e3:.2f}K'
    else:
        return f'{value:.2f}'

# Carregamento dos dados
df = load_data()
if df.empty:
    st.error("Nenhum dado encontrado na consulta.")
    st.stop()

# Mostrar a data da última atualização
last_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
st.markdown(f"<p style='color: #ffffff;'>Última atualização: {last_updated}</p>", unsafe_allow_html=True)

# Função para formatar números grandes
def format_large_numbers(value):
    if value >= 1e12:
        return f'{value / 1e12:.2f}T'
    elif value >= 1e9:
        return f'{value / 1e9:.2f}Bi'
    elif value >= 1e6:
        return f'{value / 1e6:.2f}M'
    elif value >= 1e3:
        return f'{value / 1e3:.2f}K'
    else:
        return f'{value:.2f}'

# Intervalo de datas
min_date = df['OrderDate'].min().date()
max_date = df['OrderDate'].max().date()

# Filtros da sidebar
st.sidebar.header('Filtros')
st.sidebar.markdown('<style>div[data-testid="stSidebar"] {background-color: #333;}</style>', unsafe_allow_html=True)

start_date, end_date = st.sidebar.slider(
    'Selecione o período:',
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    format='DD/MM/YYYY',
    key='date_slider'
)

# Função para filtrar regiões e produtos
def filter_region_product(df, selected_regions=None, selected_products=None):
    filtered_df = df.copy() 
    if selected_regions:
        filtered_df = filtered_df[filtered_df['StateName'].isin(selected_regions)]
    if selected_products:
        filtered_df = filtered_df[filtered_df['ProductName'].isin(selected_products)]
    
    available_regions = filtered_df['StateName'].unique().tolist()
    available_products = filtered_df['ProductName'].unique().tolist()
    
    return filtered_df, available_regions, available_products

# Filtragem inicial
initial_regions = df['StateName'].unique().tolist()
initial_products = df['ProductName'].unique().tolist()
filtered_df, available_regions, available_products = filter_region_product(df)

# Seleção de regiões e produtos
selected_regions = st.sidebar.multiselect('Selecione as Regiões', available_regions)
selected_products = st.sidebar.multiselect('Selecione os Produtos', available_products)

# Filtros de data
filtered_df = filtered_df[(filtered_df['OrderDate'] >= pd.Timestamp(start_date)) & (filtered_df['OrderDate'] <= pd.Timestamp(end_date))]

# Filtros de regiões e produtos
filtered_df, available_regions, available_products = filter_region_product(filtered_df, selected_regions, selected_products)

# Arredondando valores
filtered_df['TotalDue'] = filtered_df['TotalDue'].round(2)

# Cálculos de vendas totais
total_sales = filtered_df['TotalDue'].sum().round(2)
total_sales_formatted = format_large_numbers(total_sales)
st.markdown(f"<h2 style='color: #ff5733;'>Total de Vendas: ${total_sales_formatted}</h2>", unsafe_allow_html=True)

# Vendas por produto
sales_by_product = filtered_df.groupby('ProductName')['TotalDue'].sum().reset_index().round(2)
sales_by_product = sales_by_product.sort_values(by='TotalDue', ascending=False)

# Tooltip personalizado
sales_by_product['HoverText'] = (
    "<b>Produto:</b> " + sales_by_product['ProductName'] + "<br>" +
    "<b>Total Vendido:</b> " + sales_by_product['TotalDue'].map('${:,.2f}'.format) + "<br>" +
    "<b>Vendas %:</b> " + (sales_by_product['TotalDue'] / total_sales * 100).map('{:.2f}%'.format)
)

# Gráfico
fig_product = px.bar(sales_by_product, x='ProductName', y='TotalDue',
                      title='Vendas por Produto',
                      labels={'TotalDue': 'Total de Vendas (US$)', 'ProductName': 'Produto'},
                      color='TotalDue',
                      color_continuous_scale=px.colors.sequential.Inferno)

fig_product.update_traces(hovertemplate=sales_by_product['HoverText'],
                           customdata=sales_by_product[['HoverText']].values)

fig_product.update_layout(yaxis_title='Total de Vendas (US$)',
                          xaxis_title='Produto',
                          template='plotly_dark',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)',
                          title_font=dict(size=20, color='white'),
                          xaxis=dict(title_font=dict(size=14), tickangle=-45, color='white'),
                          yaxis=dict(title_font=dict(size=14, color='white'), tickcolor='white'),
                          margin=dict(l=40, r=40, t=40, b=40),
                          height=350)

# Vendas por região
sales_by_region = filtered_df.groupby('StateName')['TotalDue'].sum().reset_index().round(2)
sales_by_region = sales_by_region.sort_values(by='TotalDue', ascending=False)

# Tooltip personalizado
sales_by_region['HoverText'] = (
    "<b>Região:</b> " + sales_by_region['StateName'] + "<br>" +
    "<b>Total Vendido:</b> " + sales_by_region['TotalDue'].map('${:,.2f}'.format) + "<br>" +
    "<b>Vendas %:</b> " + (sales_by_region['TotalDue'] / total_sales * 100).map('{:.2f}%'.format)
)

# Gráfico
fig_region = px.bar(sales_by_region, x='StateName', y='TotalDue',
                    title='Vendas por Região',
                    labels={'TotalDue': 'Total de Vendas (US$)', 'StateName': 'Região'},
                    color='TotalDue',
                    color_continuous_scale=px.colors.sequential.Inferno)

fig_region.update_traces(hovertemplate=sales_by_region['HoverText'],
                          customdata=sales_by_region[['HoverText']].values)

fig_region.update_layout(yaxis_title='Total de Vendas (US$)',
                         xaxis_title='Região',
                         template='plotly_dark',
                         plot_bgcolor='rgba(0, 0, 0, 0)',
                         paper_bgcolor='rgba(0, 0, 0, 0)',
                         title_font=dict(size=20, color='white'),
                         xaxis=dict(title_font=dict(size=14), tickangle=-45, color='white'),
                         yaxis=dict(title_font=dict(size=14, color='white'), tickcolor='white'),
                         margin=dict(l=40, r=40, t=40, b=40),
                         height=400)

# Vendas ao longo do tempo
sales_over_time = filtered_df.groupby(pd.Grouper(key='OrderDate', freq='M'))['TotalDue'].sum().reset_index().round(2)

# Tooltip personalizado
sales_over_time['HoverText'] = (
    "<b>Data:</b> " + sales_over_time['OrderDate'].dt.strftime('%d/%m/%Y') + "<br>" +
    "<b>Total Vendido:</b> " + sales_over_time['TotalDue'].map('${:,.2f}'.format) + "<br>" +
    "<b>Vendas %:</b> " + (sales_over_time['TotalDue'] / total_sales * 100).map('{:.2f}%'.format)
)

# Gráfico
fig_time = px.line(sales_over_time, x='OrderDate', y='TotalDue',
                   title='Vendas ao Longo do Tempo',
                   labels={'TotalDue': 'Total de Vendas (US$)', 'OrderDate': 'Data'},
                   markers=True)

fig_time.update_traces(hovertemplate=sales_over_time['HoverText'],
                        customdata=sales_over_time[['HoverText']].values)

fig_time.update_layout(yaxis_title='Total de Vendas (US$)',
                       xaxis_title='Data',
                       template='plotly_dark',
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       paper_bgcolor='rgba(0, 0, 0, 0)',
                       title_font=dict(size=20, color='white'),
                       xaxis=dict(title_font=dict(size=14), color='white'),
                       yaxis=dict(title_font=dict(size=14, color='white'), tickcolor='white'),
                       margin=dict(l=40, r=40, t=40, b=40),
                       height=400)

sales_over_time = filtered_df.groupby(pd.Grouper(key='OrderDate', freq='M'))['TotalDue'].sum().reset_index().round(2)

# Tooltip personalizado
sales_over_time['HoverText'] = (
    "<b>Data:</b> " + sales_over_time['OrderDate'].dt.strftime('%d/%m/%Y') + "<br>" +
    "<b>Total Vendido:</b> " + sales_over_time['TotalDue'].map('${:,.2f}'.format) + "<br>" +
    "<b>Vendas %:</b> " + (sales_over_time['TotalDue'] / total_sales * 100).map('{:.2f}%'.format)
)

fig_time = px.line(sales_over_time, x='OrderDate', y='TotalDue',
                   title='Vendas ao Longo do Tempo',
                   labels={'TotalDue': 'Total de Vendas (US$)', 'OrderDate': 'Data'},
                   markers=True)


for index, row in sales_over_time.iterrows():
    if row['TotalDue'] >= 1e3:  
        fig_time.add_annotation(
            x=row['OrderDate'],
            y=row['TotalDue'],
            text=f"${format_large_numbers(row['TotalDue'])}", 
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40,  
            font=dict(color="#ffffff")
        )

# Definindo os valores de gridlines
gridline_values = [100_000_000, 200_000_000, 300_000_000]

fig_time.update_yaxes(
    tickvals=gridline_values,  
    showgrid=True, 
    gridcolor='rgba(255, 255, 255, 0.2)'  
)

fig_time.update_traces(hovertemplate=sales_over_time['HoverText'],
                        customdata=sales_over_time[['HoverText']].values)

fig_time.update_traces(line=dict(color='#ff5733', width=3))
fig_time.update_layout(yaxis_title='Total de Vendas (US$)',
                       xaxis_title='',
                       template='plotly_dark',
                       plot_bgcolor='rgba(0, 0, 0, 0)',
                       paper_bgcolor='rgba(0, 0, 0, 0)',
                       title_font=dict(size=20, color='white'),
                       xaxis=dict(title_font=dict(size=14), tickangle=-45, color='white'),
                       yaxis=dict(title_font=dict(size=14, color='white'), tickcolor='white'),
                       margin=dict(l=40, r=40, t=40, b=40),
                       height=350)

# Estilo do Dashboard
st.markdown("""<style>
body { background-color: #1e1e1e; }
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
h1, h2, h3, h4, h5, h6, p { font-family: 'Roboto', sans-serif; color: #f4f4f4; }
</style>""", unsafe_allow_html=True)

# Insights na sidebar
st.sidebar.header('Insights')

average_sales = filtered_df['TotalDue'].mean().round(2)
average_sales_formatted = format_large_numbers(average_sales)

num_orders = filtered_df['TotalDue'].count()

most_sold_product = filtered_df.groupby('ProductName')['TotalDue'].sum().idxmax()
most_sales_region = filtered_df.groupby('StateName')['TotalDue'].sum().idxmax()

# Insights formatados
st.sidebar.write(f"**Produto Mais Vendido:** {most_sold_product}")
st.sidebar.write(f"**Região com Maiores Vendas:** {most_sales_region}")
st.sidebar.write(f"**Total de Pedidos:** {num_orders}")
st.sidebar.write(f"**Média de Vendas por Pedido:** ${average_sales_formatted}")

st.sidebar.markdown("## Observações")
st.sidebar.write("Esses dados são filtrados com base na seleção de datas e regiões. Utilize os filtros à esquerda para ajustar a visualização.")


# Exibição dos gráficos
if 'OrderDate' in filtered_df.columns:
    filtered_df['OrderDate'] = filtered_df['OrderDate'].dt.strftime('%d/%m/%Y')
else:
    st.warning("A coluna 'OrderDate' não está disponível no DataFrame.")

if 'TotalDue' in filtered_df.columns:
    filtered_df['TotalDue'] = filtered_df['TotalDue'].round(2)
else:
    st.warning("A coluna 'TotalDue' não está disponível no DataFrame.")

filtered_df = filtered_df.rename(columns={
    'OrderDate': 'Data do Pedido',
    'TotalDue': 'Total Vendas',
    'StateName': 'Nome do Estado',
    'ProductName': 'Nome do Produto'
})

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_product, use_container_width=True)
with col2:
    st.plotly_chart(fig_region, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_time, use_container_width=True)
with col4:
    st.markdown(" ##### Detalhamento por Região e Produto")
    st.dataframe(filtered_df[['Data do Pedido', 'Total Vendas', 'Nome do Estado', 'Nome do Produto']], height=200)