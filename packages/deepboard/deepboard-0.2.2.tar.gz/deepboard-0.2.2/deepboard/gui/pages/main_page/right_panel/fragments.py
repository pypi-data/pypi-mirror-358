from fasthtml.common import *
from starlette.responses import Response
from typing import *
from deepboard.gui.components import Modal, SplitSelector, StatLine, ArtefactGroup

def _get_fragment_groups(socket, type: Literal["RAW", "HTML"]):
    if type == "RAW":
        fragments = socket.read_text()
    else:
        fragments = socket.read_fragment()

    index = list({(fragment["step"], fragment["epoch"], fragment["run_rep"], fragment["split"]) for fragment in fragments})

    splits = list({elem[3] for elem in index})

    # Package fragments
    frag_groups = {}
    for key in index:
        cropped_key = key[:-1]  # Remove split
        if cropped_key not in frag_groups:
            frag_groups[cropped_key] = {split: [] for split in splits}

    for fragment in fragments:
        key = fragment["step"], fragment["epoch"], fragment["run_rep"]
        split = fragment["split"]
        frag_groups[key][split].append(fragment["fragment"])

    # Sort fragments groups by step, and run_rep
    return dict(sorted(frag_groups.items(), key=lambda x: (x[0][0], x[0][2])))


def TextComponent(text: str):
    return Div(
        P(text, cls="fragment-text"),
        cls="fragment-text-container"
    )

def HTMLComponent(html_str: str):
    # Return whatever is in html_str as a HTML component
    return NotStr(html_str)

def FragmentCard(runID: int, step: int, epoch: Optional[int], run_rep: int, frag_type: Literal["RAW", "HTML"],
              selected: Optional[str] = None):
    from __main__ import rTable

    socket = rTable.load_run(runID)
    data = _get_fragment_groups(socket, type=frag_type)

    if (step, epoch, run_rep) not in data:
        avail_splits = []
        fragments = []
    else:
        fragment_splits = data[(step, epoch, run_rep)]
        print(fragment_splits)
        avail_splits = list(fragment_splits.keys())
        avail_splits.sort()
        if selected is None:
            selected = avail_splits[0]
        fragments = fragment_splits[selected]

    return Div(
        Div(
            SplitSelector(runID, avail_splits, selected=selected, step=step, epoch=epoch, run_rep=run_rep,
                          type=frag_type, path="/fragments/change_split"),
            Div(
                StatLine("Step", str(step)),
                StatLine("Epoch", str(epoch) if epoch is not None else "N/A"),
                StatLine("Run Repetition", str(run_rep)),
                cls="artefact-stats-column"
            ),
            cls="artefact-card-header",
        ),
        ArtefactGroup(*[
            TextComponent(frag_content) if frag_type == "RAW" else HTMLComponent(frag_content)
            for frag_content in fragments
        ]),
        id=f"artefact-card-{step}-{epoch}-{run_rep}",
        cls="artefact-card",
    )

def FragmentTab(session, runID, type: Literal["RAW", "HTML"], swap: bool = False):
    from __main__ import rTable
    socket = rTable.load_run(runID)

    fragment_groups = _get_fragment_groups(socket, type=type)
    return Div(
        *[
            FragmentCard(runID, step, epoch, run_rep, frag_type=type)
            for step, epoch, run_rep in fragment_groups.keys()
        ],
        style="display; flex; flex-direction: column; align-items: center; justify-content: center;",
        id="fragment-tab",
        hx_swap_oob="true" if swap else None,
    )


def fragment_enable(runID, type: Literal["RAW", "HTML"]):
    """
    Check if some fragments/text are logged and available for the runID. If not, we consider disable it.
    :param runID: The runID to check.
    :return: True if scalars are available, False otherwise.
    """
    from __main__ import rTable
    socket = rTable.load_run(runID)
    if type == "RAW":
        return len(socket.read_text()) > 0
    else:
        return len(socket.read_fragment()) > 0

# routes
def build_fragment_routes(rt):
    rt("/fragments/change_split")(change_split)


def change_split(session, runID: int, step: int, epoch: Optional[int], run_rep: int, split_select: str, type: str):
    """
    Change the split for the fragment.
    :param session: The session object.
    :param step: The step of the fragment.
    :param epoch: The epoch of the fragment.
    :param run_rep: The run repetition of the fragments.
    :param split: The split to change to.
    :return: The updated fragment card HTML.
    """
    return FragmentCard(
        runID,
        step,
        epoch,
        run_rep,
        frag_type=type,
        selected=split_select,
    )

