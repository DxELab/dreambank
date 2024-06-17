"""
dreambank functions
"""
import pandas as pd
import pooch


__all__ = ["fetch"]

version = "0.1"

# pup = pooch.create(
#     path=pooch.os_cache("dreambank"),
#     base_url="https://github.com/remrama/dreambank/raw/{version}/data/",
#     version=version,
#     version_dev="main",
# )
# pup.load_registry(registry_path)


def fetch(dataset_id):
    """
    """
    fp = pup.fetch(dataset_id)
    dreams = pd.read_csv(fp)
    return dreams
