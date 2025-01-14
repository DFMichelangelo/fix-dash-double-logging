import logging
import os
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

from logger import setup_logger

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash()

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    setup_logger()
    logger = logging.getLogger(__name__)
    # INFO - why this? see: https://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        logger.error("Nanananannanana")
        logger.debug("This is a debug message.")
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        logger.critical(os.environ.get("WERKZEUG_RUN_MAIN")== "true")
    app.run(debug=True, port=8000)
    print(os.environ.get("WERKZEUG_RUN_MAIN"))

    
