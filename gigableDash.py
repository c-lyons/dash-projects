import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd
import os
from sklearn import preprocessing

colors = dict(background='#111111',
              text='#FF5733',
              markers='#FF5733')
theme_url = 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/journal/bootstrap.min.css'

data_dir = os.getcwd() + '/data/'
filename= 'coffee.csv'

logo='Welcome to Gigable'
tagline='We help businesses find quality workers.'

try:
    df = pd.read_csv(data_dir+filename)
except:
    'Failed to read data from source.'

list_of_scatter_feats = ['total_cup_points','aroma', 'flavor', 'aftertaste',
                        'acidity', 'body', 'balance', 'uniformity', 'clean_cup', 'sweetness',
                        'cupper_points']
radar_feats =   ['aroma', 'flavor', 'aftertaste',
                'acidity', 'body', 'balance', 'uniformity', 'clean_cup', 'sweetness',
                'cupper_points', 'total_cup_points', 'number_of_bags']

app = dash.Dash(external_stylesheets=[theme_url])

app.layout = html.Div(children=[
                    html.Div(
                        html.Img(src=app.get_asset_url('logo.png'),style={'height':'10%', 'width':'10%'}),
                        style={'textAlign': 'center'}),
                    html.H1(children=logo,
                            style=dict(textAlign='center', color=colors['text'])),
                    html.Div(children=tagline,
                             style=dict(textAlign='center', color=colors['text'])),
                    # adding drop down for feature 1 selection
                    html.Div(
                        dcc.Dropdown(id='feat1-picker',
                             options=[{'label':str(feat), 'value':feat} for feat in list_of_scatter_feats],
                             value=list_of_scatter_feats[0], style=dict(width='50%', display='inline-block'))),
                    # adding drop down for feature 2 selection
                    html.Div(
                        dcc.Dropdown(id='feat2-picker',
                             options=[{'label':str(feat), 'value':feat} for feat in list_of_scatter_feats],
                             value=list_of_scatter_feats[1]), style=dict(width='25%', display='inline-block')),
                    # graph object for scatter plot
                    dcc.Graph(id='scatter-1'),
                    # adding checklist for radar plot. Limiting to Top 5 Countries based on value_counts
                    html.Div(
                        dcc.Checklist(
                            id='checklist-1',
                            options=[{'label':country, 'value':country} for country in df.country_of_origin.value_counts().index[:5]],
                            value=[df.country_of_origin.value_counts().index[:5][0]],
                            labelStyle={'display': 'inline-block', 'padding':10}
                                    )
                            ),
                    # graph object for radar plot
                    dcc.Graph(id='radar-1'),
                    # creating bubble scatter
                    html.Div(dcc.Graph(id='bubble-1',
                                        figure=dict(data=[go.Scatter(
                                                            x=[df[df.country_of_origin==country]['total_cup_points'].mean()],
                                                            y=[df[df.country_of_origin==country]['flavor'].mean()],
                                                            mode='markers',
                                                            name=country,
                                                            marker=dict(
                                                                opacity=0.35,
                                                                size=[df[df.country_of_origin==country]['number_of_bags'].mean()*0.5])
                                                                ) for country in df.country_of_origin.value_counts().index[:7]],
                                                    layout=go.Layout(title='Total Points vs Flavour for Top 7 Countries',
                                                                     xaxis=dict(title='Total Cup Points'),
                                                                     yaxis=dict(title='Flavour Score'),
                                                                     hovermode='closest')))
                        )
                    ],
                    style=dict(padding=10))

def normalise_df(df):
    '''Returns normalised df for radar plots to get relative importance of feats'''
    x = df.values #returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    scaled_df = pd.DataFrame(x_scaled, columns=df.columns)
    return scaled_df

@app.callback(Output('scatter-1', 'figure'),
              [Input('feat1-picker', 'value'), Input('feat2-picker', 'value')])
def update_figure(feat1, feat2):
    traces = []
    for species in df.species.unique():
        df_by_species = df[df.species==species][list_of_scatter_feats]
        traces.append(go.Scatter(
            x = df_by_species[feat1],
            y = df_by_species[feat2],
            mode='markers',
            marker=dict(size=15, opacity=0.3, line=dict(width=1, color='black')),
            name=species))

    return dict(data=traces, layout=go.Layout(title='Plot of {} against {}'.format(feat1.upper(), feat2.upper()),
                                                xaxis=dict(title=feat1.upper()),
                                                yaxis=dict(title=feat2.upper()),
                                                hovermode='closest'))

@app.callback(Output('radar-1', 'figure'),
              [Input('checklist-1', 'value')])
def update_radar(input_countries):
    traces = []
    if len(input_countries)==0:
        traces.append(go.Scatterpolar(
            r=[0 for feat in radar_feats],
            theta=radar_feats,
            fill='toself'))
    else:
        for country in input_countries:
            temp_df = df[df.country_of_origin==country][radar_feats]
            norm_df = normalise_df(temp_df)
            values = list(norm_df.mean().values)
            traces.append(go.Scatterpolar(
                r=values,
                theta=radar_feats,
                fill='toself',
                name=country))
    return dict(data=traces, layout=go.Layout(title='Coffee Characteristics'))

if __name__=='__main__':
    app.run_server()