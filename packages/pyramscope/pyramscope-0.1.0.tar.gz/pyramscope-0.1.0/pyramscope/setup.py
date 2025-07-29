from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "_pyramscope",
        ["pyramscope/core.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=["-std=c++17"],
    ),
]
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
   
 
setup(
    name="pyramscope",
    version="0.1.0",
    packages=["pyramscope"],
    ext_modules=ext_modules,
    author="Juan Jara",
    author_email="juanignaciojara505@gmail.com",
    description="Small Python library to inspect Python objects using C++",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    ext_modules=ext_modules,
    python_requires=">=3.7",
    zip_safe=False,
)
