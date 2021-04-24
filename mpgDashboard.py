import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd

df = pd.read_csv('data/auto-mpg.csv')

