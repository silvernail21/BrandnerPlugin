import logging
import os
import random
from typing import Callable, List, Optional, Tuple, Iterable, Dict, Sequence

import c4d

from bccf_constants import (
    DEFAULT_DIRECTORY_OUTPUT,
    DEFAULT_DELIMITER,
    DEFAULT_DO_GENERATE_CSV,
    DEFAULT_DO_SAVE_PROJECT,
    DEFAULT_FILENAME,
    DEFAULT_MODE_RENDER,
    DEFAULT_PREFIX,
    DEFAULT_PRODUCT_NAME,
    ID_BCB_DELIMITER,
    ID_BCB_DIRECTORY_OUTPUT,
    ID_BCB_DO_GENERATE_CSV,
    ID_BCB_DO_SAVE_PROJECT,
    ID_BCB_EXCLUSION_RULES_RAW,
    ID_BCB_FILENAME,
    ID_BCB_MODE_RENDER,
    ID_BCB_PREFIX,
    ID_BCB_PRODUCT_NAME,
    ID_BCB_TOKEN_EXAMPLE_MODE,
    PLUGIN_ID_BRANDNER,
)


DESC_ID_VIS_EDITOR = c4d.DescID(
    c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0)
)
DESC_ID_VIS_RENDER = c4d.DescID(
    c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_RENDER, c4d.DTYPE_LONG, 0)
)
DESC_ID_STAGE_CAM = c4d.DescID(
    c4d.DescLevel(c4d.STAGEOBJECT_CLINK, c4d.DTYPE_BASELISTLINK, 0)
)


def create_object(
    doc: c4d.documents.BaseDocument,
    id_type: int,
    name_obj: str,
    *,
    obj_parent: Optional[c4d.BaseObject] = None,
    add_undo: bool = False,
) -> c4d.BaseObject:
    obj = doc.SearchObject(name_obj)
    if obj is not None:
        return obj

    obj = c4d.BaseObject(id_type)
    obj.SetName(name_obj)
    if obj_parent is not None:
        obj.InsertUnderLast(obj_parent)
    else:
        doc.InsertObject(obj)

    if add_undo:
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, obj)

    return obj


def create_null(
    doc: c4d.documents.BaseDocument,
    name_null: str,
    *,
    obj_parent: Optional[c4d.BaseObject] = None,
    add_undo: bool = False,
    do_unfold: bool = True,
) -> c4d.BaseObject:
    obj_null = create_object(
        doc, c4d.Onull, name_null, obj_parent=obj_parent, add_undo=add_undo
    )
    if do_unfold:
        obj_null.ChangeNBit(c4d.NBIT_OM1_FOLD, c4d.NBITCONTROL_SET)
    return obj_null


def create_stage(
    doc: c4d.documents.BaseDocument,
    name_stage: str,
    *,
    obj_parent: Optional[c4d.BaseObject] = None,
    add_undo: bool = False,
) -> c4d.BaseObject:
    return create_object(
        doc, c4d.Ostage, name_stage, obj_parent=obj_parent, add_undo=add_undo
    )


def store_bc_brandner(
    doc: c4d.documents.BaseDocument,
    bcb: c4d.BaseContainer,
) -> c4d.BaseContainer:
    bc_doc = doc.GetDataInstance()
    bc_doc[PLUGIN_ID_BRANDNER] = bcb
    return bc_doc.GetContainerInstance(PLUGIN_ID_BRANDNER)


# Parameters remembered across documents (stored in C4D's world plugin
# data). Product name and output directory stay per-document on purpose.
IDS_WORLD_DEFAULTS = [
    ID_BCB_PREFIX,
    ID_BCB_DELIMITER,
    ID_BCB_FILENAME,
    ID_BCB_DO_GENERATE_CSV,
    ID_BCB_DO_SAVE_PROJECT,
    ID_BCB_MODE_RENDER,
]


def save_world_defaults(bcb: c4d.BaseContainer) -> None:
    """Remember the user's naming/render preferences across documents."""
    if bcb is None:
        return
    bc = c4d.BaseContainer()
    for _id in IDS_WORLD_DEFAULTS:
        if bcb[_id] is not None:
            bc[_id] = bcb[_id]
    try:
        c4d.plugins.SetWorldPluginData(PLUGIN_ID_BRANDNER, bc, add=True)
    except Exception as err:
        logging.warning("Failed to save world defaults: %s", err)


def get_bc_brandner_default() -> c4d.BaseContainer:
    bcb = c4d.BaseContainer(PLUGIN_ID_BRANDNER)
    bcb.SetString(ID_BCB_PREFIX, DEFAULT_PREFIX)
    bcb.SetString(ID_BCB_DELIMITER, DEFAULT_DELIMITER)
    num_prod = random.randint(0, 1000)
    bcb.SetString(ID_BCB_PRODUCT_NAME, f"{DEFAULT_PRODUCT_NAME}{num_prod}")
    bcb.SetString(ID_BCB_DIRECTORY_OUTPUT, DEFAULT_DIRECTORY_OUTPUT)
    bcb.SetString(ID_BCB_FILENAME, DEFAULT_FILENAME)
    bcb.SetBool(ID_BCB_DO_GENERATE_CSV, DEFAULT_DO_GENERATE_CSV)
    bcb.SetBool(ID_BCB_DO_SAVE_PROJECT, DEFAULT_DO_SAVE_PROJECT)
    bcb.SetInt32(ID_BCB_MODE_RENDER, DEFAULT_MODE_RENDER)

    # Overlay the user's remembered preferences (last-used prefix,
    # delimiter, filename pattern, ...) over the factory defaults.
    try:
        bc_world = c4d.plugins.GetWorldPluginData(PLUGIN_ID_BRANDNER)
    except Exception:
        bc_world = None
    if bc_world is not None:
        for _id in IDS_WORLD_DEFAULTS:
            if bc_world[_id] is not None:
                bcb[_id] = bc_world[_id]

    # Internal Parameters
    bcb.SetBool(ID_BCB_TOKEN_EXAMPLE_MODE, False)  # Has to be False!
    return bcb


def ensure_bc_brandner_defaults(bcb: c4d.BaseContainer) -> None:
    """Backfill parameters missing from containers stored by older
    plugin versions.

    Documents saved with an older plugin carry a container without the
    newer fields. Reading an absent field returns None, which crashes
    SetInt32()/os.path.join() during dialog initialization — and with
    EVMSG_CHANGE re-triggering the broken init, C4D appears frozen.
    Only absent (None) fields are filled; stored values are never
    overwritten.
    """
    if bcb is None:
        return

    defaults_string = [
        (ID_BCB_PREFIX, DEFAULT_PREFIX),
        (ID_BCB_DELIMITER, DEFAULT_DELIMITER),
        (ID_BCB_PRODUCT_NAME, f"{DEFAULT_PRODUCT_NAME}{random.randint(0, 1000)}"),
        (ID_BCB_DIRECTORY_OUTPUT, DEFAULT_DIRECTORY_OUTPUT),
        (ID_BCB_FILENAME, DEFAULT_FILENAME),
        (ID_BCB_EXCLUSION_RULES_RAW, ""),
    ]
    for _id, _default in defaults_string:
        if bcb[_id] is None:
            bcb.SetString(_id, _default)

    if bcb[ID_BCB_DO_GENERATE_CSV] is None:
        bcb.SetBool(ID_BCB_DO_GENERATE_CSV, DEFAULT_DO_GENERATE_CSV)
    if bcb[ID_BCB_DO_SAVE_PROJECT] is None:
        bcb.SetBool(ID_BCB_DO_SAVE_PROJECT, DEFAULT_DO_SAVE_PROJECT)
    if bcb[ID_BCB_MODE_RENDER] is None:
        bcb.SetInt32(ID_BCB_MODE_RENDER, DEFAULT_MODE_RENDER)

    # Internal flag — must never be persisted as True.
    bcb.SetBool(ID_BCB_TOKEN_EXAMPLE_MODE, False)


def get_bc_brandner_from_doc(
    doc: c4d.documents.BaseDocument,
) -> c4d.BaseContainer:
    bc_doc = doc.GetDataInstance()
    bcb = bc_doc.GetContainerInstance(PLUGIN_ID_BRANDNER)
    ensure_bc_brandner_defaults(bcb)
    return bcb


def get_bc_brandner(do_init_doc: bool) -> c4d.BaseContainer:
    doc = c4d.documents.GetActiveDocument()
    bcb = get_bc_brandner_from_doc(doc)
    if bcb is not None:
        return bcb
    bcb = get_bc_brandner_default()
    if do_init_doc:
        store_bc_brandner(doc, bcb)
    return bcb


def validate_bc_brandner(bcb: c4d.BaseContainer, *, is_dev_env: bool) -> None:
    if not is_dev_env:
        return

    prefix = bcb.GetString(ID_BCB_PREFIX, DEFAULT_PREFIX)
    bcb.SetString(ID_BCB_PREFIX, prefix)

    delim = bcb.GetString(ID_BCB_DELIMITER, DEFAULT_DELIMITER)
    bcb.SetString(ID_BCB_DELIMITER, delim)

    num_prod = random.randint(0, 1000)
    name_prod = bcb.GetString(
        ID_BCB_PRODUCT_NAME, f"{DEFAULT_PRODUCT_NAME}{num_prod}"
    )
    bcb.SetString(ID_BCB_PRODUCT_NAME, name_prod)

    dir_output = bcb.GetString(
        ID_BCB_DIRECTORY_OUTPUT, DEFAULT_DIRECTORY_OUTPUT
    )
    bcb.SetString(ID_BCB_DIRECTORY_OUTPUT, dir_output)

    filename = bcb.GetString(ID_BCB_FILENAME, DEFAULT_FILENAME)
    bcb.SetString(ID_BCB_FILENAME, filename)

    generate_csv = bcb.GetBool(
        ID_BCB_DO_GENERATE_CSV, DEFAULT_DO_GENERATE_CSV
    )
    bcb.SetBool(ID_BCB_DO_GENERATE_CSV, generate_csv)

    save_project = bcb.GetBool(
        ID_BCB_DO_SAVE_PROJECT, DEFAULT_DO_SAVE_PROJECT
    )
    bcb.SetBool(ID_BCB_DO_SAVE_PROJECT, save_project)

    mode_render = bcb.GetInt32(ID_BCB_MODE_RENDER, DEFAULT_MODE_RENDER)
    bcb.SetInt32(ID_BCB_MODE_RENDER, mode_render)

    bcb.SetBool(ID_BCB_TOKEN_EXAMPLE_MODE, False)  # internal, has to be False!


def jump_to_frame(doc: c4d.documents.BaseDocument, idx_frame: int) -> None:
    fps = doc.GetFps()
    time = c4d.BaseTime(idx_frame, fps)
    doc.SetTime(time)
    doc.ExecutePasses(None, True, True, False, c4d.BUILDFLAGS_NONE)


def get_key(
    obj: c4d.BaseObject,
    time: c4d.BaseTime,
    desc_id: c4d.DescID,
    do_create: bool = True,
) -> Optional[c4d.CKey]:
    ctrack = obj.FindCTrack(desc_id)
    if ctrack is None:
        if not do_create:
            return None
        ctrack = c4d.CTrack(obj, desc_id)
        obj.InsertTrackSorted(ctrack)

    ccurve = ctrack.GetCurve()
    result = ccurve.FindKey(time)
    if result is None and do_create:
        result = ccurve.AddKey(time)
    if result is None:
        return None
    return result["key"]


# Currently, not used, see brandner_render_tokens.py
def get_keyframed_cam(obj_stage: c4d.BaseObject) -> c4d.BaseObject:
    doc = obj_stage.GetDocument()
    time = doc.GetTime()

    key_vis = get_key(obj_stage, time, DESC_ID_STAGE_CAM, do_create=False)
    if key_vis is None:
        return None
    obj_cam = key_vis.GetGeData()
    return obj_cam


def set_keyframe_cam(
    obj_stage: c4d.BaseObject,
    obj_cam: c4d.BaseObject,
) -> None:
    doc = obj_stage.GetDocument()
    time = doc.GetTime()

    key_vis = get_key(obj_stage, time, DESC_ID_STAGE_CAM)
    key_vis.SetGeData(key_vis.GetCurve(), obj_cam)


def get_keyframe_vis(
    obj: c4d.BaseObject,
    desc_id_vis: c4d.DescID = DESC_ID_VIS_RENDER,
) -> int:
    doc = obj.GetDocument()
    time = doc.GetTime()

    key_vis = get_key(obj, time, desc_id_vis, do_create=False)
    if key_vis is None:
        return c4d.OBJECT_UNDEF

    mode_vis = int(key_vis.GetGeData())
    return mode_vis


def set_keyframe_vis(obj: c4d.BaseObject, mode_vis: int) -> None:
    doc = obj.GetDocument()
    time = doc.GetTime()

    for _desc_id in [DESC_ID_VIS_EDITOR, DESC_ID_VIS_RENDER]:
        key_vis = get_key(obj, time, _desc_id)
        key_vis.SetGeData(key_vis.GetCurve(), mode_vis)


def get_visibility(
    obj: c4d.BaseObject,
    desc_id_vis: c4d.DescID = DESC_ID_VIS_RENDER,
    *,
    do_keyframe: bool = False,
) -> int:
    if do_keyframe:
        return get_keyframe_vis(obj, desc_id_vis)
    else:
        return obj[desc_id_vis]


def set_visibility(
    obj: c4d.BaseObject,
    mode_vis: int,
    do_keyframe: bool = False,
) -> None:
    if do_keyframe:
        set_keyframe_vis(obj, mode_vis)
    else:
        obj[DESC_ID_VIS_EDITOR] = mode_vis
        obj[DESC_ID_VIS_RENDER] = mode_vis

    objs_children = obj.GetChildren()
    if objs_children is None:
        return

    for _obj_child in objs_children:
        set_visibility(_obj_child, mode_vis=mode_vis, do_keyframe=do_keyframe)



def set_visibility_direct(
    obj: c4d.BaseObject,
    mode_vis: int,
    do_keyframe: bool = False,
) -> None:
    """Set visibility only on the given object, without recursing into children."""
    if obj is None:
        return
    if do_keyframe:
        set_keyframe_vis(obj, mode_vis)
    else:
        obj[DESC_ID_VIS_EDITOR] = mode_vis
        obj[DESC_ID_VIS_RENDER] = mode_vis

def set_visibility_default(
    obj: c4d.BaseObject,
    do_keyframe: bool = False,
) -> None:
    set_visibility(obj, mode_vis=c4d.OBJECT_UNDEF, do_keyframe=do_keyframe)


def set_visibility_hide(obj: c4d.BaseObject, do_keyframe: bool = False) -> None:
    set_visibility(obj, mode_vis=c4d.OBJECT_OFF, do_keyframe=do_keyframe)


def set_visibility_show(obj: c4d.BaseObject, do_keyframe: bool = False) -> None:
    set_visibility(obj, mode_vis=c4d.OBJECT_ON, do_keyframe=do_keyframe)


def select_object(
    doc: c4d.documents.BaseDocument,
    name_obj: str,
) -> None:
    doc = c4d.documents.GetActiveDocument()
    obj = doc.SearchObject(name_obj)
    if obj is None:
        return

    doc.SetActiveObject(obj, c4d.SELECTION_NEW)


def ask_create_dir(directory: str) -> bool:
    if os.path.isdir(directory):
        return True

    if not os.path.isabs(directory):
        return False  # can not create

    msg = (
        "Output directory does not exist:\n"
        f"{directory}\n"
        "Do you want to create it, now?"
    )
    do_mkdir = c4d.gui.QuestionDialog(msg)
    if not do_mkdir:
        return False
    os.makedirs(directory, exist_ok=True)
    return True


def get_default_output_directory(dir_doc: str, dir_output: str) -> str:
    dir_output = dir_output.strip()
    dir_default = dir_doc
    if len(dir_output) > 0:
        if os.path.isabs(dir_output):
            if os.path.isdir(dir_output):
                dir_default = dir_output
        else:
            dir_default = os.path.join(dir_doc, dir_output)
            dir_default = os.path.normpath(dir_default)
            is_dir_default = ask_create_dir(dir_default)
            if not is_dir_default:
                dir_default = dir_doc

    dir_default = os.path.normpath(dir_default)
    return dir_default


def normalize_output_directory(dir_doc: str, dir_output: str) -> str:
    dir_output = dir_output.replace("\\", "/")

    if os.path.isabs(dir_doc):
        try:
            path_common = os.path.commonpath([dir_doc, dir_output])
            if os.path.samefile(path_common, dir_doc):
                dir_output = os.path.relpath(dir_output, start=path_common)
        except Exception:
            # If commonpath/samefile fails (different drives, etc.), just skip
            pass

    if not os.path.isabs(dir_output):
        if not dir_output.startswith("./"):
            dir_output = "./" + dir_output
        if not dir_output.endswith("/"):
            dir_output += "/"
    return dir_output



def resolve_output_directory(dir_doc: str, dir_output: str) -> str:
    """Resolve a stored output directory to an absolute filesystem path."""
    if not dir_output:
        return ""
    d = str(dir_output).strip().replace("\\", "/")
    if os.path.isabs(d):
        return os.path.normpath(d)
    while d.startswith("./") or d.startswith(".\\"):
        d = d[2:]
    if not dir_doc:
        return os.path.normpath(d)
    return os.path.normpath(os.path.join(dir_doc, d))

def open_error_requester(msg: str, *, do_open: bool = True) -> None:
    logging.error(msg)
    if not do_open:
        return
    c4d.gui.MessageDialog(msg, type=c4d.GEMB_ICONEXCLAMATION)


def save_project(doc: c4d.documents.BaseDocument) -> bool:
    """Save the (bake/temporary) document.

    The original ComboFlow behavior saves next to the source scene, which can clutter the
    project root. We instead save into <project>/ComboFlow_Bakes/ while keeping the
    filename the same.

    Important: We also update the document path so downstream code (e.g. Render Queue)
    can reference the correct file location.
    """
    dir_doc = doc.GetDocumentPath()
    if dir_doc == "":
        msg = (
            "Failed to save document.\n"
            "Source project should be saved before baking.\n"
            "Generated document can still be saved manually."
        )
        open_error_requester(msg)
        return False
    name_doc = doc.GetDocumentName()

    bake_subdir = "ComboFlow_Bakes"
    bake_dir = os.path.join(dir_doc, bake_subdir)
    try:
        os.makedirs(bake_dir, exist_ok=True)
    except Exception as err:
        logging.warning("Failed to create bake subfolder '%s': %s", bake_dir, err)
        bake_dir = dir_doc

    path_doc = os.path.join(bake_dir, name_doc)
    flags_save = (
        c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED
        | c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST
    )
    is_saved = c4d.documents.SaveDocument(
        doc,
        path_doc,
        saveflags=flags_save,
        format=c4d.FORMAT_C4DEXPORT,
    )
    if not is_saved:
        msg = f"Failed to save document!\n{path_doc}"
        open_error_requester(msg)
        return False

    # Ensure the document now reports the bake folder as its path. This is critical for
    # Render Queue enqueuing, which uses doc.GetDocumentPath()/GetDocumentName().
    try:
        doc.SetDocumentPath(bake_dir)
        doc.SetDocumentName(name_doc)
    except Exception:
        # Not fatal if C4D refuses; we still have a saved file on disk.
        pass
    return True
def queue_batch_render(
    doc: c4d.documents.BaseDocument,
    *,
    do_start_render: bool,
) -> bool:
    br = c4d.documents.GetBatchRender()
    if br is None:
        msg = "Failed to retrieve BatchRender instance."
        open_error_requester(msg)
        return False

    # Prefer the document-reported path, but be robust: when working with cloned docs,
    # C4D can sometimes keep the original path even after SaveDocument.
    dir_doc = doc.GetDocumentPath()
    name_doc = doc.GetDocumentName()
    path_doc = os.path.join(dir_doc, name_doc)

    if not os.path.isfile(path_doc):
        # Fallback: look in the standard bake subfolder relative to the *source* scene path.
        src_dir = c4d.documents.GetActiveDocument().GetDocumentPath()
        fallback = os.path.join(src_dir, "ComboFlow_Bakes", name_doc)
        if os.path.isfile(fallback):
            path_doc = fallback
        else:
            msg = f"Bake scene file not found for Render Queue:\n{path_doc}\n\nTried also:\n{fallback}"
            open_error_requester(msg)
            return False

    is_added = br.AddFile(path_doc, br.GetElementCount())
    if not is_added:
        msg = f"Failed to add job to Render Queue.\n{path_doc}"
        open_error_requester(msg)
        return False
    br.Open()
    if do_start_render and not br.IsRendering():
        br.SetRendering(c4d.BR_START)
    return True
g_thd_render: c4d.threading.C4DThread = None
g_results_render: List[Tuple] = []
g_progress_render: int = -1
g_idx_render_frame: int = -1
g_paths_images: List[str] = []


class ThreadRender(c4d.threading.C4DThread):

    doc: c4d.documents.BaseDocument
    bc_rd: c4d.BaseContainer

    @staticmethod
    def callback_render_progress(progress: float, type_progress: int) -> None:
        # Currently not in use.
        # We could use this to display more finegranular progress.
        # Dialog would then need to use get_render_progress() instead
        # of calculating progress based on frame number.
        global g_progress_render

        g_progress_render = int(progress * 100.0)
        c4d.SpecialEventAdd(PLUGIN_ID_BRANDNER)

    @staticmethod
    def callback_render_write(
        mode: int,
        bmp: c4d.bitmaps.BaseBitmap,
        fn: str,
        mainImage: bool,
        frame: int,
        renderTime: int,
        streamnum: int,
        streamname: str,
    ) -> None:
        global g_idx_render_frame, g_paths_images

        g_idx_render_frame = frame
        fn_exists = fn is not None and len(fn) > 0
        if fn_exists and fn not in g_paths_images:
            g_paths_images.append(fn)
            logging.info(f"Render done: #{frame}: {fn}")
        c4d.SpecialEventAdd(PLUGIN_ID_BRANDNER)

    def Main(self):
        global g_results_render
        global g_progress_render
        global g_idx_render_frame

        # Announce start
        logging.info("Start Render Thread")
        g_progress_render = 0
        g_idx_render_frame = 0
        c4d.SpecialEventAdd(PLUGIN_ID_BRANDNER)

        result, bmp = render_in_picture_viewer(
            self.doc,
            self.bc_rd,
            thd=self.Get(),
            callback_prog=self.callback_render_progress,
            callback_write=self.callback_render_write,
            is_threaded=True,
        )

        # Announce end
        g_results_render.append((self.doc, result))
        g_progress_render = 101
        g_idx_render_frame += 100000  # Beyond any reasonable num combos
        c4d.SpecialEventAdd(PLUGIN_ID_BRANDNER)
        logging.info("End Render Thread")


def get_render_progress() -> float:
    global g_progress_render
    return g_progress_render


def get_index_render_frame() -> float:
    global g_idx_render_frame
    return g_idx_render_frame


def reset_render_progress() -> None:
    global g_progress_render
    global g_idx_render_frame

    g_progress_render = -1
    g_idx_render_frame = -1

    cancel_thread_render(do_wait=True)


def is_rendering() -> bool:
    global g_thd_render
    return g_thd_render is not None


def consume_rendered_image_paths() -> List[str]:
    global g_paths_images
    paths_images = g_paths_images
    g_paths_images = []
    return paths_images


def cancel_thread_render(*, do_wait: bool = False) -> None:
    global g_thd_render

    if g_thd_render is None:
        return
    if not g_thd_render.IsRunning():
        g_thd_render = None
        return
    g_thd_render.End()
    if do_wait:
        g_thd_render.Wait(checkevents=True)
    g_thd_render = None


def consume_render_result() -> Tuple[c4d.documents.BaseDocument, int]:
    global g_results_render

    if len(g_results_render) == 0:
        return None, None

    result_render = g_results_render.pop()
    doc, result = result_render
    return doc, result


def render_in_picture_viewer_ext(
    doc: c4d.documents.BaseDocument,
    bc_rd: c4d.BaseContainer,
    *,
    do_threaded: bool = False,
) -> bool:
    if not do_threaded:
        result, bmp = render_in_picture_viewer(doc, bc_rd, is_threaded=False)
        if result != c4d.RENDERRESULT_OK:
            msg = f"Failed to render document ({result})."
            open_error_requester(msg)
        elif bmp is not None:
            c4d.bitmaps.ShowBitmap(bmp)
        return False

    global g_thd_render

    if g_thd_render is not None:
        logging.critical("g_thd_render not None")
        return False

    thd = ThreadRender()
    thd.doc = doc
    thd.bc_rd = bc_rd

    g_thd_render = thd
    thd.Start()
    return True


# ----------------------------------------------------------------------
# Combo exclusion rules: parsing + validation
# ----------------------------------------------------------------------


def parse_exclusion_rules(raw: str) -> List[Dict]:
    """
    Parse user-defined rules from a multiline string.

    Supported formats:

    Legacy (NEVER):
        IF_NAME -> TARGET1, TARGET2
        IF_NAME -> NEVER TARGET1
        IF_NAME -> TARGET1            (defaults to NEVER)

    Multi-condition IF with AND:
        A & B -> NEVER X
        A & B -> REQUIRE X
        A & B -> REQUIRE X, Y

    OR-groups on the IF side using '|':
        (A | B | C) -> NEVER X
        PM & (OS-KC | OS-EM | OS-CT) -> NEVER ISLOC_INT-ASM
        A | B -> NEVER X               (parentheses optional)

    Semantics:
      - '&' = AND across groups
      - '|' = OR within a group
      - All IF groups must be satisfied for the rule to trigger.
        Each group is satisfied if ANY token in that group is present.

    Notes:
    - Blank lines and lines starting with "#" are ignored.
    - Whitespace around tokens is stripped.
    - If no explicit mode is provided, defaults to NEVER.
    """
    rules: List[Dict] = []
    if not raw:
        return rules

    def split_top_level_and(s: str) -> List[str]:
        parts: List[str] = []
        buf: List[str] = []
        depth = 0
        for ch in s:
            if ch == "(":
                depth += 1
                buf.append(ch)
            elif ch == ")":
                depth = max(0, depth - 1)
                buf.append(ch)
            elif ch == "&" and depth == 0:
                part = "".join(buf).strip()
                if part:
                    parts.append(part)
                buf = []
            else:
                buf.append(ch)
        tail = "".join(buf).strip()
        if tail:
            parts.append(tail)
        return parts

    def parse_or_group(term: str) -> List[str]:
        t = term.strip()
        # strip surrounding parentheses
        if t.startswith("(") and t.endswith(")"):
            t = t[1:-1].strip()
        # split OR
        items = [p.strip() for p in t.split("|")]
        return [p for p in items if p]

    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "->" not in line:
            continue

        left, right = line.split("->", 1)
        left = left.strip()
        right = right.strip()
        if not left or not right:
            continue

        # IF side: AND of OR-groups
        and_terms = split_top_level_and(left)
        if_groups: List[List[str]] = []
        for term in and_terms:
            group = parse_or_group(term)
            if group:
                if_groups.append(group)

        if not if_groups:
            continue

        mode = "NEVER"
        targets_part = right

        upper = right.upper()
        if upper.startswith("REQUIRE "):
            mode = "REQUIRE"
            targets_part = right[len("REQUIRE "):].strip()
        elif upper.startswith("NEVER "):
            mode = "NEVER"
            targets_part = right[len("NEVER "):].strip()

        # Targets: comma-separated
        t_parts = [p.strip() for p in targets_part.split(",")]
        targets = [p for p in t_parts if p]
        if not targets:
            continue

        rules.append({"if_groups": if_groups, "mode": mode, "targets": targets})

    return rules
def is_valid_combo_names(combo: Sequence[str], rules: List[Dict]) -> bool:
    """
    Returns False if the combination violates any of the provided rules.

    combo: list/tuple of *names*:
        [opt_var1_name, opt_var2_name, ..., camera_name]

    Rules support:
      - NEVER:   if IF matches AND any target is present -> invalid
      - REQUIRE: if IF matches AND any required target is missing -> invalid

    IF matching supports AND/OR groups:
      - '&' = AND across groups
      - '|' = OR within a group
      - IF matches when every group has at least one token present in the combo.
    """
    names = set(combo)

    for rule in rules:
        # Preferred: new if_groups structure (list[list[str]])
        if_groups = rule.get("if_groups")

        # Backward compatibility: old if_all list[str] or single if
        if not if_groups:
            conds = rule.get("if_all") or []
            if not conds:
                single = rule.get("if")
                if single:
                    conds = [single]
            if_groups = [[c] for c in conds] if conds else []

        if not if_groups:
            continue

        # IF matches when every group is satisfied (any token in group is present)
        matched = True
        for group in if_groups:
            if not any(tok in names for tok in group):
                matched = False
                break
        if not matched:
            continue

        mode = (rule.get("mode") or "NEVER").upper()
        targets = rule.get("targets") or rule.get("never") or []
        if not targets:
            continue

        if mode == "REQUIRE":
            for t in targets:
                if t not in names:
                    return False
        else:
            for t in targets:
                if t in names:
                    return False

    return True
def render_in_picture_viewer(
    doc: c4d.documents.BaseDocument,
    bc_rd: c4d.BaseContainer,
    *,
    is_threaded: bool = False,
    thd: Optional[c4d.threading.C4DThread] = None,
    callback_prog: Optional[Callable] = None,
    callback_write: Optional[Callable] = None,
) -> Tuple[int, c4d.bitmaps.MultipassBitmap]:
    """
    Render the document with the given render settings container `bc_rd`
    into a MultipassBitmap, optionally threaded.
    """
    # Creates a Multi Pass Bitmap, render result will be stored in
    x_res = int(bc_rd[c4d.RDATA_XRES])
    y_res = int(bc_rd[c4d.RDATA_YRES])
    bmp = c4d.bitmaps.MultipassBitmap(x_res, y_res, c4d.COLORMODE_RGB)
    if bmp is None:
        msg = "Failed to create bitmap for render."
        open_error_requester(msg)
        return c4d.RENDERRESULT_MEMORY, None

    # Adds an alpha channel
    bmp.AddChannel(True, True)

    # Renders the document
    flags_render = c4d.RENDERFLAGS_EXTERNAL | c4d.RENDERFLAGS_NODOCUMENTCLONE
    if not is_threaded:
        flags_render |= (
            c4d.RENDERFLAGS_SHOWERRORS
            | c4d.RENDERFLAGS_CREATE_PICTUREVIEWER
            | c4d.RENDERFLAGS_OPEN_PICTUREVIEWER
        )

    result = c4d.documents.RenderDocument(
        doc,
        bc_rd,
        bmp,
        flags_render,
        th=thd,
        prog=callback_prog,
        wprog=callback_write,
    )
    return result, bmp