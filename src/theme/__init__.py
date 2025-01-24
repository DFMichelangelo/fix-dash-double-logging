from dash import Dash, html, dcc, callback, Output, Input

from src.theme import color_mode_switch

def get_theme():
    return html.Div(
        [
            color_mode_switch.color_mode_switch
        ]
    )
