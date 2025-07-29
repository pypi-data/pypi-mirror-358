import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

class get_pybind_include:
    def __str__(self):
        import pybind11
        return pybind11.get_include()

# Use C++20
if sys.platform == "darwin":
    cpp_args  = ["-std=c++20", "-stdlib=libc++", "-mmacosx-version-min=10.9"]
    link_args = ["-stdlib=libc++", "-mmacosx-version-min=10.9"]
else:
    cpp_args  = ["-std=c++20"]
    link_args = []

ext_modules = [
    Extension(
        name="pypearl",
        sources=["src/pybinding/binding.cpp"],
        include_dirs=[get_pybind_include()],
        language="c++",
        extra_compile_args=cpp_args,
        extra_link_args=link_args,
    ),
]

setup(
    name="pypearl",
    version="0.3.1",
    author="Brody Massad",
    author_email="brodymassad@gmail.com",
    description="C++ bindings for pypearl",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)
