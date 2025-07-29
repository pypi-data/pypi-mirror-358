import sys
from setuptools import setup, find_packages

name = "syz-base"

# 根据平台确定包名后缀
if sys.platform.startswith('win'):
    platform_suffix = 'win'
elif sys.platform.startswith('darwin'):
    platform_suffix = 'mac'
else:
    platform_suffix = ''

package_name = f"{name}-{platform_suffix}"
module_name = "syz_base_" + platform_suffix

setup(
    name=package_name,  # pip包名：syz-base-mac
    version="0.0.4",  # 更新版本号
    packages=find_packages(),  # 自动发现包
    python_requires=">=3.6",
    install_requires=[
        "PyQt6>=6.0.0",
    ],
    entry_points={
        'console_scripts': [
            f'{package_name}={module_name}.main:main',
        ],
    },
)