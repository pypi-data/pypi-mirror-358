from fasthtml.common import *


def Modal(*content, active: bool = False):
    return Div(
        Button(
            I(cls="fas fa-times"),
            hx_get="/close_modal",
            hx_target="#modal",
            hx_swap="outerHTML",
            cls="close-button",
        ) if active else None,
        Div(
            *content,
            cls="modal",
            onclick="event.stopPropagation();",
        ),
        cls="modal-overlay" if active else "modal-overlay hidden",
        id="modal"
    )