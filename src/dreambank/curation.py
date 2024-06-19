"""
Dataset
Functions that were used during setup and are not necessary for casual usage.
"""
import json
import re
from importlib.resources import files
from pathlib import Path

import pandas as pd
import pooch
from bs4 import BeautifulSoup


__all__ = [
    "load_source_repository",
    "get_all_dataset_ids",
    "fetch_grid_file",
    "fetch_source_file",
    "read_source_dreams_as_df",
    "read_source_info_as_dict",
    "write_source_registry",
    "write_curated_registry",
    "write_dreams_df_to_csv",
    "write_info_dict_to_json",
]


# Identify the cached directory for temporary storage of retrieved files.
# Place all retrieved files in a dreambank Cache folder.
# Create a dreambank cache directory to save all retrieved files.
# These files do not need permanence, as they are fetched from Pooch as needed.
# All pooch downloads go here.
_cache_dir = pooch.os_cache("dreambank")

# Identify the more permanent GitHub data directory that will be used to store
# permanent files like the tabular data files and registry.
# Write all tabular/tsv files within the local repository folder.
_repo_dir = files("dreambank").parents[1]  # for curated registry file
_data_dir = _repo_dir.joinpath("datasets")  # for curated TSV/JSON files
_source_registry_filepath = _repo_dir.joinpath("registry-source.txt")
_curated_registry_filepath = _repo_dir.joinpath("registry.txt")


def load_source_repository():
    """Load a Pooch repository for the HTML files.

    Returns
    -------
    pup : `pooch.Pooch`
        Pooch repository with all available HTML files in the registry.

    Raises
    ------
    `OSError` if the registry file has not been created yet.
    """
    # This pup fetches the raw HTML files, NOT the tabular data that is for main use.
    if not _source_registry_filepath.exists():
        raise OSError("HTML registry not found.")
    pup = pooch.create(path=_cache_dir, base_url="")
    pup.load_registry(_source_registry_filepath)
    return pup


def fetch_grid_file():
    """
    Download the DreamBank grid file (if not already downloaded)
    and return the filepath.

    The grid file is a DreamBank page that includes a table of all the
    datasets available in DreamBank. This file is used to create a registry,
    ensuring that all available datasets are included. It also provides easy
    access to all the dataset IDs, which are used for subsequent web scraping.

    Returns
    -------
    fp : str
        Full filepath of the local HTML grid file.
    """
    grid_url = "https://dreambank.net/grid.cgi"
    grid_hash = "sha256:f31487774cce789fe9bcbe3c7c680be52fbdd8380afb391aee5fa1fe11e68660"
    fp = pooch.retrieve(grid_url, path=_cache_dir, known_hash=grid_hash)
    return fp


def get_all_dataset_ids():
    """Return a list of all available datasets.

    Parses the HTML grid file to return a list of all available DreamBank
    datasets.

    .. seealso:: :func:`~dreambank.curation.fetch_grid_file`

    Returns
    -------
    datasets : list of str
        List of all available datasets in DreamBank.
    """
    fp = fetch_grid_file()
    with open(fp, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    datasets = sorted(x.get("value") for x in soup.find_all("input", type="checkbox"))
    assert len(datasets) == len(set(datasets)), "Unexpected duplicate values found in `datasets`"
    return datasets


def write_source_registry(overwrite=False):
    """Write registry txt file for HTML dreambank files.

    Extracts all available dataset IDs from the DreamBank grid page
    and creates a Pooch registry file with three space-separated columns:

    1. ``fname`` - The filename used to access and store the file using Pooch.
    2. ``hash`` - The sha256 hash/checksum used to verify file consistency.
    3. ``url`` - The unique URL used to download each dataset HTML file.

    There are 3 rows/files per DreamBank dataset:

    1. ``dreams.html`` - HTML file for dream reports from the specified dataset.
    2. ``info.html`` - HTML file for general info about the specified dataset.
    3. ``moreinfo.html`` - HTML file for extra info about the specified dataset.

    Parameters
    ----------
    overwrite : bool
        If ``False`` (default), raise `OSError` if registry file exists.
        If ``True``, overwrite registry file if present.

    Raises
    ------
    `OSError` if registry file already exists and `overwrite` is ``False``.
    """
    from tqdm import tqdm
    if _source_registry_filepath.exists() and not overwrite:
        raise OSError("Registry file already exists.")
    with open(_source_registry_filepath, "wt", encoding="utf-8", newline="\n") as f:
        for d in (pbar := tqdm(get_all_dataset_ids())):
            pbar.set_description(f"Creating source repository for {d}")
            fnames_and_urls = {
                f"{d}/dreams.html": f"https://dreambank.net/random_sample.cgi?series={d}",
                f"{d}/info.html": f"https://dreambank.net/more_info.cgi?series={d}",
                f"{d}/moreinfo.html": f"https://dreambank.net/more_info.cgi?series={d}&further=1",
            }
            for fn, url in fnames_and_urls.items():
                fp = pooch.retrieve(url=url, fname=fn, path=_cache_dir, known_hash=None)
                file_hash = pooch.file_hash(fp)
                f.write(f"{fn} sha256:{file_hash} {url}\n")


def write_curated_registry(overwrite=False):
    """Write registry txt file for the curated TSV dreambank files.

    Don't need unique URLs for this one, as they will all come from GitHub
    with standard URL formatting thing that Pooch can take advantage of.

    Parameters
    ----------
    overwrite : bool
        If ``False`` (default), raise `OSError` if registry file exists.
        If ``True``, overwrite registry file if present.

    Raises
    ------
    `OSError` if registry file already exists and `overwrite` is ``False``.
    """
    if _curated_registry_filepath.exists() and not overwrite:
        raise OSError("Curated registry file already exists.")
    with open(_curated_registry_filepath, "wt", encoding="utf-8", newline="\n") as f:
        for d in get_all_dataset_ids():
            for suffix in [".tsv", ".json"]:
                fp = _data_dir.joinpath(d).with_suffix(suffix)
                fname = fp.name
                hash_alg = "sha256"
                known_hash = pooch.file_hash(fp, alg=hash_alg)
                row_string = f"{fname} {hash_alg}:{known_hash}\n"
                f.write(row_string)


def fetch_source_file(dataset, component, **kwargs):
    """Download (if not already downloaded) a single HTML DreamBank file.

    Parameters
    ----------
    dataset : str
        Name of DreamBank dataset.
    component : str
        Dataset component to fetch.
        Available options are ``'dreams'``, ``'info'``, ``'moreinfo'``.
    **kwargs
        Optional passed to :meth:`pooch.Pooch.fetch`

    Returns
    -------
    fp : str
        Full filepath of the local HTML file.
    """
    available_components = {"dreams", "info", "moreinfo"}
    assert component in available_components, f"`component` must be one of {available_components}"
    pup = load_source_repository()
    fp = pup.fetch(f"{dataset}/{component}.html", **kwargs)
    return fp


def read_source_dreams_as_df(dataset_id):
    """
    Parse DreamBank HTML dreams page for a given dataset into a :class:`~pandas.DataFrame`.

    Parameters
    ----------
    dataset_id : str
        DreamBank dataset to load. Must be one of the available DreamBank datasets.

    Returns
    -------
    dreams : :class:`pandas.DataFrame`
        A :class:`~pandas.DataFrame` with 3 columns.

        * ``n`` - The dream number in the sequence, of type ``str``.
            String because sometimes there is 111a (e.g., Alta)
        * ``dream`` - The dream text, of type ``str``.
        * ``date`` - If present, the provided date of the dream, of type ``str``.
    """
    fp = fetch_source_file(dataset_id, "dreams")
    with open(fp, "rb") as f:
        soup = BeautifulSoup(f, "html.parser", from_encoding="ISO-8859-1")
    # Find all spans that do not have "comment" class labels.
    # Comments will already be present in the regular spans/dreams as bracketed content.
    data = []
    for span in soup.find_all("span", style=False, class_=lambda x: x != "comment"):
        span_text = span.get_text(separator=" ", strip=True)
        # Extract the dream number (and potentially date) from beginning of string
        match_ = re.match(r"^#(\S+) ((\(\S*\)) )?", span_text)
        assert match_ is not None, f"Did not find dream number match for dataset {dataset_id}, dream {dream_n}."
        dream_n = match_.group(1)  # The number of dream in the whole sequence
        dream_date = match_.group(3)  # will be None if not found
        # Remove the dream number (and potentially date) from the beginning of string
        dream_and_wc_text = re.sub(r"^#([0-9]+) ((\(\S*\)) )?", "", span_text)
        # Remove the word count from end of string
        n_wc_matches = len(re.findall(r"[ \n]?\([0-9]+ words\)$", dream_and_wc_text))
        assert n_wc_matches == 1, f"Found {n_wc_matches} WC match for dataset {dataset_id}, dream {dream_n} (expected 1)."
        dream_text = re.sub(r"[ \n]?\([0-9]+ words\)$", "", dream_and_wc_text)
        assert dream_n not in data, "Unexpected duplicate dream number"
        data.append(dict(n=dream_n, date=dream_date, dream=dream_text))
    # Make sure the correct number of dreams were extracted.
    # At the top of each page, DreamBank will say how many dreams are present in the
    # total dataset, as well as how many are displayed on the page. These, and the total
    # amount of dreams extracted, should all be the same.
    n_dreams_statement = soup.find("h4").find_next().get_text()
    n_dreams_total, n_dreams_displayed = re.findall(r"[0-9]+", n_dreams_statement)
    n_dreams_extracted = len(data)
    assert int(n_dreams_total) == int(n_dreams_displayed) == n_dreams_extracted
    dreams = pd.DataFrame(data).replace(dict(date={None: pd.NA})).astype(dict(n="string", date="string", dream="string")).dropna(how="all", axis=1).sort_index(axis=0)
    return dreams


def read_source_info_as_dict(dataset_id):
    """
    Parse DreamBank HTML info page for a given dataset into a dictionary.

    Parameters
    ----------
    dataset_id : str
        DreamBank info to load. Must be one of the available DreamBank datasets.

    Returns
    -------
    info : `dict`
        A `dict` with 3 with 3 columns.

        * ``short_name`` (`str`) - The dataset ID.
        * ``long_name`` (`str`) - The dataset title. A longer form of dataset ID.
        * ``n_dreams`` (`int`) - The total number of dreams in the dataset.
        * ``timeframe`` (`str`) - Provided year or timeframe of the dataset.
        * ``sex`` (`str`) - The provided sex of the dreamer.
        * ``description`` (`str`) - A long-form description of the dataset.
    """
    fp = fetch_source_file(dataset_id, "info")
    with open(fp, "rb") as f:
        soup = BeautifulSoup(f, "html.parser", from_encoding="ISO-8859-1")
    body = soup.find("body")
    long_name = body.find(string="Dream series:").next.get_text(strip=True)
    n_dreams = body.find(string="Number of dreams:").next.get_text(strip=True)
    timeframe = body.find(string="Year:").next.get_text(strip=True)
    sex = body.find(string="Sex of the dreamer(s):").next.get_text(strip=True)
    match_ = re.match(
        rf".*Sex of the dreamer\(s\): {sex}\n\n\n?(.*?)\s+(For the further analyses, click here.\n)?\[Back to search form\]\s+$",
        body.get_text(),
        flags=re.DOTALL
    )
    assert match_ is not None, f"Error parsing info description for dataset {dataset_id}."
    description = match_.group(1)
    info = {
        "short_name": dataset_id,
        "long_name": long_name,
        "n_dreams": n_dreams,
        "timeframe": timeframe,
        "sex": sex,
        "description": description,
    }
    return info


def write_dreams_df_to_csv(dataset_id, overwrite=False):
    """
    Parse an HTML DreamBank dataset of dream reports and write to a local tabular
    data file for the GitHub repository.

    .. seealso:: :func:`~dreambank.curation.read_source_dreams_as_df`

    Parameters
    ----------
    dataset_id : str
        DreamBank dataset to load. Must be one of the available DreamBank datasets.
    overwrite : bool
        If ``False`` (default), raise `OSError` if file already exists.
        If ``True``, overwrite file if already exists.

    Raises
    ------
    `OSError` if file already exists and `overwrite` is ``False``.
    """
    fp = _data_dir.joinpath(dataset_id).with_suffix(".tsv")
    if fp.exists() and not overwrite:
        raise OSError("File already exists. Set `overwrite` as True or delete local file.")
    dreams = read_source_dreams_as_df(dataset_id)
    # https://pandas.pydata.org/docs/user_guide/io.html#quoting-compression-and-file-format
    dreams.to_csv(
        path_or_buf=fp,
        sep="\t",
        na_rep="n/a",
        index=False,
        encoding="utf-8",
        quoting=2,  # 2 = csv.QUOTE_NONNUMERIC
        quotechar='"',
        lineterminator="\n",
        doublequote=True,
        escapechar=None,
    )

def write_info_dict_to_json(dataset_id, overwrite=False):
    """
    Parse an HTML DreamBank dataset of dream reports and write to a local tabular
    data file for the GitHub repository.

    .. seealso:: :func:`~dreambank.curation.read_source_dreams_as_df`

    Parameters
    ----------
    dataset_id : str
        DreamBank dataset to load. Must be one of the available DreamBank datasets.
    overwrite : bool
        If ``False`` (default), raise `OSError` if file already exists.
        If ``True``, overwrite file if already exists.

    Raises
    ------
    `OSError` if file already exists and `overwrite` is ``False``.
    """
    fp = _data_dir.joinpath(dataset_id).with_suffix(".json")
    if fp.exists() and not overwrite:
        raise OSError("File already exists. Set `overwrite` as True or delete local file.")
    info = read_source_info_as_dict(dataset_id)
    with open(fp, "wt", encoding="utf-8", newline="\n") as fp:
        json.dump(info, fp, indent=4, sort_keys=False, ensure_ascii=False)


def curate():
    import argparse
    from tqdm import tqdm
    parser = argparse.ArgumentParser(
        prog="dreambank",
        description="Convert the DreamBank dataset to tabular and version-controlled format.",
        epilog="For more info, see https://github.com/remrama/dreambank",
    )
    parser.add_argument("steps", nargs="+", default=[],
        choices=[
            "source",
            "tsv",
            "source_pkg",
        ])
    # parser.add_argument('-c', '--count')      # option that takes a value
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite registry files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Keeps Pooch's default logging value of INFO (instad of WARNING)")
    args = parser.parse_args()
    if not args.verbose:
        pooch_logger = pooch.get_logger()
        pooch_logger.setLevel("WARNING")
    # Download all available DreamBank files, regardless of prior downloads.
    # Determine new file hashes irrespective of prior downloads and hashes.
    if "source" in args.steps:
        write_source_registry(overwrite=args.overwrite)
    if "tsv" in args.steps:
        # Loop over all available datasets.
        for d in (pbar := tqdm(get_all_dataset_ids())):
            pbar.set_description(f"Creating tsv repository for {d}")
            # For each available dataset, convert dreams (data) and info (metadata)
            # from the source (html) to curated (tabular/tsv) format.
            # dreams = read_source_dreams_as_df(d)
            # info = read_source_info_as_dict(d)
            # Write the new/curated format to the local GitHub repository.
            write_dreams_df_to_csv(d, overwrite=args.overwrite)
            write_info_dict_to_json(d, overwrite=args.overwrite)
        # Write a new registry file for the curated/GitHub repository.
        # This is the one to be used from Python dreambank interface.
        write_curated_registry(overwrite=args.overwrite)
    if "package_source_files" in args.steps:
        make_html_binaries()

