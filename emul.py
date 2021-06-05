import os
import dash
from dash.dependencies import Input, Output 
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import re
import statsmodels.formula.api as smf
import chart_studio
import plotly.graph_objs as go

raw = pd.read_csv('emulsion.csv')

dct = {}
dct.setdefault('K3PO4', [])
dct.setdefault('buffer', [])
dct.setdefault('outcome', [])

for i in range(len(raw)):
    for case in range(raw.loc[i, 'tot_case']):
        dct['K3PO4'].append(raw.loc[i, 'K3PO4'])
        dct['buffer'].append(raw.loc[i, 'buffer'])
        if case < raw.loc[i, 'good_case']:
            dct['outcome'].append(1)
        else:
            dct['outcome'].append(0)

df = pd.DataFrame(data = dct)
model = smf.logit(data = df, formula = 'outcome ~ K3PO4 + buffer')
results = model.fit()
interval = np.linspace(1, df.K3PO4.max())


app = dash.Dash(__name__)
server = app.server
port = int(os.environ.get("PORT", 5000))

app.layout = html.Div(
                  children = [ # title
                               html.H2('Logistic regression - '),
                               html.Hr(),
                  html.Div(
                       children = [  # this container is to host control components
                                    html.H3('Select buffer volume - '),
                                    html.Div(
                                             [
                                               dcc.Slider(
                                                          id = 'slider_buffer',
                                                          min = 0,
                                                          max = 2,
                                                          value = 1,
                                                          step = 0.1,
                                                          tooltip = {'always_visible' : True}
                                                         )
                                             ],
                                               style = {
                                                         'width' : '65%',
                                                         'align-items' : 'left'
                                                       }
                                             ),
                                    html.Button(
                                                 'Clear',
                                                 id = 'button_clr',
                                                 style = {
                                                           'width' : '8%',
                                                           'height' : 25,
                                                           'fontSize' : 14                                                                                                               
                                                             }
                                                   ),
                                    html.H3(''),
                                    html.Hr()
                                      ]
                              ),
                      html.Div(
                           children = [
                                        html.H3('Likelihood of no emulsion formation - '),
                                        dcc.Graph(
                                                   id = 'graph',
                                                   style = {
                                                             'width' : '75%',
                                                             'height' : 500
                                                               }
                                                     )
                                          ]
                                  )
                                 ]
                         )

@app.callback(
               Output('graph', 'figure'),
               Output('button_clr', 'n_clicks'),
               Input('slider_buffer', 'value'),
               Input('button_clr', 'n_clicks')               
                 )
def update_graph(value_buf, clicks_clr):
    log_odds = results.params.values[0] + results.params.values[1] * interval +\
                                          results.params.values[2] * value_buf
    odds = np.exp(log_odds)
    prob = odds / (1 + odds)
    trace = go.Scatter(
                        x = interval,
                        y = prob,
                        mode = 'lines',
                        line = {'width' : 1} 
                          )
    figure = go.Figure(trace)
    figure.layout.title = 'Prediction of likelihood of not having an emulsion'
    figure.layout.xaxis.title = 'K3PO4 stoichiometry'
    figure.layout.yaxis.title = 'Likelihood of no emulsion'
            
    if clicks_clr is None:
        return figure, None
    
    else:
        return '', None

if __name__ == '__main__':
    emul.run_server(debug = False, 
                   host="0.0.0.0",
                   port=port)
