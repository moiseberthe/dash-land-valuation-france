import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, assets_url_path='assets', external_stylesheets=[dbc.themes.BOOTSTRAP])

page_name = {'Home': 'Accueil', 'Data': 'Données', 'Estimate': 'Estimer un bien'}
app.layout = html.Div([
    html.Div([
        html.H1('DashBoard', style={'margin': '0'}),
        html.Div([
            html.Div(
                dcc.Link(f"{page_name[page['name']]}", href=page["relative_path"], className='cs-nav-link'),
                className='cs-nav-div'
            ) for page in dash.page_registry.values()
        ], className='d-flex cs-nav-ul'),
    ], className='cs-navbar'),
    dash.page_container 
])

if __name__ == '__main__':
    app.run(debug=True)