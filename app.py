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

# Servidor Flask
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.FLATLY])

# Autenticação
#USERNAME_PASSWORD_PAIRS = []
#auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

# Barra de navegação
nav = html.Div(dbc.NavbarSimple(
    dbc.NavItem(dbc.NavLink("Repositório",href="https://github.com/gbnegrini/maquina-turing-inf0017-ufcspa")),
    brand="Máquina de Turing",
    sticky="top",
    color="primary",
    dark=True,
    style={'font-size': 14}
))


# Corpo da página
body = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3('Instruções', style={'textAlign': 'center'}),
                html.H6('Adição de símbolos'),
                html.P('Adicione individualmente cada um dos símbolos na máquina', style={'textAlign': 'justify'}),
                html.P('Atenção: o primeiro será considerado o marcador de início e o útimo será considerado o marcador de fim da fita', style={'textAlign': 'justify', 'margin-bottom': 20}),
                html.H6('Adição de estados'),
                html.P('Adicione os estados sequencialmente clicando no botão "Adicionar estado"', style={'textAlign': 'justify'}),
                html.P('Atenção: o primeiro estado será considerado o incial e o último será considerado o estado final', style={'textAlign': 'justify', 'margin-bottom': 20}),
                html.H6('Preenchimento da tabela'),
                html.P('Preencha a tabela com as funções de transição adequadas para cada estado no formato: próximo estado, símbolo na fita, direção', style={'textAlign': 'justify'}),
                html.P('Exemplo: q0, a, D', style={'margin-bottom': 20}),
                html.H6('Sentença de entrada'),
                html.P('Preencha o campo Sentença e clique em Run para verificar se a sentença é aceita ou rejeitada pela máquina programada', style={'textAlign': 'justify', 'margin-bottom': 20}),
            ], style={'padding': 15, 'margin-bottom': 20, 'margin-left':50}),
            dbc.Col([
                html.H3('Máquina de Turing', style={'textAlign': 'center'}),
                dbc.Row([
                    dbc.Input(
                        id='add-simbolo',
                        placeholder='Símbolo',
                        value='',
                        type = 'text',
                        style={'height': 39, 'width': '20%', 'margin-right': 15}
                    ),
                    dbc.Button('Adicionar símbolo', id='add-col-button', n_clicks=0, color='primary', style={'width':'50%'})
                ], style={'padding': 15, 'margin-bottom': 20}),

                # Tabela de input dos dados
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
                    style_table={'width':'100%', 'margin-left':0},
                    style_cell={'textAlign': 'left'},
                    editable=True,
                    row_deletable=True
                ),
                dbc.Button('Adicionar estado', id='add-rows-button', n_clicks=0, style={'margin-top': 20}, color='primary'),
                dbc.Input(
                    id='sentence',
                    placeholder='Sentença',
                    value='',
                    type = 'text',
                    style={'height': 39, 'width': '100%' ,'padding': 10, 'margin-top': 20, 'margin-bottom':20}
                ),
                html.Div([html.Button('RUN', id='run-button', n_clicks=0)], style={'text-align':'center'}),
                html.Div(id='my-div')
            ], style={'padding': 15, 'margin-left': 20}),

            dbc.Col([
                html.H3('Resultado', style={'textAlign': 'center'}),
                html.Div(id='resultado', children=[]),
                html.Div(id='fita-final', children=[]),
                html.Div(id='passos', children=[])
            ], style={'padding': 15, 'margin-bottom': 20, 'text-align': 'center'})
        ]),
    ], fluid=True
)

# Instancia a página
app.layout = html.Div([nav, body])

# Funções callback

# Adição de novo estado
@app.callback(
    Output('input-dados', 'data'),
    [Input('add-rows-button', 'n_clicks')],
    [State('input-dados', 'data'),
     State('input-dados', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({columns[0]['id']: 'q{}'.format(n_clicks-1)})
    return rows

# Adição dos símbolos
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

# Lógica da Máquina de Turing
@app.callback(
    [Output('resultado', 'children'),
     Output('fita-final', 'children'),
     Output('passos', 'children')],
    [Input('run-button', 'n_clicks')],
    [State('sentence', 'value'),
     State('input-dados', 'data')])
def exibe(n_clicks, fita, dados):
    status = ''
    erro = False
    passos = []
    if n_clicks > 0:
        if dados:
            if fita:
                try:
                    df = pd.DataFrame.from_dict(dados)
                    df.set_index('estados', inplace=True)
                    i = 0
                    s = df.index[0]
                    fita = list(fita)
                    while(s != df.index[-1]):
                        try:
                            p = fita[i]
                            f = df[p][s]
                            f = str(f).replace(' ','').split(',')
                            passos.append(f)
                            s = f[0]
                            fita[i] = f[1]
                            if f[2] == 'D':
                                i = i+1
                            else:
                                i = i-1
                        except IndexError:
                            erro = True
                            break
                except:
                    erro = True
            else:
                status = dbc.Alert("Digite uma sentença", color="warning")
                return status, html.H6('Fita: {}'.format(fita)), html.H6('Passos: {}'.format(passos))
        else:
            status = dbc.Alert("Preencha a tabela", color="warning")
            return status, html.H6('Fita: {}'.format(fita)), html.H6('Passos: {}'.format(passos))

        if erro:
            status = dbc.Alert("Sentença rejeitada", color="danger")
        else:
            status = dbc.Alert("Sentença aceita", color="success")
        fita = ''.join(fita)
        return status, html.H6('Fita: {}'.format(fita)), html.H6('Passos: {}'.format(passos))
    return html.Div(), fita, passos



# Roda o app Dash
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
