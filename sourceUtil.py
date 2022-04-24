from pathlib import Path
import plistlib
import requests
import re
from datetime import datetime
from packaging import version
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from github3.repos.release import Release
from github3.exceptions import GitHubError
import json

def compare_versions(v1: str, v2: str) -> bool:
    """
    Returns true if v1 is 'older than' v2
    """
    return version.parse(v1) < version.parse(v2)

def extract_metadata(download_url: str, extract_twice: bool = False, upload_ipa_kwargs: dict = None) -> dict:
    """
    Downloads .ipa from given url and returns all relevant .ipa metadata from the info.plist

    Returns a dictionary containing the downloadURL, size, bundleID, version
    """
    with TemporaryDirectory() as td:
        tempdir = Path(str(td))
        filename = "temp.zip"
        r = requests.get(download_url)
        with open(tempdir / filename, "wb") as file:
            file.write(r.content)
        if extract_twice:
            with ZipFile(tempdir / filename, "r") as zip:
                filename = "temp2.zip"
                for file in zip.namelist():
                    data = zip.read(file)
                    file_path = tempdir / filename
                    file_path.write_bytes(data)
            
        with ZipFile(tempdir / filename, "r") as ipa:
            ipa.extractall(path=tempdir)
        with open(list(tempdir.rglob("Info.plist"))[0], "rb") as fp:
            plist = plistlib.load(fp)

        if upload_ipa_kwargs is not None:
            upload_ipa_kwargs["ipa_path"] = tempdir / filename
            upload_ipa_kwargs["ver"] = plist["CFBundleShortVersionString"]
            download_url = upload_ipa(**upload_ipa_kwargs)
        metadata = {
            "downloadURL": download_url,
            "size": (tempdir / filename).stat().st_size,
            "bundleIdentifier": plist["CFBundleIdentifier"],
            "version": plist["CFBundleShortVersionString"]
        }
    return metadata

def upload_ipa(ipa_path: Path, github_release: Release, name: str, ver: str) -> str:
    """
    Uses PyGithub package to upload IPA to the specified Release using the Github API. The name and version are concatenated to make the github release asset name.

    Returns the download url for the uploaded IPA.
    """
    with open(ipa_path, "rb") as file:
        uploaded_asset = github_release.upload_asset(content_type="application/octet-stream", name=f"{name}-{ver}.ipa", asset=file)
    return uploaded_asset.browser_download_url

class AltSourceManager:
    def __init__(self, filepath, sources_data: list, alternate_data: dict = None, prettify: bool = True):
        """
        filepath: The location of the source to be parsed. Accepts either Path object, or string path.
        """
        self.src_data, self.alt_data, self.prettify = sources_data, alternate_data, prettify

        if not isinstance(filepath, Path):
            filepath = Path(filepath)
        self.path = filepath
        with open(self.path, "r", encoding="utf-8") as fp:
            self.src = json.load(fp)
        self.name = self.src["name"]

    def add(self):
        raise NotImplementedError()
        print("x apps added, x news added.")

    def update(self):
        print(self.src["name"])
        existingAppIDs = [app["bundleIdentifier"] for app in self.src["apps"]]
        existingNewsIDs = [app["identifier"] for app in self.src["news"]]
        updatedAppsCount = addedAppsCount = addedNewsCount = 0

        for data in self.src_data:
            try:
                parser = data["parser"](**data["kwargs"])

                # perform different actions depending on the type of file being parsed
                if isinstance(parser, AltSourceParser):
                    apps = parser.parse_apps(None if data.get("getAllApps") else data.get("ids"))
                    for app in apps:
                        bundleID = app["bundleIdentifier"]
                        if bundleID in existingAppIDs:
                            if version.parse(app["version"]) > version.parse(self.src["apps"][existingAppIDs.index(bundleID)]["version"]):
                                updatedAppsCount += 1
                            self.src["apps"][existingAppIDs.index(bundleID)] = app # note that this actually updates the app regardless of whether the version is newer
                        else:
                            addedAppsCount += 1
                            self.src["apps"].append(app)

                    if not data.get("ignoreNews"):
                        news = parser.parse_news(None if data.get("getAllNews") else data.get("ids"))
                        for article in news:
                            newsID = article["identifier"]
                            if newsID in existingNewsIDs:
                                self.src["news"][existingNewsIDs.index(newsID)] = article # overwrite existing news article
                            else:
                                addedNewsCount += 1
                                self.src["news"].append(article)

                    # create "appID" property as a duplicate of bundleIdentifier value

                elif isinstance(parser, GithubParser) or isinstance(parser, Unc0verParser):
                    for id in data["ids"]:
                        if id not in existingAppIDs:
                            print(f"{id} not found in {self.name}.")
                            continue
                        app = self.src["apps"][existingAppIDs.index(id)]
                        if version.parse(app["absoluteVersion"] if app.get("absoluteVersion") else app["version"]) < version.parse(parser.version):
                            metadata = parser.get_asset_metadata()
                            if metadata["bundleIdentifier"] != id:
                                print(app["name"] + " BundleID has changed to " + metadata["bundleIdentifier"] + "\nApp not updated.")
                                continue
                            app["absoluteVersion"] = parser.version
                            app["versionDate"] = parser.versionDate
                            app["versionDescription"] = parser.versionDescription
                            for (k,v) in metadata.items():
                                app[k] = v
                            self.src["apps"][existingAppIDs.index(data["ids"][0])] = app
                            updatedAppsCount += 1
                else:
                    raise NotImplementedError("The specified parser class is not supported.")
            except json.JSONDecodeError as err:
                print(f"Unable to process {data.get('ids')}.")
                errstr = str(err).replace('\n', '\n\t') #indent newlines for prettier printing
                print(f"{type(err).__name__}: {errstr[:300]}...") #only print first 300 chars
                continue
            except (requests.RequestException, requests.ConnectionError, GitHubError, AltSourceError) as err:
                print(f"Unable to process {data.get('ids')}.")
                print(f"{type(err).__name__}: {str(err)}")
                continue
            except StopIteration as err:
                print(f"Unable to process {data.get('ids')}.")
                print(f"{type(err).__name__}: Could not find download asset with matching criteria.")
                continue
            
            # end of for loop

        if self.alt_data is not None:
            self.alter_app_info()

        with open(self.path, "w", encoding="utf-8") as fp:
            json.dump(self.src, fp, indent = 2 if self.prettify else None)
            fp.write("\n") # add missing newline to EOF
        print(f"{updatedAppsCount} app(s) updated.\n{addedAppsCount} app(s) added, {addedNewsCount} news article(s) added.")

    def alter_app_info(self) -> list:
        apps = self.src["apps"]
        for i in range(len(apps)):
            bundleID = apps[i]["bundleIdentifier"]
            if bundleID in self.alt_data.keys():
                for key in self.alt_data[bundleID].keys():
                    apps[i][key] = self.alt_data[bundleID][key]
        self.src["apps"] = apps

class AltSourceParser:
    def __init__(self, filepath):
        """
        filepath: The location of the source to be parsed. Accepts either Path object, string path to local object, or url.
        """
        if isinstance(filepath, Path) and filepath.exists():
            with open(filepath, "r", encoding="utf-8") as fp:
                self.src = json.load(fp)
        elif isinstance(filepath, str) and filepath.startswith("http"):
            self.src = requests.get(filepath).json()
        else:
            try:
                path = Path(filepath)
                with open(path, "r", encoding="utf-8") as fp:
                    self.src = json.load(fp)
            except Exception as err:
                raise AltSourceError("Filepath must be a path-like object or a url.")

        if not self.valid_source():
            raise AltSourceError("Invalid source formatting.")

    def parse_apps(self, ids: list = None) -> list:
        apps, keys = list(), list()
        for app in self.src["apps"]:
            if self.valid_app(app):
                id = app["bundleIdentifier"]
                if id in keys: # bundleID already exists in list of apps processed (meaning there's a duplicate)
                    index = keys.index(id)
                    if version.parse(apps[index]["version"]) > version.parse(app["version"]):
                        next
                    else:
                        apps[index] = app
                elif ids is None:
                    apps.append(app)
                elif id in ids:
                    apps.append(app)
                keys.append(id)
        return apps

    def parse_news(self, ids: list = None) -> list:
        news = list()
        if "news" not in self.src.keys():
            return news
        for article in self.src["news"]:
            if self.valid_news(article):
                if ids is None:
                    news.append(article)
                elif article["identifier"] in ids:
                    news.append(article)
        return news

    def valid_app(self, app: dict) -> bool:
        requiredKeys = ["name", "bundleIdentifier", "developerName", "version", "versionDate", "downloadURL", "localizedDescription", "iconURL", "size"]
        for key in requiredKeys:
            if key not in app.keys():
                return False
        return True

    def valid_news(self, article: dict) -> bool:
        requiredKeys = ["title", "identifier", "caption", "date"]
        for key in requiredKeys:
            if key not in article.keys():
                return False
        return True

    def valid_source(self) -> bool:
        requiredKeys = ["name", "identifier", "apps"]
        for key in requiredKeys:
            if key not in self.src.keys():
                return False
        return True

class Unc0verParser:
    def __init__(self, url: str = None, ver_parse = lambda x: x.lstrip("v"), prefer_date: bool = False):
        """
        Supply either the api url, or the repo_author and repo_name.
        Include a lambda function for ver_parse if needed. ex: (lambda x: x.replace("-r", "."))
        """
        releases = requests.get(url).json()

        # alter the release tags to match altstore version tags
        releases = [{k: ver_parse(v) if k == "tag_name" else v for (k, v) in x.items()} for x in releases]

        if prefer_date:
            self.data = sorted(releases, key=lambda x: datetime.strptime(x["published_at"], "%Y-%m-%dT%H:%M:%S%z"))[-1] # only grab the most recent release
        else:
            self.data = sorted(releases, key=lambda x: version.parse(x["tag_name"]))[-1] # only grab the release with the highest version

    @property
    def version(self) -> str:
        return self.data["tag_name"]

    @property
    def versionDate(self) -> str:
        return self.data["published_at"]

    @property
    def versionDescription(self) -> str:
        return "# " + self.data["name"] + "\n\n" + self.data["body"]

    def get_asset_metadata(self) -> dict:
        """
        Returns a dictionary containing the downloadURL, size, bundleID, version
        """
        download_url = "https://unc0ver.dev" + self.data["browser_download_url"]
        return extract_metadata(download_url)

class GithubParser:
    def __init__(self, url: str = None, repo_author: str = None, repo_name: str = None, ver_parse = lambda x: x.lstrip("v"), include_pre: bool = False, prefer_date: bool = False, asset_regex: str = None, extract_twice: bool = False, upload_ipa_kwargs: dict = None):
        """
        Supply either the api url, or the repo_author and repo_name.
        Include a lambda function for ver_parse if needed. ex: (lambda x: x.replace("-r", "."))
        """
        self.asset_regex, self.extract_twice, self.upload_ipa_kwargs = asset_regex, extract_twice, upload_ipa_kwargs
        if url is not None:
            releases = requests.get(url).json()
        else:
            releases = requests.get("https://api.github.com/repos/{0}/{1}/releases".format(repo_author, repo_name)).json()
        if isinstance(releases, dict):
            if releases.get("message") == "Not Found":
                raise GitHubError("Github Repo not found.")
            elif releases.get("message").startswith("API rate limit exceeded"):
                raise GitHubError("Github API rate limit has been exceeded for this hour.")
            else:
                raise GitHubError("Github API issue: " + releases.get("message"))
        if not include_pre:
            releases = list(filter(lambda x: x["prerelease"] != True, releases)) # filter out prereleases

        # alter the github release tags to match altstore version tags
        releases = [{k: ver_parse(v) if k == "tag_name" else v for (k, v) in x.items()} for x in releases]

        if prefer_date:
            self.data = sorted(releases, key=lambda x: datetime.strptime(x["published_at"], "%Y-%m-%dT%H:%M:%S%z"))[-1] # only grab the most recent release
        else:
            self.data = sorted(releases, key=lambda x: version.parse(x["tag_name"]))[-1] # only grab the release with the highest version

    @property
    def version(self) -> str:
        return self.data["tag_name"]

    @property
    def versionDate(self) -> str:
        return self.data["published_at"]

    @property
    def versionDescription(self) -> str:
        return "# " + self.data["name"] + "\n\n" + self.data["body"]

    def get_asset_metadata(self) -> dict:
        """
        Returns a dictionary containing the downloadURL, size, bundleID, version
        """
        regex = self.asset_regex if self.asset_regex is not None else r".*\.ipa"
        download_url = next(x for x in self.data["assets"] if re.fullmatch(regex, x["name"]))["browser_download_url"]
        return extract_metadata(download_url, extract_twice=self.extract_twice, upload_ipa_kwargs=self.upload_ipa_kwargs)

class AltSourceError(Exception):
    """Raised when there is an error related to the GithubAPI"""
    pass
