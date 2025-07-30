import requests
from ycpm import clyp_packages_folder, ycpm_version, clyp_version
import zipfile
from io import BytesIO
import os
import logging
from typing import Optional, Tuple, Dict, Any
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }
    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(levelname)s: %(message)s"))
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)

GITHUB_RAW_URL = "https://raw.githubusercontent.com/{package}/refs/heads/main/ycpm.json"
GITHUB_RELEASES_URL = "https://api.github.com/repos/{package}/releases/latest"


def _get_github_ycpm_json(package: str) -> Optional[Dict[str, Any]]:
    """Fetch ycpm.json from the GitHub repository."""
    url = GITHUB_RAW_URL.format(package=package)
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"{Fore.CYAN}Loaded ycpm.json from GitHub for {package}{Style.RESET_ALL}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to load 'ycpm.json' from GitHub: {e}")
        return None


def _get_github_latest_release_asset(package: str, asset_name: str) -> Optional[Tuple[str, str]]:
    """Get the download URL and tag for the latest release asset from GitHub."""
    url = GITHUB_RELEASES_URL.format(package=package)
    try:
        response = requests.get(url)
        response.raise_for_status()
        for asset in response.json().get("assets", []):
            if asset.get("name") == asset_name:
                return asset.get("browser_download_url"), asset.get("tag")
        logger.error(f"Asset {asset_name} not found in latest release.")
        return None
    except requests.RequestException as e:
        logger.error(f"Failed to get latest release info from GitHub: {e}")
        return None


def _download_and_extract_zip(download_url: str, extract_path: str) -> bool:
    """Download a ZIP file from the given URL and extract it to the specified path."""
    try:
        download_response = requests.get(download_url)
        download_response.raise_for_status()
        with zipfile.ZipFile(BytesIO(download_response.content)) as zf:
            os.makedirs(extract_path, exist_ok=True)
            zf.extractall(extract_path)
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to download file: {e}")
        return False
    except zipfile.BadZipFile as e:
        logger.error(f"Failed to extract ZIP file: {e}")
        return False


def install(source: Optional[str] = None, package: Optional[str] = None) -> None:
    """
    Install a package from the specified source.
    :param source: The source from which to install the package (optional).
    :param package: The name of the package to install (optional).
    """
    if not source and not package:
        logger.warning(f"{Fore.YELLOW}No source or package specified. Please provide at least one.{Style.RESET_ALL}")
        return
    logger.info(f"{Fore.BLUE}Installing package '{package}' from source '{source}'...{Style.RESET_ALL}")
    if source == "gh":
        logger.info(f"{Fore.CYAN}Loading 'ycpm.json' from GitHub...{Style.RESET_ALL}")
        ycpm_json = _get_github_ycpm_json(package)
        if not ycpm_json:
            return
        package_name = ycpm_json.get("name")
        package_file = ycpm_json.get("file")
        if not (package_name and package_file):
            logger.error(f"{Fore.RED}Invalid ycpm.json: missing 'name' or 'file'.{Style.RESET_ALL}")
            return
        asset = _get_github_latest_release_asset(package, package_file)
        if not asset:
            return
        download_url, package_version = asset
        logger.info(f"{Fore.BLUE}Downloading {package_file} from {download_url}...{Style.RESET_ALL}")
        extract_path = os.path.join(clyp_packages_folder, package_name)
        if _download_and_extract_zip(download_url, extract_path):
            logger.info(f"{Fore.GREEN}Successfully downloaded and installed {package_file} {package_version}{Style.RESET_ALL}")