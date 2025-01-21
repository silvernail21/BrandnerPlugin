import os
import c4d # type: ignore
from c4d import plugins, gui, bitmaps
import json
import webbrowser
import random
import itertools
import logging

PLUGIN_ID = 1000003  # Use a unique ID obtained from Plugin Cafe

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BrandnerDialog(gui.GeDialog):
    ID_BTN_RENDER = 1
    ID_RANDOMIZE = 2

    ID_TAB_GROUP = 10000
    ID_RENDER_TAB = 10001
    ID_COMPONENT_TAB = 10002
    ID_PARAM_TAB = 10003
    ID_SCROLL_GROUP = 10004
    ID_SCENE_GROUP = 10005
    ID_COMPONENT_GROUP = 10006
    ID_FILE_STRUCTURE_GROUP = 10007  # New Group for File Structure

    ID_PREFIX = 10100
    ID_DELIMITER = 10101
    ID_OUT_DIR = 10102
    ID_OUT_COUNT = 10103
    ID_PRODUCT_NAME = 10104
    ID_USE_PRODUCT_NAME = 10107  # New Checkbox ID
    ID_VIEWS_LIST = 10105

    ID_VAR_LIST = 10200
    ID_CONST_LIST = 10201
    ID_OPTIONS_LIST = 10202

    ID_HIERARCHY = 11000
    ID_REFRESH = 11001

    ID_FILE_STRUCTURE_LIST = 12000  # New List for File Structure
    ID_GENERATE_CSV = 12001  # New Checkbox ID for generating CSV

    def __init__(self):
        self.component_list = []
        self.dyn_options = []
        self.variables = self.get_elements("BR_VARIABLES")
        self.constants = self.get_elements("BR_CONSTANTS")
        self.cameras = self.get_elements("BR_CAMERAS")

        self.n_components = None
        self.n_variables = None
        self.n_constants = None

        self.possible_combinations = []

        self.file_structure = []  # New: To store file structure elements

    def CreateLayout(self):
        self.SetTitle("Brandner Plugin")

        # Plugin Window
        self.GroupBegin(1, c4d.BFH_SCALEFIT, 1, 0, "Plugin", initw=500)
        self.TabGroupBegin(self.ID_TAB_GROUP, c4d.BFH_SCALE | c4d.BFH_FIT | c4d.BFV_SCALEFIT)
        self.LoadMainTab()
        self.GroupEnd()
        self.GroupEnd()

        self.setDefaultValues()
        self.UpdateDropdowns()
        self.UpdateFileStructurePreview()  # Initial preview update

        return True

    def LoadMainTab(self):
        width = 200    
        self.GroupBegin(self.ID_RENDER_TAB, c4d.BFH_SCALEFIT, 1, 0, "Render",  initw=width)

        self.GroupBegin(self.ID_RENDER_TAB, c4d.BFH_SCALEFIT, 2, 0, "General Settings", initw=width)
        
        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Product Name", initw=10, inith=20)
        self.AddEditText(self.ID_PRODUCT_NAME, c4d.BFH_SCALEFIT, initw=width)
        
        self.AddCheckbox(self.ID_USE_PRODUCT_NAME, c4d.BFH_SCALEFIT, name="Use Product Name in Filename", initw=30, inith=20)

        # Group for the buttons
        self.GroupBegin(20000, c4d.BFH_SCALEFIT, 2, 1, "ButtonsGroup", c4d.BFH_LEFT)
        self.AddButton(self.ID_HIERARCHY, c4d.BFH_SCALEFIT, name="Set Up File Hierarchy", inith=10)
        self.AddButton(self.ID_REFRESH, c4d.BFH_SCALEFIT, name="Refresh", initw=15, inith=10)
        self.GroupEnd()

        self.GroupEnd()
        
        self.GroupBegin(self.ID_COMPONENT_GROUP, c4d.BFH_SCALEFIT, 1, 0, "Components", 0, initw=width)
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.componentsSection()
        self.GroupEnd()

        self.renderSection()

        self.AddButton(self.ID_RANDOMIZE, c4d.BFH_SCALEFIT, name="Randomize In Viewport", inith=10)
        self.AddButton(self.ID_BTN_RENDER, c4d.BFH_SCALEFIT, name="Render Combinations", inith=20)
        
        # Add the new checkbox for generating CSV
        self.AddCheckbox(self.ID_GENERATE_CSV, c4d.BFH_SCALEFIT, name="Generate CSV", initw=30, inith=20)

        self.GroupBegin(self.ID_FILE_STRUCTURE_GROUP, c4d.BFH_SCALEFIT, 1, 0, "File Structure Preview", 0, initw=width)
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.AddMultiLineEditText(self.ID_FILE_STRUCTURE_LIST, c4d.BFH_SCALEFIT, initw=width, inith=100, style=c4d.DR_MULTILINE_READONLY)
        self.GroupEnd()

        self.GroupEnd()

    def componentsSection(self, n=0):
        width = 200

        # Group for Variables
        self.GroupBegin(self.ID_COMPONENT_TAB, c4d.BFH_SCALEFIT, 1, 0, "Variables", 0, initw=width)
        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Variables", inith=20)
        self.AddComboBox(self.ID_VAR_LIST, c4d.BFH_SCALEFIT, initw=width)
        for i, var in enumerate(self.variables):
            self.AddChild(self.ID_VAR_LIST, i, var)
        self.SetInt32(self.ID_VAR_LIST, n)
        self.GroupEnd()

        # Group for Options
        self.GroupBegin(self.ID_COMPONENT_TAB, c4d.BFH_SCALEFIT, 1, 0, "Options", 0, initw=width)
        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Options", inith=20)
        self.AddComboBox(self.ID_OPTIONS_LIST, c4d.BFH_SCALEFIT, initw=width)
        for i, option in enumerate(self.dyn_options):
            self.AddChild(self.ID_OPTIONS_LIST, i, option)
        self.GroupEnd()

        # Group for Constants
        self.GroupBegin(self.ID_COMPONENT_TAB, c4d.BFH_SCALEFIT, 1, 0, "Constants", 0, initw=width)
        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Constants", inith=20)
        self.AddComboBox(self.ID_CONST_LIST, c4d.BFH_SCALEFIT, initw=width)
        for i, const in enumerate(self.constants):
            self.AddChild(self.ID_CONST_LIST, i, const)
        self.GroupEnd()

        # Group for Views
        self.GroupBegin(self.ID_COMPONENT_TAB, c4d.BFH_SCALEFIT, 1, 0, "Views", 0, initw=width)
        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Views", inith=20)
        self.AddComboBox(self.ID_VIEWS_LIST, c4d.BFH_SCALEFIT, initw=width)
        for i, var in enumerate(self.cameras):
            self.AddChild(self.ID_VIEWS_LIST, i, var)
        self.SetInt32(self.ID_VIEWS_LIST, n)
        self.GroupEnd()

    def renderSection(self):
        width = 200
        self.GroupBegin(self.ID_RENDER_TAB, c4d.BFH_SCALEFIT, 4, 0, "Render", 0, initw=400)
        self.GroupBorder(c4d.BORDER_THIN_IN)

        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Output Prefix", inith=20)
        self.AddEditText(self.ID_PREFIX, c4d.BFH_SCALEFIT, initw=width)

        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Delimiter", inith=20)
        self.AddEditText(self.ID_DELIMITER, c4d.BFH_SCALEFIT, initw=width)

        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Output Directory", inith=20)
        self.AddEditText(self.ID_OUT_DIR, c4d.BFH_SCALEFIT, initw=width)

        self.AddStaticText(1, c4d.BFH_SCALEFIT, name="Output Count", inith=20)
        self.AddStaticText(self.ID_OUT_COUNT, c4d.BFH_SCALEFIT, name=len(self.possible_combinations), inith=20)

        self.GroupEnd()
    
    def UpdateDropdowns(self, n=0):
        self.LayoutFlushGroup(self.ID_COMPONENT_GROUP)
        self.componentsSection(n)
        self.LayoutChanged(self.ID_COMPONENT_GROUP)

    def get_elements(self, element_name):
        doc = c4d.documents.GetActiveDocument()
        element = doc.SearchObject(element_name)
        elements = []
        if not element:
            return elements
        
        for child in element.GetChildren():
            elements.append(child.GetName())
        return elements

    def getOptions(self, variable):
        doc = c4d.documents.GetActiveDocument()
        n_variables = doc.SearchObject("BR_VARIABLES")
        options = []
        if not n_variables:
            return options
        
        for child in n_variables.GetChildren():
            if child.GetName() == variable:
                for sub_child in child.GetChildren():
                    options.append(sub_child.GetName())

        return options
    
    def Command(self, id, msg):
        doc = c4d.documents.GetActiveDocument()
        if id == self.ID_BTN_RENDER:
            self.Render()

        elif id == self.ID_RANDOMIZE:
            self.Randomize()

        elif id == self.ID_HIERARCHY:
            self.setHierarchy()
        
        elif id == self.ID_REFRESH:
            self.variables = self.get_elements("BR_VARIABLES")
            self.constants = self.get_elements("BR_CONSTANTS")
            self.cameras = self.get_elements("BR_CAMERAS")
            self.UpdateDropdowns()
            self.possible_combinations = self.calculateCombinations()
            self.SetString(self.ID_OUT_COUNT, str(len(self.possible_combinations)))
            self.UpdateFileStructurePreview()  # Update preview on refresh
        
        elif id == self.ID_VAR_LIST:
            chosen_variable = self.GetInt32(self.ID_VAR_LIST)
            varname = self.variables[chosen_variable]
            self.dyn_options = self.getOptions(varname)
            self.UpdateDropdowns(n=chosen_variable)
            self.UpdateFileStructurePreview()  # Update preview on variable change
        
        elif id == self.ID_VIEWS_LIST:
            chosen_camera = self.GetInt32(self.ID_VIEWS_LIST)
            camname = self.cameras[chosen_camera]
            doc.GetActiveBaseDraw().SetSceneCamera(doc.SearchObject(camname))
            c4d.EventAdd()

        elif id == self.ID_FILE_STRUCTURE_LIST:
            new_order = self.GetString(self.ID_FILE_STRUCTURE_LIST).split(self.GetString(self.ID_DELIMITER))
            self.ReorderFileStructure(new_order)

        elif id == self.ID_OUT_DIR:
            output_dir = self.GetString(self.ID_OUT_DIR).strip()
            if output_dir and os.path.isdir(output_dir) and os.access(output_dir, os.W_OK):
                self.Enable(self.ID_BTN_RENDER, True)  # Enable button if valid directory
            else:
                self.Enable(self.ID_BTN_RENDER, False)  # Disable button otherwise

        return True

    def UpdateFileStructurePreview(self):
        prefix = self.GetString(self.ID_PREFIX)
        delimiter = self.GetString(self.ID_DELIMITER)
        product_name = self.GetString(self.ID_PRODUCT_NAME)
        use_product_name = self.GetBool(self.ID_USE_PRODUCT_NAME)

        if use_product_name:
            self.file_structure = [prefix, product_name, delimiter.join(self.variables), "View"]
        else:
            self.file_structure = [prefix, delimiter.join(self.variables), "View"]

        preview_text = delimiter.join(self.file_structure)
        self.SetString(self.ID_FILE_STRUCTURE_LIST, preview_text)

    def ReorderFileStructure(self, new_order):
        self.file_structure = new_order
        self.UpdateFileStructurePreview()

    def calculateCombinations(self):
        doc = c4d.documents.GetActiveDocument()
        n_variables = doc.SearchObject("BR_VARIABLES")
        n_cameras = doc.SearchObject("BR_CAMERAS")

        options = []
        for variable in n_variables.GetChildren():
            var_options = [option.GetName() for option in variable.GetChildren()]
            options.append(var_options)

        combinations = list(itertools.product(*options))

        updated_combinations = []
        for combo in combinations:
            for cam in [cam.GetName() for cam in n_cameras.GetChildren()]:
                updated_combinations.append(combo + (cam,))  

        return updated_combinations

    def setHierarchy(self):
        doc = c4d.documents.GetActiveDocument()
        self.n_components = createNull("BR_COMPONENTS")
        self.n_constants = createNull("BR_CONSTANTS", self.n_components)
        self.n_variables = createNull("BR_VARIABLES", self.n_components)
        self.n_cameras = createNull("BR_CAMERAS", self.n_components)
        if not self.n_variables.GetChildren():
            createNull("Variable_01", self.n_variables)
            createNull("Variable_02", self.n_variables)
            createNull("Variable_03", self.n_variables)
            
        c4d.EventAdd()

    def setDefaultValues(self):
        self.SetString(self.ID_PRODUCT_NAME, f"Product #{random.randint(0, 1000)}")
        self.SetBool(self.ID_USE_PRODUCT_NAME, True)  # Default to checked
        self.SetString(self.ID_PREFIX, "SC")
        self.SetString(self.ID_DELIMITER, "_")
        self.SetString(self.ID_OUT_DIR, r"\Output\\")
        self.SetBool(self.ID_GENERATE_CSV, True)  # Default to checked

    def Randomize(self):
        doc = c4d.documents.GetActiveDocument()
        n_variables = doc.SearchObject("BR_VARIABLES")
        n_cameras = doc.SearchObject("BR_CAMERAS")
        if not n_variables:
            return
        for variable in n_variables.GetChildren():
            for option in variable.GetChildren():
                hideObject(option)
            random_option = random.choice(variable.GetChildren())
            showObject(random_option)
        c4d.EventAdd()
        random_camera = random.choice(n_cameras.GetChildren())
        doc.GetActiveBaseDraw().SetSceneCamera(random_camera)
        c4d.EventAdd()

    def Render(self):
        doc = c4d.documents.GetActiveDocument()
        n_variables = doc.SearchObject("BR_VARIABLES")
        n_cameras = doc.SearchObject("BR_CAMERAS")

        d = self.GetString(self.ID_DELIMITER)
        product_name = self.GetString(self.ID_PRODUCT_NAME)
        prefix = self.GetString(self.ID_PREFIX)
        output_dir = self.GetString(self.ID_OUT_DIR).strip()  # Remove leading/trailing whitespace
        use_product_name = self.GetBool(self.ID_USE_PRODUCT_NAME)
        generate_csv = self.GetBool(self.ID_GENERATE_CSV)

        # Check if output directory path is set and exists
        if not output_dir or not os.path.isdir(output_dir):
            gui.MessageDialog("Please specify a valid output directory.")
            return

        # Check if output directory is writable
        if not os.access(output_dir, os.W_OK):
            gui.MessageDialog("The specified output directory is not writable.")
            return

        # Additional check to ensure output directory path is not a file
        if os.path.isfile(output_dir):
            gui.MessageDialog("The specified output directory is a file. Please select a directory.")
            return

        if self.possible_combinations:
            if generate_csv:
                self.write_csv(output_dir, product_name, is_header=True)

            for combo in self.possible_combinations:
                camera = combo[-1]
                idx = self.possible_combinations.index(combo)
                for var in n_variables.GetChildren():
                    for obj in var.GetChildren():
                        hideObject(obj)
                parts = ""
                for option in combo:
                    if option != camera:
                        showObject(doc.SearchObject(option))
                        parts += option + d
                c4d.EventAdd()

                camObj = doc.SearchObject(camera)
                doc.GetActiveBaseDraw().SetSceneCamera(camObj)
                c4d.EventAdd()

                filename = prefix + d
                if use_product_name:
                    filename += product_name + d
                filename += parts + camera + ".png"
                
                render_and_save(doc, output_dir, filename)
                if generate_csv:
                    self.write_csv(output_dir, product_name, False, camera, str(idx))
    
    def write_csv(self, output_dir, product_name, is_header=False, cam="Camera", index="index"):
        doc = c4d.documents.GetActiveDocument()
        n_variables = doc.SearchObject("BR_VARIABLES")
        n_cameras = doc.SearchObject("BR_CAMERAS")
        try:
            with open(os.path.join(output_dir, f"{product_name}_metadata.csv"), "a") as f:
                line = index + ";"
                if is_header:
                    for var in n_variables.GetChildren():
                        line += var.GetName() + ";"
                else:
                    for var in n_variables.GetChildren():
                        for option in var.GetChildren():
                            if option[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] == c4d.OBJECT_ON:
                                line += option.GetName() + ";"
                line += cam + ";" + "\n"
                logging.info(f"Writing line: {line}")
                f.write(line)
        except Exception as e:
            logging.error(f"Failed to write CSV: {e}")

def hideObject(obj):
    obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.OBJECT_OFF
    obj[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.OBJECT_OFF
    if obj.GetChildren():
        for child in obj.GetChildren():
            hideObject(child)

def showObject(obj):
    obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.OBJECT_ON
    obj[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.OBJECT_ON
    if obj.GetChildren():
        for child in obj.GetChildren():
            showObject(child)

def render_and_save(doc, path, filename):
    if not path.endswith('/'):
        path += '/'

    rd = doc.GetActiveRenderData().GetClone()
    rd[c4d.RDATA_PATH] = os.path.join(path, filename)
    rd[c4d.RDATA_FORMAT] = c4d.FILTER_PNG

    doc.InsertRenderData(rd)

    bmp = c4d.bitmaps.MultipassBitmap(int(rd[c4d.RDATA_XRES]), int(rd[c4d.RDATA_YRES]), c4d.COLORMODE_RGB)
    if bmp is None:
        raise RuntimeError("Failed to create the bitmap.")
    bmp.AddChannel(True, True)

    render_flags = c4d.RENDERFLAGS_EXTERNAL | c4d.RENDERFLAGS_NODOCUMENTCLONE
    c4d.EventAdd()
    result = c4d.documents.RenderDocument(doc, rd.GetDataInstance(), bmp, render_flags)
    
    c4d.bitmaps.ShowBitmap(bmp)
    if result is None:
        logging.error("Rendering failed.")
    else:
        logging.info(f"Rendering completed successfully. Image saved at: {rd[c4d.RDATA_PATH]}")

def createNull(name, parent=None):
    doc = c4d.documents.GetActiveDocument()
    null = doc.SearchObject(name)
    if not null:
        null = c4d.BaseObject(c4d.Onull)
        null.SetName(name)
        doc.InsertObject(null)
        c4d.EventAdd()

    if parent:
        null.InsertUnder(parent)
    return null

class Brandner(plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = BrandnerDialog()
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=200)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = BrandnerDialog()
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

if __name__ == "__main__":
    pluginIcon = bitmaps.BaseBitmap()

    if not plugins.RegisterCommandPlugin(
            id=PLUGIN_ID,
            str="Brandner Plugin",
            help="Brandner Plugin for Cinema 4D",
            info=0,
            dat=Brandner(),
            icon=pluginIcon):
        print("Plugin registration failed.")
