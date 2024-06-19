"""
dreambank functions
"""
import json
import pandas as pd
import pooch

from importlib.metadata import version as installed_version
from importlib.resources import files

__all__ = [
    "available_datasets",
    "fetch",
    "read_dreams",
    "read_info",
]


repository = pooch.create(
    base_url="https://github.com/dxelab/dreambank/raw/{version}/data/",
    path=pooch.os_cache("dreambank"),
    version=f"v{installed_version("dreambank")}",
    version_dev="dev",
)
repository.load_registry(files("dreambank.data").joinpath("registry.txt"))



def available_datasets():
    """Return a list of all unique dataset IDs available in `dreambank`.

    Returns
    -------
    dataset_ids : list
        A sorted list of strings, each a unique dataset ID.

    Examples
    --------
    >>> import dreambank
    >>> dataset_ids = dreambank.available_datasets()
    >>> print(dataset_ids[:5])
    ['alta', 'angie', 'arlie', 'b', 'b-baseline']
    >>> print(dataset_ids[-5:])
    ['vonuslar', 'wedding', 'west_coast_teens', 'zurich-f', 'zurich-m']
    """
    return sorted(set(fn.split(".")[0] for fn in repository.registry_files))


def fetch(fname):
    """Fetch a single `dreambank` file and return the filepath.

    The main use case of this would be if a user wants to read the file with custom code.

    Parameters
    ----------
    fname : str
        Dataset ID and extension (e.g., ``'alta.tsv'``, ``'alta.json'``).

    Returns
    -------
    fp : str
        Full filepath of local file.

    Examples
    --------
    >>> import dreambank
    >>> import pandas as pd
    >>>
    >>> fp = dreambank.fetch("bosnak.tsv")
    >>> bosnak = pd.read_table(fp, index_col="n")
    """
    fp = repository.fetch(fname)
    return fp

def read_dreams(dataset_id):
    """Return a :class:`pandas.DataFrame` of dreams.

    Parameters
    ----------
    dataset_id : str
        The dataset to read in.

    Returns
    -------
    dreams : :class:`pandas.DataFrame`
        A :class:`~pandas.DataFrame` with 2 or 3 columns.

    Examples
    --------
    >>> import dreambank
    >>> dreams = dreambank.read_dreams("izzy22_25")
    >>> dreams.head(3)
    """
    fp = fetch(f"{dataset_id}.tsv")
    dreams = pd.read_table(fp, dtype="string")
    return dreams

def read_info(dataset_id):
    """Read info (i.e., metadata) for a given dataset.

    Parameters
    ----------
    dataset_id : str
        The dataset to read in.

    Returns
    -------
    info : dict
        A dictionary with metadata for the given dataset.
    
        * ``short_name``: dataset_id
        * ``long_name``: long_name
        * ``n_dreams``: n_dreams
        * ``timeframe``: timeframe
        * ``sex``: sex
        * ``description``: description

    Examples
    --------
    >>> import dreambank
    >>> info = dreambank.read_info("izzy22_25")
    >>> info
    """
    fp = fetch(f"{dataset_id}.json")
    with open(fp, "rt", encoding="utf-8") as f:
        info = json.load(f)
    return info
