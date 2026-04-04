import pandas as pd
import numpy as np
from dash import Dash, html, dcc, Input, Output
from datetime import datetime
import plotly.express as px

df1 = pd.read_csv('data/daily_sales_data_0.csv')
df2 = pd.read_csv('data/daily_sales_data_1.csv')
df3 = pd.read_csv('data/daily_sales_data_2.csv')
# combine into 1 dataframe
df_candy = pd.concat([df1, df2, df3], ignore_index=True)

# convert date to datetime
df_candy['date'] = pd.to_datetime(df_candy['date'])
# Filter for Pink Morsels only
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

# force numericc, remove NaNs
df_pinkmorsel['sales'] = pd.to_numeric(df_pinkmorsel['sales'], errors='coerce')
df_pinkmorsel = df_pinkmorsel.dropna(subset=['sales'])

# clean df for Dash
df_output = df_pinkmorsel.drop(columns=['product', 'price', 'quantity'])

# df containing: [sales], [date], [region]
df_output = df_output[['sales', 'date', 'region']].copy()

# output CSV file
df_output.to_csv(r"C:\Users\eilis\Downloads\Vis_pink_morsel_output.csv", index=False)

np.random.seed(42)
df_grouped = (
    df_output
    .groupby([pd.Grouper(key='date', freq='3D'), 'region']) # every 3 days
    .agg(
        sales=('sales', 'sum'),
        last_date=('date', 'max')  # last actual date in the bucket, 'last_date' is new col in df
    )
    .reset_index()
)

df_grouped = df_grouped.sort_values('date')
# filter for graph date-range
df_filtered = df_grouped[
    (df_grouped["date"] >= "2021-01-01") &
    (df_grouped["date"] <= "2021-02-01")
]
df_filtered['region'] = df_filtered['region'].str.title()
df_complete = df_filtered

# create line chart
fig1 = px.line(
    df_filtered,
    x="date",   # date uses month start
    y="sales",
    color="region",
    markers=True,
)

app = Dash(__name__)

#####
app.layout = html.Div([

    # header
    html.H1(
        "Pink Morsel Sales before and after price increase"
    ),

    # MAIN CONTAINER (CSS controls layout)
    html.Div([

        # left panel
        html.Div([
            dcc.Graph(
                id='sales-graph',
                figure=fig1
            )
        ], className="graph-panel"),

        # right panel (radio buttons)
        #####################################################
html.Div([
    dcc.RadioItems(
        id='radio-region',
        options=[
            {'label': 'North', 'value': 'north'},
            {'label': 'South', 'value': 'south'},
            {'label': 'East', 'value': 'east'},
            {'label': 'West', 'value': 'west'},
            {'label': 'All Regions', 'value': 'all'},
        ],
        value='all',
        labelClassName="radio-label"
    ),

    html.Img#
        src="/assets/pink_morsel.png",
        style={
            "width": "100%",
            "marginTop": "20px",
            "borderRadius": "10px"
        }
    )

], className="controls-panel")
        #############################################
#        html.Div([
#            dcc.RadioItems(
#                id='radio-region',
#                options=[
#                    {'label': 'North', 'value': 'north'},
#                    {'label': 'South', 'value': 'south'},
#                    {'label': 'East', 'value': 'east'},
#                    {'label': 'West', 'value': 'west'},
#                    {'label': 'All Regions', 'value': 'all'},
#                ],
#                value='all',
#                labelClassName="radio-label"
#            )
#        ], className="controls-panel")

    ], className="main-container")

])
#####

@app.callback(
    Output('sales-graph', 'figure'),
    Input('radio-region', 'value')
)
def update_graph(selected_region):
    # Filter data-radio buttons
    if selected_region == "all":
        df_filtered = df_complete
    else:
        df_filtered = df_complete[
            df_complete["region"].str.lower() == selected_region
        ]
    # Create updated figure
    fig1 = px.line(
        df_filtered,
        x="date",
        y="sales",
        color="region",
        markers=True
    )
    fig1.update_layout(
        plot_bgcolor='lightpink',  # graph area
        paper_bgcolor='lightpink',  # border area
        height = 400,
        showlegend=False
    )
    # Hover style
    fig1.update_traces(
        hoverlabel=dict(
        bgcolor='#ffe6f0',
        font_color='black',
        bordercolor = '#ffb6c1'
    ),
    hovertemplate = (
        "<b>%{x|%d %b %Y}</b><br><br>"
        "Region: %{fullData.name}<br>"
        "Sales: $%{y:,.0f}"
        "<extra></extra>"
    )
)
    # Add vertical line (price increase Date)
    dt_obj = datetime.strptime(
        '15.01.2021 00:00:00,76',
        '%d.%m.%Y %H:%M:%S,%f'
    )
    dt_obj = datetime.strptime('15.01.2021 00:00:00,76',
                               '%d.%m.%Y %H:%M:%S,%f')
    DtPriceInc_millisec = dt_obj.timestamp() * 1000 # put date in milliseconds

    # vertical line showing date of price increase, after callback
    fig1.add_vline(
    #    x=dt_obj,
        x=DtPriceInc_millisec,
        line_dash="solid",
        line_color="red",
        annotation_text="Price Increase (15 Jan 2021)",
        annotation_position="top right"
    )

    return fig1
if __name__ == "__main__":
    app.run(debug=True)
#    app.run_server(debug=True)