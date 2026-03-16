# import libraries
import pandas as pd
import numpy as np
from dash import Dash, html, dcc, dash_table
from datetime import datetime
import plotly.express as px
# print("dash version - ", dash.__version__)

df1 = pd.read_csv('data/daily_sales_data_0.csv')
df2 = pd.read_csv('data/daily_sales_data_1.csv')
df3 = pd.read_csv('data/daily_sales_data_2.csv')

# combine into 1 dataframe
df_candy = pd.concat([df1, df2, df3], ignore_index=True)

# convert date to datetime
df_candy['date'] = pd.to_datetime(df_candy['date'])

df_pinkmorsel = (
    df_candy[df_candy['product'] == 'pink morsel']
    .sort_values(by='date', ascending=True)
)
# is  'price' & 'quantity' numeric? for adding to give 'sales'
# clean 'price', remove dollar sign, convert type to float
df_pinkmorsel['price'] = (
    df_pinkmorsel['price']
    .str.replace('$', '', regex=False)
    .astype(float)
)
quantityType = df_pinkmorsel['quantity'].dtype
df_pinkmorsel['quantity'] = pd.to_numeric(df_pinkmorsel['quantity'], errors='coerce')

# 'sales' = 'quantity' * 'price'
df_pinkmorsel['sales'] = df_pinkmorsel['quantity'] * df_pinkmorsel['price']

# clean df for Dash
df_output = df_pinkmorsel.drop(columns=['product', 'price', 'quantity'])

# df containing: [sales], [date], [region]
df_output = df_output[['sales', 'date', 'region']].copy()

# output CSV file
# C:\Users\eilis\OneDrive\Documents\Forage SD Pycharm\data
df_output.to_csv(r"C:\Users\eilis\Downloads\Vis_pink_morsel_output.csv", index=False)

np.random.seed(42)

df_grouped = (
    df_output
    .groupby([pd.Grouper(key='date', freq='MS'), 'region'])
    .agg(
        sales=('sales', 'sum'),
        last_date=('date', 'max')  # last actual date in the bucket, 'last_date' is new col in df
    )
    .reset_index()
)

# REMOVE all records for first and last month, incomplete months, causing inaccurate graph, due to groupby behavour
#Find the first and last months directly from the date column
first_month = df_grouped['date'].dt.to_period('M').min()
last_month = df_grouped['date'].dt.to_period('M').max()

#Filter them out
df_complete = df_grouped[
    (df_grouped['date'].dt.to_period('M') != first_month) &
    (df_grouped['date'].dt.to_period('M') != last_month)
]
df_complete = df_complete.sort_values('date')

# create line chart
fig1 = px.line(
    df_complete,
    x="date",   # date uses month start
    y="sales",
    color="region",
    markers=True,
    hover_data={
        "date": "|%b %Y",
        "sales": ":,.0f"
    }
)
# does code Impact? ans No
#fig1.update_layout(
#  xaxis=dict(
#    range=[df_grouped['date'].min(), df_grouped['date'].max()]
#  )
#)
# put date in milliseconds - Price Increase Date
dt_obj = datetime.strptime('15.01.2021 00:00:00,76',
                           '%d.%m.%Y %H:%M:%S,%f')
DtPriceInc_millisec = dt_obj.timestamp() * 1000

print('Date of price inc. in millisecs: ', DtPriceInc_millisec)
# vertical line showing date of price increase
fig1.add_vline(
    x=DtPriceInc_millisec,
    line_dash="solid",
    line_color="red",
    annotation_text="Price Increase (15 Jan 2021)",
    annotation_position="top right"
)

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Visualisation2 Sales before and after price increase",
        style={'textAlign': 'center'}
    ),

    dcc.Graph(
        id='sales-graph',
        figure=fig1
    )
])

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)