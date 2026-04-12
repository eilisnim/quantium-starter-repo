import dash
from dash import html
import pytest

from Visualisation2 import app

def test_visuals_present(dash_duo):

    dash_duo.start_server(app)

    # is main header present?
    try:
        dash_duo.wait_for_element("#main-header", timeout=5)
    except Exception:
        assert False, "ERROR: Main header is not present"

    header = dash_duo.find_element("#main-header")
    assert header.text == "Pink Morsel Sales before and after price increase"

    # is main graph present?
    # wait until graph exists in DOM

    try:
        dash_duo.wait_for_element("#sales-graph", timeout=5)
    except Exception:
        assert False, "ERROR: Sales graph is not present"

    graph = dash_duo.find_element("#sales-graph")
    assert graph is not None

    # is radio-button present?
    # wait until graph exists in DOM

    try:
        dash_duo.wait_for_element("#radio-region", timeout=5)
    except Exception:
        assert False, "ERROR: Radio buttons are not present"

    radio = dash_duo.find_element("#radio-region")
    assert radio is not None

assert dash_duo.get_logs() == [], "Browser console should contain no errors"