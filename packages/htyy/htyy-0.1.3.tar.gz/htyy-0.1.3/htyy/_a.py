import sys
import sysconfig
import argparse
import platform
from distutils.core import setup
from distutils.extension import Extension
from distutils.command.build_ext import build_ext

def compile_c_to_pyd(
    c_files,
    module_name,
    output_dir="dist",
    libraries=None,
    include_dirs=None,
    extra_compile_args=None,
    extra_link_args=None,
    optimize_level=2
):
    """
    Encapsulates the complete distutils compilation process
    :param c_files: C Source File List (required)
    :param module_name: Generated module name (required)
    :param output_dir: output directory (default "dist")
    :param Libraries: A list of libraries that need to be linked (e.g. ["m"])
    :param include_dirs: Header file search path (Python header files are automatically included by default)
    :param extra_compile_args: Additional compilation parameters (e.g. ["-Wall"])
    :param extra_link_args: Additional link parameters (e.g. ["-L/usr/lib"])
    :param optimize_level: Optimization level 0-3 (default 2)
    """
    # 自动获取 Python 头文件路径
    python_include = sysconfig.get_path("include")
    if not include_dirs:
        include_dirs = [python_include]
    else:
        include_dirs = include_dirs + [python_include]

    # 根据优化级别添加编译参数
    default_compile_args = _get_optimization_args(optimize_level)
    if extra_compile_args:
        default_compile_args += extra_compile_args

    # 定义 Extension 对象
    ext = Extension(
        name=module_name,
        sources=c_files,
        include_dirs=include_dirs,
        libraries=libraries or [],
        extra_compile_args=default_compile_args,
        extra_link_args=extra_link_args or [],
    )

    # 自定义构建类：修改输出目录
    class CustomBuild(build_ext):
        def initialize_options(self):
            super().initialize_options()
            self.build_lib = output_dir  # 指定输出目录
            self.inplace = False          # 禁用原地构建

    # 调用 setup 函数
    setup(
        name=module_name + "_pkg",
        version="0.1",
        ext_modules=[ext],
        script_args=["build_ext"],       # 仅执行 build_ext 命令
        cmdclass={"build_ext": CustomBuild},
    )

def _get_optimization_args(level: int) -> list:
    """根据优化级别返回平台相关的编译参数"""
    system = platform.system()
    args = []

    if system == "Windows":
        # MSVC 编译器参数
        if level >= 1:
            args.append("/O2")  # Windows 下最高优化级别为 /O2
    else:
        # GCC/Clang 编译器参数
        if level >= 3:
            args.append("-O3")
        elif level >= 2:
            args.append("-O2")
        elif level >= 1:
            args.append("-O1")
        else:
            args.append("-O0")

    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="C extension build tool based on distutils.")
    parser.add_argument("c_files", nargs="+", help="C List of source files")
    parser.add_argument("-o", "--output", required=True, help="Output module name")
    parser.add_argument("-d", "--dir", default="dist", help="Output directory")
    parser.add_argument("-O", "--optimize", type=int, choices=range(0,4), default=2,
                       help="Optimization level 0-3 (default 2)")
    parser.add_argument("-l", "--libs", nargs="+", help="Linked libraries (e.g. -l m math)")
    parser.add_argument("-I", "--includes", nargs="+", help="Header file search path")
    parser.add_argument("-c", "--compile-args", nargs="+", help="Additional compilation parameters (e.g. -c -Wall)")
    parser.add_argument("-L", "--link-args", nargs="+", help="Additional link parameters (e.g. -L -Wl)")

    args = parser.parse_args()

    # 调用封装函数
    compile_c_to_pyd(
        c_files=args.c_files,
        module_name=args.output,
        output_dir=args.dir,
        libraries=args.libs,
        include_dirs=args.includes,
        extra_compile_args=args.compile_args,
        extra_link_args=args.link_args,
        optimize_level=args.optimize
    )