# importlib.resources.files introduced in python 3.9
from importlib.resources import files as pkgfiles  # noqa: F401
from pathlib import Path
from types import ModuleType


def data_location_as_path(package: ModuleType, sub_path) -> Path:
    """
    Convert a package and subpath to a Path object.

    Parameters
    ----------
    package : ModuleType
        The package containing the data.
    sub_path : str
        The subpath within the package.

    Returns
    -------
    Path
        A Path object representing the location of the subpath within the package.
    """
    # joinpath() returns a Traversable
    # to turn it into Path we first turn it into a string
    if not isinstance(sub_path, str):
        sub_path = str(sub_path)  # pragma: no coverage
    _data_path = pkgfiles(package).joinpath(sub_path)
    _data_path_str = str(_data_path)
    data_path = Path(_data_path_str)
    return data_path
