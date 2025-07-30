from typing import *
from fasthtml.common import *
from deepboard.gui.components import Legend, ChartType, Smoother, LogSelector

def CompareSetup(session, swap: bool = False):
    from __main__ import CONFIG
    from __main__ import rTable
    if "hidden_lines" in session["compare"]:
        hidden_lines = session["compare"]["hidden_lines"]
    else:
        hidden_lines = []
    raw_labels = [int(txt) for txt in session["compare"]["selected-rows"]]
    raw_labels = sorted(raw_labels)
    sockets = [rTable.load_run(runID) for runID in raw_labels]
    repetitions = [socket.get_repetitions() for socket in sockets]
    if any(len(rep) > 1 for rep in repetitions):
        labels = [(f"{label}.{rep}", CONFIG.COLORS[i % len(CONFIG.COLORS)], f"{label}.{rep}" in hidden_lines) for i, label in enumerate(raw_labels) for rep in sockets[i].get_repetitions()]
    else:
        labels = [(f"{label}", CONFIG.COLORS[i % len(CONFIG.COLORS)], f"{label}" in hidden_lines) for
                  i, label in enumerate(raw_labels)]
    return Div(
        H1("Setup", cls="chart-scalar-title"),
        Legend(session, labels, path="/compare", selected_rows_key="compare"),
        ChartType(session, path="/compare", selected_rows_key="compare", session_path="compare"),
        LogSelector(session, path="/compare", selected_rows_key="compare", session_path="compare"),
        Smoother(session, path="/compare", selected_rows_key="compare", session_path="compare"),
        cls="setup-card",
        id="setup-card",
        hx_swap_oob="true" if swap else None,
    )
