from fasthtml.common import *
from starlette.responses import Response
from typing import *
from deepboard.gui.components import Modal, SplitSelector, StatLine, ArtefactGroup

def _get_images_groups(socket, type: Literal["IMAGE", "PLOT"]):
    if type == "IMAGE":
        images = socket.read_images()
    else:
        images = socket.read_figures()

    index = list({(img["step"], img["epoch"], img["run_rep"], img["split"]) for img in images})

    splits = list({elem[3] for elem in index})

    # Package images
    images_groups = {}
    for key in index:
        cropped_key = key[:-1]  # Remove split
        if cropped_key not in images_groups:
            images_groups[cropped_key] = {split: [] for split in splits}

    for img in images:
        key = img["step"], img["epoch"], img["run_rep"]
        split = img["split"]
        images_groups[key][split].append(img["id"])

    # Sort image groups by step, and run_rep
    return dict(sorted(images_groups.items(), key=lambda x: (x[0][0], x[0][2])))


def ImageComponent(image_id: int):
    """
    Create a single image component with a specific style.
    :param image: PIL Image object.
    :return: Div containing the image.
    """
    return Div(
        A(
            Img(src=f"/images/id={image_id}", alt="Image"),
            hx_get=f"/images/open_modal?id={image_id}",
            hx_target="#modal",
            hx_swap="outerHTML",
            style='cursor: pointer;',
        ),
        cls="image",
    )

def InteractiveImage(image_id: int):
    return Div(
        Script(
            """
    // For image zoom and pan in modal
    var scale = 1;
    var translateX = 0;
    var translateY = 0;
    var zoomableDiv = document.getElementById('zoomableDiv');
    var container = document.querySelector('.interactive-image-container');

    // Mouse/touch state
    var isDragging = false;
    var lastX = 0;
    var lastY = 0;

    // Apply transform with both scale and translate
    function applyTransform() {
        zoomableDiv.style.transform = `scale(${scale}) translate(${translateX}px, ${translateY}px)`;
    }

    // Mouse wheel and trackpad zoom
    var lastWheelTime = 0;
    var wheelAccumulator = 0;

    container.addEventListener('wheel', (e) => {
        e.preventDefault();

        const currentTime = Date.now();
        const timeDelta = currentTime - lastWheelTime;

        // Detect if this is likely a Mac trackpad (rapid events with ctrlKey)
        const isMacTrackpad = e.ctrlKey || (timeDelta < 50 && Math.abs(e.deltaY) > 10);

        let zoomFactor;
        if (isMacTrackpad) {
            // For Mac trackpad: use smaller, more gradual changes
            // Accumulate small changes for smoother zooming
            wheelAccumulator += e.deltaY;

            // Only apply zoom when accumulator reaches threshold
            if (Math.abs(wheelAccumulator) > 20) {
                zoomFactor = wheelAccumulator > 0 ? 0.95 : 1.05;
                wheelAccumulator *= 0.7; // Reduce accumulator but don't reset completely
            } else {
                lastWheelTime = currentTime;
                return; // Skip this event
            }
        } else {
            // For regular mouse wheel: use normal zoom steps
            zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
            wheelAccumulator = 0; // Reset accumulator for mouse wheel
        }

        const newScale = Math.max(0.5, Math.min(3, scale * zoomFactor));

        // Get cursor position relative to container
        const rect = container.getBoundingClientRect();
        const mouseX = e.clientX - rect.left - rect.width / 2;
        const mouseY = e.clientY - rect.top - rect.height / 2;

        // Adjust translation to zoom towards cursor position
        const scaleRatio = newScale / scale;
        translateX = mouseX * (1 - scaleRatio) + translateX * scaleRatio;
        translateY = mouseY * (1 - scaleRatio) + translateY * scaleRatio;

        scale = newScale;
        lastWheelTime = currentTime;
        applyTransform();
    });

    // Mouse drag for panning
    container.addEventListener('mousedown', (e) => {
        if (scale > 1) { // Only allow panning when zoomed
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
            container.style.cursor = 'grabbing';
            e.preventDefault();
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const deltaX = e.clientX - lastX;
            const deltaY = e.clientY - lastY;

            translateX += deltaX / scale; // Adjust for current scale
            translateY += deltaY / scale;

            lastX = e.clientX;
            lastY = e.clientY;

            applyTransform();
            e.preventDefault();
        }
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            container.style.cursor = scale > 1 ? 'grab' : 'default';
        }
    });

    // Touch zoom (pinch)
    var initialDistance = 0;
    var initialScale = 1;
    var touchStartX = 0;
    var touchStartY = 0;
    var initialTranslateX = 0;
    var initialTranslateY = 0;

    container.addEventListener('touchstart', (e) => {
        if (e.touches.length === 2) {
            // Two finger pinch zoom
            initialDistance = getDistance(e.touches[0], e.touches[1]);
            initialScale = scale;
            e.preventDefault();
        } else if (e.touches.length === 1 && scale > 1) {
            // Single finger pan when zoomed
            isDragging = true;
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            initialTranslateX = translateX;
            initialTranslateY = translateY;
            e.preventDefault();
        }
    });

    container.addEventListener('touchmove', (e) => {
        if (e.touches.length === 2) {
            // Handle pinch zoom
            const currentDistance = getDistance(e.touches[0], e.touches[1]);
            const ratio = currentDistance / initialDistance;
            const dampedRatio = 1 + (ratio - 1) * 0.5; // 50% sensitivity
            scale = Math.max(0.5, Math.min(3, initialScale * dampedRatio));
            applyTransform();
            e.preventDefault();
        } else if (e.touches.length === 1 && isDragging) {
            // Handle single finger pan
            const deltaX = e.touches[0].clientX - touchStartX;
            const deltaY = e.touches[0].clientY - touchStartY;

            translateX = initialTranslateX + deltaX / scale;
            translateY = initialTranslateY + deltaY / scale;

            applyTransform();
            e.preventDefault();
        }
    });

    container.addEventListener('touchend', (e) => {
        if (e.touches.length === 0) {
            isDragging = false;
        }
    });

    // Reset on double click/tap
    container.addEventListener('dblclick', () => {
        scale = 1;
        translateX = 0;
        translateY = 0;
        applyTransform();
        container.style.cursor = 'default';
    });

    // Update cursor based on zoom level
    container.addEventListener('mouseenter', () => {
        container.style.cursor = scale > 1 ? 'grab' : 'default';
    });

    function getDistance(touch1, touch2) {
        const dx = touch1.clientX - touch2.clientX;
        const dy = touch1.clientY - touch2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    // Prevent context menu on long press for mobile
    container.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    });
            """
        ),
        Div(
            Div(
                Img(src=f"/images/id={image_id}", alt="Image"),
                cls="interactive-image",
                id="zoomableDiv",
                style="transition: transform 0.1s ease-out;"
            ),
            cls="interactive-image-container",
            style="overflow: hidden; position: relative; user-select: none; touch-action: none;"
        )
    )



def ImageCard(runID: int, step: int, epoch: Optional[int], run_rep: int, img_type: Literal["IMAGE", "PLOT"],
              selected: Optional[str] = None):
    from __main__ import rTable

    socket = rTable.load_run(runID)
    data = _get_images_groups(socket, type=img_type)

    if (step, epoch, run_rep) not in data:
        avail_splits = []
        images = []
    else:
        images_splits = data[(step, epoch, run_rep)]
        avail_splits = list(images_splits.keys())
        avail_splits.sort()
        if selected is None:
            selected = avail_splits[0]
        images = images_splits[selected]

    return Div(
        Div(
            SplitSelector(runID, avail_splits, selected=selected, step=step, epoch=epoch, run_rep=run_rep,
                          type=img_type, path="/images/change_split"),
            Div(
                StatLine("Step", str(step)),
                StatLine("Epoch", str(epoch) if epoch is not None else "N/A"),
                StatLine("Run Repetition", str(run_rep)),
                cls="artefact-stats-column"
            ),
            cls="artefact-card-header",
        ),
        ArtefactGroup(*[ImageComponent(image_id) for image_id in images]),
        id=f"artefact-card-{step}-{epoch}-{run_rep}",
        cls="artefact-card",
    )

def ImageTab(session, runID, type: Literal["IMAGE", "PLOT"], swap: bool = False):
    from __main__ import rTable
    socket = rTable.load_run(runID)

    images_groups = _get_images_groups(socket, type=type)
    return Div(
        *[
            ImageCard(runID, step, epoch, run_rep, img_type=type)
            for step, epoch, run_rep in images_groups.keys()
        ],
        style="display; flex; flex-direction: column; align-items: center; justify-content: center;",
        id="images-tab",
        hx_swap_oob="true" if swap else None,
    )


def images_enable(runID, type: Literal["IMAGES", "PLOT"]):
    """
    Check if some scalars are logged and available for the runID. If not, we consider disable it.
    :param runID: The runID to check.
    :return: True if scalars are available, False otherwise.
    """
    from __main__ import rTable
    socket = rTable.load_run(runID)
    if type == "IMAGES":
        return len(socket.read_images()) > 0
    else:
        return len(socket.read_figures()) > 0

# routes
def build_images_routes(rt):
    rt("/images/change_split")(change_split)
    rt("/images/id={image_id}")(load_image)
    rt("/images/open_modal")(open_image_modal)


def change_split(session, runID: int, step: int, epoch: Optional[int], run_rep: int, split_select: str, type: str):
    """
    Change the split for the images.
    :param session: The session object.
    :param step: The step of the images.
    :param epoch: The epoch of the images.
    :param run_rep: The run repetition of the images.
    :param split: The split to change to.
    :param type: The type of split to change.
    :return: The updated image card HTML.
    """
    return ImageCard(
        runID,
        step,
        epoch,
        run_rep,
        img_type=type,
        selected=split_select,
    )

def load_image(image_id: int):
    from __main__ import rTable
    img = rTable.get_image_by_id(image_id)
    if img is None:
        return Response(f"Image not found with id: {image_id}:(", status_code=404)
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return Response(
        content=img_buffer.getvalue(),
        media_type="image/png"
    )

def open_image_modal(session, id: int):
    return Modal(
        InteractiveImage(
            id
        ),
        active=True,
    )