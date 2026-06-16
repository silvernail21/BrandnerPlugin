# bccf_constants.py

# ----------------------------------------------------------------------
# Plugin info
# ----------------------------------------------------------------------
PLUGIN_VERSION = "2.0"
PLUGIN_ID_BRANDNER = 1064979  # Use a unique ID obtained from Plugin Cafe
PLUGIN_NAME_BRANDNER = "BC-ComboFlow"
PLUGIN_TOOLTIP_BRANDNER = "BC-ComboFlow v2.0 for Cinema 4D"

# ----------------------------------------------------------------------
# BaseContainer (BCB) parameter IDs
#
# NOTE:
# - BCB parameter IDs live in the range 10000 <= id < 20000.
# - Many of these are also reused as GeDialog IDs in the main dialog.
# ----------------------------------------------------------------------

ID_BCB_PREFIX            = 10100
ID_BCB_DELIMITER         = 10101
ID_BCB_DIRECTORY_OUTPUT  = 10102
ID_BCB_PRODUCT_NAME      = 10104
ID_BCB_DO_GENERATE_CSV   = 10105
ID_BCB_FILENAME          = 10107
ID_BCB_DO_SAVE_PROJECT   = 10109
ID_BCB_MODE_RENDER       = 10111

# --- Exceptions / combo exclusion rules --------------------------------
# Multiline text field storing all rules as plain text.
# One rule per line, format:
#   IF_NAME -> NEVER1, NEVER2, ...
ID_BCB_EXCLUSION_RULES_RAW = 10112

# UI-only IDs for the exception builder controls (not stored in BCB):
ID_BCB_RULE_IF    = 9001  # "If part" combo box
ID_BCB_RULE_NEVER = 9002  # "Never with" combo box
ID_BCB_RULE_ADD   = 9003  # "Add rule" button

# Extended exception builder UI IDs (not stored in BCB):
# - Target replaces the old 'Never' control (kept as alias for backwards compat).
# - Action selects NEVER vs REQUIRE.
# - Add AND/OR build complex IF groups; Clear resets the IF builder state.
ID_BCB_RULE_TARGET = ID_BCB_RULE_NEVER  # alias; target can be camera/option/const-group
ID_BCB_RULE_ACTION   = 9004  # action combo box: NEVER / REQUIRE
ID_BCB_RULE_ADD_AND  = 9005  # add token as AND condition
ID_BCB_RULE_ADD_OR   = 9006  # add token as OR within current group
ID_BCB_RULE_CLEAR_IF = 9007  # clears the current IF builder
ID_TXT_RULE_IF_PREVIEW = 9008  # static text showing current IF expression
ID_STR_RULE_STATUS     = 9009  # rule validation / exclusion feedback label


# ----------------------------------------------------------------------
# Internal IDs (parameters not shown in UI, stored only in BCB)
# Range: id > 50000.
# ----------------------------------------------------------------------
ID_BCB_TOKEN_EXAMPLE_MODE = 50001

# ----------------------------------------------------------------------
# Render mode values (stored in ID_BCB_MODE_RENDER)
# ----------------------------------------------------------------------
MODE_RENDER_NO_RENDER       = 0
MODE_RENDER_PV              = 1  # threaded background render (RenderDocument)
MODE_RENDER_RQ_QUEUE        = 2
MODE_RENDER_RQ_QUEUE_START  = 3
MODE_RENDER_CMD_RENDER      = 4  # interactive "Render to Picture Viewer" (CallCommand 12099)

# ----------------------------------------------------------------------
# Null object names for project components
# ----------------------------------------------------------------------
BR_CAMERAS    = "BR_CAMERAS"
BR_COMPONENTS = "BR_COMPONENTS"
BR_CONSTANTS  = "BR_CONSTANTS"
BR_STAGE      = "BR_STAGE"
BR_VARIABLES  = "BR_VARIABLES"

# ----------------------------------------------------------------------
# Misc / UI helpers
# ----------------------------------------------------------------------
# Prefix used in token help strings
PREFIX_TOKEN_NAME = "Brandner: "

# In case there are no options in a variable, SUFFIX_NO_OPTION gets
# appended to variable names in the combo box.
SUFFIX_NO_OPTION = " [No Options]"

# ----------------------------------------------------------------------
# Parameter defaults
# ----------------------------------------------------------------------
DEFAULT_DELIMITER        = "_"
DEFAULT_DIRECTORY_OUTPUT = "./Output/"
DEFAULT_DO_GENERATE_CSV  = True
DEFAULT_DO_SAVE_PROJECT  = True

# DEFAULT_FILENAME:
#   Prefix | Product Name | Variable Options | Camera |
DEFAULT_FILENAME = "$_b_pre$_d$_b_prod$_d$_b_vars$_d$_b_cam$_d"

DEFAULT_MODE_RENDER  = MODE_RENDER_CMD_RENDER
DEFAULT_PREFIX       = "SCH"
# Product number will be appended in bccf_utils.get_bc_brandner_default()
DEFAULT_PRODUCT_NAME = "Product #"
