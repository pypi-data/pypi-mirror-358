import os
import hashlib
import time
import urllib.request
import urllib.error
import json

from typing import Callable


BASE_URL = "https://secure.reinforced.app"
CONFIG_URL = f"{BASE_URL}/config/settings.json"

LIBRARY_BASE_NAME = "libvuldb2"


def library_name(environment: str) -> str:
    return f"{LIBRARY_BASE_NAME}.{environment}.so"

def library_url(version: str, environment: str) -> str:
    return f"{BASE_URL}/dataset/{version}/{library_name(environment)}"

def library_abspath(version: str, environment: str) -> str:
    return os.path.join(
        os.path.dirname(__file__),
        "lib64",
        version,
        library_name(environment),
    )


def download_library(version: str, environment: str, expected_hashes: set[str]) -> str:
    """
    Downloads the dataset library and returns the path to it.
    """

    url = library_url(version, environment)
    path = library_abspath(version, environment)
    modified_time = None

    if os.path.exists(path):
        # On hash mismatch, remove the file and download again.
        if not is_file_hash_valid(path, expected_hashes):
            os.remove(path)
        # On hash match, we pass read mtime to pass it to server to check if the file is up to date
        else:
            modified_time = int(os.path.getmtime(path))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    downloaded = download_file(url, path, modified_time)
    if downloaded:
        print(f"\nSuccessfully downloaded library")
    
    if not is_file_hash_valid(path, expected_hashes):
        raise ValueError(f"Invalid dataset library hash")

    return path

def is_file_hash_valid(path: str, expected_hashes: set[str]):    
    with open(path, 'rb') as f:
        actual_hash = hashlib.sha1(f.read()).hexdigest()
        return actual_hash in expected_hashes

def download_file(url: str, path: str, modified_time: int | None = None):
    request = urllib.request.Request(url)

    if modified_time:
        formatted_time = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(modified_time))
        request.add_header('If-Modified-Since', formatted_time)

    try:
        _download_file_impl(
            request,
            path,
            lambda mbytes, progress: print(f"\rDownload progress: {mbytes:.1f} MiB ({progress:.1f}%)", end="", flush=True)
        )
    except urllib.error.HTTPError as e:
        if e.code == 304:
            # File is up to date, no need to download again
            return False
        raise

    return True

def _download_file_impl(request: urllib.request.Request, path: str, callback: Callable[[float, float], None]):
    CHUNK_SIZE = 128 * 1024
    
    with (
        urllib.request.urlopen(request) as response,
        open(path, 'wb') as f,
    ):
        total_size = int(response.headers.get('Content-Length'))
        downloaded = 0
        
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            
            f.write(chunk)
            downloaded += len(chunk)
            
            mbytes = downloaded / 1024 / 1024
            percentage = (downloaded / total_size) * 100

            callback(mbytes, percentage)


def fetch_config() -> dict[str, dict]:
    with urllib.request.urlopen(CONFIG_URL) as response:
        data = json.load(response)
        validators = data.get("validators", [])

        return {
            validator["network"]: validator
            for validator in validators
        }
