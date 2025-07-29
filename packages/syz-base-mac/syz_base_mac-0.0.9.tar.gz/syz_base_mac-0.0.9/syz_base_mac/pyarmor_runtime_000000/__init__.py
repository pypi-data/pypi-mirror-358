"""PyArmor Runtime"""
import os
import sys

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将 pyarmor_runtime.so 所在目录添加到 sys.path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from .pyarmor_runtime import __pyarmor__
