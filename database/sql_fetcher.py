import os
from functools import cache


@cache
def fetch(*paths: str):
    """
    Fetches the SQL code in the file `file_name` located in the given directory.

    :param *paths: Path components, as would be passed to os.path.join(). Relative to `sql_folder` passed to the constructor.
    """
    path = os.path.join(".", *paths)
    return open(path, "r").read()


for path in [
    os.path.join(directory, file_name)
    for directory, _, file_names in os.walk(".")
    for file_name in file_names
    if file_name[-4:] == ".sql"
]:
    fetch(path)  # load all sql files on initialisation
