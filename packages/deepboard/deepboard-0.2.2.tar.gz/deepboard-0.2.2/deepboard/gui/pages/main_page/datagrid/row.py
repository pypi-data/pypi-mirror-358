from typing import *
from fasthtml.common import *
from .utils import format_value
def Row(data, run_id, selected: bool, hidden: bool, max_decimals: int, fullscreen: bool):
    cls = "table-row"
    if selected:
        cls += " table-row-selected"

    if hidden:
        cls += " table-row-hidden"

    return Tr(
        *[Td(format_value(value, decimals=max_decimals)) for value in data],
        hx_get=f"/click_row?run_id={run_id}&fullscreen={fullscreen}",  # HTMX will GET this URL
        hx_trigger="click[!event.ctrlKey && !event.metaKey]",
        hx_target="#experiment-table",  # Target DOM element to update
        hx_swap="innerHTML",  # Optional: how to replace content
        id=f"grid-row-{run_id}",
        cls=cls,
    )