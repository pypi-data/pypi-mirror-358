import sys
from setuptools import setup, find_packages

name = "syz-base"

# 根据平台确定包名后缀
if sys.platform.startswith('win'):
    platform_suffix = '-win'
elif sys.platform.startswith('darwin'):
    platform_suffix = '-mac'
else:
    platform_suffix = ''

setup(
    name=f"{name}{platform_suffix}",
    version="0.0.1",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "PyQt6>=6.0.0",
    ],
    entry_points={
        'console_scripts': [
            f'{name}=src.main:main',
        ],
    },
)