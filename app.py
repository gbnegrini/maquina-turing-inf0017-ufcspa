# Import required libraries
import os
from random import randint

import plotly.plotly as py
from plotly.graph_objs import *

import flask
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_auth

USERNAME_PASSWORD_PAIRS = [['infobio', 'infobio']]

# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
app.layout = html.Div([

    html.Div([html.P('Máquina de Turing - Entrada de dados'),
              html.P('Grupo: Alice Nascimento, Guilherme Negrini, Júlia Martins, Sofia Faber')]),
    html.Div([
        dcc.Input(
            id='add-simbolo',
            placeholder='Símbolo',
            value='',
            style={'height': 4, 'padding': 10}
        ),
        html.Button('Adicionar símbolo', id='adding-rows-button', n_clicks=0)
    ], style={'marginBottom': 20}),

    dash_table.DataTable(
        id='input-dados',
        columns=[{
            'name': 'Estados',
            'id': 'estados',
            'deletable': True,
            'renamable': True
        }],
        data=[
            {'estados': 'q{}'.format(j)}
            for j in range(0,5)
        ],
        style_table={'width':800},
        style_cell={'textAlign': 'left'},
        editable=True,
        row_deletable=True
    ),

    html.Button('Adicionar estado', id='editing-rows-button', n_clicks=0),
])


@app.callback(
    Output('input-dados', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('input-dados', 'data'),
     State('input-dados', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output('input-dados', 'columns'),
    [Input('adding-rows-button', 'n_clicks')],
    [State('add-simbolo', 'value'),
     State('input-dados', 'columns')])
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
