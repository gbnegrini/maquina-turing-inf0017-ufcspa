# Imports
import os
from random import randint
import pandas as pd
import time

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
                        type = 'text',
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
                    type = 'text',
                    style={'height': 39, 'width': '50%' ,'padding': 10, 'margin-top': 20, 'margin-bottom':20}
                ),
                html.Button('RUN', id='run-button', n_clicks=0),
                html.Div(id='my-div')
            ]),

            dbc.Col([
                html.Div(id='fita-out', children=[])
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
    [Output('input-dados', 'columns'),
    Output('add-simbolo', 'value')],
    [Input('add-col-button', 'n_clicks')],
    [State('add-simbolo', 'value'),
     State('input-dados', 'columns')])
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': False, 'deletable': True
        })
        value = ''
    return existing_columns, value

@app.callback(
    [Output('fita-out', 'children')],
    [Input('run-button', 'n_clicks')],
    [State('sentence', 'value'),
     State('input-dados', 'data')])
def exibe(n_clicks, fita, dados):
    if n_clicks > 0:
        df = pd.DataFrame.from_dict(dados)
        df.set_index('estados', inplace=True)
        i = 0
        s = df.index[0]
        fita = list(fita)
        status = 'Aceita: '
        while(s != df.index[-1]):
            try:
                p = fita[i]
                f = df[p][s]
                f = str(f).replace(' ','').split(',')
                s = f[0]
                fita[i] = f[1]
                if f[2] == 'D':
                    i = i+1
                else:
                    i = i-1
            except IndexError:
                status = 'Não aceita: '
                break
        fita = ''.join(fita)
    return ['{}\n{}'.format(status,fita)]



# Roda o app Dash
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
