import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# import plotly.offline as pyo
import numpy as np
import pandas as pd
import os
import time
from datetime import datetime

from urllib.request import urlopen
import json

colors = dict(background='#111111',
              text='#FF5733',
              figureTitles='#0048a6',
              markers='#FF5733')
# theme_url = 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/journal/bootstrap.min.css'
logo='Welcome to Gigable'
tagline='We help businesses find quality workers.'

# run once to save data locally
# url = 'https://opendata-geohive.hub.arcgis.com/datasets/d9be85b30d7748b5b7c09450b8aede63_0.geojson?outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D'
# with urlopen(url) as response:
#     counties = json.load(response)
#
# writing json to local dir
# with open('data/geoJson.json', 'w') as outfile:
#     json.dump(counties['features'], outfile)

def convertToTimestamp(df):
    '''Converts input df timestamp col to datetime format'''
    df['properties.TimeStamp'] = df['properties.TimeStamp'].apply(lambda x: pd.to_datetime(x))
    return df

def getDates(date_time_col):
    '''Converts datetime to date in new col'''
    date_col = date_time_col.apply(lambda x: x.date())
    return date_col

def getTimeSeries(df, start=None, end=None):
    '''filters dataframe between start and end dates and returns groupby county'''
    if start==None: start=df['properties.Date'].min()
    if end==None: end=df['properties.Date'].max()
    df_filtered = df[(df['properties.Date']>=pd.to_datetime(start))&(df['properties.Date']<=pd.to_datetime(end))]
    return df_filtered.groupby('properties.ORIGID').mean()

# For date range slider workaround
def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')

def getMarks(start, end, Nth=30):
    ''' Returns the marks for labeling.
        Every Nth value will be used.
    '''
    result = {}
    for i, date in enumerate(daterange):
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m'))
    return result

def get_cases_and_rates(df):
    '''gets new daily cases and incidence rates and saves to new cols in df'''
    # getting new daily cases for each county for plots
    results = []
    for county in df['properties.CountyName'].unique():
        # appending new cases results to list of series
        results.append(df[df['properties.CountyName']==county]['properties.ConfirmedCovidCases'].diff().fillna(0))
    # saving daily new cases by county to new column
    df['NewCases'] = pd.concat([result for result in results], axis=0)

    # getting new daily cases for each county for plots
    results = []
    for county in df['properties.CountyName'].unique():
        # appending new cases results to list of series
        results.append(df[df['properties.CountyName']==county]['NewCases'].rolling(window=14).mean())
    # saving daily new cases by county to new column
    df['TwoWeekIncidence'] = pd.concat([result for result in results], axis=0)

    results = []
    for county in df['properties.CountyName'].unique():
        # appending new cases results to list of series
        results.append(df[df['properties.CountyName']==county]['properties.ConfirmedCovidDeaths'].diff())
    # saving daily new cases by county to new column
    df['NewDeaths'] = pd.concat([result for result in results], axis=0)

    # getting new daily cases for each county for plots
    results = []
    for county in df['properties.CountyName'].unique():
        # appending new cases results to list of series
        results.append(df[df['properties.CountyName']==county]['NewDeaths'].rolling(window=14).mean())
    # saving daily new cases by county to new column
    df['TwoWeekIncidenceDeaths'] = pd.concat([result for result in results], axis=0)

    return df

with open('data/geoJson.json', 'r') as f:
    json_data = json.load(f)
all_counties = json_data[0:26]  # creating subset of full JSON and taking first 26 entries to get 26 counties geometry

# importing second df which contains country level info on deaths/ additional world socio econ info
world_df = pd.read_csv('data/owid-covid-data.csv')
ire_df = world_df[world_df['location']=='Ireland']  # Try using .loc[row_indexer,col_indexer] = value instead TODO
ire_df.date = pd.to_datetime(ire_df.date)  # converting date to datetime
ire_df.date = getDates(ire_df.date)
# TODO - move to main function?
df = pd.json_normalize(json_data)
df = convertToTimestamp(df)
df['properties.Date'] = getDates(df['properties.TimeStamp'])
df['CasesPer100k'] = df['properties.ConfirmedCovidCases']/(df['properties.PopulationCensus16']/100000)
df.fillna(0, inplace=True)
df = get_cases_and_rates(df)

full_df = ire_df.merge(df, left_on=ire_df.date, right_on=df['properties.Date'], how='inner')

daterange = pd.date_range(start=full_df['properties.Date'].min(),
                          end=full_df['properties.Date'].max(),
                          freq='D')

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
                    dbc.Row([
                        dbc.Col(
                            html.Div(
                                html.Img(src=app.get_asset_url('logo.png'),style={'height':'100%', 'width':'100%'}),
                                style={'textAlign': 'centre'}),
                            width=2),
                        dbc.Col([
                            html.H1(children=logo,
                                    style=dict(textAlign='left', color=colors['text'])),
                            html.Div(children=tagline,
                                    style=dict(textAlign='left', color=colors['text']))],
                            width=5)]),
                    dbc.Row(html.Div(' ')),
                    dbc.Row([
                            dbc.Col([
                                html.Div(['COVID Cases in Ireland - Per 100k Population'], style=dict(textAlign='center', color=colors['figureTitles'])),
                                html.Div(dcc.Graph(id='choropleth'))],
                                         width=5),
                            dbc.Col([
                                html.Div(['COVID-19 in Ireland'], style=dict(textAlign='center', color=colors['figureTitles'])),
                                html.Div(dcc.Graph(id='scatter'))], width=5),
                            dbc.Col([
                                daq.ToggleSwitch(
                                        id='cases-deaths-toggle',
                                        label={'label':'Cases - Deaths','display': 'inline-block', 'padding':3},
                                        value=False),
                                daq.ToggleSwitch(
                                        id='county-country-toggle',
                                        label={'label':'County - Country','display': 'inline-block', 'padding':3},
                                        value=False),
                                daq.ToggleSwitch(
                                        id='daily-cum-toggle',
                                        label={'label':'Daily - Cumulative','display': 'inline-block', 'padding':3},
                                        value=False),
                                daq.ToggleSwitch(
                                        id='linear-log-toggle',
                                        label={'label':'Linear - Log','display': 'inline-block', 'padding':3},
                                        value=False),
                                    ])]),
                    html.Div(['Date Range Slider - Select the dates you want using the slider'], style=dict(textAlign='center', color=colors['figureTitles'])),
                    dcc.RangeSlider(
                                id='year_slider',
                                min = unixTimeMillis(daterange.min()),
                                max = unixTimeMillis(daterange.max()),
                                value = [unixTimeMillis(daterange.min()),
                                        unixTimeMillis(daterange.max())],
                                marks=getMarks(daterange.min(),
                                            daterange.max())
                                        )
                    ])

@app.callback(Output('choropleth', 'figure'), [Input('year_slider', 'value')])
def update_figure(input_list):
    traces = []
    start = datetime.fromtimestamp(input_list[0])  # converting unix ts to datetime
    end = datetime.fromtimestamp(input_list[1])  # converting unix ts to datetime
    date_df = getTimeSeries(full_df, start=start, end=end)
    date_df = date_df.join(full_df[['properties.ORIGID', 'properties.CountyName']], on='properties.ORIGID', how='inner')
    for county in date_df['properties.CountyName'].unique():
        ix = int(date_df[date_df['properties.CountyName']==county]['properties.ORIGID'].values)
        traces.append(go.Choroplethmapbox(geojson=all_counties[ix-1],
                                    locations=date_df['properties.ORIGID'],
                                    z=date_df['properties.PopulationProportionCovidCases'],
                                    name=county,
                                    featureidkey='properties.ORIGID',
                                    colorscale="Viridis",
                                    marker_opacity=0.35,
                                    marker_line_width=2))
    return dict(data=traces,
                layout=go.Layout(title='COVID-19 Cases Ireland',
                                mapbox_style="carto-positron",
                                mapbox_zoom=5.25,
                                mapbox_center={"lat": 53.7168, "lon": -7.8367},
                                margin={"r":0,"t":0,"l":0,"b":0}))
@app.callback(Output('county-country-toggle', 'value'),
              [Input('cases-deaths-toggle', 'value'), Input('county-country-toggle', 'value')])
def update_toggles(deaths_toggle, county_toggle):
    '''make sure county level info disabled for deaths True toggle'''
    if (deaths_toggle==True)&(county_toggle==False):
        return True
    else:
        return county_toggle

@app.callback(Output('scatter', 'figure'),
              [Input('year_slider', 'value'),
               Input('cases-deaths-toggle', 'value'),
               Input('county-country-toggle', 'value'),
               Input('daily-cum-toggle', 'value'),
               Input('linear-log-toggle', 'value')])
def update_scatter(input_list, cases_toggle, county_toggle, daily_toggle, log_toggle):
    traces = []
    start = datetime.fromtimestamp(input_list[0]).date()  # converting unix ts to datetime
    end = datetime.fromtimestamp(input_list[1]).date()  # converting unix ts to datetime
    # setting temp_df for use in plotting filtered by dates
    temp_df = full_df[(full_df['properties.Date']>=start)&(full_df['properties.Date']<=end)]
    # setting column to plot from cases_toggle
    # if not cases_toggle: plot = 'NewCases'
    # else: plot = 'NewDeaths'
    if log_toggle==False:
        plot_type='linear'
    else:
        plot_type='log'
    if cases_toggle==False:
        plot='NewCases'
    else:
        plot='new_deaths'
    if not county_toggle:
        # if county toggle set to True plotting county level info
        if not daily_toggle:
            # if set to county True / daily True
            for county in temp_df['properties.CountyName'].unique():
                df_by_county = temp_df[temp_df['properties.CountyName']==county]
                traces.append(go.Scatter(
                    x = df_by_county['properties.Date'],
                    y = df_by_county[plot],
                    mode='lines',
                    opacity=0.75,
                    line=dict(width=2),
                    name=county))

            return dict(data=traces,
                    layout=go.Layout(xaxis=dict(title='Date'),
                                    yaxis=dict(title='New Daily Cases', type=plot_type),
                                    hovermode='closest'))
        else:
            # else if set to county True / daily false (i.e. cumulative)
            for county in temp_df['properties.CountyName'].unique():
                df_by_county = temp_df[temp_df['properties.CountyName']==county].groupby('properties.Date').mean().cumsum()
                traces.append(go.Scatter(
                    x = df_by_county.index,
                    y = df_by_county[plot],
                    mode='lines',
                    opacity=0.75,
                    line=dict(width=2),
                    name=county))

            return dict(data=traces,
                    layout=go.Layout(xaxis=dict(title='Date'),
                                    yaxis=dict(title='Cumulative Cases', type=plot_type),
                                    hovermode='closest'))
    else:
        if not daily_toggle:
            df_by_date = temp_df.groupby('properties.Date').mean()  # setting to mean - duplicate vals for each county row so mean is accurate
            if plot == 'NewCases': y_temp = 'new_cases'
            else: y_temp = 'new_deaths'
            traces.append(go.Scatter(
                    x = df_by_date.index,
                    y = df_by_date[y_temp],
                    mode='lines',
                    opacity=0.75,
                    line=dict(width=2),
                    name='New Daily Cases'))
            return dict(data=traces,
                        layout=go.Layout(xaxis=dict(title='Date'),
                                        yaxis=dict(title='New Cases', type=plot_type),
                                        hovermode='closest'))
        else:
            df_by_date = temp_df.groupby('properties.Date').mean().cumsum()
            if plot == 'NewCases': y_temp = 'new_cases'
            else: y_temp = 'new_deaths'
            traces.append(go.Scatter(
                    x = df_by_date.index,
                    y = df_by_date[y_temp],
                    mode='lines',
                    opacity=0.75,
                    line=dict(width=2),
                    name='New Daily Cases'))
            return dict(data=traces,
                        layout=go.Layout(xaxis=dict(title='Date'),
                                        yaxis=dict(title='Cumulative Cases', type=plot_type),
                                        hovermode='closest'))

if __name__=='__main__':
    app.run_server()