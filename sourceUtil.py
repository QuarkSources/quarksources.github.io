
from pathlib import Path
import plistlib
import requests
import re
from datetime import datetime
from packaging import version
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import json

def compare_versions(v1: str, v2: str) -> bool:
    """
    Returns true if v1 is 'older than' v2
    """
    return version.parse(v1) < version.parse(v2)

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

    def create(self):
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
            except (json.JSONDecodeError, requests.RequestException) as err:
                print(f"Unable to process {data.get('ids')}.")
                print(f"{type(err).__name__}: {str(err)}")
                continue

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
                            primarySource["news"].append(article)

            elif isinstance(parser, GithubParser) or isinstance(parser, Unc0verParser):
                app = self.src["apps"][existingAppIDs.index(data["ids"][0])]
                if version.parse(app["absoluteVersion"] if app.get("absoluteVersion") else app["version"]) < version.parse(parser.version):
                    metadata = parser.get_asset_metadata()
                    if metadata["bundleID"] != data["ids"][0]:
                        print(app["name"] + " BundleID has changed to " + metadata["bundleID"] + "\nApp not updated.")
                        continue
                    app["absoluteVersion"] = parser.version
                    app["versionDate"] = parser.versionDate
                    app["versionDescription"] = parser.versionDescription
                    for (k,v) in metadata.items():
                        app[k] = v
                    self.src["apps"][existingAppIDs.index(data["ids"][0])] = app
                    updatedAppsCount += 1
            else:
                raise NotImplementedError()
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
                raise TypeError("Filepath must be a path-like object or a url.")

        if not self.valid_source():
            raise Exception("Invalid source formatting.")

    def parse_apps(self, ids: list = None) -> list:
        apps = list()
        for app in self.src["apps"]:
            if self.valid_app(app):
                if ids is None:
                    apps.append(app)
                elif app["bundleIdentifier"] in ids:
                    apps.append(app)
        return apps

    def parse_news(self, ids: list = None) -> list:
        news = list()
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
        requiredKeys = ["name", "identifier", "apps", "news"]
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

    def get_asset_metadata(self, asset_name: str = None) -> dict:
        """
        Returns a dictionary containing the downloadURL, size, bundleID, version
        """
        name = asset_name + ".ipa" if asset_name is not None else ".ipa"
        download_url = "https://unc0ver.dev" + self.data["browser_download_url"]
        with TemporaryDirectory() as td:
            tempdir = Path(str(td))
            r = requests.get(download_url)
            with open(tempdir / name, "wb") as file:
                file.write(r.content)
            with ZipFile(tempdir / name, "r") as ipa:
                ipa.extractall(path=tempdir)
            with open(list(tempdir.rglob("Info.plist"))[0], "rb") as fp:
                plist = plistlib.load(fp)

            metadata = {
                "downloadURL": download_url,
                "size": (tempdir / name).stat().st_size,
                "bundleID": plist["CFBundleIdentifier"],
                "version": plist["CFBundleShortVersionString"]
            }
        return metadata

class GithubParser:
    def __init__(self, url: str = None, repo_author: str = None, repo_name: str = None, ver_parse = lambda x: x.lstrip("v"), include_pre: bool = False, prefer_date: bool = False):
        """
        Supply either the api url, or the repo_author and repo_name.
        Include a lambda function for ver_parse if needed. ex: (lambda x: x.replace("-r", "."))
        """
        if url is not None:
            releases = requests.get(url).json()
        else:
            releases = requests.get("https://api.github.com/repos/{0}/{1}/releases".format(repo_author, repo_name)).json()
        if isinstance(releases, dict) and releases.get("message") == "Not Found":
            raise Exception("Github Repo not found.")
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

    def get_asset_metadata(self, asset_name: str = None) -> dict:
        """
        Returns a dictionary containing the downloadURL, size, bundleID, version
        """
        name = asset_name + ".ipa" if asset_name is not None else ".ipa"
        download_url = next(x for x in self.data["assets"] if x["name"].endswith(name))["browser_download_url"]
        with TemporaryDirectory() as td:
            tempdir = Path(str(td))
            r = requests.get(download_url)
            with open(tempdir / name, "wb") as file:
                file.write(r.content)
            with ZipFile(tempdir / name, "r") as ipa:
                ipa.extractall(path=tempdir)
            with open(list(tempdir.rglob("Info.plist"))[0], "rb") as fp:
                plist = plistlib.load(fp)

            metadata = {
                "downloadURL": download_url,
                "size": (tempdir / name).stat().st_size,
                "bundleID": plist["CFBundleIdentifier"],
                "version": plist["CFBundleShortVersionString"]
            }
        return metadata
