import pandas as pd
import plotly.express as px
import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import json

df = pd.read_csv(f'./data/dashboard-data.csv', sep='|', low_memory=False)
dfRegions = pd.read_csv('./data/regions.csv', sep=';')
dfDepts = pd.read_csv('./data/departement.csv', sep=';')
df.code_departement = df.code_departement.astype('str').str.pad(2, side='left', fillchar='0')

dfScales = {'region': dfRegions, 'departement': dfDepts}
geojson = {}

with open('./data/metropole-version-simplifiee.geojson') as response:
    geojson['metropole'] = json.load(response)

with open('./data/regions-version-simplifiee.geojson') as response:
    geojson['region'] = json.load(response)

with open('./data/departements-version-simplifiee.geojson') as response:
    geojson['departement'] = json.load(response)

echelle = {
    'Departement': 'departement',
    'Region' : 'region',
}

def inputTolist(value):
    if(type(value) == str):
        return [int(value)]
    else:
        return [int(x) for x in value]
    
def card(title, body=[], id=''):
    return html.Div([
            html.H3(children=title, className='cs-card-title'),
            html.Label(id=id, className='cs-card-body')
        ], className='cs-card'),
def roundFormat(amount, rounded=True):
    if(rounded):
        amount = round(amount, 2)
    return format(amount, ',').replace(',', ' ')

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.Div([
            html.Label(children='Année'),
            dcc.Dropdown(df['annee'].unique(), '2018', id='years-selection', className='select-field', multi=True),
        ], className='filter-item'),

        html.Div([
            html.Label(children='Echelle'),
            dcc.Dropdown(list(echelle.keys()), 'Departement', id='scale-selection', className='select-field'),
        ], className='filter-item'),
    ], className='filters',),

    html.Div([
        html.H3(children=[
            html.Span('Chiffres des ventes '), 
            html.Span(id='filter-dates-name'), 
            html.Span(' par '), 
            html.Span(id='filter-scale-name'), 
        ], id='number-title', className='d-none')
    ]),
    html.Div([
        html.Div([
            html.H3(children='Total de vente', className='cs-card-title'),
            html.Label(id='nb-vente', className='cs-card-body')
        ], className='cs-card'),
        html.Div([
            html.H3(children='Moyenne', className='cs-card-title'),
            html.Label(id='avg-vente', className='cs-card-body')
        ], className='cs-card'),
        html.Div([
            html.H3(children='Médiane', className='cs-card-title'),
            html.Label(id='median-vente', className='cs-card-body')
        ], className='cs-card'),
    ], className='cs-card-container'),
    html.Div([
        html.H3(children='Evolution des ventes en fonciton du temps', id='time-title', className='d-none')
    ],),
    html.Div([
        html.Div([
            html.H3(children='Evolution des ventes par mois', className='cs-chart-title'),
            dcc.Graph(id='graph-content', style={'height':'400px'}),
        ], className='month-chart cs-chart'),
        html.Div([
            html.H3(children='Evolution des ventes par année', className='cs-chart-title'),
            dcc.Graph(id='years-graph', style={'height':'400px'}),
        ], className='years-chart cs-chart'),
    ], className='date-charts', style={ 'gap' : '', }),
    html.Div([
        html.H3(children='Représentation géographique des ventes', id='geo-title', className='d-none')
    ]),
    html.Div([
        html.Div([
            html.H3(children='Représentation géographique des ventes', className='cs-chart-title'),
            dcc.Graph(id='graph-map'),
        ], className='map-chart cs-chart'),
        html.Div([
            html.H3(children='Cliquez sur un departement !!', id='mapd-title', className='cs-chart-title'),
            dbc.ListGroup(
                [
                    dbc.ListGroupItem([
                        html.Div('Population:', className='fw-bold me-2'),
                        html.Div(id='mapd-population'),
                    ], color='secondary', className='d-flex justify-content-between'),
                    dbc.ListGroupItem([
                        html.Label('Nombre de ventes:', className='fw-bold me-2'),
                        html.Label(id='mapd-nbvente'),
                    ], color='light', className='d-flex justify-content-between'),
                    dbc.ListGroupItem([
                        html.Label('Valeur foncière:', className='fw-bold me-2'),
                        html.Label(id='mapd-avgvente'),
                    ], color='secondary', className='d-flex justify-content-between'),
                    dbc.ListGroupItem([
                        html.Label('Prix du mètre carré:', className='fw-bold me-2'),
                        html.Label(id='mapd-prix'),
                    ], color='light', className='d-flex justify-content-between'),
                ], className='mt-2'
            )
        ], id='map-details', className='map-details cs-chart'),
    ], className='geo-charts'),
    html.Div([
        html.H3(children='Représentation des ventes par Type de bien', id='type-local-title', className='d-none')
    ]),
    html.Div([
        html.Div([
            html.H3(children='Détails des ventes par type de propriété', className='cs-chart-title'),
            dcc.Graph(id='graph-bar', style={'max-height': '400px', 'height': '100%'}),
        ], className='type-bar-chart cs-chart'),
        html.Div([
            html.H3(children='Proportion des types propriété vendus', className='cs-chart-title'),
            dcc.Graph(id='pie-chart-local'),
        ], className='type-pie-chart cs-chart'),
    ], className='type-charts align-items-'),
], className='mx-3')


@callback(
    [
        Output('nb-vente', 'children'),
        Output('avg-vente', 'children'),
        Output('median-vente', 'children'),
        Output('filter-dates-name', 'children'),
    ],
    Input('years-selection', 'value')
)
def update_stats(value):
    years =inputTolist(value)
    dff = df[df['annee'].isin(years)]
    value = dff['Valeur fonciere']
    if len(years) > 1:
        dates = f'de {min(years)} à {max(years)}'
    elif len(years) == 1:
        dates = f'en {years[0]}'
    else:
        dates = 'par année'
    return roundFormat(dff.shape[0]), roundFormat(value.mean()), roundFormat(value.median()), dates


@callback(
    Output('graph-content', 'figure'),
    Input('years-selection', 'value')
)
def update_graph(value):
    years = inputTolist(value)
    dff = df[df['annee'].isin(years)]
    fig = px.line(
        dff.groupby(['annee', 'mois', 'nom_mois'])['Valeur fonciere'].mean().reset_index(),
        x='nom_mois',
        y='Valeur fonciere',
        color='annee',
        # title='Évolution de la moyenne de la valeur foncièce au cours de l\'année'
    )
    fig.update_layout(margin={'r': 0, 't': 24, 'l': 0, 'b': 0})
    fig.update_layout(legend={'orientation': 'h', 'yanchor': 'top', 'y': 1.1, 'xanchor': 'right', 'x': 1 , 'bgcolor': 'rgba(255,0,0,0)'})
    return fig

@callback(
    Output('years-graph', 'figure'),
    Input('years-selection', 'value')
)
def update_years_graph(value):
    years = inputTolist(value)
    dff = df[df['annee'].isin([2018, 2019, 2020, 2021])]
    # dff = df[df['annee'].isin(years)]
    fig = px.bar(
        dff.groupby(['annee'])['Valeur fonciere'].mean().reset_index(),
        x='annee',
        y='Valeur fonciere',
    )
    fig.update_layout(margin={'r': 0, 't': 24, 'l': 0, 'b': 0})
    fig.update_layout(legend={'orientation': 'h', 'yanchor': 'top', 'y': 1.1, 'xanchor': 'right', 'x': 1 , 'bgcolor': 'rgba(255,0,0,0)'})
    return fig


@callback(
    Output('graph-bar', 'figure'),
    Input('years-selection', 'value')
)
def update_bar_graph(value):
    years = inputTolist(value)
    dff = df[df['annee'].isin(years)]
    fig = px.histogram(
        dff.groupby(['Type local', 'annee'])['Valeur fonciere'].mean().reset_index(),
        x='Type local',
        y='Valeur fonciere',
        height=300,
        color='annee',
        barmode='group',
        # title='Title'
    )
    fig.update_layout(margin={'r': 0, 't': 24, 'l': 0, 'b': 0})
    fig.update_layout(legend={'orientation': 'h', 'yanchor': 'top', 'y': 1.1, 'xanchor': 'right', 'x': 1 , 'bgcolor': 'rgba(255,0,0,0)'})
    return fig


@callback(
    [
        Output('graph-map', 'figure'),
        Output('filter-scale-name', 'children'),
    ],
    Input('scale-selection', 'value'),
    Input('years-selection', 'value')
)
def update_map(value, year):
    scale = echelle[value]
    years = inputTolist(year)
    dff = df[df['annee'].isin(years)].groupby(['annee', 'code_'+scale])['Valeur fonciere'].mean().reset_index()
    dff = dfScales[scale].merge(dff, how='left', on='code_'+scale).fillna(0)
    fig = px.choropleth(dff, geojson=geojson[scale], featureidkey='properties.code', locations='code_'+scale, color='Valeur fonciere',
                        projection="mercator", color_continuous_scale=px.colors.sequential.Blues)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(showlegend=False,
                        margin={"r":0,"t":0,"l":0,"b":0},
                    )
    return fig, scale

@callback(
    [
        Output('mapd-title', 'children'),
        Output('mapd-population', 'children'),
        Output('mapd-nbvente', 'children'),
        Output('mapd-avgvente', 'children'),
        Output('mapd-prix', 'children'),
    ],
    [
        Input('graph-map', 'clickData'),
        Input('scale-selection', 'value'),
        Input('years-selection', 'value')
    ],
)
def update_figure(clickData, scale, yValues):
    title = f'Cliquez sur un {scale} !!'
    if clickData is not None:
        scale = echelle[scale]
        years = inputTolist(yValues)
        # recuperer le code departement ou le code region
        location = clickData['points'][0]['location']
        dff = df[(df['annee'].isin(years)) & (df['code_'+scale] == location)]
        
        dfLoc = dfScales[scale]
        address = dfLoc[dfLoc['code_'+scale] == location]['nom_'+scale]
        if(address.shape[0] > 0):
            title = address.iloc[0]

        if(dff.shape[0] > 0):
            return title, roundFormat(dff.population.iloc[0], False), roundFormat(dff.shape[0], False), roundFormat(dff['Valeur fonciere'].mean()), roundFormat(dff['metre carre'].iloc[0])
        else:
            return title, 0,0,0,0
        
    return title, 0, 0, 0, 0
@callback(
    Output('pie-chart-local', 'figure'),
    Input('years-selection', 'value')
)
def update_pie_local(value):
    years = inputTolist(value)
    dff = df[df['annee'].isin(years)].groupby(['annee', 'Type local'])['Valeur fonciere'].mean().reset_index()
    fig = px.pie(dff, values='Valeur fonciere', names='Type local')
    # fig.update_layout(legend={'orientation': 'h', 'yanchor': 'top', 'y': 1.02, 'xanchor': 'right', 'x': 1 , 'bgcolor': 'rgba(255,0,0,0)'})
    fig.update_layout(showlegend=False)
    return fig