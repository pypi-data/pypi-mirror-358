from setuptools import find_packages, setup
import os
from glob import glob

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 获取所有二进制文件路径
def get_bin_files():
    bin_files = []
    # 遍历kms_activator/bin目录下的所有文件
    for root, _, files in os.walk("htyy/kms_activator/bin"):
        for file in files:
            bin_files.append(os.path.relpath(os.path.join(root, file), "htyy"))
    return bin_files

# 获取所有其他资源文件（如配置文件）
def get_resource_files():
    resource_files = []
    # 添加配置文件
    resource_files.append("kms_activator/config.json")
    
    # 添加其他资源文件（如果有）
    # resource_files.extend(glob("kms_activator/resources/*"))
    
    return resource_files

setup(
    name='htyy',
    version='0.1.5',  # 更新版本号
    description='htyy - All-in-one productivity tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='huang yi yi',
    author_email='363766687@qq.com',
    packages=find_packages(),
    package_dir={'htyy': 'htyy'},
    package_data={
        "htyy": [
            "*.pyd", 
            "*.pyi",
            # 包含KMS模块的所有二进制文件和资源
            "kms_activator/bin/**/*", 
            "kms_activator/bin/**/**/*",
            "kms_activator/config.json"
        ],
    },
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        "watchdog",
        "paramiko",
        "pycryptodome",
        "pywin32",
        "rich",
        "plyer",
        "mpmath",
        "miniaudio",
        "argostranslate",
        "googletrans",
        "pyautogui",
        "py7zr",
        "cryptography",
        # 添加KMS模块的依赖
        "requests>=2.25.1",
        "tqdm>=4.60.0",
        "colorama>=0.4.4",
    ],
    entry_points={
        'console_scripts': [
            # KMS激活器命令行工具
            'htyy-kms = htyy.kms_activator.cli:main',
            'kms-activator = htyy.kms_activator.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    project_urls={
        "Source": "https://github.com/hyy-PROG/htyy",
    },
)