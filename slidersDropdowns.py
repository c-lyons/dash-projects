import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np
import pandas as pd

df = pd.read_csv('data/abalone.txt')

x = df.Height
y = df.Diameter

markdown = '''
### This is my Markdown Title
Ok so this is the text below
\n
\n
i did a line break there^ does it show?

how about this [hyperlink](https://www.wikipedia.com)?

is this **bold** and is this *italic*?

Great! :)
'''

app = dash.Dash()

app.layout = html.Div([

                    dcc.Markdown(markdown),
                    html.Label('Dropdown'),
                    dcc.Dropdown(options=[{'label':'New York City',
                                            'value':'NYC'},
                                            {'label':'San Francisco',
                                            'value':'SF'}],
                                value='SF'),
                    html.Label('Slider'),
                    dcc.Slider(min=0,
                                max=10,
                                step=1,
                                value=0,
                                marks={i: i for i in range(0,11)}),
                    html.Label('Radio Items'),
                    dcc.RadioItems(options=[{'label':'New York City',
                                            'value':'NYC'},
                                            {'label':'San Francisco',
                                            'value':'SF'}],
                                value='SF')])

if __name__=='__main__':
    app.run_server()