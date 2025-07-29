from setuptools import setup, find_packages
from setuptools import setup, Extension
import io
from os import path

this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, "readme.md"), encoding="utf-8") as f:
    long_description = f.read()


version_file = "namo/version.py"


def get_version():
    with open(version_file, "r") as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


setup(
    name="namo",
    version=get_version(),
    keywords=["deep learning", "LLM", "VLM", "namo multi-modal training", "framework"],
    description="namo is a nano level multi-modal training framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPL-3.0",
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(include=["namo", "namo.*"]),
    entry_points={"console_scripts": ["namo = namo.cli:main"]},
    include_package_data=True,
    exclude_package_data={
        "namo": ["dataset_qwenvl.py", "dataset.py", "trainer_mdpo.py", "trainer.py"],
    },
    author="lucasjin",
    author_email="aa@qq.com",
    url="https://ccc.cc/a",
    platforms="any",
    install_requires=[
        "timm",
        "pydub",
        "coreai-all",
        "termcolor",
        "loguru",
        "peft",
        "python-datauri",
        "pydantic",
        "uvicorn",
        "fastapi",
        "shortuuid",
        "openai",
    ],
)
