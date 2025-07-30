# def demo():
#     print("[zero] hello, zero!i am demo")
# def pcli():
#     print("[zero] hello, zero!i am pcli")
#     print("[zero] this file",__file__)
#     demo()
# if __name__  == "__main__":
#     # print("[zero] hello, zero!i am name")
#     pcli()

# v0: from .main import entry, node_install_requirements
# from .main import entry, node_install_requirements

# v1: only from .main import *
from .main import *

# v2 from .main import * + __all__
# from .main import *

# add next to:
# 1. only the names listed in __all__ will be imported
# 2. the linter will not raise the F403 error
# __all__ = ['entry', 'node_install_requirements'] 