# import asyncio
import os
# import json
# import shutil
# import inspect
# import aiohttp
# from server import PromptServer
# from tqdm import tqdm
import sys
import re
# import folder_paths
import importlib
from typing import List
import subprocess
config = None


# feat(core): def func to padd msg
def msg_padd(msg:str, msg_max_len:int, msg_fill_char:str="-"):
    msg_len = len(msg)
    msg_fill_length = (msg_max_len - msg_len + 2) // 2
    msg_padding = msg_fill_char * msg_fill_length
    padded_msg = f"{msg_padding}-{msg}-{msg_padding}"
    return padded_msg[:msg_max_len]

# feat(core): def func to print status msg
def info_status(msg_body:str, status:int):
    msg_success = "✅"
    msg_failed = "❌"
    msg_warn = "ℹ️"

    if status == 0:
        print(f"{msg_success} {msg_body}")
    elif status == 1:
        print(f"{msg_failed} {msg_body}")
    else:
        print(f"{msg_warn} {msg_body}")

# feat(core): def func to print step msg
def info_step(msg:str,msg_max_len:int=60, msg_fill_char:str="-"):
    print(msg_padd(msg, msg_max_len,msg_fill_char))


# feat(core): pyio_read_dirs_name - read dirs name in some location
def pyio_read_dirs_name(loc:str):
    """
    read dirs name in some location
    """

    files_file = [
        f for f in os.listdir(loc) if os.path.isdir(os.path.join(loc, f))
    ]
    return files_file

# feat(core): pyio_read_file_name - read file name in some location
def pyio_read_file_name(loc:str):
    """
    read file name in some location
    """
    files_file = [
        f for f in os.listdir(loc) if os.path.isfile(os.path.join(loc, f))
    ]
    return files_file

# feat(core): pyio_read_module_name - read python module name in some location
def pyio_read_module_name(loc:str,ignore_list:list[str]=["__pycache__"]):
    """
    read module name in some location
    """

    dirs_name = pyio_read_dirs_name(loc)
    # docs(core): ignore name in ignore_list
    dirs_name = [x for x in dirs_name if x not in ignore_list]

    return dirs_name

# feat(core): get_sys_module - get python module in sys with name
def get_sys_module(name:str):
    """
    get python module in sys with name

    ```
    get_sys_module(__name__)
    ```
    """
    return sys.modules[name]

# feat(core): get_classes_in_module - get class list in python module
def get_classes_in_module(module):
    """
    get class list in python module

    ```
    get_classes_in_module(sys.modules[__name__])
    ```
    """
    classes = []
    for name in dir(module):
        member = getattr(module, name)
        if isinstance(member, type):
            classes.append(member)
    return classes


# feat(core): get_module_name_list - get module name list in sys.modules with substring name 
def get_module_name_list(name:str):
    """
    get module name list in sys.modules with substring name 
    """
    module_name_list=[]

    print(f"[info] read name in sys.modules if name including {name} (loaded)")
    
    for key,value in sys.modules.items():
        # print(key)
        if name in key :
            # """do nothing"""
            # print(key)
            module_name_list.append(key)
    return module_name_list


# feat(core): list_ignore_them - list ignore them
def list_ignore_them(namelist:list,them:list=[]):
    """
    name list ignore some
    """

    dirs_name = [x for x in namelist if x not in them]
    return dirs_name

# feat(core): std_stro_name - std name in stro
def std_stro_name(name:str):
    """
    std name in stro
    
    ```
    std_stro_name('YMC/MASK//  mask ') # 'YMC/MASK/ mask'
    ```
    """
    # Normalize hyphens (replace multiple '-' with single '-')
    stded = re.sub(r'-+', "-", name)
    # Normalize spaces (replace multiple ' ' with single ' ')
    stded = re.sub(r' +', " ", stded)
    # Normalize slashes (replace multiple '/' with single '/')
    stded = re.sub(r'/+', "/", stded)
    # Trim leading/trailing whitespace
    return stded

# feat(core): std_module_name - std name for module
def std_module_name(name:str):
    """
    std name for module

    ```
    std_module_name('YMC/MASK//  mask ') # 'YMC/MASK//_mask_'
    std_module_name('YMC/MASK//  mask ') # 'YMC_MASK_mask' # todo
    ```
    """
    stded = re.sub(r'-+', "_",name)
    stded = re.sub(r' +', "_",stded)
    stded = re.sub(r'_+', "_",stded)
    stded = stded.strip()
    return stded




# feat(core): import_custom_node_module - import custom node module in some sub location
def import_custom_node_module(root_path:str,root_name:str,sub_name="modules"):
    """
    import custom node module in some sub location

    ```
    import_custom_node_module(os.path.dirname(__file__),__name__,"modules")
    ```
    """
    # root_path=os.path.dirname(__file__)
    dirs_name = pyio_read_module_name(os.path.join(root_path,sub_name),["__pycache__"])
    for node_name in dirs_name:
        # print(node_name)
        rel_name=".".join(['',sub_name,node_name])
        # print(rel_name)
        importlib.import_module(rel_name, package=root_name)

# feat(core): is_yors_style_node - check if a node class is yors-style node
def is_yors_style_node(cls,ver:str='3.0'):
    """
    check if a node class is yors-style node
    """
    
    cver = ver.lower()
    if cver == '2.0':
        return any(hasattr(cls, attr) for attr in ['NODE_DESC','NODE_NAME'])
    if cver == '3.0':
        return any(hasattr(cls, attr) for attr in ['FUNCTION','NODE_DESC','NODE_NAME'])  
    return hasattr(cls, 'NODE_DESC')


# feat(core): get_node_class_in_sys_modules - get node (yors style) class name in sys modules with substring name
def get_node_class_in_sys_modules(name:str):
    """
    get node (yors style) class name in sys modules with substring name
    """
    # print(f"[info] read class name if key in sys.modules including {__name__}")
    # docs(core): print class name if key in sys.modules including this module name
    ValidNodeClassList=[]
    ALL_CLASS_NAMES=[]
    for key,value in sys.modules.items():
        if name in key :
            # print(key)
            # docs(core): get all classes in name module
            # module = sys.modules[key]
            module = get_sys_module(key)

            all_classes = get_classes_in_module(module)
            for cls in all_classes:
                # dup class name
                if cls.__name__ not in ALL_CLASS_NAMES:
                    ALL_CLASS_NAMES.append(cls.__name__)
                    # print(cls.__name__)
                    if is_yors_style_node(cls):
                        ValidNodeClassList.append(cls)
                # print name of them
                # print(cls.__name__)

                # collect class that match ymc style - has attr NODE_DESC in class
                # if is_yors_style_node(cls):
                #     if cls not in ValidNodeClassList:
                #         ValidNodeClassList.append(cls)
    return ValidNodeClassList,ALL_CLASS_NAMES

# feat(core): get_all_classs_in_sys - get all class in sys
def get_all_classs_in_sys(name:str,infoimport=None):
    debug_status(infoimport)
    debug_print('[info] get all module name of this module in sys')
    this_module_all_names= get_module_name_contains_x_in_sys(name)

    debug_print('[info] get all classes of this module in this module')
    this_module_all_classes=[]
    for x in this_module_all_names:
        # debug_print(x)
        # cl = get_classes_in_module(sys.modules[x])
        cl = get_classes_in_module(get_sys_module(x))
        this_module_all_classes.extend(cl)
    return this_module_all_classes


# topic:node - register - helper
# NODE_CLASS_MAPPINGS = {}
# NODE_DISPLAY_NAME_MAPPINGS = {}
# NODE_MENU_NAMES=[]   

# feat(core): register_node_list - register comfyui node (yors style) through udate node class map and and display name map and more
# feat(core): use global vars
# feat(core): use default category in node when custom categoty not passed
# feat(core): info repeat node when node 

def register_node_list(NodeClassList:list,info_name:bool=False,category:str=None):
    """
    register_node_list(all_classes,False)

    NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list(all_classes,False)
    """
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}
    NODE_MENU_NAMES=[]
    # global NODE_CLASS_MAPPINGS
    # global NODE_DISPLAY_NAME_MAPPINGS
    # global NODE_MENU_NAMES
    for cls in NodeClassList:
        # print name of them
        # print(cls.__name__)

        # docs(core): only register node (yors style)
        if is_yors_style_node(cls):
            node_menu_name,node_desc=gen_node_menu_name(cls,NODE_DISPLAY_NAME_MAPPINGS,category,info_name)
            # set node name set
            NODE_MENU_NAMES.append(node_menu_name)
            # put node class map
            NODE_CLASS_MAPPINGS[node_menu_name]=cls
            # set node name map
            NODE_DISPLAY_NAME_MAPPINGS[node_menu_name]=node_desc
            # info_status(f'register node {node_menu_name}',0)
    return NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES

# feat(core): register_node_list_local - not using global vars
def register_node_list_local(NodeClassList:list,info_name:bool=False,category:str=None):
    """
    NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list_local(all_classes,False)
    """
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}
    NODE_MENU_NAMES=[]
    for cls in NodeClassList:
        # print name of them
        # print(cls.__name__)

        # docs(core): only register node (yors style)
        if is_yors_style_node(cls):
            node_menu_name,node_desc=gen_node_menu_name(cls,NODE_DISPLAY_NAME_MAPPINGS,category,info_name)
            # set node name set
            NODE_MENU_NAMES.append(node_menu_name)
            # put node class map
            NODE_CLASS_MAPPINGS[node_menu_name]=cls
            # set node name map
            NODE_DISPLAY_NAME_MAPPINGS[node_menu_name]=node_desc
            # info_status(f'register node {node_menu_name}',0)
    return NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES


def desc_from_name(name:str)->str:
    """
    NODE_DESC = desc_from_name(x.FUNCTION)
    """
    return name.replace("_"," ").capitalize()
    
# feat(core): get_node_desc - get yors-style node desc from node class
def get_node_desc(cls):
#   node_desc = std_stro_name(cls.NODE_DESC)
  node_desc =  std_stro_name(cls.NODE_DESC) if hasattr(cls,"NODE_DESC") else ""
  if node_desc == "":
    # node_desc = cls.__name__
    # use cls.FUNCTION to be desc
    node_desc =  std_stro_name(cls.FUNCTION) if hasattr(cls,"FUNCTION") else ""
    node_desc = desc_from_name(node_desc)

  if node_desc == "exec":
    #  use class name to be desc for cls.FUNCTION == exec
     node_desc = cls.__name__
  return node_desc 

# feat(core): get_node_name - get yors-style node name from node class
def get_node_name(cls):
  node_name =  std_stro_name(cls.NODE_NAME) if hasattr(cls,"NODE_NAME") else ""
  return node_name 

# feat(core): get_node_menu_name - get yors-style node menu name from node class
def get_node_menu_name(cls,node_category:str):
    node_desc = get_node_desc(cls)
    node_name = get_node_name(cls)
    # 1.0 {node_category}/{node_desc}
    # 2.0 {node_category}/{node_name}

    # docs(core): make menu name with NODE_DESC,CATEGORY
    node_menu_name = f'{node_category}/{node_desc}' 

    # docs(core): make menu name with NODE_NAME,CATEGORY if exits
    if node_name:
        #   info_status(f'use <node_category>/<node_name> to make node menu name since node_name {node_name} is not empty!',0)
        node_menu_name =  f'{node_category}/{node_name}'

    # info_status(f'category:{node_category} desc:{node_desc} name:{node_name}',2)
    # info_status(f'menu:{node_menu_name}',2)
    return (node_desc,node_name,node_menu_name)

# feat(core): gen_menu_name - gen yors-style node display name
def gen_node_menu_name(cls,menu_dict:dict,category:str=None,info_name=None):
  """
  gen_node_menu_name(cls,NODE_DISPLAY_NAME_MAPPINGS,category,info_name)
  """

  node_category = std_stro_name(category if category is not None else cls.CATEGORY)
  node_desc,node_name,node_menu_name = get_node_menu_name(cls,node_category)
 
  # docs(core): print repeat menu name
  if  menu_dict.get(node_menu_name,None) is not None:
      info_status(f'node name {node_menu_name} is repeat!',2)

  # docs(core): print menu name
  # if infoname ==True:
  if info_name:
      print(node_menu_name)
  return node_menu_name,node_desc


# feat(core): import_py_file - import py file in location
def import_py_file(fileloc:str,rootname=None):
    """
    import_py_file(__file__,None)

    import_py_file(__file__,".")

    import_py_file(__file__,".YmcNodeArtComfyui")
    """
    step_name="import py file"
    info_step(step_name)

    # get root path and name for file
  
    root_path = os.path.dirname(fileloc)
    root_name= os.path.split(root_path)[-1]
    if rootname is not None:
        root_name=".".join([rootname,root_name])

    # info_status(f"read root path and name",0)
    # print(root_name)

    filename_list = pyio_read_file_name(root_path)
    # info_status(f"read filename list",0)

    # print(filename_list)
    filename_list = list_ignore_them(filename_list,["__init__.py"])
    # info_status(f"ignore __init__.py",0)

    # ignore when space in name
    filename_list = [x for x in filename_list if x.find(" ") == -1]
    # info_status(f"ignore space in name",0)

    # print(filename_list)

    for filename in filename_list:
        name = os.path.splitext(filename)[0]
        # rel_name=".".join(['',name])
        # importlib.import_module(rel_name, package=root_name)
        # importlib.import_module(rel_name)
        importlib.import_module(name)
    info_status("import module with file name",0)
    return filename_list

# feat(core): read_py_file_name_list - read py file name list in location
# feat(core): ignore `__init__.py` 
def read_py_file_name_list(loc:str):
    """
    read_py_file_name_list(__file__)
    """
    root_path = os.path.dirname(loc)
    # root_name= os.path.split(root_path)[-1]
    filename_list = pyio_read_file_name(root_path)
    filename_list = list_ignore_them(filename_list,["__init__.py"])
    filename_list = [x for x in filename_list if x.find(" ") == -1]
    names=[]
    for filename in filename_list:
        name = os.path.splitext(filename)[0]
        names.append(name)
    return filename_list

# feat(core): read_py_file_name_list_no_suffix - read py file name list in location wihout .py suffix
# feat(core): ignore `__init__.py` 
def read_py_file_name_list_no_suffix(location:str):
    """
    __all__= read_py_file_name_list_no_suffix(__file__)
    """
    all_py_file=[]
    root_path=os.path.dirname(location)
    for fileanme in os.listdir(root_path):
        if fileanme == '__init__.py' or fileanme[-3:] != '.py':
            continue
        goodname=fileanme[:-3]
        all_py_file.append(goodname)
        # importlib.import_module(goodname)
        # importlib.import_module(os.path.join(root_path,goodname))
        # importlib.import_module(os.path.join(root_path,fileanme))
    return all_py_file

# feat(core): get_module_name_contains_x_in_sys - get all module name with subtring name in sys 
# feat(core): ignore eq x
def get_module_name_contains_x_in_sys(x):
    """
    get_module_name_contains_x_in_sys(__name__)
    """
    all_names_of_x=[]
    for key,value in sys.modules.items():
        # if 'ymc' in key:
        #     print(key)
        if x in key and x != key:
            # print(key)
            all_names_of_x.append(key)
    return all_names_of_x

# feat(core): get_module_contains_x_name_in_sys - get all module with subtring name in sys 
# feat(core): ignore eq x
def get_module_contains_x_name_in_sys(x):
    """
    get_module_contains_x_name_in_sys(__name__)
    """
    all_module_of_x=[]
    for key,value in sys.modules.items():
        # if 'ymc' in key:
        #     print(key)
        if x in key and x != key:
            # print(key)
            all_module_of_x.append(value)
    return all_module_of_x


NODE_LOADING_DEBUG=True

# feat(core): debug_print - print msg if node loading debug status opened
def debug_print(msg):
    # global NODE_LOADING_DEBUG
    # if NODE_LOADING_DEBUG == True:
    if NODE_LOADING_DEBUG:
        print(msg)
    return msg

# feat(core): debug_status - update node loading debug status
def debug_status(opened=None):
    global NODE_LOADING_DEBUG
    NODE_LOADING_DEBUG=NODE_LOADING_DEBUG if opened is None else opened

# topic:node - import - helper

# __all__=[]
# feat(core): entry_pre_import - make `__all__` with name and file location
def entry_pre_import(name:str,file:str,infoimport=None,):
    """
    __all__ = entry_pre_import(__name__,__file__,infoimport)


    __all__ = entry_pre_import(name,file,infoimport)
    """
    debug_status(infoimport)
    
    # debug_print(f'[init] {__file__} do:')
    debug_print(f'[init] {name} do:')

    stdfile = re.sub(r'\\', "/",file)
    debug_print(f'[info] this module file in {stdfile}')

    debug_print('[info] import utils from parent file')

    debug_print('[info] define __all__ with utils.make_all_import')
    # docs(core): define what it need to import in __all__
    __all__= read_py_file_name_list_no_suffix(file)
    return __all__

# feat(core): entry_import - import module with importlib.import_module and `__all__`
def entry_import(name,modx:list[str]=None):
    """
    entry_import(__name__)
    """
    global __all__
    module_list = modx if modx is not None else __all__
    debug_print('[info] import __all__ with from . import * ')
    # docs(core): automatically import
    # from . import * 
    for x in module_list:
        importlib.import_module(".".join([name,x]))


# feat(core): entry_post_import - prepare import for comfyui node
def entry_post_import(name:str,file:str,infoimport=None,):
    """
    NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = entry_post_import(__name__,__file__,infoimport)

    NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = entry_post_import(name,file,infoimport)
    """
    debug_status(infoimport)
    this_module_all_classes = get_all_classs_in_sys(name,infoimport)

    debug_print('[info] make valid node class map of this module')
    NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list(this_module_all_classes,False)
    # debug_print(f'[init] {__file__} done.')
    debug_print(f'[init] {name} done.')
    return NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES


# feat(core): entry - make entry vars for comfyui node
def entry(name,file,infoimport=None,):
    """
    __all__,NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES = entry(__name__,__file__)
    """
    step_name="make entry vars for comfyui node"
    info_step(step_name)

    debug_status(infoimport)

    global __all__
    __all__ = entry_pre_import(name,file,infoimport)
    # info_status(f"prepare vars __all__",0)

    entry_import(name,__all__)
    # info_status(f"import module with importlib.import_module and __all__",0)

    # this_module_all_classes = get_all_classs_in_sys(name,infoimport)
    # NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES  = register_node_list(this_module_all_classes,False)

    NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES = entry_post_import(name,file,infoimport)
    # info_status(f"prepare NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES",0)

    return __all__,NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES

# topic:deps - install - helper

# feat(core): pyio_install_requirements - install requirements in file location without installed packages checking before installing
def pyio_install_requirements(file):
    """
    piio_install_requirements(Path(__file__).parent / "requirements.txt")

    piio_install_requirements(os.path.join(os.path.dirname(__file__),"requirements.txt"))
    """
    # code based on custom_nodes/ComfyUI-Frame-Interpolation/install.py
    s_param = '-s' if "python_embeded" in sys.executable else '' 
    if not os.path.isfile(file):
        # print('file does not exist.')
        """
        do nothing
        """
    else:
        with open(file, 'r') as f:

            for package in f.readlines():
                package = package.strip()
                if package != "":
                    print(f"installing {package}...")
                    os.system(f'"{sys.executable}" {s_param} -m pip install {package}')



# 
# python -c "import sys; print(sys.executable)"
# python -m pip freeze
# pip list freeze
# python -c "import sys;import subprocess; print(subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).split())"

# only pkgs name
# python -c "import sys;import subprocess; package_list = [r.decode().split('==')[0] for r in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).split()];print(package_list)"

# pkgs name and version
# python -c "import sys;import subprocess; package_list = [r.decode().split(' ')[0] for r in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).split()];print(package_list)"

# python -c "import os;os.system(f'pip freeze')"
# pip list --format=freeze

# docs(core): you can install package in requirements.txt with utils.node_install_requirements

# code base on:
# custom_nodes\masquerade-nodes-comfyui\MaskNodes.py
package_list = None
# docs(core): support install package in your node 
def update_package_list():
    global package_list
    # package_list = [r.decode().split('==')[0] for r in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).split()]

    try:
        # Execute the 'pip list' command and capture the output
        output = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--format=freeze'], stderr=subprocess.STDOUT)
        # Split the output into lines
        lines = output.decode('utf-8').splitlines()
        # Skip the header line (if any) and extract the package names from each line
        package_list = [line.split('==')[0] for line in lines if '==' in line]
    except subprocess.CalledProcessError as e:
        # Print an error message if the 'pip list' command fails
        print(f"Error executing 'pip list' command: {e.output.decode('utf-8').strip()}")
        package_list = []
    except UnicodeDecodeError:
        # Print an error message if decoding the output fails
        print("Error decoding 'pip list' output. Please check the encoding settings.")
        package_list = []


def ep_get_package_exp(package_name:str, import_path=None):
    return package_name if import_path is None else import_path

def ep_is_installed(package_name:str, package_list:List[str]):
    """
    ep_is_installed("yors_comfyui_node_setup",package_list)

    ep_is_installed("yors_comfyui_node_setup==1.0.0",package_list)
    """
    # return package_name in package_list:
    pattern = re.compile(rf'^{package_name}(==.*)?$')
    is_installed = any(pattern.match(pkg) for pkg in package_list)
    return is_installed

def ep_intall_pkg(package_exp:str):
    # A
    subprocess.check_call([sys.executable, '-m', 'pip', '-q', 'install', package_exp])
    # B
    # s_param = '-s' if "python_embeded" in sys.executable else '' 
    # os.system(f'"{sys.executable}" {s_param} -m pip install {package_exp}')

    # A vs B

# feat(core): ensure_package - install some python package if not installed
def ensure_package(package_name, import_path=None):
    """
    ensure_package("qrcode")

    ensure_package("clipseg", "clipseg@git+https://github.com/timojl/clipseg.git@bbc86cfbb7e6a47fb6dae47ba01d3e1c2d6158b0")
    """
    global package_list
    package_exp = ep_get_package_exp(package_name,import_path)
    if package_list is None:
        update_package_list()
    pkg_is_installed = ep_is_installed(package_name,package_list)

    if not pkg_is_installed:
        print("(First Run) Installing missing package %s" % package_name)
        ep_intall_pkg(package_exp)
        # put pkg list since installing news
        update_package_list()

# feat(core): spio_install_requirements - install some python package in file location if not installed
def spio_install_requirements(file):
    """
    spio_install_requirements(Path(__file__).parent / "requirements.txt")

    spio_install_requirements(os.path.join(os.path.dirname(__file__),"requirements.txt"))
    """

    if not os.path.isfile(file):
        return  # do nothing if file doesn't exist

    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Extract package name (ignore version specifiers)
            package_name = re.split(r'[=<>~!\[\]]', line)[0].strip()
            if package_name:
                ensure_package(package_name)

# feat(core): node_install_requirements - install requirements in dir and file name
def node_install_requirements(location:str,name="requirements.txt"):
    """

    node_install_requirements(__file__,"requirements.txt"))
    """

    step_name="install requirements in dir and file name"
    info_step(step_name)
    # code based on custom_nodes/ComfyUI-Frame-Interpolation/install.py
    
    file = os.path.join(os.path.dirname(location),name)
    # info_status(f"get requirements.txt location",0)

    # pyio_install_requirements(file)
    spio_install_requirements(file)
    # info_status(f"spio install requirements",0)

# topic:node - set category alias
# feat(core): set_node_class_category_alias - set node category alias through extended class
def set_node_class_category_alias(base,this_py_module,category_alias:str,is_info_step=None):
  """
  import yors_comfyui_node_as_x_type as base

  from yors_comfyui_node_setup import get_sys_module,set_node_class_category_alias

  this_py_module = get_sys_module(__name__)

  set_node_class_category_alias(base,this_py_module,"YMC/as_x_type")
  """

  step_name="set node class category alias"
  info_step(step_name)
  
  base_classs = get_classes_in_module(base)
  count=len(base_classs)
#   info_status(f"get classes in module",0)

  if is_info_step:
     info_status(f"base node count: {count}",0)
     info_status(f"set base node category alias: {category_alias}",0)

  
  # this_py_module = get_sys_module(__name__)
  for cls in base_classs:
      #  cls.__class__.__name__ 
      extended_cls_name= cls.__name__ 
      new_class_name = "Cloned" + extended_cls_name
      # print(new_class_name)
      if is_info_step:
        info_status(f"class {new_class_name}({extended_cls_name})",0)

      extende_class=cls
      new_cls = type(new_class_name,(extende_class,),{'CATEGORY':category_alias})
      
      setattr(this_py_module,new_class_name,new_cls) # add it to this py module

    # class clsCloneed(cls):
    #   CATEGORY=CATEGORY_ALIAS
    #   pass
#   info_status(f"clone class and add it to this py module",0)


# [create dynamic class in python](https://blog.csdn.net/qdPython/article/details/121381363)

# feat(core): custom_nodes_get_path - get comfui/custom_nodes path
def custom_nodes_get_path(thisfile:str,relative:str='../../custom_nodes') -> str:
    """
    custom_nodes_path = custom_nodes_get_path(__file__,'../../custom_nodes')
    """
    # global folder_names_and_paths
    # folder_name = map_legacy(folder_name)
    # return folder_names_and_paths[folder_name][0][:]
    base_path = os.path.dirname(os.path.realpath(thisfile))
    return os.path.realpath(os.path.join(base_path, "custom_nodes"))


# feat(core): custom_nodes_add_to_sys - add comfui/custom_nodes to sys.path and return custom_nodes
def custom_nodes_add_to_sys(custom_nodes:list[str]=[]):
    """
    custom_nodes_add_to_sys([custom_nodes_get_path(__file__,'../../custom_nodes')])

    add comfui/custom_nodes/xx to sys.path
    """
    
    # custom_nodes = folder_paths.get_folder_paths("custom_nodes")
    for dir in custom_nodes:
        if dir not in sys.path:
            print("Adding", dir, "to sys.path")
            sys.path.append(dir)
    return custom_nodes

# feat(core): read_module_class_name - read name in sys.modules if name including name
def read_module_class_name(name):
    YMC_CLASSS_NAME=[]
    # print(f"[info] read name in sys.modules if name including {name} (loaded)")
    for key,value in sys.modules.items():
        # print(key)
        if name in key :
            # """do nothing"""
            # print(key)
            YMC_CLASSS_NAME.append(key)
    return YMC_CLASSS_NAME

# feat(core): read_module_valid_node_class - read class name if key in sys.modules including name
def read_module_valid_node_class(name):
    # print(f"[info] read class name if key in sys.modules including {__name__}")
    # docs(core): print class name if key in sys.modules including this module name
    ValidNodeClassList=[]
    ALL_CLASS_NAMES=[]
    for key,value in sys.modules.items():
        if name in key :
            # print(key)
            # docs(core): get all classes in name module
            module = sys.modules[key]
            all_classes = get_classes_in_module(module)
            for cls in all_classes:
                # dup class name
                if cls.__name__ not in ALL_CLASS_NAMES:
                    ALL_CLASS_NAMES.append(cls.__name__)
                    # print(cls.__name__)
                    # if hasattr(cls,"NODE_DESC"):
                    if is_yors_style_node(cls):
                        ValidNodeClassList.append(cls)
                # print name of them
                # print(cls.__name__)

                # collect class that match ymc style - has attr NODE_DESC in class
                # if hasattr(cls,"NODE_DESC"):
                #     if cls not in ValidNodeClassList:
                #         ValidNodeClassList.append(cls)
    return ValidNodeClassList,ALL_CLASS_NAMES

