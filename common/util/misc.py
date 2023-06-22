import requests
from requests.adapters import HTTPAdapter, Retry
from requests import Response

from pathlib import Path


def HTTP_get_with_retries(src_url: str, total_retries: int = 5, backoff_factor: float = 0.1) -> Response:
    """
    Get a HTTP response object by trying to download the contents of an URL

    Args:
        src_url: The URL to get content from
        total_retries: The total number of retries before the repsonse is returned even with failure
        backoff_factor: The backoff factor which sets the time elapsed between two retries

    Returns: a requests.Response object

    """
    s = requests.Session()

    retries = Retry(total=total_retries,
                    backoff_factor=backoff_factor,
                    status_forcelist=[500, 502, 503, 504])

    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))

    return s.get(src_url)


def download_file(src_url: str, dst_path: Path | str) -> None:
    """
    Downloads a file locally from an URL

    Args:
        src_url: The source URL from where the file should be downloaded
        dst_path: The destination path where the file should be saved
    """

    response = HTTP_get_with_retries(src_url)
    response.raise_for_status()  # Raise an exception if the response is not successful

    dst_path = Path(dst_path)
    dst_path.parent.mkdir(exist_ok=True, parents=True)

    with dst_path.open("wb") as file:
        file.write(response.content)
