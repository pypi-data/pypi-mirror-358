""" python depedencies for this project """
from typing import List, Dict


scripts: Dict[str, str] = {
    "pytsv": "pytsv.main:main",
}
dev_requires: List[str] = [
]
config_requires: List[str] = [
    "pyclassifiers",
]
install_requires: List[str] = [
    "pytconf",
    "tqdm",
    "pyanyzip",
    "numpy",
    "pandas",
    "pylogconf",
    "attrs",
]
build_requires: List[str] = [
    "hatch",
    "pymakehelper",
    "pydmt",
    "pandas-stubs",
    "types-tqdm",
    "ruff",
]
test_requires: List[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "mypy",
]
requires = config_requires + install_requires + build_requires + test_requires
