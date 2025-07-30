<!-- inject desc here -->
<!-- inject-desc -->

A python library for setup comfyui custom nodes for developers in development

## File size

<!-- inject size of bundles here -->
<!-- inject-file-size -->

## Features

<!-- inject feat here -->
- feat(core): pyio_read_dirs_name - read dirs name in some location
- feat(core): pyio_read_file_name - read file name in some location
- feat(core): pyio_read_module_name - read python module name in some location
- feat(core): get_sys_module - get python module in sys with name
- feat(core): get_classes_in_module - get class list in python module
- feat(core): get_module_name_list - get module name list in sys.modules with substring name
- feat(core): list_ignore_them - list ignore them
- feat(core): std_stro_name - std name in stro
- feat(core): std_module_name - std name for module
- feat(core): import_custom_node_module - import custom node module in some sub location
- feat(core): is_yors_style_node - check if a node class is yors-style node
- feat(core): get_node_class_in_sys_modules - get node (yors style) class name in sys modules with substring name
- feat(core): get_all_classs_in_sys - get all class in sys
- feat(core): register_node_list - register comfyui node (yors style) through udate node class map and and display name map and more
- feat(core): use global vars
- feat(core): use default category in node when custom categoty not passed
- feat(core): info repeat node when node
- feat(core): register_node_list_local - not using global vars
- feat(core): get_node_desc - get yors-style node desc from node class
- feat(core): get_node_name - get yors-style node name from node class
- feat(core): get_node_menu_name - get yors-style node menu name from node class
- feat(core): gen_menu_name - gen yors-style node display name
- feat(core): import_py_file - import py file in location
- feat(core): read_py_file_name_list - read py file name list in location
- feat(core): ignore `__init__.py`
- feat(core): read_py_file_name_list_no_suffix - read py file name list in location wihout .py suffix
- feat(core): ignore `__init__.py`
- feat(core): get_module_name_contains_x_in_sys - get all module name with subtring name in sys
- feat(core): ignore eq x
- feat(core): get_module_contains_x_name_in_sys - get all module with subtring name in sys
- feat(core): ignore eq x
- feat(core): debug_print - print msg if node loading debug status opened
- feat(core): debug_status - update node loading debug status
- feat(core): entry_pre_import - make `__all__` with name and file location
- feat(core): entry_import - import module with importlib.import_module and `__all__`
- feat(core): entry_post_import - prepare import for comfyui node
- feat(core): entry - make entry vars for comfyui node
- feat(core): pyio_install_requirements - install requirements in file location without installed packages checking before installing
- feat(core): ensure_package - install some python package if not installed
- feat(core): spio_install_requirements - install some python package in file location if not installed
- feat(core): node_install_requirements - install requirements in dir and file name
- feat(core): set_node_class_category_alias - set node category alias through extended class

## Usage

```bash
pip install yors_comfyui_node_setup
```

<!-- inject demo here -->
## Demo

###  case 1
- code your `__init__.py`
```py
# v1
from yors_comfyui_node_setup import entry,node_install_requirements # global

# install requirements
node_install_requirements(__file__)

# export comfyui node vars
__all__,NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES = entry(__name__,__file__)
```

- code your nodes . `xx.py`
```py
# from .conf import CURRENT_CATEGORY,CURRENT_FUNCTION

CURRENT_CATEGORY="ymc/text" # as default category
CURRENT_FUNCTION="exec" 

class TextInput:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "text": ("STRING",{"multiline": True,"default": ""}),
                  },
                }
    
    RETURN_TYPES = ("STRING",) 
    CATEGORY = CURRENT_CATEGORY
    FUNCTION = CURRENT_FUNCTION
    # NODE_NAME = "strm input"
    NODE_DESC = "multiline text" # NODE_NAME or NODE_DESC must be set. I prefer use NODE_DESC only.
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (False,)

    # must has method named xx bind to FUNCTION
    def exec(self,**kwargs):
        text = kwargs.get("text","")
        return (text,)
    
```

###  case 2
- code your `__init__.py`
```py
# v2
from yors_comfyui_node_setup import node_install_requirements,entry_pre_import,entry_import,get_all_classs_in_sys,register_node_list_local
from yors_pano_ansi_color import info_status

# install requirements
# node_install_requirements(__file__)

# gen __all__
__all__ = entry_pre_import(__name__,__file__)

# import moudle with __all__
entry_import(__name__,__all__)

# get class after importing moudle with __all__
this_module_all_classes = get_all_classs_in_sys(__name__)

# register node with default category
NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list(this_module_all_classes,False)

# addtional register node with custom category
# NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list_local(this_module_all_classes,True,"ymc/suite")
# print(NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES)
# print("\n".join(NODE_MENU_NAMES))
```

- code your nodes `xx.py`

###  case 3 (recomended)
- code your `__init__.py`

```py
# Set the web directory, any .js file in that directory will be loaded by the frontend as a frontend extension
WEB_DIRECTORY = "./web"

INFO_NODE_NAME=True
INSTALL_NODE_WITH_DEFAULT_CATEGORY=False
INFO_RIGHT_MENU=True
INFO_NODE_SETUP_STEP=True
def info_usage_step(msg):
    global INFO_NODE_SETUP_STEP
    if INFO_NODE_SETUP_STEP:
        print(f'[step] {msg}')
# v1
# from yors_comfyui_node_setup import entry,node_install_requirements # global

# info_usage_step("v1 1. install requirements")
# node_install_requirements(__file__)

# # 
# info_usage_step("v1 2. export comfyui node vars")
# __all__,NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES = entry(__name__,__file__)

# v2
info_usage_step("v2 1. import node setup utils")
from yors_comfyui_node_setup import node_install_requirements,entry_pre_import,entry_import,get_all_classs_in_sys,register_node_list_local,register_node_list

info_usage_step("v2 1.1 install requirements")
node_install_requirements(__file__)

info_usage_step("v2 1.2 gen __all__")
__all__ = entry_pre_import(__name__,__file__)

info_usage_step("v2 1.3 import moudle with __all__")
entry_import(__name__,__all__)

info_usage_step("v2 1.4 get class after importing moudle with __all__")
this_module_all_classes = get_all_classs_in_sys(__name__)

if INSTALL_NODE_WITH_DEFAULT_CATEGORY:
    info_usage_step("v2 1.5 register node with default category")
    NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list(this_module_all_classes,INFO_NODE_NAME)

info_usage_step("v2 1.6 addtional register node with custom category")
NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list_local(this_module_all_classes,INFO_NODE_NAME,"ymc/strm")
# print(NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES)

info_usage_step("v2 1.7 addtional register node with custom category")
if INFO_RIGHT_MENU:
    print("\n".join(NODE_MENU_NAMES))


# docs(core): load web ext
WEB_DIRECTORY = "./web"

# __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
# docs(core): export NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,WEB_DIRECTORY
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
```

- code your nodes `xx.py`

