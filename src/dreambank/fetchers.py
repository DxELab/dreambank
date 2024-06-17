"""
dreambank functions
"""
import json
import pandas as pd
import pooch

from importlib.metadata import version as importlib_version
from importlib.resources import files


__all__ = [
    "available_datasets",
    "fetch",
    "read_dreams",
    "read_info",
]




old_registry_hashes = {
    "v0": "sha256:fe0d7f655f1363dc2cc7f2e5eac3dbe7e7b299446aafe19c872f737e90454a5a",
}

def get_registry_filepath(version_str):
    current_version_str = "v" + importlib_version("dreambank")
    if version_str == current_version_str:
        fp = files("dreambank.data").joinpath("registry.txt")
    else:
        url = f"https://github.com/dxelab/dreambank/raw/{version_str}/src/dreambank/data/registry.txt"
        known_hash = old_registry_hashes[version_str]
        fp = pooch.retrieve(url, known_hash=known_hash)
    return fp

def create_pup(version):
    # Offers version control.
    version_str = f"v{version}"
    pup = pooch.create(
        path=pooch.os_cache("dreambank"),
        base_url="https://github.com/dxelab/dreambank/raw/{version}/data/",
        version=version_str,
        version_dev="main",
    )
    registry_filepath = get_registry_filepath(version_str)
    pup.load_registry(registry_filepath)
    return pup


def available_datasets(version=1):
    return sorted(set(x.split(".")[0] for x in create_pup(version).registry_files))

def fetch(fname, version=1):
    """
    If you just want filepath to load manually
    """
    fp = create_pup(version).fetch(fname)
    return fp

def read_dreams(dataset_id, version=1):
    fp = create_pup(version).fetch(f"{dataset_id}.tsv")
    return pd.read_table(fp)

def read_info(fname, version=1):
    fp = create_pup(version).fetch(f"{dataset_id}.json")
    with open(fp, "rt", encoding="utf-8") as f:
        data = json.load(f)
    return data
