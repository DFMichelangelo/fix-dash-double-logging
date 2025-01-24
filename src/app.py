import logging
import os
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

from src import theme
from src.logger import setup_logger

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.icons.FONT_AWESOME])

app.layout = theme.get_theme


def start_app():
    setup_logger()
    log = logging.getLogger(__name__)
    # INFO - why this? see: https://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        log.info("This is an info message.")
    app.run(debug=True, port=8000)