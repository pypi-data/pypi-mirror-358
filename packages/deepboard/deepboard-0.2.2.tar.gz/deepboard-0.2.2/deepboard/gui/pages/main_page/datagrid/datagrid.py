from typing import *
from fasthtml.common import *
from .row import Row
from .header import Header, HeaderRename

def DataGrid(session, rename_col: str = None, wrapincontainer: bool = False, fullscreen: bool = False):
    """
    Note that fullscreen only work if the container is requested because it applies on the container
    """
    from __main__ import rTable, CONFIG

    if "datagrid" not in session:
        session["datagrid"] = dict()
    show_hidden = session.get("show_hidden", False)
    rows_selected = session["datagrid"].get("selected-rows") or []
    sort_by: Optional[str] = session["datagrid"].get("sort_by", None)
    sort_order: Optional[str] = session["datagrid"].get("sort_order", None)
    columns, col_ids, data = rTable.get_results(show_hidden=show_hidden)
    # If the columns to sort by is hidden, we reset it
    if sort_by is not None and sort_by not in col_ids:
        session["datagrid"]["sort_by"] = sort_by = None
        session["datagrid"]["sort_order"] = sort_order = None

    if sort_by is not None and sort_order is not None:
        data = sorted(
            data,
            key=lambda x: (
                x[col_ids.index(sort_by)] is None,  # True = 1, False = 0 — Nones last
                x[col_ids.index(sort_by)]
            ),
            reverse=(sort_order == "desc")
        )

    run_ids = [row[col_ids.index("run_id")] for row in data]
    rows_hidden = rTable.get_hidden_runs() if show_hidden else []
    table = Table(
                # We put the headers in a form so that we can sort them using htmx
                Thead(
                    Tr(
                        *[
                            HeaderRename(col_name, col_id) if col_id == rename_col else Header(
                                col_name,
                                col_id,
                                sort_order if col_id == sort_by else None)
                            for col_name, col_id in zip(columns, col_ids)],
                        id="column-header-row"
                    )
                    ),
                Tbody(
                    *[Row(row,
                          run_id,
                          max_decimals=CONFIG.MAX_DEC,
                          selected=run_id in rows_selected,
                          hidden=run_id in rows_hidden,
                          fullscreen=fullscreen) for row, run_id in zip(data, run_ids)],
                ),
                cls="data-grid"
            ),

    if wrapincontainer:
        return Div(
                table,
                cls="scroll-container" if not fullscreen else "scroll-container fullscreen",
                id="experiment-table",
            ),
    else:
        return table