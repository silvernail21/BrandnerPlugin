from datetime import datetime
import itertools
import logging
import os
import random
from typing import List, Optional, Dict, Tuple

import c4d

from bccf_constants import (
    BR_COMPONENTS,
    BR_VARIABLES,
    BR_CONSTANTS,
    BR_CAMERAS,
    BR_STAGE,
    ID_BCB_PREFIX,
    ID_BCB_DELIMITER,
    ID_BCB_PRODUCT_NAME,
    ID_BCB_DIRECTORY_OUTPUT,
    ID_BCB_DO_GENERATE_CSV,
    ID_BCB_DO_SAVE_PROJECT,
    ID_BCB_FILENAME,
    ID_BCB_MODE_RENDER,
    ID_BCB_TOKEN_EXAMPLE_MODE,
    MODE_RENDER_CMD_RENDER,
    MODE_RENDER_NO_RENDER,
    MODE_RENDER_PV,
    MODE_RENDER_RQ_QUEUE,
    MODE_RENDER_RQ_QUEUE_START,
    PLUGIN_ID_BRANDNER,
    PLUGIN_NAME_BRANDNER,
    PLUGIN_VERSION,
    SUFFIX_NO_OPTION,
    ID_BCB_EXCLUSION_RULES_RAW,
    ID_BCB_RULE_IF,
    ID_BCB_RULE_TARGET,
    ID_BCB_RULE_ACTION,
    ID_BCB_RULE_ADD,
    ID_BCB_RULE_ADD_AND,
    ID_BCB_RULE_ADD_OR,
    ID_BCB_RULE_CLEAR_IF,
    ID_TXT_RULE_IF_PREVIEW,
    ID_STR_RULE_STATUS,
)

from bccf_render_tokens import (
    add_tokens_submenu,
    add_tokens_to_bc_menu,
    get_all_tokens,
    sort_brandner_tokens,
    token_path_to_token_names,
)
from bccf_utils import (
    cancel_thread_render,
    consume_render_result,
    consume_rendered_image_paths,
    create_null,
    create_stage,
    get_bc_brandner_default,
    get_bc_brandner_from_doc,
    get_bc_brandner,
    get_default_output_directory,
    get_index_render_frame,
    get_visibility,
    is_rendering,
    jump_to_frame,
    normalize_output_directory,
    open_error_requester,
    queue_batch_render,
    save_project,
    select_object,
    set_keyframe_cam,
    set_visibility_hide,
    set_visibility_show,
    set_visibility_direct,
    resolve_output_directory,
    store_bc_brandner,
    render_in_picture_viewer_ext,
    reset_render_progress,
    validate_bc_brandner,
    parse_exclusion_rules,
    is_valid_combo_names,
)


# Dialog IDs
NO_ID = 0

ID_BTN_RENDER = 1001
ID_BTN_RANDOMIZE = 1002
ID_BTN_DEFAULT_VISIBILITY = 1003
ID_BTN_OUT_DIR = 1004
ID_BTN_ADD_TOKEN = 1005
ID_BTN_INIT_HIERARCHY = 1006
ID_BTN_REFRESH = 1007
ID_BTN_WRITE_CSV = 1008
ID_BTN_COMBO_PREV = 1009
ID_BTN_COMBO_NEXT = 1010

ID_TGRP_TABS = 2000
ID_GRP_RENDER = 2001
ID_GRP_COMPONENT = 2002
ID_GRP_TAB_SETUP = 2003
ID_GRP_TAB_OUTPUT = 2004
ID_GRP_TAB_RULES = 2005

OFFSET_LABEL = 1
OFFSET_WARN = 2
OFFSET_NO_ENTITIES = 3
ID_CMB_VARS = 2100
ID_STR_VARS_LABEL = ID_CMB_VARS + OFFSET_LABEL
ID_STR_VARS_WARN = ID_CMB_VARS + OFFSET_WARN
ID_CMB_OPTS = 2110
ID_STR_OPTS_LABEL = ID_CMB_OPTS + OFFSET_LABEL
ID_STR_OPTS_WARN = ID_CMB_OPTS + OFFSET_WARN
ID_CMB_VIEWS = 2120
ID_STR_VIEWS_LABEL = ID_CMB_VIEWS + OFFSET_LABEL
ID_STR_VIEWS_WARN = ID_CMB_VIEWS + OFFSET_WARN
ID_CMB_CONSTS = 2130
ID_STR_CONSTS_LABEL = ID_CMB_CONSTS + OFFSET_LABEL
ID_STR_CONSTS_WARN = ID_CMB_CONSTS + OFFSET_WARN

ID_STR_COMBO_COUNT = 2190
ID_STR_SCENE_WARNINGS = 2191
ID_STR_COMBO_POS = 2192

ID_FILE_STRUCTURE_LIST = 2300
ID_TXT_TOKEN_HELP = 2301
ID_TXT_TOKEN_HELP_TT = 2302

# Range 10000 <= id < 20000 reserved for BCB IDs
ID_STR_PREFIX = ID_BCB_PREFIX
ID_STR_DELIMITER = ID_BCB_DELIMITER
ID_STR_FILENAME = ID_BCB_FILENAME
ID_STR_DIR_OUT = ID_BCB_DIRECTORY_OUTPUT
ID_STR_PRODUCT_NAME = ID_BCB_PRODUCT_NAME
ID_CHK_GENERATE_CSV = ID_BCB_DO_GENERATE_CSV
ID_CHK_SAVE_PROJECT = ID_BCB_DO_SAVE_PROJECT
ID_CMB_MODE_RENDER = ID_BCB_MODE_RENDER


IDS_PARAMETERS = [
    ID_CHK_GENERATE_CSV,
    ID_CHK_SAVE_PROJECT,
    ID_CMB_MODE_RENDER,
    ID_STR_DELIMITER,
    ID_STR_PREFIX,
    ID_STR_PRODUCT_NAME,
]

IDS_PARAMETERS_BOOL = [
    ID_CHK_GENERATE_CSV,
    ID_CHK_SAVE_PROJECT,
]

IDS_PARAMETERS_INT = [
    ID_CMB_MODE_RENDER,
]

IDS_PARAMETERS_STRING = [
    ID_STR_DELIMITER,
    ID_STR_FILENAME,
    ID_STR_DIR_OUT,
    ID_STR_PREFIX,
    ID_STR_PRODUCT_NAME,
]


IDS_DISABLE_ALL = [
    ID_BTN_RANDOMIZE,
    ID_BTN_COMBO_PREV,
    ID_BTN_COMBO_NEXT,
    ID_BTN_DEFAULT_VISIBILITY,
    ID_BTN_OUT_DIR,
    ID_BTN_ADD_TOKEN,
    ID_BTN_INIT_HIERARCHY,
    ID_BTN_REFRESH,
    ID_BTN_WRITE_CSV,
    ID_CMB_VARS,
    ID_CMB_CONSTS,
    ID_CMB_OPTS,
    ID_CMB_VIEWS,
    ID_STR_PREFIX,
    ID_STR_DELIMITER,
    ID_STR_FILENAME,
    ID_STR_DIR_OUT,
    ID_STR_PRODUCT_NAME,
    ID_CHK_GENERATE_CSV,
    ID_CHK_SAVE_PROJECT,
    ID_CMB_MODE_RENDER,
    ID_FILE_STRUCTURE_LIST,
]

IDS_ENABLE_ALL = [
    ID_BTN_RANDOMIZE,
    ID_BTN_COMBO_PREV,
    ID_BTN_COMBO_NEXT,
    ID_BTN_DEFAULT_VISIBILITY,
    ID_BTN_OUT_DIR,
    ID_BTN_ADD_TOKEN,
    ID_BTN_INIT_HIERARCHY,
    ID_BTN_REFRESH,
    ID_CMB_VARS,
    ID_CMB_CONSTS,
    ID_CMB_OPTS,
    ID_CMB_VIEWS,
    ID_STR_PREFIX,
    ID_STR_DELIMITER,
    ID_STR_FILENAME,
    ID_STR_DIR_OUT,
    ID_STR_PRODUCT_NAME,
    ID_CHK_GENERATE_CSV,
    ID_CHK_SAVE_PROJECT,
    ID_CMB_MODE_RENDER,
    ID_FILE_STRUCTURE_LIST,
]


# Layout flags, BF_h[h][v[v]]
BF_L = c4d.BFH_LEFT
BF_R = c4d.BFH_RIGHT
BF_RS = c4d.BFH_RIGHT | c4d.BFH_SCALE
BF_SF = c4d.BFH_SCALEFIT
BF_SFSF = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT
BF_SFT = c4d.BFH_SCALEFIT | c4d.BFV_TOP


BAKE_FRAME_OFFSET = 1  # start baked combo frames at 1

class BrandnerDialog(c4d.gui.GeDialog):

    doc_last: c4d.documents.BaseDocument

    bcb: c4d.BaseContainer

    variables: List[str]
    variables_combobox: List[str]
    dyn_options: List[str]
    dyn_options_combobox: List[str]
    cameras: List[str]
    cameras_combobox: List[str]
    constants: List[str]
    constants_combobox: List[str]

    possible_combinations: List[List[str]]

    def __init__(self):
        super().__init__()

        # map combo index → option name (for exception rules UI)
        self._rule_option_names: Dict[int, str] = {}

        self.bcb = get_bc_brandner(do_init_doc=False)

        self._scene_cache: Dict[str, Dict] = {}
        self._combos_dirty: bool = True
        self._raw_combo_count: int = 0
        self._preview_combo_idx: Optional[int] = None
        self._preview_cache_key: Optional[tuple] = None

        self.init_component_names()
        self.possible_combinations = self.calculate_combinations()
        self._combos_dirty = False

    # ------------------------------------------------------------------
    # Component discovery
    # ------------------------------------------------------------------

    def init_component_names(self) -> None:
        self.build_scene_cache()
        self.variables = self._scene_cache.get("variable_names", [])
        self.variables_combobox = self._scene_cache.get("variable_names_combo", [])
        self.init_dyn_options(idx_var_selected=0)
        self.cameras = self._scene_cache.get("camera_names", [])
        self.cameras_combobox = self._scene_cache.get("camera_names_combo", [])
        self.constants = self._scene_cache.get("constant_names", [])
        self.constants_combobox = self._scene_cache.get("constant_names_combo", [])
        self._combos_dirty = True

    def build_scene_cache(self) -> None:
        doc = c4d.documents.GetActiveDocument()
        cache: Dict[str, Dict] = {
            "variables_root": None,
            "cameras_root": None,
            "constants_root": None,
            "variables": {},
            "options": {},
            "cameras": {},
            "constants": {},
            "variable_names": [],
            "variable_names_combo": [],
            "camera_names": [],
            "camera_names_combo": [],
            "constant_names": [],
            "constant_names_combo": [],
        }
        if doc is None:
            self._scene_cache = cache
            return

        null_vars = doc.SearchObject(BR_VARIABLES)
        null_cams = doc.SearchObject(BR_CAMERAS)
        null_consts = doc.SearchObject(BR_CONSTANTS)

        cache["variables_root"] = null_vars
        cache["cameras_root"] = null_cams
        cache["constants_root"] = null_consts

        if null_vars is not None:
            for var in null_vars.GetChildren():
                vname = var.GetName()
                cache["variables"][vname] = {
                    "root": var,
                    "options": {child.GetName(): child for child in var.GetChildren()},
                    "option_names": [child.GetName() for child in var.GetChildren()],
                }
                num_grandchildren = len(var.GetChildren())
                suffix_no_option = SUFFIX_NO_OPTION if num_grandchildren == 0 else ""
                id_icon = var.GetType()
                cache["variable_names"].append(vname)
                cache["variable_names_combo"].append(f"{vname}{suffix_no_option}&i{id_icon}&")
                for child in var.GetChildren():
                    cache["options"][child.GetName()] = child

        if null_cams is not None:
            for cam in null_cams.GetChildren():
                name = cam.GetName()
                cache["cameras"][name] = cam
                cache["camera_names"].append(name)
                cache["camera_names_combo"].append(f"{name}&i{cam.GetType()}&")

        if null_consts is not None:
            for const in null_consts.GetChildren():
                name = const.GetName()
                cache["constants"][name] = const
                cache["constant_names"].append(name)
                cache["constant_names_combo"].append(f"{name}&i{const.GetType()}&")

        self._scene_cache = cache

    @staticmethod
    def get_elements(
        name_obj: str,
        *,
        append_icon: bool = False,
        append_warn: bool = False,
    ) -> List[str]:
        doc = c4d.documents.GetActiveDocument()
        obj_element = doc.SearchObject(name_obj)
        if obj_element is None:
            return []

        elements = []
        for _obj_child in obj_element.GetChildren():
            num_grandchildren = len(_obj_child.GetChildren())
            suffix_no_option = ""
            if append_warn and num_grandchildren == 0:
                suffix_no_option = SUFFIX_NO_OPTION

            id_icon = _obj_child.GetType()
            suffix_icon = f"&i{id_icon}&" if append_icon else ""

            name_child = _obj_child.GetName()
            name = f"{name_child}{suffix_no_option}{suffix_icon}"
            elements.append(name)
        return elements

    def init_dyn_options(self, *, idx_var_selected: Optional[int] = None) -> None:
        num_variables = len(self.variables)
        if num_variables == 0:
            self.dyn_options = []
            self.dyn_options_combobox = []
            return

        if idx_var_selected is None:
            idx_var_selected = self.GetInt32(ID_CMB_VARS)
        idx_var_selected = max(0, idx_var_selected)
        idx_var_selected = min(idx_var_selected, num_variables - 1)

        name_var = self.variables[idx_var_selected]
        self.dyn_options = self.get_options(name_var)
        self.dyn_options_combobox = self.get_options(name_var, append_icon=True)

    def get_options(self, name_var: str, *, append_icon: bool = False) -> List[str]:
        var_info = self._scene_cache.get("variables", {}).get(name_var)
        if var_info is None:
            return []

        options = []
        for _obj_option in var_info.get("options", {}).values():
            name_option = _obj_option.GetName()
            if append_icon:
                id_icon = _obj_option.GetType()
                name_option = f"{name_option}&i{id_icon}&"
            options.append(name_option)
        return options

    # Helpers to build combinations from scene
    def get_variables_options_names(self) -> List[List[str]]:
        """Return [[opt names for var1], [opt names for var2], ...]."""
        result: List[List[str]] = []
        for vname in self._scene_cache.get("variable_names", []):
            opts = list(self._scene_cache.get("variables", {}).get(vname, {}).get("option_names", []))
            if opts:
                result.append(opts)
        return result

    def get_camera_names(self) -> List[str]:
        """Return list of camera names under BR_CAMERAS."""
        return list(self._scene_cache.get("camera_names", []))

    def ensure_combinations(self) -> None:
        if getattr(self, "_combos_dirty", True):
            self.possible_combinations = self.calculate_combinations()
            self._combos_dirty = False

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def CreateLayout(self):
        self.SetTitle(f"{PLUGIN_NAME_BRANDNER} v{PLUGIN_VERSION}")

        if self.GroupBegin(NO_ID, BF_SFSF, cols=1):
            self.GroupBorderSpace(5, 5, 5, 5)
            self.GroupSpace(0, 8)

            self.cl_group_topbar()

            if self.TabGroupBegin(ID_TGRP_TABS, BF_SFSF):
                self.cl_group_tab_setup()
                self.cl_group_tab_output()
                self.cl_group_tab_rules()
                self.cl_group_tab_render()
            self.GroupEnd()  # TabGroup

            # Primary action — always visible regardless of active tab.
            # Its label doubles as a status/guidance line.
            self.AddButton(ID_BTN_RENDER, BF_SF, name=" ", inith=20)
        self.GroupEnd()  # Dialog

        return True

    def cl_group_topbar(self) -> None:
        """Always-visible bar: scene refresh + live combination count + warnings."""
        if self.GroupBegin(NO_ID, BF_SF, cols=1):
            self.GroupSpace(0, 2)

            if self.GroupBegin(NO_ID, BF_SF, cols=2, rows=1):
                self.GroupSpace(10, 0)

                self.AddButton(
                    ID_BTN_REFRESH, BF_L, name="Refresh Scene", initw=140, inith=12
                )
                self.AddStaticText(
                    ID_STR_COMBO_COUNT,
                    BF_RS,
                    name="00000 / 00000 Combinations",  # replaced in InitValues()
                    borderstyle=c4d.BORDER_WITH_TITLE_BOLD,
                )
            self.GroupEnd()

            # Scene/setup problem line — blank when everything is OK.
            self.AddStaticText(ID_STR_SCENE_WARNINGS, BF_SF, name=" ")
        self.GroupEnd()

    # ---- Tabs ---------------------------------------------------------

    def cl_group_tab_setup(self) -> None:
        if self.GroupBegin(ID_GRP_TAB_SETUP, BF_SFT, cols=1, title=" 1. Setup "):
            self.GroupSpace(0, 10)
            self.GroupBorderSpace(0, 8, 0, 0)

            self.cl_group_general_settings()
            self.cl_group_components()
            self.cl_group_preview_tools()
        self.GroupEnd()

    def cl_group_tab_output(self) -> None:
        if self.GroupBegin(ID_GRP_TAB_OUTPUT, BF_SFT, cols=1, title=" 2. Output "):
            self.GroupSpace(0, 10)
            self.GroupBorderSpace(0, 8, 0, 0)

            self.cl_group_render_parameters()
        self.GroupEnd()

    def cl_group_tab_rules(self) -> None:
        if self.GroupBegin(ID_GRP_TAB_RULES, BF_SFSF, cols=1, title=" 3. Rules "):
            self.GroupSpace(0, 10)
            self.GroupBorderSpace(0, 8, 0, 0)

            self.cl_group_exceptions()
        self.GroupEnd()

    def cl_group_tab_render(self) -> None:
        if self.GroupBegin(ID_GRP_RENDER, BF_SFSF, cols=1, title=" 4. Render "):
            self.GroupSpace(0, 10)
            self.GroupBorderSpace(0, 8, 0, 0)

            self.cl_group_render_options()
            self.cl_group_file_structure_preview()
        self.GroupEnd()

    # ---- Setup tab groups ----------------------------------------------

    def cl_group_general_settings(self) -> None:
        if self.GroupBegin(NO_ID, BF_SF, title="Product", cols=1):
            self.GroupBorder(c4d.BORDER_WITH_TITLE_BOLD)
            self.GroupBorderSpace(10, 5, 10, 10)
            self.GroupSpace(0, 6)

            if self.GroupBegin(NO_ID, BF_SF, cols=2, rows=1):
                self.GroupSpace(5, 0)
                self.AddStaticText(NO_ID, BF_L, name="Product Name")
                self.AddEditText(ID_STR_PRODUCT_NAME, BF_SF)
            self.GroupEnd()

            self.AddButton(
                ID_BTN_INIT_HIERARCHY,
                BF_SF,
                name="Set Up Project Hierarchy",
                inith=10,
            )
            self.AddStaticText(
                NO_ID,
                BF_L,
                name="Creates BR_VARIABLES / BR_CAMERAS / BR_CONSTANTS groups in the Object Manager.",
            )
        self.GroupEnd()  # Settings

    def cl_group_components(self, idx_var: int = 0) -> None:
        if self.GroupBegin(ID_GRP_COMPONENT, BF_SF, cols=1, title="Scene Components"):
            self.GroupBorder(c4d.BORDER_WITH_TITLE_BOLD)
            self.GroupBorderSpace(10, 5, 10, 10)
            self.GroupSpace(0, 10)

            self.AddStaticText(
                NO_ID,
                BF_L,
                name="Items found in your scene. Press Refresh Scene after changing objects.",
            )

            self.cl_add_combo_box(ID_CMB_VARS)
            self.cl_add_combo_box(ID_CMB_OPTS)
            self.cl_add_combo_box(ID_CMB_VIEWS)
            self.cl_add_combo_box(ID_CMB_CONSTS)
        self.GroupEnd()  # Components

    def cl_group_preview_tools(self) -> None:
        if self.GroupBegin(NO_ID, BF_SF, cols=1, title="Preview Tools"):
            self.GroupBorder(c4d.BORDER_WITH_TITLE_BOLD)
            self.GroupBorderSpace(10, 5, 10, 10)
            self.GroupSpace(0, 6)

            # Step through every valid combination in the viewport
            if self.GroupBegin(NO_ID, BF_SF, cols=3, rows=1):
                self.GroupSpace(5, 0)
                self.AddButton(ID_BTN_COMBO_PREV, BF_L, name="< Prev", initw=80)
                self.AddStaticText(
                    ID_STR_COMBO_POS,
                    BF_SF | c4d.BFV_CENTER,
                    name="Combination - of -",
                )
                self.AddButton(ID_BTN_COMBO_NEXT, BF_R, name="Next >", initw=80)
            self.GroupEnd()

            if self.GroupBegin(NO_ID, BF_SF, cols=2, rows=1):
                self.AddButton(
                    ID_BTN_RANDOMIZE,
                    BF_SF,
                    name="Show Random Combination",
                    inith=10,
                )
                self.AddButton(
                    ID_BTN_DEFAULT_VISIBILITY,
                    BF_SF,
                    name="Reset Default Visibility",
                    inith=10,
                )
            self.GroupEnd()
        self.GroupEnd()

    def cl_add_combo_box(
        self,
        id_combo: int,
        *,
        do_vertical: bool = True,
    ) -> None:
        cols = 1 if do_vertical else 0
        rows = 1 if not do_vertical else 0
        if self.GroupBegin(NO_ID, BF_SF, cols=cols, rows=rows):
            self.AddStaticText(id_combo + OFFSET_LABEL, BF_SF, name=" ")
            self.AddComboBox(id_combo, BF_SF)
            self.AddStaticText(
                id_combo + OFFSET_WARN,
                BF_SF,
                name="Some entities have no options.",
                borderstyle=c4d.BORDER_WITH_TITLE_BOLD,
            )
        self.GroupEnd()

    # ---- Output tab groups ----------------------------------------------

    def cl_group_render_parameters(self) -> None:
        if self.GroupBegin(NO_ID, BF_SF, cols=1, title="File Naming & Output"):
            self.GroupBorder(c4d.BORDER_WITH_TITLE_BOLD)
            self.GroupBorderSpace(10, 5, 10, 10)
            self.GroupSpace(0, 10)

            self.cl_group_render_parameters_prefix()
            self.cl_group_render_parameters_filename()
        self.GroupEnd()

    def cl_group_render_parameters_prefix(self) -> None:
        if self.GroupBegin(NO_ID, BF_SF, rows=1):  # Prefix/Delim
            self.GroupSpace(5, 10)

            self.AddStaticText(NO_ID, BF_L, name="Prefix")
            self.AddEditText(ID_STR_PREFIX, BF_SF)
            self.AddStaticText(NO_ID, BF_L, name=" ", initw=10)  # spacer
            self.AddStaticText(NO_ID, BF_L, name="Delimiter")
            self.AddEditText(ID_STR_DELIMITER, BF_SF)
        self.GroupEnd()

    def cl_group_render_parameters_filename(self) -> None:
        if self.GroupBegin(NO_ID, BF_SF, cols=3):  # Dir/Filename
            self.GroupSpace(5, 10)

            self.AddStaticText(NO_ID, BF_L, name="Output Folder")
            self.AddEditText(ID_STR_DIR_OUT, BF_SF)
            self.AddButton(ID_BTN_OUT_DIR, BF_R, name="Browse...")

            self.AddStaticText(NO_ID, BF_L, name="Filename Pattern")
            self.AddEditText(ID_STR_FILENAME, BF_SF)
            self.AddButton(ID_BTN_ADD_TOKEN, BF_R, name="+ Token")

            self.cl_render_parameters_filename_help()
        self.GroupEnd()

    def cl_render_parameters_filename_help(self) -> None:
        self.AddStaticText(NO_ID, BF_L, name=" ")
        if self.GroupBegin(NO_ID, BF_SF, cols=3):
            self.AddStaticText(NO_ID, BF_L, name=" ", initw=10)
            self.AddStaticText(ID_TXT_TOKEN_HELP, BF_SFT, name=" ")
            self.AddStaticText(NO_ID, BF_R, name=" ", initw=10)
        self.GroupEnd()

        self.AddStaticText(ID_TXT_TOKEN_HELP_TT, BF_R, name=" " * 10)

    # ---- Render tab groups ----------------------------------------------

    def cl_group_render_options(self) -> None:
        if self.GroupBegin(NO_ID, BF_SF, cols=1, title="Render Settings"):
            self.GroupBorder(c4d.BORDER_WITH_TITLE_BOLD)
            self.GroupBorderSpace(10, 5, 10, 10)
            self.GroupSpace(0, 10)

            self.cl_group_combobox_render_mode()
            self.cl_group_render_extras()
        self.GroupEnd()

    def cl_group_render_extras(self) -> None:
        if self.GroupBegin(NO_ID, BF_SF, cols=3, rows=1):
            self.GroupSpace(20, 0)

            self.AddCheckbox(
                ID_CHK_SAVE_PROJECT,
                BF_L,
                name="Save Project",
                initw=0,
                inith=0,
            )
            self.AddCheckbox(
                ID_CHK_GENERATE_CSV,
                BF_L,
                name="Generate CSV",
                initw=0,
                inith=0,
            )
            self.AddButton(ID_BTN_WRITE_CSV, BF_RS, name="Export CSV Only")
        self.GroupEnd()

    def cl_group_combobox_render_mode(self) -> None:
        if self.GroupBegin(NO_ID, BF_SF, rows=1):
            self.GroupSpace(5, 0)

            self.AddStaticText(NO_ID, BF_R, name="Render Mode:")
            self.AddComboBox(ID_CMB_MODE_RENDER, BF_SF, initw=60)
        self.GroupEnd()

    def cl_group_file_structure_preview(self) -> None:
        title = "File Structure Preview"
        if self.GroupBegin(NO_ID, BF_SFSF, cols=1, title=title):
            self.GroupBorder(c4d.BORDER_WITH_TITLE_BOLD)
            self.GroupBorderSpace(5, 5, 5, 5)

            self.AddMultiLineEditText(
                ID_FILE_STRUCTURE_LIST,
                BF_SFSF,
                inith=70,
                style=c4d.DR_MULTILINE_READONLY,
            )
        self.GroupEnd()


    # ---- Rules tab groups -----------------------------------------------

    def cl_group_exceptions(self) -> None:
        title = "Exclusion Rules"
        if self.GroupBegin(NO_ID, BF_SFSF, cols=1, title=title):
            self.GroupBorder(c4d.BORDER_WITH_TITLE_BOLD)
            self.GroupBorderSpace(10, 5, 10, 10)
            self.GroupSpace(0, 6)

            self.AddStaticText(
                NO_ID,
                BF_L,
                name="Build IF: pick item, use + AND / + OR to combine, then set action + target.",
            )

            # IF picker + AND / OR / Clear
            if self.GroupBegin(NO_ID, BF_SF, cols=4, rows=1):
                self.GroupSpace(4, 0)
                self.AddComboBox(ID_BCB_RULE_IF, BF_SF)
                self.AddButton(ID_BCB_RULE_ADD_AND, BF_L, name="+ AND")
                self.AddButton(ID_BCB_RULE_ADD_OR, BF_L, name="+ OR")
                self.AddButton(ID_BCB_RULE_CLEAR_IF, BF_L, name="Clear IF")
            self.GroupEnd()

            # IF preview (read-only)
            if self.GroupBegin(NO_ID, BF_SF, cols=2, rows=1):
                self.GroupSpace(4, 0)
                self.AddStaticText(NO_ID, BF_L, name="IF:")
                self.AddEditText(ID_TXT_RULE_IF_PREVIEW, BF_SF)
                self.Enable(ID_TXT_RULE_IF_PREVIEW, False)
            self.GroupEnd()

            # Action + Target + Add Rule
            if self.GroupBegin(NO_ID, BF_SF, cols=3, rows=1):
                self.GroupSpace(4, 0)
                self.AddComboBox(ID_BCB_RULE_ACTION, BF_SF)
                self.AddComboBox(ID_BCB_RULE_TARGET, BF_SF)
                self.AddButton(ID_BCB_RULE_ADD, BF_L, name="+ Add Rule")
            self.GroupEnd()

            # Raw rules editor — source of truth; edit/delete rules directly here
            self.AddMultiLineEditText(
                ID_BCB_EXCLUSION_RULES_RAW,
                BF_SFSF,
                inith=90,
                style=c4d.DR_MULTILINE_MONOSPACED,
            )

            # Rule status / exclusion feedback
            self.AddStaticText(ID_STR_RULE_STATUS, BF_SF, name=" ")
        self.GroupEnd()

    # ------------------------------------------------------------------
    # Init / Refresh
    # ------------------------------------------------------------------

    def InitValues(self):
        if get_index_render_frame() > -1:
            self.enable_render_buttons()
            return True

        validate_bc_brandner(self.bcb, is_dev_env=False)

        self.SetString(ID_STR_PRODUCT_NAME, self.bcb[ID_BCB_PRODUCT_NAME] or "")
        self.SetString(ID_STR_PREFIX, self.bcb[ID_BCB_PREFIX] or "")
        self.SetString(ID_STR_DELIMITER, self.bcb[ID_BCB_DELIMITER] or "")
        self.SetString(ID_STR_DIR_OUT, self.bcb[ID_BCB_DIRECTORY_OUTPUT] or "")
        self.SetBool(ID_CHK_GENERATE_CSV, bool(self.bcb.GetBool(ID_BCB_DO_GENERATE_CSV)))
        self.SetBool(ID_CHK_SAVE_PROJECT, bool(self.bcb.GetBool(ID_BCB_DO_SAVE_PROJECT)))

        filename = self.bcb[ID_BCB_FILENAME] or ""
        self.SetString(ID_STR_FILENAME, filename)
        token_names = token_path_to_token_names(filename)
        self.SetString(ID_TXT_TOKEN_HELP, token_names)
        self.SetString(ID_TXT_TOKEN_HELP_TT, " " * 30 + " | " + token_names)

        self.update_render_mode_combobox()
        self.ensure_combinations()
        self.update_component_combo_boxes()
        self.enable_render_buttons()
        self.update_file_structure_preview()

        # Exceptions UI values
        self.populate_exception_combos()
        rules_raw = self.bcb.GetString(ID_BCB_EXCLUSION_RULES_RAW, "")
        self.SetString(ID_BCB_EXCLUSION_RULES_RAW, rules_raw)

        self.update_warnings()
        self._update_combo_pos_label()

        return True

    def update_combinations(self) -> None:
        """Recompute combos + UI bits after rules change."""
        self._combos_dirty = True
        self.ensure_combinations()
        self.update_component_combo_boxes()
        self.enable_render_buttons()
        self.update_file_structure_preview()

    def _update_after_rules_change(self) -> None:
        """Lightweight combination refresh after a rule edit.

        Skips update_file_structure_preview() (which clones the entire scene
        and freezes the UI) so that Add Rule / raw-text edits feel instant.
        The file structure preview stays consistent because it is rebuilt in
        full on the next Refresh or render.
        """
        self._combos_dirty = True
        self.ensure_combinations()
        self.update_component_combo_boxes()
        self.enable_render_buttons()
        self.update_warnings()
        self._update_combo_pos_label()

    # ------------------------------------------------------------------
    # Warnings (duplicate names / filename collisions / stale rules)
    # ------------------------------------------------------------------

    def _check_duplicate_names(self) -> List[str]:
        """Find names used more than once among options, cameras and constants.

        All matching (combos, rules, visibility) is done by object name, so a
        duplicated name silently produces wrong renders.
        Returns e.g. ["'Red' x2"].
        """
        counts: Dict[str, int] = {}

        for vname in self._scene_cache.get("variable_names", []):
            var_info = self._scene_cache.get("variables", {}).get(vname, {})
            for opt_name in var_info.get("option_names", []):
                counts[opt_name] = counts.get(opt_name, 0) + 1

        for cam_name in self._scene_cache.get("camera_names", []):
            counts[cam_name] = counts.get(cam_name, 0) + 1

        for const_name in self._scene_cache.get("constant_names", []):
            counts[const_name] = counts.get(const_name, 0) + 1

        return [
            f"'{name}' x{num}"
            for name, num in sorted(counts.items())
            if num > 1
        ]

    def _check_filename_collision_warnings(self) -> List[str]:
        """Warn when the filename pattern cannot distinguish combinations.

        Without a differentiating token, every combination renders to the
        same file and silently overwrites the previous image.
        Conservative checks only (no false alarms):
          - >1 camera but no $_b_cam token
          - a variable with >1 option but no $_b_vars / $_b_v* token
        """
        filename = self.bcb.GetString(ID_BCB_FILENAME) or ""
        warnings: List[str] = []

        if len(self.get_camera_names()) > 1 and "_b_cam" not in filename:
            warnings.append(
                "Filename pattern has no $_b_cam token — renders from "
                "different cameras will overwrite each other."
            )

        has_var_token = "_b_vars" in filename or "_b_v" in filename
        has_multi_option_var = any(
            len(opts) > 1 for opts in self.get_variables_options_names()
        )
        if has_multi_option_var and not has_var_token:
            warnings.append(
                "Filename pattern has no $_b_vars token — different option "
                "combinations will overwrite each other."
            )

        return warnings

    def _check_rule_warnings(self) -> List[str]:
        """Validate exclusion rules against the current scene.

        Flags lines that cannot be parsed and rule tokens that match no
        object name in the scene (typically after a rename), since such
        rules silently stop excluding anything.
        """
        raw = self.bcb.GetString(ID_BCB_EXCLUSION_RULES_RAW, "") or ""
        if not raw.strip():
            return []

        # Same token set the rule builder offers (includes nested objects),
        # so anything built via the UI can never be flagged as unknown.
        known = {raw_token for _label, raw_token in self.get_exception_items()}

        warnings: List[str] = []
        for num, line in enumerate(raw.splitlines(), start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parsed = parse_exclusion_rules(line)
            if not parsed:
                warnings.append(f"Rule line {num} cannot be parsed.")
                continue

            rule = parsed[0]
            tokens = [t for group in rule["if_groups"] for t in group]
            tokens += rule["targets"]
            for tok in tokens:
                if tok not in known:
                    warnings.append(
                        f"Rule line {num}: '{tok}' not found in scene."
                    )

        return warnings

    def update_warnings(self) -> None:
        """Refresh the top warning line and the rule status label."""
        problems: List[str] = []

        duplicates = self._check_duplicate_names()
        if duplicates:
            shown = ", ".join(duplicates[:3])
            more = f" (+{len(duplicates) - 3} more)" if len(duplicates) > 3 else ""
            problems.append(f"Duplicate names: {shown}{more}")

        collisions = self._check_filename_collision_warnings()
        if collisions:
            problems.append("filename pattern may overwrite files (see Render tab)")

        rule_warnings = self._check_rule_warnings()
        if rule_warnings:
            problems.append(
                f"{len(rule_warnings)} rule problem"
                f"{'s' if len(rule_warnings) != 1 else ''} (see Rules tab)"
            )

        if problems:
            self.SetString(ID_STR_SCENE_WARNINGS, "⚠ " + "  ·  ".join(problems))
        else:
            self.SetString(ID_STR_SCENE_WARNINGS, " ")

        # Rule status label: warnings take priority over the info text that
        # _update_combo_count_label may have written.
        if rule_warnings:
            shown = rule_warnings[0]
            if len(rule_warnings) > 1:
                shown += f"  (+{len(rule_warnings) - 1} more)"
            self.SetString(ID_STR_RULE_STATUS, "⚠ " + shown)

    def update_component_combo_boxes(self) -> None:
        self.update_variables_combo_box()
        self.update_options_combo_box()
        self.update_cameras_combo_box()
        self.update_constants_combo_box()
        self._update_combo_count_label()

    def _update_combo_count_label(self) -> None:
        num_valid = len(self.possible_combinations)
        raw_total = getattr(self, "_raw_combo_count", num_valid)
        excluded = raw_total - num_valid

        if raw_total == 0:
            self.SetString(ID_STR_COMBO_COUNT, "0 Combinations")
        elif excluded > 0:
            self.SetString(
                ID_STR_COMBO_COUNT,
                f"{num_valid} / {raw_total} Combinations  ({excluded} excluded by rules)",
            )
            self.SetString(
                ID_STR_RULE_STATUS,
                f"Rules active: {excluded} of {raw_total} combinations excluded.",
            )
        else:
            self.SetString(
                ID_STR_COMBO_COUNT,
                f"{num_valid} Combinations",
            )
            rules_raw = self.bcb.GetString(ID_BCB_EXCLUSION_RULES_RAW, "").strip()
            if rules_raw:
                self.SetString(ID_STR_RULE_STATUS, "Rules parsed — no combinations excluded.")
            else:
                self.SetString(ID_STR_RULE_STATUS, " ")

    def update_variables_combo_box(self) -> None:
        idx_var_selected = self.GetInt32(ID_CMB_VARS)
        idx_var_selected = max(0, idx_var_selected)
        idx_var_selected = min(
            idx_var_selected, len(self.variables_combobox) - 1
        )
        self.update_combo_box_component(
            ID_CMB_VARS,
            "Variables",
            self.variables_combobox,
            idx_selected=idx_var_selected,
            do_warn=True,
        )

    def update_options_combo_box(self) -> None:
        idx_var_selected = self.GetInt32(ID_CMB_VARS)
        num_variables = len(self.variables)
        if num_variables > 0 and idx_var_selected < num_variables:
            varname_label = f": {self.variables[idx_var_selected]}"
        else:
            varname_label = ""

        self.update_combo_box_component(
            ID_CMB_OPTS,
            f"Options{varname_label}",
            self.dyn_options_combobox,
        )

    def update_cameras_combo_box(self) -> None:
        self.update_combo_box_component(
            ID_CMB_VIEWS,
            "Cameras",
            self.cameras_combobox,
        )

    def update_constants_combo_box(self) -> None:
        self.update_combo_box_component(
            ID_CMB_CONSTS,
            "Constants",
            self.constants_combobox,
        )

    def update_combo_box_component(
        self,
        id_combo: int,
        label: str,
        names: List[str],
        *,
        idx_selected: int = 0,
        do_warn: bool = False,
        do_count_in_label: bool = True,
    ) -> None:
        self.FreeChildren(id_combo)

        num_names = len(names)
        if num_names == 0:
            self.HideElement(id_combo + OFFSET_LABEL, True)
            self.HideElement(id_combo, True)
            self.SetString(id_combo + OFFSET_WARN, f"No {label}")
            self.HideElement(id_combo + OFFSET_WARN, False)
            return

        if do_count_in_label:
            name = f"{label} [{num_names}]"
        else:
            name = label

        self.SetString(id_combo + OFFSET_LABEL, name)
        self.HideElement(id_combo + OFFSET_LABEL, False)

        options_missing = False
        for _idx_name, _name in enumerate(names):
            self.AddChild(id_combo, _idx_name, _name)
            options_missing |= not self.check_element_options(_name)
        self.SetInt32(id_combo, idx_selected)
        self.HideElement(id_combo, False)

        if not do_warn:
            self.HideElement(id_combo + OFFSET_WARN, True)
            return

        label_low = label.lower()
        self.SetString(
            id_combo + OFFSET_WARN,
            f"Some {label_low} have no options.",
        )
        self.HideElement(id_combo + OFFSET_WARN, not options_missing)

    def update_render_mode_combobox(self) -> None:
        is_save_enabled = self.bcb[ID_BCB_DO_SAVE_PROJECT]
        has_multiple_cams = len(self.cameras) > 1
        disable_rq_queue = "" if is_save_enabled else "&d&"
        disable_rq_start = (
            "" if is_save_enabled and not has_multiple_cams else "&d&"
        )

        self.FreeChildren(ID_CMB_MODE_RENDER)
        self.AddChild(ID_CMB_MODE_RENDER, MODE_RENDER_NO_RENDER, "Bake Only (no render)")
        self.AddChild(
            ID_CMB_MODE_RENDER,
            MODE_RENDER_CMD_RENDER,
            "Render to Picture Viewer",
        )
        self.AddChild(
            ID_CMB_MODE_RENDER,
            MODE_RENDER_PV,
            "Background Render (threaded)",
        )
        self.AddChild(
            ID_CMB_MODE_RENDER,
            MODE_RENDER_RQ_QUEUE,
            f"Add to Render Queue{disable_rq_queue}",
        )
        self.AddChild(
            ID_CMB_MODE_RENDER,
            MODE_RENDER_RQ_QUEUE_START,
            f"Add to Render Queue & Start{disable_rq_start}",
        )

        self.SetInt32(ID_CMB_MODE_RENDER, self.bcb[ID_BCB_MODE_RENDER])

    def update_file_structure_preview(self) -> None:
        """
        Show example output file names based on valid combinations.

        Uses combo cache and avoids duplicated preview work.
        """
        doc_src = c4d.documents.GetActiveDocument()
        if doc_src is None:
            self.SetString(ID_FILE_STRUCTURE_LIST, "")
            return

        filename = self.bcb.GetString(ID_BCB_FILENAME)

        self.ensure_combinations()
        combos = self.possible_combinations

        # Building the preview clones the whole scene — skip it when nothing
        # it depends on has changed. cmd_refresh clears the key to force a
        # rebuild on explicit refresh.
        cache_key = (
            filename,
            self.bcb.GetString(ID_BCB_PREFIX),
            self.bcb.GetString(ID_BCB_DELIMITER),
            self.bcb.GetString(ID_BCB_PRODUCT_NAME),
            self.bcb.GetString(ID_BCB_DIRECTORY_OUTPUT),
            len(combos),
            tuple(tuple(c) for c in combos[:3]),  # preview shows first 3
            tuple(self.get_camera_names()),
        )
        if cache_key == self._preview_cache_key:
            return
        self._preview_cache_key = cache_key

        token_names = token_path_to_token_names(filename)
        preview_text = token_names + "\n"

        for _warning in self._check_filename_collision_warnings():
            preview_text += f"⚠ {_warning}\n"
        preview_text += "\n"

        if not combos:
            rd = doc_src.GetActiveRenderData().GetClone()
            bc_rd = self.prepare_render_data_for_render(doc_src, rd)

            bcb_doc = get_bc_brandner_from_doc(doc_src)
            do_remove_bcb = False
            if bcb_doc is None:
                do_remove_bcb = True
                bc_doc_src = doc_src.GetDataInstance()
                bc_doc_src[PLUGIN_ID_BRANDNER] = get_bc_brandner_default()
                bcb_doc = get_bc_brandner_from_doc(doc_src)

            bcb_doc[ID_BCB_TOKEN_EXAMPLE_MODE] = True
            for _idx in range(3):
                rpd = {"_doc": doc_src, "_rData": rd, "_rBc": bc_rd, "_frame": 0}
                line = c4d.modules.tokensystem.StringConvertTokens(filename, rpd)
                preview_text += line + "\n"

            bcb_doc[ID_BCB_TOKEN_EXAMPLE_MODE] = False
            if do_remove_bcb:
                doc_src.GetDataInstance().RemoveData(PLUGIN_ID_BRANDNER)

            self.SetString(ID_FILE_STRUCTURE_LIST, preview_text)
            return

        rd = doc_src.GetActiveRenderData().GetClone()
        bc_rd = self.prepare_render_data_for_render(doc_src, rd)

        doc = doc_src.GetClone(c4d.COPYFLAGS_NO_MATERIALPREVIEW)
        if doc is None:
            self.SetString(ID_FILE_STRUCTURE_LIST, preview_text)
            return

        bc_doc = doc.GetDataInstance()
        bc_doc.SetContainer(PLUGIN_ID_BRANDNER, self.bcb)

        null_variables = doc.SearchObject(BR_VARIABLES)
        null_components = doc.SearchObject(BR_COMPONENTS)
        if null_components is None:
            null_components = create_null(doc, BR_COMPONENTS, add_undo=False)
        obj_stage = create_stage(doc, BR_STAGE, obj_parent=null_components, add_undo=False)

        # Use deterministic first-3 so the preview is stable on repeated open.
        # Showing random samples caused the preview to flicker on every refresh.
        preview_count = min(3, len(combos))
        examples = combos[:preview_count]
        total = len(combos)
        if total > preview_count:
            preview_text += f"(showing {preview_count} of {total} combinations)\n"

        for idx, combo in enumerate(examples):
            jump_to_frame(doc, idx)
            if null_variables is not None:
                self.set_combination_keyframes(doc, obj_stage, null_variables, combo)
            rpd = {"_doc": doc, "_rData": rd, "_rBc": bc_rd, "_frame": idx}
            line = c4d.modules.tokensystem.StringConvertTokens(filename, rpd)
            preview_text += line + "\n"

        self.SetString(ID_FILE_STRUCTURE_LIST, preview_text)

    # ------------------------------------------------------------------
    # Render setup & validation
    # ------------------------------------------------------------------

    def set_label_button_render(
        self,
        *,
        is_dir: bool,
        is_writeable: bool,
        is_rendering_flag: bool,
    ) -> None:
        num_combinations = len(self.possible_combinations)
        has_combinations = num_combinations > 0

        idx_frame = get_index_render_frame()
        if idx_frame >= 0:
            progress = idx_frame * 100.0 / num_combinations
            self.SetString(
                ID_BTN_RENDER,
                f"Rendering in Progress: {progress:.02f}%, click to cancel",
            )
        elif not is_dir:
            self.SetString(
                ID_BTN_RENDER, "Please set/create output directory"
            )
        elif not is_writeable:
            self.SetString(
                ID_BTN_RENDER,
                "Please fix permissions for output directory",
            )
        elif not has_combinations:
            raw_total = getattr(self, "_raw_combo_count", 0)
            if len(self.variables) == 0:
                self.SetString(
                    ID_BTN_RENDER,
                    "Please add a variable and press Refresh Scene",
                )
            elif len(self.cameras) == 0:
                self.SetString(
                    ID_BTN_RENDER,
                    "Please add a camera and press Refresh Scene",
                )
            elif raw_total > 0:
                self.SetString(
                    ID_BTN_RENDER,
                    f"All {raw_total} combinations excluded by rules — check the Rules tab",
                )
            else:
                self.SetString(
                    ID_BTN_RENDER,
                    "No combinations — add options to each variable and press Refresh Scene",
                )
        else:
            self.SetString(
                ID_BTN_RENDER,
                f"Bake {num_combinations} Combinations",
            )

    def enable_render_buttons(self) -> None:
        num_combinations = len(self.possible_combinations)
        has_combinations = num_combinations > 0

        dir_output = self.bcb[ID_BCB_DIRECTORY_OUTPUT]
        is_dir = dir_output is not None and os.path.isdir(dir_output)
        is_writeable = is_dir and os.access(dir_output, os.W_OK)
        enable_render = (
            is_writeable and has_combinations and not is_rendering()
        )

        self.set_label_button_render(
            is_dir=is_dir,
            is_writeable=is_writeable,
            is_rendering_flag=is_rendering(),
        )

        self.enable_all(enable_render)

    def enable_all(self, enable_render: bool) -> None:
        if is_rendering():
            for _id_widget in IDS_DISABLE_ALL:
                self.Enable(_id_widget, False)

            self.Enable(ID_BTN_RENDER, True)
        else:
            for _id_widget in IDS_ENABLE_ALL:
                self.Enable(_id_widget, True)

            self.Enable(ID_BTN_RENDER, enable_render)
            self.Enable(ID_BTN_WRITE_CSV, enable_render)

    @staticmethod
    def check_element_options(name_element: str) -> bool:
        idx_icon_id = name_element.find("&")
        name_check_opt = name_element
        if idx_icon_id != -1:
            name_check_opt = name_check_opt[:idx_icon_id]

        has_options = True
        if name_check_opt.endswith(SUFFIX_NO_OPTION):
            has_options = False
        return has_options

    def calculate_combinations(self) -> List[List[str]]:
        """
        Build all valid combinations of variable options + cameras.

        Each combo is:
            [opt_var1_name, opt_var2_name, ..., camera_name]

        Also stores self._raw_combo_count (before rule filtering) so the UI
        can display how many were excluded.
        """
        variables_options = self.get_variables_options_names()
        cameras = self.get_camera_names()

        if not variables_options or not cameras:
            self._raw_combo_count = 0
            return []

        rules_raw = self.bcb.GetString(ID_BCB_EXCLUSION_RULES_RAW, "")
        rules = parse_exclusion_rules(rules_raw)

        raw_combos = [
            list(combo)
            for combo in itertools.product(*variables_options, cameras)
        ]
        self._raw_combo_count = len(raw_combos)

        if not rules:
            return raw_combos

        valid_combos: List[List[str]] = [
            combo
            for combo in raw_combos
            if is_valid_combo_names(combo, rules)
        ]
        return valid_combos

    def validate_directory_output(self) -> bool:
        dir_doc = c4d.documents.GetActiveDocument().GetDocumentPath()
        dir_output = resolve_output_directory(dir_doc, self.bcb[ID_BCB_DIRECTORY_OUTPUT])

        if dir_output is None or not os.path.isdir(dir_output):
            msg = "Please specify a valid output directory."
            open_error_requester(msg)
            return False

        if not os.access(dir_output, os.W_OK):
            msg = "The specified output directory is not writable."
            open_error_requester(msg)
            return False

        if os.path.isfile(dir_output):
            msg = (
                "The specified output directory is a file. "
                "Please select a directory."
            )
            open_error_requester(msg)
            return False

        return True

    @staticmethod
    def set_render_document_name(doc: c4d.documents.BaseDocument) -> None:
        name_doc = doc.GetDocumentName()
        name_doc, ext = os.path.splitext(name_doc)
        dt_now = datetime.now()
        time_suffix = dt_now.strftime("_%Y%m%d_%H%M%S")
        doc.SetDocumentName(f"{name_doc}{time_suffix}{ext}")

    def prepare_render_data_for_render(
        self,
        doc: c4d.documents.BaseDocument,
        rd: Optional[c4d.documents.RenderData],
    ) -> c4d.BaseContainer:
        if rd is None:
            rd = doc.GetActiveRenderData()

        dir_doc = c4d.documents.GetActiveDocument().GetDocumentPath() or doc.GetDocumentPath()
        dir_output = resolve_output_directory(dir_doc, self.bcb[ID_BCB_DIRECTORY_OUTPUT])
        filename = self.bcb[ID_BCB_FILENAME]

        rd[c4d.RDATA_PATH] = os.path.join(dir_output, filename)
        rd[c4d.RDATA_FORMAT] = c4d.FILTER_PNG

        fps = doc.GetFps()
        rd[c4d.RDATA_FRAMESEQUENCE] = 0  # Manual

        idx_frame_from = c4d.BaseTime(BAKE_FRAME_OFFSET, fps)
        rd[c4d.RDATA_FRAMEFROM] = idx_frame_from

        num_combinations = len(self.possible_combinations)
        idx_frame_to = c4d.BaseTime(BAKE_FRAME_OFFSET + num_combinations - 1, fps)
        rd[c4d.RDATA_FRAMETO] = idx_frame_to

        bc_rd_inst = rd.GetDataInstance()
        bc_rd = bc_rd_inst.GetClone(c4d.COPYFLAGS_NONE)
        return bc_rd

    @staticmethod
    def set_combination_keyframes(
        doc: c4d.documents.BaseDocument,
        obj_stage: c4d.BaseObject,
        null_variables: c4d.BaseObject,
        combo: List[str],
    ) -> None:
        # Build top-level option lookup once per call and only toggle option roots.
        opt_lookup: Dict[str, c4d.BaseObject] = {}
        for _obj_var in null_variables.GetChildren():
            for _obj_opt in _obj_var.GetChildren():
                opt_lookup[_obj_opt.GetName()] = _obj_opt
                set_visibility_direct(_obj_opt, c4d.OBJECT_OFF, do_keyframe=True)

        for _name_opt in combo[:-1]:
            obj_selected = opt_lookup.get(_name_opt)
            if obj_selected is not None:
                set_visibility_direct(obj_selected, c4d.OBJECT_ON, do_keyframe=True)

        name_cam = combo[-1]
        obj_cam = doc.SearchObject(name_cam)
        if obj_cam is not None:
            set_keyframe_cam(obj_stage, obj_cam)

    @staticmethod
    def gather_csv_lines(
        doc: c4d.documents.BaseDocument,
        lines_csv: List[str],
        name_cam: str = "Camera",
        index: str = "index",
        *,
        is_header: bool = False,
    ) -> None:
        null_variables = doc.SearchObject(BR_VARIABLES)

        line = index + ";"
        if is_header:
            for _obj_var in null_variables.GetChildren():
                line += _obj_var.GetName() + ";"
        else:
            for _obj_var in null_variables.GetChildren():
                for _obj_opt in _obj_var.GetChildren():
                    mode_vis = get_visibility(
                        _obj_opt, do_keyframe=True
                    )
                    if mode_vis == c4d.OBJECT_ON:
                        line += _obj_opt.GetName() + ";"
        line += name_cam + ";" + "\n"

        lines_csv.append(line)

    def write_csv(
        self,
        doc: c4d.documents.BaseDocument,
        lines_csv: List[str],
    ) -> None:
        product_name = self.bcb[ID_BCB_PRODUCT_NAME]
        dir_doc = c4d.documents.GetActiveDocument().GetDocumentPath() or doc.GetDocumentPath()
        dir_output = resolve_output_directory(dir_doc, self.bcb[ID_BCB_DIRECTORY_OUTPUT])

        try:
            filename_csv = f"{product_name}_metadata.csv"
            path_csv = os.path.join(dir_output, filename_csv)
            with open(path_csv, "w") as fd_csv:
                for _line in lines_csv:
                    logging.info(f"Writing lines {_line}")
                    fd_csv.write(_line)
        except Exception as e:
            logging.error(f"Failed to write CSV: {e}")

    @staticmethod
    def set_stage_as_render_camera(doc: c4d.documents.BaseDocument) -> None:
        """Link BR_STAGE as the scene camera of the baked document.

        The Render Queue's per-job Camera setting is not exposed in the
        Python API, but it defaults to the camera the scene file was saved
        with. jump_to_frame() lets the stage resolve to frame 1's concrete
        camera, so without this the queue pins that single camera for the
        whole job. Saving with the stage object linked instead makes the
        queue follow the stage's per-frame camera switching by default.
        """
        obj_stage = doc.SearchObject(BR_STAGE)
        if obj_stage is None:
            return
        for bd in (doc.GetRenderBaseDraw(), doc.GetActiveBaseDraw()):
            if bd is not None:
                try:
                    bd.SetSceneCamera(obj_stage)
                except Exception:
                    pass

    def finalize_project_and_render(
        self,
        doc: c4d.documents.BaseDocument,
        bc_rd: c4d.BaseContainer,
        *,
        do_save_project: Optional[bool] = None,
    ) -> bool:
        jump_to_frame(doc, BAKE_FRAME_OFFSET)
        self.set_stage_as_render_camera(doc)

        if do_save_project is None:
            do_save_project = self.bcb[ID_BCB_DO_SAVE_PROJECT]

        # Save is optional — render queue modes need a file on disk, but
        # threaded/PV modes work on the in-memory clone. Always proceed to
        # do_render_mode; only skip if the save itself fails when requested.
        if do_save_project:
            is_saved = save_project(doc)
            if not is_saved:
                return False

        is_threaded = self.do_render_mode(doc, bc_rd)
        return is_threaded

    def do_render_mode(
        self,
        doc: c4d.documents.BaseDocument,
        bc_rd: c4d.BaseContainer,
    ) -> bool:
        is_threaded = False
        mode_render = self.bcb[ID_BCB_MODE_RENDER]
        if mode_render == MODE_RENDER_NO_RENDER:
            return False
        elif mode_render == MODE_RENDER_PV:
            is_threaded = render_in_picture_viewer_ext(
                doc, bc_rd, do_threaded=True
            )
        elif mode_render == MODE_RENDER_CMD_RENDER:
            is_threaded = True
            c4d.documents.InsertBaseDocument(doc)
            c4d.EventAdd()
            c4d.CallCommand(12099)  # Render to Picture Viewer
        elif mode_render in [MODE_RENDER_RQ_QUEUE, MODE_RENDER_RQ_QUEUE_START]:
            do_start = mode_render == MODE_RENDER_RQ_QUEUE_START
            queue_batch_render(doc, do_start_render=do_start)
        return is_threaded

    # ------------------------------------------------------------------
    # Command handling
    # ------------------------------------------------------------------

    def Command(self, id, msg):
        if id == ID_BTN_RENDER:
            self.cmd_render()
        elif id == ID_BTN_COMBO_PREV:
            self.cmd_step_combination(-1)
        elif id == ID_BTN_COMBO_NEXT:
            self.cmd_step_combination(1)
        elif id == ID_BTN_RANDOMIZE:
            self.cmd_randomize_visibility()
        elif id == ID_BTN_DEFAULT_VISIBILITY:
            self.cmd_default_visibility()
        elif id == ID_BTN_INIT_HIERARCHY:
            self.cmd_set_hierarchy()
        elif id == ID_BTN_REFRESH:
            self.cmd_refresh()
        elif id == ID_BTN_WRITE_CSV:
            self.cmd_render(
                do_insert_doc=False,
                do_generate_csv=True,
                do_save_project=False,
            )

        elif id == ID_CMB_VARS:
            self.cmd_variables_combobox()
        elif id == ID_CMB_VIEWS:
            self.cmd_views_combobox()
        elif id == ID_CMB_OPTS:
            self.cmd_options_combobox()
        elif id == ID_CMB_CONSTS:
            self.cmd_constants_combobox()

        elif id == ID_STR_DIR_OUT:
            self.cmd_output_directory_edit()
        elif id == ID_BTN_OUT_DIR:
            self.cmd_output_directory_button()
        elif id == ID_STR_FILENAME:
            self.cmd_filename_edit()
        elif id == ID_BTN_ADD_TOKEN:
            self.cmd_filename_button()
        elif id in IDS_PARAMETERS:
            self.cmd_set_ui_param(id)

        # Exceptions — AND / OR / Clear IF builder
        if id in (ID_BCB_RULE_ADD_AND, ID_BCB_RULE_ADD_OR, ID_BCB_RULE_CLEAR_IF):
            if not hasattr(self, "_exc_if_groups"):
                self._exc_if_groups = []

            if id == ID_BCB_RULE_CLEAR_IF:
                self._exc_if_groups = []
                self._exc_update_if_preview()
                return True

            tok = self._exc_get_selected_if_token()
            if not tok:
                return True

            if id == ID_BCB_RULE_ADD_AND:
                self._exc_if_groups.append([tok])
            else:  # ADD_OR
                if not self._exc_if_groups:
                    self._exc_if_groups = [[tok]]
                elif tok not in self._exc_if_groups[-1]:
                    self._exc_if_groups[-1].append(tok)

            self._exc_update_if_preview()
            return True

        # Exceptions — Add Rule button
        if id == ID_BCB_RULE_ADD:
            if not hasattr(self, "_exc_if_groups"):
                self._exc_if_groups = []

            # Use builder state if available, otherwise fall back to the IF combo selection
            if_expr = self._exc_build_if_expr()
            if not if_expr:
                tok = self._exc_get_selected_if_token()
                if tok:
                    self._exc_if_groups = [[tok]]
                    if_expr = tok

            target = self._exc_get_selected_target_token()
            if not if_expr or not target or if_expr.strip() == target.strip():
                return True

            action_id = self.GetInt32(ID_BCB_RULE_ACTION)
            action = "REQUIRE" if action_id == 1 else "NEVER"
            new_line = f"{if_expr} -> {action} {target}"
            rules_raw = self.GetString(ID_BCB_EXCLUSION_RULES_RAW) or ""
            rules_raw = (rules_raw.rstrip() + "\n" + new_line).strip() if rules_raw.strip() else new_line

            self.SetString(ID_BCB_EXCLUSION_RULES_RAW, rules_raw)
            self.bcb.SetString(ID_BCB_EXCLUSION_RULES_RAW, rules_raw)
            doc = c4d.documents.GetActiveDocument()
            if doc:
                # store_bc_brandner replaces the container stored in the doc;
                # self.bcb MUST be reassigned to the returned instance or it
                # dangles and every later read returns None.
                self.bcb = store_bc_brandner(doc, self.bcb)
                doc.SetChanged()

            # Reset builder state after successful add
            self._exc_if_groups = []
            self._exc_update_if_preview()
            self._update_after_rules_change()
            return True

        if id == ID_BCB_EXCLUSION_RULES_RAW:
            rules_raw = self.GetString(ID_BCB_EXCLUSION_RULES_RAW)
            self.bcb.SetString(ID_BCB_EXCLUSION_RULES_RAW, rules_raw)
            doc = c4d.documents.GetActiveDocument()
            if doc:
                # Persist hand-typed rules to the document (previously they
                # were only saved when some other parameter was edited).
                self.bcb = store_bc_brandner(doc, self.bcb)
                doc.SetChanged()
            self._update_after_rules_change()
            return True

        return True


    def _set_prepare_status(
        self,
        text_status: str,
        *,
        progress: Optional[float] = None,
        update_button: bool = True,
    ) -> None:
        """Show prep progress in the C4D status bar and optionally on the Bake button."""
        try:
            c4d.StatusSetText(text_status)
            if progress is not None:
                progress = max(0.0, min(1.0, float(progress)))
                c4d.StatusSetBar(int(progress * 100.0))
        except Exception:
            pass

        if update_button:
            try:
                self.SetString(ID_BTN_RENDER, text_status)
            except Exception:
                pass

        try:
            c4d.EventAdd()
        except Exception:
            pass

    def _clear_prepare_status(self) -> None:
        try:
            c4d.StatusClear()
        except Exception:
            pass

    def cmd_render(
        self,
        *,
        do_insert_doc: bool = True,
        do_generate_csv: Optional[bool] = None,
        do_save_project: Optional[bool] = None,
    ) -> None:
        if is_rendering():
            msg = "Cancel Render?"
            do_cancel = c4d.gui.QuestionDialog(msg)
            if do_cancel:
                cancel_thread_render()
            self.InitValues()
            return

        if not self.validate_directory_output():
            return
        self.ensure_combinations()
        if len(self.possible_combinations) == 0:
            msg = "No combinations to generate from."
            open_error_requester(msg)
            return

        total_combos = len(self.possible_combinations)
        self._set_prepare_status("Preparing bake: cloning scene…", progress=0.02)

        doc_active = c4d.documents.GetActiveDocument()
        doc = doc_active.GetClone(c4d.COPYFLAGS_NO_MATERIALPREVIEW)

        self.bcb[ID_BCB_TOKEN_EXAMPLE_MODE] = False

        bc_doc = doc.GetDataInstance()
        bc_doc.SetContainer(PLUGIN_ID_BRANDNER, self.bcb)

        self.set_render_document_name(doc)
        bc_rd = self.prepare_render_data_for_render(doc, rd=None)

        null_variables = doc.SearchObject(BR_VARIABLES)
        null_components = doc.SearchObject(BR_COMPONENTS)
        obj_stage = create_stage(
            doc,
            BR_STAGE,
            obj_parent=null_components,
            add_undo=False,
        )

        if do_generate_csv is None:
            do_generate_csv = self.bcb[ID_BCB_DO_GENERATE_CSV]
        lines_csv = []
        if do_generate_csv:
            self.gather_csv_lines(doc, lines_csv, is_header=True)

        self._set_prepare_status("Preparing bake: building lookups…", progress=0.08)

        # Performance: build fast lookups to avoid repeated doc.SearchObject() calls.
        opt_lookup = {}
        try:
            for _obj_var in null_variables.GetChildren():
                for _obj_opt in _obj_var.GetChildren():
                    opt_lookup[_obj_opt.GetName()] = _obj_opt
        except Exception:
            opt_lookup = {}

        cam_lookup = {}
        try:
            null_cameras = doc.SearchObject(BR_CAMERAS)
            if null_cameras is not None:
                for _cam in null_cameras.GetChildren():
                    cam_lookup[_cam.GetName()] = _cam
        except Exception:
            cam_lookup = {}

        if total_combos <= 25:
            status_step = 1
        elif total_combos <= 100:
            status_step = 5
        else:
            status_step = 10

        try:
            for _idx_combo, combo in enumerate(self.possible_combinations):
                if (
                    _idx_combo == 0
                    or (_idx_combo % status_step == 0)
                    or (_idx_combo == total_combos - 1)
                ):
                    prep_progress = 0.10 + (0.70 * ((_idx_combo + 1) / float(total_combos)))
                    self._set_prepare_status(
                        f"Preparing bake: keyframing {_idx_combo + 1}/{total_combos}…",
                        progress=prep_progress,
                    )

                jump_to_frame(doc, BAKE_FRAME_OFFSET + _idx_combo)

                # Hide all options
                for _obj_var in null_variables.GetChildren():
                    for _obj_opt in _obj_var.GetChildren():
                        set_visibility_direct(_obj_opt, c4d.OBJECT_OFF, do_keyframe=True)

                # Show selected options (combo[-1] is camera)
                for _name_opt in combo[:-1]:
                    _obj_selected = opt_lookup.get(_name_opt)
                    if _obj_selected is None:
                        _obj_selected = doc.SearchObject(_name_opt)
                    if _obj_selected is not None:
                        set_visibility_direct(_obj_selected, c4d.OBJECT_ON, do_keyframe=True)

                # Keyframe camera on the Stage object
                name_cam = combo[-1]
                obj_cam = cam_lookup.get(name_cam)
                if obj_cam is None:
                    obj_cam = doc.SearchObject(name_cam)
                if obj_cam is not None:
                    set_keyframe_cam(obj_stage, obj_cam)

                # Force C4D to evaluate the cloned doc's animation state so
                # keyframes are written with correct visibility/camera data.
                # EventAdd is intentionally omitted here — it would trigger
                # unnecessary redraws of the active (non-cloned) document on
                # every iteration, which is a significant slowdown.
                try:
                    doc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_NONE)
                except Exception:
                    try:
                        doc.ExecutePasses(None, True, True, True, 0)
                    except Exception:
                        pass

                if do_generate_csv:
                    self.gather_csv_lines(doc, lines_csv, name_cam, str(_idx_combo))

            if do_generate_csv:
                self._set_prepare_status(
                    f"Bake complete — writing CSV for {total_combos} combinations…",
                    progress=0.86,
                )
                self.write_csv(doc, lines_csv)

            self._set_prepare_status(
                "Saving baked scene…" if self.bcb[ID_BCB_DO_SAVE_PROJECT] else "Launching render…",
                progress=0.92,
            )
            is_threaded = self.finalize_project_and_render(
                doc, bc_rd, do_save_project=do_save_project
            )

            self._set_prepare_status("Launching render…", progress=0.98)

            if do_insert_doc and not is_threaded:
                c4d.documents.InsertBaseDocument(doc)

            c4d.EventAdd()
        finally:
            self._clear_prepare_status()
            try:
                self.InitValues()
            except Exception:
                pass

    def _apply_combination(self, combo: List[str]) -> None:
        """Show one combination in the viewport (with undo).

        combo: [opt_var1_name, opt_var2_name, ..., camera_name]
        """
        doc = c4d.documents.GetActiveDocument()
        if doc is None:
            return

        null_variables = doc.SearchObject(BR_VARIABLES)
        null_cameras = doc.SearchObject(BR_CAMERAS)
        if null_variables is None or null_cameras is None:
            return

        doc.StartUndo()

        # Hide all options first
        for _obj_variable in null_variables.GetChildren():
            for _obj_option in _obj_variable.GetChildren():
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, _obj_option)
                set_visibility_direct(_obj_option, c4d.OBJECT_OFF, do_keyframe=False)

        # Show only the options in the chosen combo (except last, which is camera)
        for name_opt in combo[:-1]:
            obj = doc.SearchObject(name_opt)
            if obj is not None:
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
                set_visibility_direct(obj, c4d.OBJECT_ON, do_keyframe=False)

        # Set camera from combo
        cam_name = combo[-1]
        obj_cam = doc.SearchObject(cam_name)
        if obj_cam is not None:
            doc.GetActiveBaseDraw().SetSceneCamera(obj_cam)
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj_cam)

        doc.EndUndo()
        c4d.EventAdd()

    def _update_combo_pos_label(self) -> None:
        num_combos = len(self.possible_combinations)
        idx = getattr(self, "_preview_combo_idx", None)
        if idx is not None and idx >= num_combos:
            # Combo list changed (rules/scene edit) — stored position is stale.
            idx = None
            self._preview_combo_idx = None
        if num_combos == 0:
            self.SetString(ID_STR_COMBO_POS, "Combination - of 0")
        elif idx is None:
            self.SetString(ID_STR_COMBO_POS, f"Combination - of {num_combos}")
        else:
            self.SetString(
                ID_STR_COMBO_POS, f"Combination {idx + 1} of {num_combos}"
            )

    def cmd_step_combination(self, step: int) -> None:
        """Show the previous/next valid combination in the viewport."""
        self.ensure_combinations()
        num_combos = len(self.possible_combinations)
        if num_combos == 0:
            self._preview_combo_idx = None
            self._update_combo_pos_label()
            return

        idx = getattr(self, "_preview_combo_idx", None)
        if idx is None:
            # First step: Next shows the first combo, Prev shows the last.
            idx = 0 if step >= 0 else num_combos - 1
        else:
            idx = (idx + step) % num_combos

        self._preview_combo_idx = idx
        self._apply_combination(self.possible_combinations[idx])
        self._update_combo_pos_label()

    def cmd_randomize_visibility(self) -> None:
        """
        Show a single random *valid* combination, respecting exclusion rules.

        It uses self.possible_combinations, which already applies
        parse_exclusion_rules + is_valid_combo_names.
        """
        self.ensure_combinations()
        if not self.possible_combinations:
            return

        idx = random.randrange(len(self.possible_combinations))
        self._preview_combo_idx = idx
        self._apply_combination(self.possible_combinations[idx])
        self._update_combo_pos_label()

    @staticmethod
    def cmd_default_visibility() -> None:
        doc = c4d.documents.GetActiveDocument()
        null_variables = doc.SearchObject(BR_VARIABLES)
        if null_variables is None:
            return

        doc.StartUndo()

        for _obj_var in null_variables.GetChildren():
            objs_options = _obj_var.GetChildren()
            if len(objs_options) == 0:
                continue

            doc.AddUndo(c4d.UNDOTYPE_CHANGE, objs_options[0])
            set_visibility_direct(objs_options[0], c4d.OBJECT_ON, do_keyframe=False)
            for _obj_opt in objs_options[1:]:
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, _obj_opt)
                set_visibility_direct(_obj_opt, c4d.OBJECT_OFF, do_keyframe=False)

        null_cameras = doc.SearchObject(BR_CAMERAS)
        if null_cameras is None:
            doc.EndUndo()
            c4d.EventAdd()
            return

        objs_cameras = null_cameras.GetChildren()
        if len(objs_cameras) > 0:
            doc.GetActiveBaseDraw().SetSceneCamera(objs_cameras[0])

        doc.EndUndo()
        c4d.EventAdd()

    def cmd_set_hierarchy(self) -> None:
        doc = c4d.documents.GetActiveDocument()

        doc.StartUndo()

        self.bcb = store_bc_brandner(doc, self.bcb)
        null_components = create_null(doc, BR_COMPONENTS, add_undo=True)
        null_variables = create_null(
            doc,
            BR_VARIABLES,
            obj_parent=null_components,
            add_undo=True,
        )
        create_null(
            doc,
            BR_CAMERAS,
            obj_parent=null_components,
            add_undo=True,
        )
        create_null(
            doc,
            BR_CONSTANTS,
            obj_parent=null_components,
            add_undo=True,
        )

        self.cmd_set_hierarchy_variables(doc, null_variables, add_undo=True)

        doc.EndUndo()

        self.cmd_refresh()
        c4d.EventAdd()

    @staticmethod
    def cmd_set_hierarchy_variables(
        doc: c4d.documents.BaseDocument,
        null_variables: c4d.BaseObject,
        *,
        add_undo: bool,
        num_variables: int = 3,
    ) -> None:
        var_children = null_variables.GetChildren()
        if len(var_children) > 0:
            return
        for _idx_var in range(num_variables):
            idx_var_name = _idx_var + 1
            create_null(
                doc,
                f"Variable_{idx_var_name:02}",
                obj_parent=null_variables,
                add_undo=add_undo,
            )

    def layout_changed_components(self) -> None:
        self.LayoutChanged(ID_GRP_COMPONENT)

    def cmd_refresh(self) -> None:
        doc = c4d.documents.GetActiveDocument()
        bcb_doc = get_bc_brandner_from_doc(doc)
        if bcb_doc is not None:
            self.bcb = bcb_doc

        self.init_component_names()
        self._combos_dirty = True
        self._preview_cache_key = None  # force preview rebuild on explicit refresh
        self.ensure_combinations()

        self.InitValues()
        self.layout_changed_components()

    def cmd_variables_combobox(self):
        self.init_dyn_options()
        self.InitValues()

        doc = c4d.documents.GetActiveDocument()
        idx_var_selected = self.GetInt32(ID_CMB_VARS)
        if idx_var_selected < len(self.variables):
            name_var = self.variables[idx_var_selected]
            select_object(doc, name_var)
        c4d.EventAdd()

    def cmd_views_combobox(self):
        doc = c4d.documents.GetActiveDocument()
        idx_cam_selected = self.GetInt32(ID_CMB_VIEWS)
        if idx_cam_selected < len(self.cameras):
            name_cam = self.cameras[idx_cam_selected]
            doc.GetActiveBaseDraw().SetSceneCamera(doc.SearchObject(name_cam))
            select_object(doc, name_cam)
        c4d.EventAdd()

    def cmd_constants_combobox(self):
        doc = c4d.documents.GetActiveDocument()
        idx_const_selected = self.GetInt32(ID_CMB_CONSTS)
        if idx_const_selected < len(self.constants):
            name_const = self.constants[idx_const_selected]
            select_object(doc, name_const)
        c4d.EventAdd()

    def cmd_options_combobox(self):
        doc = c4d.documents.GetActiveDocument()
        idx_option_selected = self.GetInt32(ID_CMB_OPTS)
        if idx_option_selected < len(self.dyn_options):
            name_opt = self.dyn_options[idx_option_selected]
            select_object(doc, name_opt)
        c4d.EventAdd()

    def cmd_output_directory_edit(self) -> None:
        self.cmd_set_ui_param(ID_STR_DIR_OUT)

        doc = c4d.documents.GetActiveDocument()
        doc.SetChanged()
        c4d.EventAdd()

    def cmd_output_directory_button(self) -> None:
        doc = c4d.documents.GetActiveDocument()
        dir_doc = doc.GetDocumentPath()
        dir_output = self.GetString(ID_STR_DIR_OUT)
        dir_default = get_default_output_directory(dir_doc, dir_output)

        dir_output_new = c4d.storage.LoadDialog(
            type=c4d.FILESELECTTYPE_ANYTHING,
            title="Output Directory",
            flags=c4d.FILESELECT_DIRECTORY,
            def_path=dir_default,
        )
        if dir_output_new is None or len(dir_output_new) == 0:
            return

        dir_output_new = normalize_output_directory(dir_doc, dir_output_new)

        self.SetString(ID_STR_DIR_OUT, dir_output_new)
        self.cmd_output_directory_edit()

    def cmd_filename_edit(self) -> None:
        self.cmd_set_ui_param(ID_STR_FILENAME)
        c4d.EventAdd()

    def cmd_filename_button(self) -> None:
        ID_CLEAR_FILENAME = c4d.FIRST_POPUP_ID + 10000
        OFFSET_VARS = 20000
        OFFSET_CONSTS = 30000
        OFFSET_OTHER = 40000
        ID_BC_SUBMENU_VARS = c4d.FIRST_POPUP_ID + 50000
        ID_BC_SUBMENU_CONSTS = c4d.FIRST_POPUP_ID + 50001

        tokens_brandner = []
        tokens_brandner_vars = []
        tokens_brandner_consts = []
        tokens_other = []
        get_all_tokens(
            tokens_brandner,
            tokens_brandner_vars,
            tokens_brandner_consts,
            tokens_other,
        )
        tokens_other.sort(key=lambda x: x["_help"])
        sort_brandner_tokens(tokens_brandner)
        sort_brandner_tokens(tokens_brandner_vars)
        sort_brandner_tokens(tokens_brandner_consts)

        bc_menu = c4d.BaseContainer()

        bc_menu.InsData(ID_CLEAR_FILENAME, "Clear Filename")
        bc_menu.InsData(0, "")  # separator

        dict_menu_tokens = {}
        add_tokens_to_bc_menu(
            bc_menu, dict_menu_tokens, tokens_brandner
        )

        bc_menu.InsData(0, "")  # separator

        add_tokens_submenu(
            bc_menu,
            dict_menu_tokens,
            tokens_brandner_vars,
            id_submeu=ID_BC_SUBMENU_VARS,
            name_submenu="Variables by Index",
            offset_ids=OFFSET_VARS,
        )
        add_tokens_submenu(
            bc_menu,
            dict_menu_tokens,
            tokens_brandner_consts,
            id_submeu=ID_BC_SUBMENU_CONSTS,
            name_submenu="Constants by Index",
            offset_ids=OFFSET_CONSTS,
        )

        bc_menu.InsData(0, "")  # separator

        add_tokens_to_bc_menu(
            bc_menu, dict_menu_tokens, tokens_other, offset_ids=OFFSET_OTHER
        )

        result = c4d.gui.ShowPopupDialog(
            cd=None,
            bc=bc_menu,
            x=c4d.MOUSEPOS,
            y=c4d.MOUSEPOS,
            flags=c4d.POPUP_ALLOW_FILTERING,
        )
        if result == 0:
            return

        if result == ID_CLEAR_FILENAME:
            self.SetString(ID_STR_FILENAME, "")
            self.cmd_filename_edit()
            return

        token = dict_menu_tokens[result]
        filename = self.GetString(ID_STR_FILENAME)
        if len(filename) == 0:
            filename_new = f"${token}"
        else:
            filename_new = f"{filename}$_d${token}"

        self.SetString(ID_STR_FILENAME, filename_new)
        self.cmd_filename_edit()

    def cmd_set_ui_param(self, id_param: int) -> None:
        doc = c4d.documents.GetActiveDocument()

        if id_param in IDS_PARAMETERS_BOOL:
            value = self.GetBool(id_param)
        elif id_param in IDS_PARAMETERS_INT:
            value = self.GetInt32(id_param)
        elif id_param in IDS_PARAMETERS_STRING:
            value = self.GetString(id_param)
        else:
            return

        self.bcb[id_param] = value
        self.bcb = store_bc_brandner(doc, self.bcb)
        doc.SetChanged()
        self.InitValues()

    # ------------------------------------------------------------------
    # Core messages
    # ------------------------------------------------------------------

    def CoreMessage(self, id, msg):
        if id == c4d.EVMSG_CHANGE:
            self.cmsg_change()
        elif id == PLUGIN_ID_BRANDNER:
            self.cmsg_brandner_render_progress()
        return True

    def cmsg_change(self) -> None:
        doc_current = c4d.documents.GetActiveDocument()
        doc_last_exists = (
            getattr(self, "doc_last", None) is not None
            and self.doc_last.IsAlive()
        )
        doc_still_current = doc_last_exists and doc_current == self.doc_last

        if doc_still_current:
            return

        self.doc_last = doc_current
        self.bcb = get_bc_brandner(do_init_doc=False)
        self.cmd_refresh()

    # ------------------------------------------------------------------
    # Exceptions helpers
    # ------------------------------------------------------------------

    def get_exception_items(self) -> List[Tuple[str, str]]:
        """
        Build (label, raw_token) pairs for the Exceptions rule builder.

        Labels are user-friendly and grouped:
          - VAR: <Variable Name> / <Option Name>
          - CAM: <Camera/View Name>   (includes Redshift cameras or any non-null objects under BR_CAMERAS)
          - CONST: <Group Name>       (direct children under BR_CONSTANTS only)

        Raw tokens are the *exact names* used for matching in combos.
        """
        doc = c4d.documents.GetActiveDocument()
        if doc is None:
            return []

        items: List[Tuple[str, str]] = []

        # ---- Variables: include option object names, labeled with their variable group ----
        null_vars = doc.SearchObject(BR_VARIABLES)
        if null_vars:
            var = null_vars.GetDown()
            while var:
                var_name = var.GetName()

                def walk_opts(op: c4d.BaseObject):
                    while op:
                        # options can be nested; include every non-null object name as a token
                        items.append((f"VAR: {var_name} / {op.GetName()}", op.GetName()))
                        walk_opts(op.GetDown())
                        op = op.GetNext()

                first_opt = var.GetDown()
                if first_opt:
                    walk_opts(first_opt)
                var = var.GetNext()

        # ---- Cameras/Views: include any non-null objects under BR_CAMERAS ----
        null_cams = doc.SearchObject(BR_CAMERAS)
        if null_cams:
            def walk_views(op: c4d.BaseObject):
                while op:
                    # exclude grouping nulls; include any actual object (Redshift camera, standard camera, etc.)
                    if op.GetType() != c4d.Onull:
                        items.append((f"CAM: {op.GetName()}", op.GetName()))
                    walk_views(op.GetDown())
                    op = op.GetNext()
            walk_views(null_cams.GetDown())

        # ---- Constants: include only direct children of BR_CONSTANTS as group tokens ----
        null_consts = doc.SearchObject(BR_CONSTANTS)
        if null_consts:
            c = null_consts.GetDown()
            while c:
                items.append((f"CONST: {c.GetName()}", c.GetName()))
                c = c.GetNext()

        # sort by group (VAR -> CAM -> CONST) then label
        def sort_key(it: Tuple[str, str]):
            label, _ = it
            if label.startswith("VAR:"):
                g = 0
            elif label.startswith("CAM:"):
                g = 1
            else:
                g = 2
            return (g, label.lower())

        # Deduplicate by label+raw pair (keep stable)
        seen = set()
        out: List[Tuple[str, str]] = []
        for it in sorted(items, key=sort_key):
            if it in seen:
                continue
            seen.add(it)
            out.append(it)

        return out


    
    def populate_exception_combos(self) -> None:
        """Populate the Exceptions rule-builder combo boxes."""
        items = self.get_exception_items()

        # Build ID maps for label/raw pairs.
        self._exc_item_label_by_id = {}
        self._exc_item_raw_by_id = {}
        self._exc_item_id_by_raw = {}

        # Clear and repopulate IF + TARGET combos.
        try:
            self.FreeChildren(ID_BCB_RULE_IF)
            self.FreeChildren(ID_BCB_RULE_TARGET)
            self.FreeChildren(ID_BCB_RULE_ACTION)
        except Exception:
            # Some C4D builds can throw if the gadget isn't created yet.
            return

        # Action combo: NEVER / REQUIRE
        self.AddChild(ID_BCB_RULE_ACTION, 0, "NEVER")
        self.AddChild(ID_BCB_RULE_ACTION, 1, "REQUIRE")
        # Default selection
        self.SetInt32(ID_BCB_RULE_ACTION, 0)

        # Items for IF + TARGET
        base_id = 1000
        for i, (label, raw) in enumerate(items):
            cid = base_id + i
            self._exc_item_label_by_id[cid] = label
            self._exc_item_raw_by_id[cid] = raw
            # raw->id: keep first occurrence
            self._exc_item_id_by_raw.setdefault(raw, cid)

            self.AddChild(ID_BCB_RULE_IF, cid, label)
            self.AddChild(ID_BCB_RULE_TARGET, cid, label)

        # Set defaults if any items exist
        if items:
            first_id = base_id
            self.SetInt32(ID_BCB_RULE_IF, first_id)
            self.SetInt32(ID_BCB_RULE_TARGET, first_id)

        # Reset builder state + preview
        self._exc_if_groups = []   # list[list[str]] raw tokens
        self._exc_if_preview = ""
        self.SetString(ID_TXT_RULE_IF_PREVIEW, "")

    def _exc_get_selected_if_token(self) -> Optional[str]:
            sel_id = self.GetInt32(ID_BCB_RULE_IF)
            return self._exc_item_raw_by_id.get(sel_id)

    def _exc_get_selected_target_token(self) -> Optional[str]:
        sel_id = self.GetInt32(ID_BCB_RULE_TARGET)
        return self._exc_item_raw_by_id.get(sel_id)

    def _exc_build_if_expr(self) -> str:
        """Serialize current IF builder state to a rule IF expression string."""
        groups = getattr(self, "_exc_if_groups", []) or []
        parts: List[str] = []
        for g in groups:
            toks = [t for t in g if t]
            if not toks:
                continue
            if len(toks) == 1:
                parts.append(toks[0])
            else:
                parts.append("(" + " | ".join(toks) + ")")
        return " & ".join(parts)

    def _exc_update_if_preview(self) -> None:
        expr = self._exc_build_if_expr()
        if not expr:
            expr = "(no IF tokens selected)"
        self.SetString(ID_TXT_RULE_IF_PREVIEW, expr)



    def cmsg_brandner_render_progress(self) -> None:
        idx_frame = get_index_render_frame()
        num_combinations = len(self.possible_combinations)
        if idx_frame >= num_combinations:
            reset_render_progress()

            paths_images = consume_rendered_image_paths()
            num_images = len(paths_images)

            msg = (
                f"Rendering finished: {num_images}/{num_combinations}\n"
                "Open all in Picture Viewer?"
            )
            do_open_pv = c4d.gui.QuestionDialog(msg)
            if do_open_pv:
                for _path_bmp in paths_images:
                    bmp = c4d.bitmaps.BaseBitmap()
                    result, _ = bmp.InitWith(_path_bmp)
                    if result == c4d.IMAGERESULT_OK:
                        c4d.bitmaps.ShowBitmap(bmp)

        self.InitValues()

        doc, result = consume_render_result()
        if doc is not None and doc.IsAlive():
            c4d.documents.InsertBaseDocument(doc)
        if result is not None and result != c4d.RENDERRESULT_OK:
            msg = f"Failed to render document ({result})."
            open_error_requester(msg)

        c4d.EventAdd()