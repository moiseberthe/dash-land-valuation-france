import pickle
import pandas as pd
import dash
import requests
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback, State

regions = pd.read_csv('./data/regions.csv', sep=';')
departements = pd.read_csv('./data/departement.csv', sep=';')


with open("./models/random-forest-regressor-tree-all.pkl", "rb") as f:
    model = pickle.load(f)
regresssor = model['model']
scaler = model['scaler']

def estimate(metre_carre, population, surface):
    x = pd.DataFrame([[metre_carre,	population,	surface]], columns=regresssor.feature_names_in_)
    x = pd.DataFrame(scaler.transform(x), columns=regresssor.feature_names_in_)
    v = regresssor.predict(x)[0]
    return v

fields = [
    {'id': 'select-departement'},
    {'id': 'select-type-local'},
    {'id': 'surfaces'},
    {'id': 'nb-pieces'},
]
locatType_to_code = {
    'Maison': 1,
    'Appartement': 2,
    'Dépendance': 3,
    'Local industriel. commercial ou assimilé': 4,
}
dash.register_page(__name__)

layout = html.Div([
    html.H3('Estimer votre propriété', className='mb-3'),
    html.Div([
        html.H3('Localisation', className='mb-3'),
        dbc.Row([
            dbc.Col(
                dbc.FormFloating([
                    dbc.Select(
                        id="select-region",
                        options=[{'label': r['nom_region'], 'value': r['code_region']} for i, r in regions.iterrows()],
                        value='84'
                    ),
                    dbc.Label(['Région']),
                ]),
                width=6
            ),
            dbc.Col(
                dbc.FormFloating([
                    dbc.Select(
                        id="select-departement",
                        options=[{"label": "Option 0", "value": "0"},],
                        value='0'
                    ),
                    dbc.Label(['Département']),
                ]),
                width=6
            ),
        ], className='mb-5'),
    ],
    className='form-section'),
    html.Div([
        html.H3('Caractéristiques du bien', className='mb-3'),
        dbc.Row([
            dbc.Col(
                dbc.FormFloating([
                    dbc.Select(
                        id="select-type-local",
                        options=[
                            {'label': 'Maison', 'value': 'Maison'},
                            {'label': 'Appartement', 'value': 'Appartement'},
                            {'label': 'Dépendance', 'value': 'Dépendance'},
                            {'label': 'Local industriel', 'value': 'Local industriel. commercial ou assimilé'},
                        ],
                        value='Maison',
                    ),
                    dbc.Label(['Type']),
                ]),
                width=4
            ),
            dbc.Col(
                dbc.FormFloating([
                    dbc.Input(type='number', id='surfaces', placeholder='surface'),
                    dbc.Label('Surface'),
                ]),
                width=4
            ),
            dbc.Col(
                dbc.FormFloating([
                    dbc.Input(type='number', id='nb-pieces', placeholder='surface'),
                    dbc.Label('Nombre de pièces principales'),
                ]),
                width=4
            ),
        ], className='mb-4'),
    ],
    className='form-section'),
    html.Div([
        html.H3('Estimation', className='mb-3'),
        dbc.Row([
            dbc.Col([
                html.Span('Selon les informations fournies votre propiété est estimer à '),
                html.Span('100000', id='valeur-fonciere', className='fw-bold'),
                html.Span(' Euro'),
            ], width=12, id='estimation-result')
        ],className='mb-4')
    ],
    id='estimation',
    className='form-section estimate'),
    
    dbc.Button('Estimer', color='primary', className='p-3 px-5', id='submit-val', n_clicks=0),
    html.Div(id='container-button-basic')
], className='container')

@callback(
    [
        Output('select-departement', 'options'),
        Output('select-departement', 'value'),
    ],
    Input('select-region', 'value')
)
def update_depts(value):
    value = 84 if value == '0' else int(value)
    depts = departements[departements['code_region'] == value]
    options = [{'label': r['nom_departement'], 'value': r['code_departement']} for i, r in depts.iterrows()]
    return options, options[0]['value']

@callback(
    [
        Output('estimation', 'className'),
        Output('estimation-result', 'children'),
    ],
    Input('submit-val', 'n_clicks'),
    [State(f['id'], 'value') for f in fields],
    prevent_initial_call=True
)
def update_output(n_clicks, departement, type, surface, nbPiece):
    dep_info = departements[departements['code_departement'] == departement]
    
    population = dep_info['population'].values[0]
    metre_carre = dep_info['metre carre'].values[0]

    try:
        valeur = estimate(metre_carre, population, surface)
        valeur = round(valeur, 2)
        valeur = format(valeur, ',').replace(',', ' ')
        return 'form-section estimate show', [
                html.Span('Selon les informations fournies votre propiété est estimer à '),
                html.Span(valeur, id='valeur-fonciere', className='fw-bold'),
                html.Span(' Euro'),
            ]
    except:
        return 'form-section estimate show', [
                html.Span('Une erreur est survenue !! Verifiez que tous les champs sont correctement remplis ', className='alert alert-danger'),
            ]
        
    # response = requests.get(f'http://127.0.0.1:5000/estimate?departement={departement}={metre_carre}&surface={surface}')
    # response = response.json()['data']
    # return f'Selon les informations fournies votre propriété est estimée à : {response}'
