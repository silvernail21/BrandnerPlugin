import random
from typing import Callable, Dict, List, Optional, Tuple

import c4d

from bccf_constants import (
    BR_CAMERAS,
    BR_CONSTANTS,
    BR_VARIABLES,
    BR_STAGE,
    DEFAULT_DIRECTORY_OUTPUT,
    DEFAULT_DELIMITER,
    DEFAULT_PREFIX,
    DEFAULT_PRODUCT_NAME,
    ID_BCB_DELIMITER,
    ID_BCB_DIRECTORY_OUTPUT,
    ID_BCB_PREFIX,
    ID_BCB_PRODUCT_NAME,
    ID_BCB_TOKEN_EXAMPLE_MODE,
    PREFIX_TOKEN_NAME)
from bccf_utils import (
    get_bc_brandner_from_doc,
    jump_to_frame)


TOKENS_CAMERA = "_b_cam"
TOKENS_CONSTANTS = "_b_consts"
TOKEN_CONST_0 = "_b_c0"
TOKEN_CONST_1 = "_b_c1"
TOKEN_CONST_2 = "_b_c2"
TOKEN_CONST_3 = "_b_c3"
TOKEN_CONST_4 = "_b_c4"
TOKEN_CONST_5 = "_b_c5"
TOKEN_CONST_6 = "_b_c6"
TOKEN_CONST_7 = "_b_c7"
TOKEN_CONST_8 = "_b_c8"
TOKEN_CONST_9 = "_b_c9"
TOKEN_DELIMITER = "_d"
TOKEN_DIRECTORY_OUTPUT = "_b_dir"
TOKEN_PREFIX = "_b_pre"
TOKEN_PRODUCT_NAME = "_b_prod"
TOKEN_VARIABLES = "_b_vars"
TOKEN_VAR_0 = "_b_v0"
TOKEN_VAR_1 = "_b_v1"
TOKEN_VAR_2 = "_b_v2"
TOKEN_VAR_3 = "_b_v3"
TOKEN_VAR_4 = "_b_v4"
TOKEN_VAR_5 = "_b_v5"
TOKEN_VAR_6 = "_b_v6"
TOKEN_VAR_7 = "_b_v7"
TOKEN_VAR_8 = "_b_v8"
TOKEN_VAR_9 = "_b_v9"


def get_mode_example(bcb: c4d.BaseContainer) -> bool:
    return bcb.GetBool(ID_BCB_TOKEN_EXAMPLE_MODE, False)


def get_brandner_token_string(
        data: c4d.BaseContainer, id_param: int, default: str) -> str:
    doc = data[0]
    bcb = get_bc_brandner_from_doc(doc)
    if bcb is None:
        return str()
    result = bcb.GetString(id_param, default)
    if len(result) == 0:
        result = default
    return result


def render_token_product_name(data: c4d.BaseContainer) -> str:
    return get_brandner_token_string(
        data, ID_BCB_PRODUCT_NAME, DEFAULT_PRODUCT_NAME)


def render_token_prefix(data: c4d.BaseContainer) -> str:
    return get_brandner_token_string(
        data, ID_BCB_PREFIX, DEFAULT_PREFIX)


def render_token_delimiter(data: c4d.BaseContainer) -> str:
    return get_brandner_token_string(
        data, ID_BCB_DELIMITER, DEFAULT_DELIMITER)


def render_output_directory(data: c4d.BaseContainer) -> str:
    return get_brandner_token_string(
        data, ID_BCB_DIRECTORY_OUTPUT, DEFAULT_DIRECTORY_OUTPUT)


def init_component_token(
    data: c4d.BaseContainer,
    name_component: str
) -> Tuple[Optional[c4d.BaseContainer],
           Optional[c4d.BaseObject]]:
    idx_frame = data[4]
    if idx_frame < 0:
        return None, None

    doc = data[0]
    bcb = get_bc_brandner_from_doc(doc)
    if bcb is None:
        return None, None

    obj_null = doc.SearchObject(name_component)
    if obj_null is None:
        return bcb, None

    jump_to_frame(doc, idx_frame)

    return bcb, obj_null


def get_random_option(obj_null: c4d.BaseObject) -> str:
    objs_children = obj_null.GetChildren()
    if len(objs_children) == 0:
        return str()

    obj_opt = random.choice(objs_children)
    if obj_opt is None:
        return str()

    return obj_opt.GetName()


def get_option(obj_null: c4d.BaseObject) -> str:
    name_opt = None
    for _obj_opt in obj_null.GetChildren():
        # In case we won't find a visible option, return first
        if name_opt is None:
            name_opt = _obj_opt.GetName()

        mode_vis_render = _obj_opt.GetRenderMode()
        if mode_vis_render != c4d.OBJECT_ON:
            continue

        name_opt = _obj_opt.GetName()

    return name_opt if name_opt is not None else str()


def render_token_variables(data: c4d.BaseContainer) -> str:
    bcb, null_variables = init_component_token(data, BR_VARIABLES)
    if bcb is None or null_variables is None:
        return str()

    is_mode_example = get_mode_example(bcb)
    names_selected = []
    for _obj_var in null_variables.GetChildren():
        if is_mode_example:
            name_opt = get_random_option(_obj_var)
            names_selected.append(name_opt)
            continue

        name_opt = get_option(_obj_var)
        names_selected.append(name_opt)

    delim = bcb.GetString(ID_BCB_DELIMITER, DEFAULT_DELIMITER)
    combination = delim.join(names_selected)
    return combination


def _render_token_variable_by_index(
        data: c4d.BaseContainer, idx_variable: int) -> str:

    bcb, null_variables = init_component_token(data, BR_VARIABLES)
    if bcb is None or null_variables is None:
        return str()

    objs_variables = null_variables.GetChildren()
    if idx_variable < 0 or idx_variable >= len(objs_variables):
        return f"Var{idx_variable}NotFound"

    obj_var = objs_variables[idx_variable]

    if get_mode_example(bcb):
        return get_random_option(obj_var)

    return get_option(obj_var)


def render_token_variable_0(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=0)


def render_token_variable_1(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=1)


def render_token_variable_2(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=2)


def render_token_variable_3(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=3)


def render_token_variable_4(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=4)


def render_token_variable_5(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=5)


def render_token_variable_6(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=6)


def render_token_variable_7(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=7)


def render_token_variable_8(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=8)


def render_token_variable_9(data: c4d.BaseContainer) -> str:
    return _render_token_variable_by_index(data, idx_variable=9)


FUNCS_VARIABLE_BY_INDEX = [
    render_token_variable_0,
    render_token_variable_1,
    render_token_variable_2,
    render_token_variable_3,
    render_token_variable_4,
    render_token_variable_5,
    render_token_variable_6,
    render_token_variable_7,
    render_token_variable_8,
    render_token_variable_9
]


def render_token_constants(data: c4d.BaseContainer) -> str:
    bcb, null_constants = init_component_token(data, BR_CONSTANTS)
    if bcb is None or null_constants is None:
        return str()

    names_constants = []
    for _obj_const in null_constants.GetChildren():
        name_const = _obj_const.GetName()
        names_constants.append(name_const)

    delim = bcb.GetString(ID_BCB_DELIMITER, DEFAULT_DELIMITER)
    combination = delim.join(names_constants)
    return combination


def _render_token_constant_by_index(
        data: c4d.BaseContainer, idx_constant: int) -> str:
    bcb, null_constants = init_component_token(data, BR_CONSTANTS)
    if bcb is None or null_constants is None:
        return str()

    objs_constants = null_constants.GetChildren()
    if idx_constant < 0 or idx_constant >= len(objs_constants):
        return f"Const{idx_constant}NotFound"

    obj_const = objs_constants[idx_constant]
    return obj_const.GetName()


def token_variable_by_index(idx_var: int) -> Tuple[Callable, str, str]:
    return (FUNCS_VARIABLE_BY_INDEX[idx_var],
            f"{PREFIX_TOKEN_NAME}Variable {idx_var}",
            f"v{idx_var}")


def render_token_constant_0(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=0)


def render_token_constant_1(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=1)


def render_token_constant_2(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=2)


def render_token_constant_3(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=3)


def render_token_constant_4(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=4)


def render_token_constant_5(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=5)


def render_token_constant_6(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=6)


def render_token_constant_7(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=7)


def render_token_constant_8(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=8)


def render_token_constant_9(data: c4d.BaseContainer) -> str:
    return _render_token_constant_by_index(data, idx_constant=9)


FUNCS_CONSTANT_BY_INDEX = [
    render_token_constant_0,
    render_token_constant_1,
    render_token_constant_2,
    render_token_constant_3,
    render_token_constant_4,
    render_token_constant_5,
    render_token_constant_6,
    render_token_constant_7,
    render_token_constant_8,
    render_token_constant_9
]


def token_constant_by_index(idx_constant: int) -> Tuple[Callable, str, str]:
    return (FUNCS_CONSTANT_BY_INDEX[idx_constant],
            f"{PREFIX_TOKEN_NAME}Constant {idx_constant}",
            f"c{idx_constant}")


def render_token_camera_mode_example(data: c4d.BaseContainer) -> str:
    doc = data[0]
    null_cameras = doc.SearchObject(BR_CAMERAS)
    if null_cameras is None:
        return str()
    objs_cameras = null_cameras.GetChildren()
    if len(objs_cameras) == 0:
        return "CamNoCameras"
    obj_cam = random.choice(objs_cameras)
    name_cam = obj_cam.GetName()
    return name_cam


def render_token_camera(data: c4d.BaseContainer) -> str:
    bcb, obj_stage = init_component_token(data, BR_STAGE)
    if bcb is None:
        return str()

    if get_mode_example(bcb):
        return render_token_camera_mode_example(data)

    if obj_stage is None:
        return "CamNoStage"

    # We could also read selected cam from keyframe
    # (no more need to jump to frame).
    # Yet, I considered below simpler.
    # obj_cam = get_keyframed_cam(obj_stage)
    obj_cam = obj_stage[c4d.STAGEOBJECT_CLINK]
    if obj_cam is None:
        return "CamNoneStaged"
    name_cam = obj_cam.GetName()
    return name_cam


# Order defines order in menus
RENDER_TOKENS = {
    TOKEN_PREFIX:
        (render_token_prefix,
         f"{PREFIX_TOKEN_NAME}Prefix",
         "SCH"),
    TOKEN_PRODUCT_NAME:
        (render_token_product_name,
         f"{PREFIX_TOKEN_NAME}Product Name",
         "Product #42"),
    TOKEN_VARIABLES:  # Variable combination / Visible object names
        (render_token_variables,
         f"{PREFIX_TOKEN_NAME}Variables",
         "v1_v2_v3_..."),
    # Variable by index / Visible object name
    TOKEN_VAR_0: token_variable_by_index(0),
    TOKEN_VAR_1: token_variable_by_index(1),
    TOKEN_VAR_2: token_variable_by_index(2),
    TOKEN_VAR_3: token_variable_by_index(3),
    TOKEN_VAR_4: token_variable_by_index(4),
    TOKEN_VAR_5: token_variable_by_index(5),
    TOKEN_VAR_6: token_variable_by_index(6),
    TOKEN_VAR_7: token_variable_by_index(7),
    TOKEN_VAR_8: token_variable_by_index(8),
    TOKEN_VAR_9: token_variable_by_index(9),
    TOKENS_CONSTANTS:  # Constant combination / Visible object names
        (render_token_constants,
         f"{PREFIX_TOKEN_NAME}Constants",
         "c1_c2_c3_..."),
    # Constant by index / Visible object name
    TOKEN_CONST_0: token_constant_by_index(0),
    TOKEN_CONST_1: token_constant_by_index(1),
    TOKEN_CONST_2: token_constant_by_index(2),
    TOKEN_CONST_3: token_constant_by_index(3),
    TOKEN_CONST_4: token_constant_by_index(4),
    TOKEN_CONST_5: token_constant_by_index(5),
    TOKEN_CONST_6: token_constant_by_index(6),
    TOKEN_CONST_7: token_constant_by_index(7),
    TOKEN_CONST_8: token_constant_by_index(8),
    TOKEN_CONST_9: token_constant_by_index(9),
    TOKENS_CAMERA:
        (render_token_camera,
         f"{PREFIX_TOKEN_NAME}Camera Name",
         "Camera"),
    TOKEN_DIRECTORY_OUTPUT:
        (render_output_directory,
         f"{PREFIX_TOKEN_NAME}Output Directory",
         "./output/"),
    TOKEN_DELIMITER:  # rather keep short
        (render_token_delimiter,
         f"{PREFIX_TOKEN_NAME}Delimiter",
         "_"),
}


LIST_TOKENS_CONSTANTS = [
    TOKEN_CONST_0,
    TOKEN_CONST_1,
    TOKEN_CONST_2,
    TOKEN_CONST_3,
    TOKEN_CONST_4,
    TOKEN_CONST_5,
    TOKEN_CONST_6,
    TOKEN_CONST_7,
    TOKEN_CONST_8,
    TOKEN_CONST_9
]


LIST_TOKENS_VARIABLES = [
    TOKEN_VAR_0,
    TOKEN_VAR_1,
    TOKEN_VAR_2,
    TOKEN_VAR_3,
    TOKEN_VAR_4,
    TOKEN_VAR_5,
    TOKEN_VAR_6,
    TOKEN_VAR_7,
    TOKEN_VAR_8,
    TOKEN_VAR_9
]


def get_tokens_list() -> List[Dict[str, str]]:
    """Returns dict with Brandner tokens to register.

    Removes already registered tokens from global list to avoid re-register.
    """

    tokens_to_register = RENDER_TOKENS.copy()
    for _registered_token in c4d.modules.tokensystem.GetAllTokenEntries():
        token = _registered_token["_token"]
        if token in tokens_to_register.keys():
            del tokens_to_register[token]
    return tokens_to_register


def get_all_tokens(
    tokens_brandner: List[Dict[str, str]],
    tokens_brandner_vars: List[Dict[str, str]],
    tokens_brandner_consts: List[Dict[str, str]],
    tokens_other: List[Dict[str, str]]
) -> None:
    registered_tokens = c4d.modules.tokensystem.GetAllTokenEntries()
    for _dict_token in registered_tokens:
        token = _dict_token["_token"]
        if token in LIST_TOKENS_VARIABLES:
            tokens_brandner_vars.append(_dict_token)
        elif token in LIST_TOKENS_CONSTANTS:
            tokens_brandner_consts.append(_dict_token)
        elif token in RENDER_TOKENS:
            tokens_brandner.append(_dict_token)
        else:
            tokens_other.append(_dict_token)


def sort_brandner_tokens(tokens_brandner: List[Dict[str, str]]):
    for _token_search in RENDER_TOKENS.keys():
        dict_token_brandner = None
        for _dict_token in tokens_brandner:
            token = _dict_token["_token"]
            if token == _token_search:
                dict_token_brandner = _dict_token
                break
        if dict_token_brandner is None:
            continue
        # Move to end of list
        tokens_brandner.remove(dict_token_brandner)
        tokens_brandner.append(dict_token_brandner)


def add_tokens_to_bc_menu(
    bc_menu: c4d.BaseContainer,
    dict_menu_tokens: Dict[int, str],
    tokens: List[Dict[str, str]],
    offset_ids: int = 0
) -> None:
    id_base = c4d.FIRST_POPUP_ID + offset_ids
    for _idx_token, _dict_token in enumerate(tokens):
        token = _dict_token["_token"]
        name = _dict_token["_help"]
        example = _dict_token["_example"]

        id_token = id_base + _idx_token
        bc_menu.InsData(id_token, f"{name} - {example}")
        dict_menu_tokens[id_token] = token


def add_tokens_submenu(
    bc_menu: c4d.BaseContainer,
    dict_menu_tokens: Dict[int, str],
    tokens: List[Dict[str, str]],
    *,
    id_submeu: int,
    name_submenu: str = "",
    offset_ids: int = 0
) -> None:
    bc_submenu_vars = c4d.BaseContainer()
    bc_submenu_vars.InsData(1, f"{PREFIX_TOKEN_NAME}{name_submenu}")
    add_tokens_to_bc_menu(
        bc_submenu_vars, dict_menu_tokens, tokens, offset_ids=offset_ids)
    bc_menu.InsData(id_submeu, bc_submenu_vars)


def get_token_bc_menu() -> c4d.BaseContainer:
    OFFSET_VARS = 10000
    OFFSET_CONSTS = 20000
    OFFSET_OTHER = 30000

    tokens_brandner = []
    tokens_brandner_vars = []
    tokens_brandner_consts = []
    tokens_other = []
    get_all_tokens(
        tokens_brandner,
        tokens_brandner_vars,
        tokens_brandner_consts,
        tokens_other)
    sort_brandner_tokens(tokens_brandner)
    sort_brandner_tokens(tokens_brandner_vars)
    sort_brandner_tokens(tokens_brandner_consts)

    bc_menu = c4d.BaseContainer()
    dict_menu_tokens = {}
    add_tokens_to_bc_menu(bc_menu, dict_menu_tokens, tokens_brandner)

    bc_menu.InsData(0, "")  # separator

    bc_submenu_vars = c4d.BaseContainer()
    bc_submenu_vars.InsData(1, f"{PREFIX_TOKEN_NAME}Variables by Index")
    add_tokens_to_bc_menu(
        bc_submenu_vars, dict_menu_tokens, tokens_brandner_vars,
        offset_ids=OFFSET_VARS)
    bc_menu.InsData(99000, bc_submenu_vars)
    bc_submenu_consts = c4d.BaseContainer()
    bc_submenu_consts.InsData(1, f"{PREFIX_TOKEN_NAME}Constants by Index")
    add_tokens_to_bc_menu(
        bc_submenu_consts, dict_menu_tokens, tokens_brandner_consts,
        offset_ids=OFFSET_CONSTS)
    bc_menu.InsData(99001, bc_submenu_consts)

    bc_menu.InsData(0, "")  # separator

    add_tokens_to_bc_menu(
        bc_menu, dict_menu_tokens, tokens_other, offset_ids=OFFSET_OTHER)

    return bc_menu


def token_path_to_token_names(path: str) -> str:
    words = []
    word = ""
    for _char in path:
        if _char == "$":
            if len(word) > 0:
                words.append(word)
                word = ""
            continue

        word += _char
        if word not in RENDER_TOKENS:
            continue

        if word != TOKEN_DELIMITER:
            name = RENDER_TOKENS[word][1]
            name = name.replace(PREFIX_TOKEN_NAME, "")
        else:
            name = "|"
        words.append(name)
        word = ""
    if len(word) > 0:
        words.append(word)

    token_names = " ".join(words)
    return token_names
