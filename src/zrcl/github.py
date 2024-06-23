from datetime import datetime
import io
import re
import typing
import requests
import zrcl.ext as ext

GITHUB_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}

raw_url = "https://raw.githubusercontent.com/{url}"


def download_github_raw_content(url: str, save: str = None):
    """
    Downloads the raw content from the given GitHub URL.

    Args:
        url (str): The URL of the content to be downloaded.

    Returns:
        bytes: The raw content downloaded from the specified URL.
    """
    url = raw_url.format(url=url)
    res = requests.get(url, headers=GITHUB_HEADERS)
    # if 404
    if res.status_code == 404:
        raise RuntimeError("File not found on github")

    if not save:
        return res.content

    with open(save, "wb") as f:
        f.write(res.content)


last_commit_api_url = "https://api.github.com/repos/{id}/commits?path={filename}"


def git_last_commit(id, filename):
    """
    A function to retrieve the last commit date for a given id and filename using the last_commit_api_url.

    Args:
        id: The identifier for the commit.
        filename: The name of the file.

    Returns:
        The date of the last commit as a datetime object, or None if there was an error.
    """

    url = last_commit_api_url.format(id=id, filename=filename)
    url += "&limit=1"

    r = requests.get(url, headers=GITHUB_HEADERS)
    try:
        rjson = r.json()
    except Exception:
        return None

    return rjson


def extract_commit(commitjson: dict, type: typing.Literal["date", "sha"] = "sha"):
    if type == "date":
        datestr = ext.get_deep(commitjson, 0, "commit", "committer", "date")
        if datestr is None:
            return None

        dateobj = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")

        return dateobj
    elif type == "sha":
        return ext.get_deep(commitjson, 0, "sha")


def github_get_releases(repo: str, limit=10):
    url = f"https://api.github.com/repos/{repo}/releases?limit={limit}"
    response = requests.get(url, headers=GITHUB_HEADERS)
    return response.json()


def github_release_meta(
    repo: str,
    name: str = None,
    match: typing.Literal[
        "exact", "startswith", "contains", "endswith", "glob"
    ] = "exact",
    match_release_tag=False,
):
    """
    A function to retrieve metadata about a GitHub release based on various matching criteria.

    Args:
        repo (str): The GitHub repository name.
        name (str, optional): The name of the release tag. Defaults to None.
        match (Literal["exact", "startswith", "contains", "endswith", "glob"], optional):
            The matching criteria for the release tag. Defaults to "exact".
        match_release_tag (bool, optional): Whether to match the release tag. Defaults to False.

    Returns:
        dict: The metadata of the GitHub release.
    """
    # Base URL for GitHub API
    base_url = f"https://api.github.com/repos/{repo}/releases"

    # Determine the URL to use based on whether a specific release tag is provided
    if name and match == "exact":
        url = f"{base_url}/tags/{name}"
    elif name:
        releases = github_get_releases(repo, 10)
        for release in releases:
            match_var = release["tag_name"] if match_release_tag else release["name"]

            if match == "startswith" and match_var.startswith(name):
                return release
            elif match == "contains" and name in match_var:
                return release
            elif match == "endswith" and match_var.endswith(name):
                return release
            elif match == "glob" and re.match(name, match_var) is not None:
                return release

        raise ValueError(f"Could not find release with tag {name}")
    else:
        url = f"{base_url}/latest"

    # Request the release data from GitHub
    response = requests.get(url, headers=GITHUB_HEADERS)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json()


def download_release(
    releasejson: dict,
    filename: str = None,
    match: typing.Literal[
        "exact", "startswith", "contains", "endswith", "glob"
    ] = "exact",
    save: str = None,
):
    """
    Downloads a release asset from a GitHub release based on matching criteria.

    Args:
        releasejson (dict): The JSON representation of the GitHub release.
        filename (str, optional): The name of the release asset to download. Defaults to None.
        match (Literal["exact", "startswith", "contains", "endswith", "glob"], optional):
            The matching criteria for the release asset. Defaults to "exact".
        save (str, optional): The path to save the downloaded asset. Defaults to None.

    Returns:
        io.BytesIO or None: If `save` is provided, returns None. Otherwise, returns the downloaded asset as a BytesIO object.

    Raises:
        requests.exceptions.HTTPError: If there is an error in the HTTP response.
    """
    for asset in releasejson.get("assets", []):
        if match == "exact" and asset["name"] != filename:
            continue
        elif match == "startswith" and not asset["name"].startswith(filename):
            continue
        elif match == "contains" and filename not in asset["name"]:
            continue
        elif match == "endswith" and not asset["name"].endswith(filename):
            continue
        elif match == "glob" and re.match(filename, asset["name"]) is None:
            continue

        download_url = asset["browser_download_url"]
        # download using stream
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        content = io.BytesIO()

        for block in response.iter_content(1024):
            content.write(block)

        if save:
            with open(save, "wb") as f:
                f.write(content.getvalue())
            return

        return content
