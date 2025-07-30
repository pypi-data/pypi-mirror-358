import sys
from setuptools import setup
from Cython.Build import cythonize
from distutils.extension import Extension
import shutil
import platform
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.plat_name = "manylinux_x86_64"  # 指定平台标签


# 获取系统架构
arch = platform.machine()


# 根据平台设置库文件路径和名称
if sys.platform == "win32":
    # 源文件路径
    src_file = "lib/win/hs.dll"
    # 目标目录路径
    dst_dir = "pyhyperscan"
    # 复制文件
    shutil.copy(src_file, dst_dir)
    src_file = "lib/win/hs.lib"
    dst_dir = "pyhyperscan"
    shutil.copy(src_file, dst_dir)

    libraries = ["hs"]
    extra_link_args = []
    package_data = {"pyhyperscan": ["hs.dll"]}
    plat_name = 'win_amd64'
elif sys.platform == "linux":
    if arch in ("x86_64", "i386", "i686"):
        print("This is an x86 architecture.")
        # 源文件路径
        src_file = "lib/linux/x64/libhs.so.5"
        # 目标目录路径
        dst_dir = "pyhyperscan"
        # 复制文件
        shutil.copy(src_file, dst_dir)
        dst_dir = "pyhyperscan/libhs.so"
        shutil.copy(src_file, dst_dir)
        plat_name = 'manylinux2014_x86_64'
    elif arch in ("aarch64", "armv7l", "armv8l"):
        raise RuntimeError(f"Unsupported platform: {arch}")

    libraries = ["hs"]
    extra_link_args = ["-Wl,-rpath,$ORIGIN"]
    package_data = {"pyhyperscan": ["libhs.so.5"]}
elif sys.platform == "darwin":
    libraries = ["hs"]
    extra_link_args = ["-Llib"]
    package_data = {"pyhyperscan": ["libhs.dylib"]}
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

# 定义扩展模块
ext_modules = [
    Extension(
        "pyhyperscan.pyhyperscan",  # 模块名称
        sources=["pyhyperscan/pyhyperscan.pyx"],  # Cython 源文件
        include_dirs=["include"],  # 头文件路径
        library_dirs=["pyhyperscan"],  # 库文件路径
        libraries=libraries,  # 库名称
        extra_link_args=extra_link_args,  # 额外的链接参数
    )
]

setup(
    name="pyhyperscan",
    version="0.1.8",
    options={
        "bdist_wheel": {
            "plat_name": plat_name,  # 指定平台标签
        },
    },
    author="fgc",
    author_email="13654918696@163.com",
    description="A Python wrapper for Hyperscan",
    long_description=open("README.md", encoding='utf8').read(),
    long_description_content_type="text/markdown",
    url="https://gitee.com/fgc1/regex_engine_py.git",
    packages=["pyhyperscan"],
    ext_modules=cythonize(ext_modules),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Cython>=0.29.0",
    ],
    package_data=package_data,  # 包含动态库
)
