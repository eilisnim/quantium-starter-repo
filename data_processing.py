# import libraries
import pandas as pd
import numpy as np
from dash import Dash, html, dcc, dash_table, Input, Output

from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# To do
# FILTER PINK Morsel, output scv file of same
# input $ in displays

df1 = pd.read_csv('data/daily_sales_data_0.csv')
df2 = pd.read_csv('data/daily_sales_data_1.csv')
df3 = pd.read_csv('data/daily_sales_data_2.csv')

# Prepare dataframe
# combine into 1 dataframe
df_candy = pd.concat([df1, df2, df3], ignore_index=True)

# convert date to datetime
df_candy['date'] = pd.to_datetime(df_candy['date'])
# is  'price' & 'quantity' numeric? for adding to give 'sales'
# clean 'price', remove dollar sign, convert type to float
df_candy['price'] = (
    df_candy['price']
    .str.replace('$', '', regex=False)
    .astype(float)
)
df_candy['quantity'] = pd.to_numeric(df_candy['quantity'], errors='coerce')
# Add column 'sales' to dataframe, 'quantity' * 'price' = 'sales'
df_candy['sales'] = df_candy['quantity'] * df_candy['price']

df_pinkmorsel = (
    df_candy[df_candy['product'] == 'pink morsel']
    .sort_values(by='date', ascending=True)
)
# clean df for dash
df_pinkmorsel = df_pinkmorsel.drop(columns=['product', 'price', 'quantity'])

df_output = df_pinkmorsel[['sales', 'date', 'region']].copy()
# output csv file to Downloads
df_pinkmorsel.to_csv(r"C:\Users\eilis\Downloads\data_processing_pink_morsel.csv", index=False)

np.random.seed(42)  # location?

# adjust graph to reflect min and max dates (accurately)
first_date = df_output['date'].min()
last_date = df_output['date'].max()
print ("first_date:", first_date)
print ("last_date:", last_date)

print ("date type: ", df_output["date"].dtype.name)

df_monthly = (
    df_output
    #.groupby([pd.Grouper(key='date', freq='6MS'), 'region'])
    .groupby([pd.Grouper(key='date', freq='MS'), 'region'])
    .agg(
        sales=('sales', 'sum'),
        last_date=('date', 'max')  # last actual date in the bucket - not working
        # 14/02/2022
    )
    .reset_index()
)

df_monthly["region"] = df_monthly["region"].astype(str)
### TRY  for CLIPPING Graph at end date of dataframe
df_monthly = df_monthly[df_monthly['sales'] > 0]

# create line chart
fig1 = px.line(
    df_monthly,
    x="date",   # date uses month start
    y="sales",
    color="region",
    color_discrete_map={
        "north": "blue",
        "south": "red",
        "east": "green",
        "west": "orange"
    },
    markers=True,
    hover_data={
        "date": "|%b %Y",
        "sales": ":,.0f"
    }
)

# don't show legend, in top right corner
fig1.update_layout(showlegend=False)

# Replace each trace label starting with capital
fig1.for_each_trace(lambda t: t.update(name=t.name.title()))
###
#start_date = df_output['date'].min()
#end_date = df_output['date'].max()

#fig1.update_xaxes(range=[start_date, end_date])
### CLIP by date below - from StackOverflow

#fig1.update_layout(
#  xaxis=dict(
#    range=[df_monthly['last_date'].min(), df_monthly['last_date'].max()]
#  )
#)
# NOT CLIPPING GRAPH
fig1.update_layout(
    xaxis=dict(
        #range=[df_monthly['date'].min(), df_monthly['date'].max()]
        # last_date from above
        range = [df_monthly['date'].min(), last_date]
    )
)
### CLIP by date above NOT WORKING
#fig1.update_layout(
#    xaxis=dict(title_text="Date", range=[df_monthly['date'].min(), df_monthly['date'].max()]),
#    yaxis = dict(title_text="Sales"),
#)
#################

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
        "data_processing.py Sales before and after Pink Morsel price increase",
        style={'textAlign': 'center'}
    ),

    # Radio buttons
    html.Div([
        html.H3("Select Region"),
        dcc.RadioItems(
            id="region-selector",
            options=[
    # lower case: north etc
                {"label": "North", "value": "north"},
                {"label": "South", "value": "south"},
                {"label": "East", "value": "east"},
                {"label": "West", "value": "west"},
            ],
            value="north"
        )
    ], style={"width": "20%", "display": "inline-block", "verticalAlign": "top"}),

    # Main content
    html.Div([
        dcc.Graph(id="region-chart")
    ], style={"width": "75%", "display": "inline-block"})
])

@app.callback(
    Output("region-chart", "figure"),
    Input("region-selector", "value")
)
def update_chart(selected_region):
    filtered = df_monthly[df_monthly["region"].str.lower() == selected_region.lower()]

    fig1 = px.line(
        filtered,
        x="date",
        y="sales",
        # color="region",
        title=f"Sales - {selected_region.title()}"  # 'north' → 'North'
    )
    # put date in milliseconds for vertical line
    dt_obj = datetime.strptime('15.01.2021 00:00:00,76',
                               '%d.%m.%Y %H:%M:%S,%f')
    DtPriceInc_millisec = dt_obj.timestamp() * 1000
    # vertical line showing date of price increase Pink Morsel
    fig1.add_vline(
        x=DtPriceInc_millisec,
        line_dash="solid",
        line_color="red",
        annotation_text="Price Increase Pink Morsel (15 Jan 2021)",
        # annotation_position="center"
    )

    return fig1

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)