# import libraries
import pandas as pd
import dash
from dash import Dash, html, dcc, dash_table
import plotly.express as px

# print("dash version - ", dash.__version__)

df1 = pd.read_csv('data/daily_sales_data_0.csv')
df2 = pd.read_csv('data/daily_sales_data_1.csv')
df3 = pd.read_csv('data/daily_sales_data_2.csv')

# combine into 1 dataframe
df_candy = pd.concat([df1, df2, df3], ignore_index=True)

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
# clean 'price', remove dollar sign, convert type to float
df_pinkmorsel['price'] = (
    df_pinkmorsel['price']
    .str.replace('$', '', regex=False)
    .astype(float)
)
quantityType = df_pinkmorsel['quantity'].dtype
df_pinkmorsel['quantity'] = pd.to_numeric(df_pinkmorsel['quantity'], errors='coerce')

# 'quantity' * 'price' = 'sales'
df_pinkmorsel['sales'] = df_pinkmorsel['quantity'] * df_pinkmorsel['price']

sales_pre_increase = df_pinkmorsel[df_pinkmorsel['date'] < '2021-01-15']['sales'].sum()
sales_post_increase = df_pinkmorsel[df_pinkmorsel['date'] >= '2021-01-15']['sales'].sum()

print("sales_pre_increase: ", sales_pre_increase)
print("sales_post_increase: ", sales_post_increase)

# clean df for dash
df_dash = df_pinkmorsel.drop(columns=['product', 'price', 'quantity'])
# filter
# df containing: [sales], [date], [region]
df_output = df_dash[['sales', 'date', 'region']].copy()
# ###
# output CSV file
df_output.to_csv("pink_morsel_output.csv", index=False)

# ###

# df_feb = df_output[df_output['date'].dt.month == 2].copy()
df_feb1 = df_output[(df_output['date'].dt.month == 2) & (df_output['date'].dt.day == 1)].copy()
# ###

app = Dash(__name__)

fig = px.line(
    df_feb1,
    x='date',
    y='sales',
    color='region',   # This creates 4 separate lines
    markers=True,
)

app.layout = html.Div([
    html.H1(
        "Pink Morsels Sales Dashboard",
        style={'textAlign': 'center'}
    ),

    dcc.Graph(
        id='sales-graph',
        figure=fig
    )
])

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)