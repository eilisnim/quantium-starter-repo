# import libraries
import pandas as pd
import dash
from dash import Dash, html, dcc, dash_table
import plotly.express as px

# print("dash version - ", dash.__version__)

df1 = pd.read_csv('data/daily_sales_data_0.csv')
df2 = pd.read_csv('data/daily_sales_data_1.csv')
df3 = pd.read_csv('data/daily_sales_data_2.csv')

# print headers and footers for each dataframe
# print(df1.head())
# print(df1.tail())
# print(df2.head())
# print(df2.tail())
# print(df3.head())
# print(df3.tail())

# check column names are same in each excel file
# print(df1.columns)
# print(df2.columns)
# print(df3.columns)

# combine into 1 dataframe
df_candy = pd.concat([df1, df2, df3], ignore_index=True)

# print(df_candy.head())
# print(df_candy.tail())

# convert date to datetime
df_candy['date'] = pd.to_datetime(df_candy['date'])
# print(df_candy.dtypes)

# filter 'pink morsel' only, and order by 'date' ascending
df_pinkmorsel = (
    df_candy[df_candy['product'] == 'pink morsel']
    .sort_values(by='date', ascending=True)
)
# look at 'price' in dataset
# print(df_pinkmorsel['price'].unique())

# is  'price' & 'quantity' numeric? for adding to give 'sales'
quantityType = df_pinkmorsel['quantity'].dtype
# clean 'price', remove dollar sign, convert type to float
df_pinkmorsel['price'] = (
    df_pinkmorsel['price']
    .str.replace('$', '', regex=False)
    .astype(float)
)
df_pinkmorsel['quantity'] = pd.to_numeric(df_pinkmorsel['quantity'], errors='coerce')

# 'quantity' * 'price' = 'sales'
df_pinkmorsel['sales'] = df_pinkmorsel['quantity'] * df_pinkmorsel['price']

print(df_pinkmorsel.head())
print(df_pinkmorsel.tail())

sales_pre_increase = df_pinkmorsel[df_pinkmorsel['date'] < '2021-01-15']['sales'].sum()
sales_post_increase = df_pinkmorsel[df_pinkmorsel['date'] >= '2021-01-15']['sales'].sum()

# clean df for dash
# df_dash = df_pinkmorsel.drop(columns=['product', 'price', 'quantity'])
df_dash = df_pinkmorsel.drop(columns=['product', 'price', 'quantity'])
df_dash = df_dash[df_dash['region'] == 'north']

print(df_dash)

print("Sales before increase ", sales_pre_increase)
print("Sales after increase ", sales_post_increase)

app = Dash(__name__)

fig = px.line(
#     df_region_sales,
    df_dash,
    x='date',
    y='sales',
    color='region',   # This creates 4 separate lines
    markers=True,
    title='Pink Morsel Sales by Region'
)

app.layout = html.Div([
    html.H1("Sales by Region"),
    dcc.Graph(figure=fig)
])

# if __name__ == "__main__":
#     app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)