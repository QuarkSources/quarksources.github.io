import os
import plistlib
import atexit
import re
from pathlib import Path
import shutil
from tempfile import mkdtemp, TemporaryDirectory
from zipfile import ZipFile

import requests
import logging
from github3 import login
from github3.exceptions import GitHubError
from github3.repos.release import Release

def cleanup_tempdir(fp: Path):
    try:
        if fp.is_dir():
            shutil.rmtree(fp.as_posix())
        else:
            os.remove(fp.as_posix())
    except FileNotFoundError as err:
        logging.debug(f"File not found in temporary directory: {str(fp)}")
    except Exception as err:
        logging.warning(f"Unable to cleanup files in temporary directory: {str(fp)} due to {err.__class__}")

class IPA_Info:
    """A wrapper class that makes getting relevant information from the IPAs Info.plist file easier for those who don't have Apple's absurd lingo memorized.
    """
    def __init__(self, ipa_path: Path | None = None, plist_path: Path | None = None, plist: dict | None = None):
        """Encapsulates an IPA to retrieve metadata more easily.

        Processing priority: `plist` > `plist_path` > `ipa_path`. The `ipa_path` and `plist` will be saved for later use to return various aspects of the IPA.
        If any property of the IPA should return None, the IPA simply does not have that property.

        Args:
            ipa_path (Path | None, optional): The Path to the .ipa file. Defaults to None.
            plist_path (Path | None, optional): The Path to the Info.plist file. Defaults to None.
            plist (dict | None, optional): The plist as loaded into a dictionary object. Defaults to None.

        Raises:
            InsufficientArgError: Occurs if there were no arguments received.
        """
        if plist is None:
            if ipa_path is None and plist_path is None:
                raise InsufficientArgError("Not enough arguments supplied to create IPA_Info object.")
            if ipa_path is not None and plist_path is None:
                payload_path = extract_ipa(ipa_path, use_temp_dir=True)
                plist_path = list(payload_path.rglob("Info.plist"))[0] # locate the Info.plist path within the extracted data
            if plist_path is not None:
                with open(plist_path, "rb") as fp:
                    plist = plistlib.load(fp)
        self._ipa_path, self._plist = ipa_path, plist
    
    @property 
    def DisplayName(self) -> str:
        """The name that is shown on the iOS Home Screen.
        """
        return self._plist.get("CFBundleDisplayName")
        
    @property
    def DevelopmentRegion(self) -> str:
        """The development region as determined by the written language used. 
        
        Example: "en"444
        """
        return self._plist.get("CFBundleDevelopmentRegion")
        
    @property 
    def Identifier(self) -> str:
        return self._plist.get("CFBundleIdentifier")
        
    @property 
    def InfoDictionaryVersion(self) -> str:
        """The plist version this data was stored in.
        """
        return self._plist.get("CFBundleInfoDictionaryVersion")
        
    @property 
    def Name(self) -> str:
        return self._plist.get("CFBundleName")
        
    @property 
    def ShortVersion(self) -> str:
        """The most commonly used and more accurate version.
        """
        return self._plist.get("CFBundleShortVersionString").lstrip("v")
        
    @property 
    def SupportedPlatforms(self) -> list[str]:
        return self._plist.get("CFBundleSupportedPlatforms")
        
    @property 
    def Version(self) -> str:
        """Version that sometimes only contains the major version point.
        """
        return self._plist.get("CFBundleVersion")
    
    @property 
    def MinimumOSVersion(self) -> str:
        return self._plist.get("MinimumOSVersion")
    
    @property 
    def NetworkUsageDescription(self) -> str:
        return self._plist.get("NSLocalNetworkUsageDescription")
    
    @property 
    def MicUsageDescription(self) -> str:
        return self._plist.get("NSMicrophoneUsageDescription")
    
    @property 
    def FileSharingEnabled(self) -> bool:
        return self._plist.get("UIFileSharingEnabled", False)

def download_tempfile(download_url: str) -> Path:
    """Downloads file to a temporary directory.

    Args:
        download_url (str): The url of the file to be downloaded.

    Returns:
        Path: The Path obj pointing to the downloaded file.
    """
    tempdir = Path(mkdtemp())
    atexit.register(cleanup_tempdir, tempdir)
    filename = "temp"
    r = requests.get(download_url)
    with open(tempdir / filename, "wb") as file:
        file.write(r.content)
    return tempdir / filename

def extract_ipa(ipa_path: Path, extract_twice: bool = False, use_temp_dir: bool = False) -> Path | Path:
    """Extracts the ipa data into a directory.

    If you are extracting twice, the normal .ipa file will be located in the parent directory of the returned path with the name "temp2.ipa".
    
    Args:
        ipa_path (Path): The Path to the ipa file.
        extract_twice (bool, optional): Set True if the ipa file is compressed in a zip file. Defaults to False.
        use_temp_dir (bool, optional): Uses a temporary directory to extract to instead of the same directory as the ipa. Defaults to False.

    Raises:
        FileError: If there was an issue processing the zipped files.

    Returns:
        Path: A Path object pointing to the extracted IPA contents (the "Payload" folder).
    """
    if use_temp_dir:
        dest_path = Path(mkdtemp())
        atexit.register(cleanup_tempdir, dest_path)
    else:
        dest_path = ipa_path.parent
        atexit.register(cleanup_tempdir, ipa_path / "Payload")
    if extract_twice:
        with ZipFile(ipa_path, "r") as zip:
            ipa_path = dest_path / "temp2.ipa"
            r = re.compile(r".*\.ipa")
            files = list(filter(r.match, zip.namelist()))
            if len(files) == 1:
                file = files[0]
            elif len(files > 1):
                raise FileError(str(ipa_path), "More files than just an IPA in the zip file.")
            else:
                raise FileError(str(ipa_path), "No IPA files found in the zip file.")
            data = zip.read(file)
            ipa_path.write_bytes(data)
        
    with ZipFile(ipa_path, "r") as ipa:
        ipa.extractall(path=dest_path)
    dest_path = dest_path / "Payload"
    if not dest_path.exists():
        raise FileError("Invalid IPA file does not have a Payload folder inside.")
    return dest_path

def extract_altstore_metadata(ipa_path: Path | None = None, plist_path: Path | None = None) -> dict[str]:
    """Extracts all relevant ipa metadata from the IPA and its Info.plist and converts it into the format AltStore uses as stored in a dictionary.

    Args:
        ipa_path (Path): Path to the .ipa file.
        plist_path (Path): Path to the Info.plist file.

    Raises:
        InsufficientArgError: Occurs if there were no arguments received.

    Returns:
        dict[str, Any]: Returns a dictionary containing the bundleID, version, and more
    """
    plist = IPA_Info(ipa_path=ipa_path, plist_path=plist_path)
    
    metadata = {
        "bundleIdentifier": plist.Identifier,
        "version": plist.ShortVersion
    }
    if ipa_path is not None:
        metadata["size"] = ipa_path.stat().st_size
    return metadata

def get_github_release(github_token: str, repo_id: int | None = None, repo_name: str | None = None) -> Release:
    """Gets the github3.py Release object required to upload assets to.
    
    If neither a repo_id or repo_name is provided, a repository will be automatically generated. And if the selected repository does not contain any releases, one will be automatically generated.

    Args:
        github_token (str): Your personal GitHub access token to use the GitHub API.
        repo_id (int | None, optional): The id number of the desired repository. Defaults to None.
        repo_name (str | None, optional): The name of the desired repository. Defaults to None.

    Returns:
        Release: A Release object that can be used to access assets and upload new assets.
    """
    try:
        g_repo, g_release = None, None
        gh = login(token=github_token)
        
        # Use either the repo_id or repo_name to locate the repository, otherwise create a new one
        if repo_id is not None:
            g_repo = gh.repository_with_id(repo_id)
        elif repo_name is not None:
            g_repo = gh.repository(repo_name)
        else:
            g_repo = gh.create_repository("IPA_Uploads", description="This repository is used for uploading IPA files to.", issues=False, has_projects=False, has_wiki=False, auto_init=True)
            
        # If a release doesn't exist, create one. Otherwise grab latest release.
        if len(list(g_repo.releases())) == 0:
            g_release = g_repo.create_release("v0.0", name="IPA Storage Release", body="This release has been automatically generated for the use of uploading IPAs for storage and download by the general public.")
        else:
            g_release = g_repo.latest_release()
    except GitHubError as err:
        print(f"GitHub Authentication failed.")
        print(f"{type(err).__name__}: {str(err)}")
    return g_release

def upload_ipa_github(ipa_path: Path, github_release: Release, name: str | None = None, ver: str | None = None) -> str:
    """Uses github3.py package to upload IPA to the specified Release using the GitHub API.
    
    The name and version are concatenated to make the github release asset name, otherwise the filename from the ipa_path is used.

    Args:
        ipa_path (Path): Path to the ipa to be uploaded.
        github_release (Release): github3.py Release object that will be used as the location to upload to.
        name (str): The filename to be used on the uploaded ipa (do not include the .ipa extension).
        ver (str): The version to be concatenated to the end of the filename on the uploaded ipa.

    Returns:
        str: The download url for the uploaded IPA.
    """
    with open(ipa_path, "rb") as file:
        label = f"{name}-{ver}.ipa" if name is not None and ver is not None else ipa_path.name
        uploaded_asset = github_release.upload_asset(content_type="application/octet-stream", name=label, asset=file)
    return uploaded_asset.browser_download_url

class IPAError(Exception):
    """Base exception for all IPA processing errors."""
    pass

class InsufficientArgError(IPAError):
    """Occurs when there are insufficient number of arguments."""
    pass

class FileError(IPAError):
    """Occurs if there are issues when processing files."""
    pass
