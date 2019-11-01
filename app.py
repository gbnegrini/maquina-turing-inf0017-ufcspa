# Imports
import os
from random import randint
import pandas as pd

import plotly.plotly as py
from plotly.graph_objs import *

import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_auth
import dash_bootstrap_components as dbc

# Servidor Flaks
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Autenticação
USERNAME_PASSWORD_PAIRS = [['infobio', 'infobio']]
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

# Barra de navegação
nav = html.Div(dbc.NavbarSimple(
    dbc.NavItem(dbc.NavLink("Repositório",href="https://github.com/gbnegrini/maquina-turing-inf0017-ufcspa")),
    brand="Máquina de Turing",
    sticky="top",
    color="secondary",
    dark=True,
    style={'font-size': 14}
))

# Corpo da página
body = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3('Entrada de dados'),
                dbc.Row([
                    dbc.Input(
                        id='add-simbolo',
                        placeholder='Símbolo',
                        value='',
                        style={'height': 39, 'width': 100, 'margin-right': 15}
                    ),
                    dbc.Button('Adicionar símbolo', id='add-col-button', n_clicks=0)
                ], style={'padding': 15, 'margin-bottom': 20}),

                dash_table.DataTable(
                    id='input-dados',
                    columns=[{
                        'name': 'Estados',
                        'id': 'estados',
                        'deletable': True,
                        'renamable': False
                    }],
                    data=[
                    ],
                    style_table={'width':'50%', 'margin-left':0},
                    style_cell={'textAlign': 'left'},
                    editable=True,
                    row_deletable=True
                ),
                dbc.Button('Adicionar estado', id='add-rows-button', n_clicks=0, style={'margin-top': 20}),
                dbc.Input(
                    id='sentence',
                    placeholder='Sentença',
                    value='',
                    style={'height': 39, 'width': '50%' ,'padding': 10, 'margin-top': 20, 'margin-bottom':20}
                ),
                html.Button('RUN', id='run-button')
            ])
        ])
    ]
)

# Instancia a página
app.layout = html.Div([nav, body])

# Funções callback
@app.callback(
    Output('input-dados', 'data'),
    [Input('add-rows-button', 'n_clicks')],
    [State('input-dados', 'data'),
     State('input-dados', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({columns[0]['id']: 'q{}'.format(n_clicks-1)})
    return rows


@app.callback(
    Output('input-dados', 'columns'),
    [Input('add-col-button', 'n_clicks')],
    [State('add-simbolo', 'value'),
     State('input-dados', 'columns')])
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': False, 'deletable': True
        })
    return existing_columns

# Roda o app Dash
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
