import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import requests
from packaging import version

from ipaUtil import *


def current_altstore_datetime() -> str:
    """Generates and returns the current UTC date and time in a format accepted by AltStore.

    The format used is the same as the GitHub API: yyyy-mm-ddThh:mm:ss-z
    Ex. 2022-05-25T03:39:23Z

    Returns:
        str: A formatted string containing the current date and time.
    """
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_github_datetime(dt: str) -> datetime:
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z")

def is_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def flatten_ids(ids: list[str | dict[str, str]], use_keys: bool = True) -> list[str]:
    """Takes a list of mixed data types (str and dict) and converts them all to a list[str] by removing either the key or value of any dict objects.

    Args:
        ids (list[str  |  dict[str, str]]): The list of ids which is either just the `str` id or a `dict` where the `appID` is the key and `bundleID` the value.
        use_keys (bool, optional): If True, the method will flatten the list using the keys of any `dict` objects, rather than their values (disposing of the unused key/value). Defaults to True.

    Returns:
        list[str]: A flattened list of app ids.
    """
    nested_ids = [[id] if isinstance(id, str) else id.keys() if use_keys else id.values() for id in ids] # converts a mixed list of strings and dicts to a flat list using the dict keys or values
    flat_ids = [item for sublist in nested_ids for item in sublist] # flatten list
    return flat_ids

def gen_id_parse_table(ids: list[str | dict[str, str]]) -> dict[str, str] | None:
    """Creates a singular dictionary that combines the all the dict objects in `ids`.

    Args:
        ids (list[str  |  dict[str, str]]): _description_

    Returns:
        dict[str, str] | None: A dict that allows conversion from key:`appID` and value:`bundleID` based on the list of ids given.
    """
    convert_ids = [dic for dic in ids if isinstance(dic, dict)]
    if convert_ids is not None:
        return {k: v for d in convert_ids for k, v in d.items()} # combine into one dict
    return None

class AltSource:
    class App:
        class Permission:
            _validTypes = ["photos", "camera", "location", "contacts", "reminders", "music", "microphone", "speech-recognition", "background-audio", "background-fetch", "bluetooth", "network", "calendars", "faceid", "siri", "motion"]
            _requiredKeys = ["type", "usageDescription"]
            
            def __init__(self, src: dict[str] | None = None):
                if src is not None:
                    self._src = src
                    if not all(x in src.keys() for x in self._requiredKeys):
                        logging.warning(f"Missing required AltSource.App.Permission keys. Must have both `type` and `usageDescription`.")
                    if "type" in src.keys() and not self.is_valid():
                        logging.warning(f"Permission type not found in valid permission types.")
                else:
                    logging.info(f"Brand new AltSource.App.Permission created. Please remember to set the following properties: {self._requiredKeys}")
                    src = {}
            
            def to_dict(self) -> dict[str]:
                ret = self._src
                ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
                return ret
            
            def missing_keys(self) -> list[str]:
                """Checks to see if the Permission has all the required values and returns the missing keys.
                
                Note that if the list is empty, it will evaluate as False.

                Returns:
                    list[str]: The list of required keys that are missing. If the Permission is valid, the list will be empty.
                """
                missing_keys = list()
                for key in self._requiredKeys:
                    if key not in self._src.keys():
                        missing_keys.append(key)
                return missing_keys
            
            def is_valid(self) -> bool:
                """Checks to see if the AltSource.App.Permission is valid and contains all the required information.

                Returns:
                    bool: True if the `Permission` is a valid AltSource.App.Permission.
                """
                return not self.missing_keys()
            
            def is_valid_type(self) -> bool:
                """Checks to see if the Permission type is valid.

                Returns:
                    bool: True if the listed type is valid
                """
                return self._src.get("type") in self._validTypes
            
            @property 
            def type(self) -> str:
                return self._src.get("type")
            @type.setter
            def type(self, value: str):
                if value in self._validTypes:
                    self._src["type"] = value
                else:
                    raise ValueError("Invalid permission type.")
                
            @property 
            def usageDescription(self) -> str:
                return self._src.get("usageDescription")
            @usageDescription.setter
            def usageDescription(self, value: str):
                self._src["usageDescription"] = value
        # End class Permission
        class Version:
            _requiredKeys = ['version', 'date', 'downloadURL', 'size']
            
            def __init__(self, src: dict[str] | None = None):
                if src is not None:
                    self._src = src
                    if not all(x in src.keys() for x in self._requiredKeys):
                        logging.warning(f"Missing required AltSource.App.Permission keys.")
                else:
                    logging.info(f"Brand new AltSource.App.Version created. Please remember to set the following properties: {self._requiredKeys}")
                    src = {}
            
            def to_dict(self) -> dict[str]:
                ret = self._src
                ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
                return ret
            
            def missing_keys(self) -> list[str]:
                """Checks to see if the Version has all the required values and returns the missing keys.
                
                Note that if the list is empty, it will evaluate as False.

                Returns:
                    list[str]: The list of required keys that are missing. If the Version is valid, the list will be empty.
                """
                missing_keys = list()
                for key in self._requiredKeys:
                    if key not in self._src.keys():
                        missing_keys.append(key)
                return missing_keys
            
            def is_valid(self) -> bool:
                """Checks to see if the AltSource.App.Permission is valid and contains all the required information.

                Returns:
                    bool: True if the `Permission` is a valid AltSource.App.Permission.
                """
                return not self.missing_keys()
            
            @property 
            def version(self) -> str:
                return self._src.get("version")
            @version.setter
            def version(self, value: str):
                self._src["version"] = value
                
            @property 
            def date(self) -> str:
                return self._src.get("date")
            @date.setter
            def date(self, value: str):
                self._src["date"] = value
                
            @property 
            def downloadURL(self) -> str:
                return self._src.get("downloadURL")
            @downloadURL.setter
            def downloadURL(self, value: str):
                self._src["downloadURL"] = value
                
            @property 
            def size(self) -> str:
                return self._src.get("size")
            @size.setter
            def size(self, value: str):
                self._src["size"] = value
                
            @property 
            def localizedDescription(self) -> str:
                return self._src.get("localizedDescription")
            @localizedDescription.setter
            def localizedDescription(self, value: str):
                self._src["localizedDescription"] = value

            # Start unofficial AltSource properties
            
            @property 
            def absoluteVersion(self) -> str:
                return self._src.get("absoluteVersion")
            @absoluteVersion.setter
            def absoluteVersion(self, value: str):
                self._src["absoluteVersion"] = value
            
            @property 
            def sha256(self) -> str:
                return self._src.get("sha256")
            @sha256.setter
            def sha256(self, value: str):
                self._src["sha256"] = value

        # End class Version
        
        _requiredKeys = ["name", "bundleIdentifier", "developerName", "versions", "localizedDescription", "iconURL"]
        
        def __init__(self, src: dict[str] | None = None):
            if src is None:
                logging.info(f"Brand new AltSource.App created. Please remember to set the following properties: {self._requiredKeys}")
                self._src = {
                    "name": "Example App", 
                    "bundleIdentifier": "com.example.app", 
                    "developerName": "Example.com", 
                    "versions": [],
                    "localizedDescription": "An app that is an example.", 
                    "iconURL": "https://example.com/icon.png"
                    }
            else:
                self._src = src
                if "permissions" in src.keys():
                    self._src["permissions"] = [self.Permission(perm) for perm in src["permissions"]]
                if "versions" in src.keys():
                    self._src["versions"] = [AltSource.App.Version(ver) for ver in src["versions"]]
                else: # create the first Version 
                    self._src["versions"] = [AltSource.App.Version({
                        "version": src.get("version"),
                        "date": src.get("versionDate"),
                        "downloadURL": src.get("downloadURL"),
                        "localizedDescription": src.get("versionDescription"),
                        "size": src.get("size"),
                        "sha256": src.get("sha256"),
                        "absoluteVersion": src.get("absoluteVersion")
                    })]
                missing_keys = self.missing_keys()
                if missing_keys:
                    logging.warning(f"Missing required AltSource.App keys: {missing_keys}")
        
        def to_dict(self) -> dict[str]:
            ret = self._src
            if "permissions" in self._src.keys():
                ret["permissions"] = [perm.to_dict() for perm in self.permissions]
            if "versions" in self._src.keys():
                ret["versions"] = [ver.to_dict() for ver in self.versions]
            ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
            return ret
        
        def missing_keys(self) -> list[str]:
            """Checks to see if the App has all the required values and returns the missing keys.
            
            Note that if the list is empty, it will evaluate as False.

            Returns:
                list[str]: The list of required keys that are missing. If the App is valid, the list will be empty.
            """
            missing_keys = list()
            for key in self._requiredKeys:
                if key not in self._src.keys():
                    missing_keys.append(key)
            return missing_keys
        
        def is_valid(self) -> bool:
            """Checks to see if the AltSource.App is valid and contains all the required information.

            Returns:
                bool: True if the `App` is a valid AltSource.App.
            """
            return not self.missing_keys()
        
        def _update_old_version_util(self, ver: Version):
            """Takes an `AltSource.App.Version` and uses it to update all the original AltStore API 
               properties for managing updates. Utilize this method to maintain backwards compatibility.
            """
            self._src["version"] = ver.version
            self._src["size"] = ver.size
            self._src["downloadURL"] = ver.downloadURL
            self._src["versionDate"] = ver.date
        
        @property 
        def name(self) -> str:
            return self._src.get("name")
        @name.setter
        def name(self, value: str):
            self._src["name"] = value
            
        @property 
        def bundleIdentifier(self) -> str:
            return self._src.get("bundleIdentifier")
        @bundleIdentifier.setter
        def bundleIdentifier(self, value: str):
            logging.warning(f"App `bundleIdentifier` changed from {self._src['bundleIdentifier']} to {value}.")
            self._src["bundleIdentifier"] = value
            
        @property 
        def developerName(self) -> str:
            return self._src.get("developerName")
        @developerName.setter
        def developerName(self, value: str):
            self._src["developerName"] = value
            
        @property 
        def subtitle(self) -> str:
            return self._src.get("subtitle")
        @subtitle.setter
        def subtitle(self, value: str):
            self._src["subtitle"] = value
            
        @property 
        def versions(self) -> list[Version]:
            return self._src.get("versions")
        @versions.setter
        def versions(self, value: list[Version]):
            if self.versions is not None:
                logging.warning(f"Entire `versions` section has been replaced for {self.name}.")
            self._src["versions"] = value
            
        @property 
        def version(self) -> str:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("version")
        @version.setter
        def version(self, value: str):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["version"] = value
            
        @property 
        def versionDate(self) -> str:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("versionDate")
        @versionDate.setter
        def versionDate(self, value: str):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["versionDate"] = value
            
        @property 
        def versionDescription(self) -> str:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("versionDescription")
        @versionDescription.setter
        def versionDescription(self, value: str):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["versionDescription"] = value
            
        @property 
        def downloadURL(self) -> str:
            logging.warning(f"Using deprecated v1 AltSource API.")
            return self._src.get("downloadURL")
        @downloadURL.setter
        def downloadURL(self, value: str):
            logging.warning(f"Using deprecated v1 AltSource API.")
            self._src["downloadURL"] = value
            
        @property 
        def localizedDescription(self) -> str:
            return self._src.get("localizedDescription")
        @localizedDescription.setter
        def localizedDescription(self, value: str):
            self._src["localizedDescription"] = value
            
        @property 
        def iconURL(self) -> str:
            return self._src.get("iconURL")
        @iconURL.setter
        def iconURL(self, value: str):
            self._src["iconURL"] = value
            
        @property 
        def tintColor(self) -> str:
            return self._src.get("tintColor")
        @tintColor.setter
        def tintColor(self, value: str):
            self._src["tintColor"] = value
            
        @property 
        def size(self) -> int:
            return self._src.get("size")
        @size.setter
        def size(self, value: int):
            self._src["size"] = value
            
        @property 
        def beta(self) -> bool:
            return self._src.get("beta")
        @beta.setter
        def beta(self, value: bool):
            self._src["beta"] = value
            
        @property 
        def screenshotURLs(self) -> list[str]:
            return self._src.get("screenshotURLs")
        @screenshotURLs.setter
        def screenshotURLs(self, value: list[str]):
            self._src["screenshotURLs"] = value
            
        @property 
        def permissions(self) -> list[Permission]:
            return self._src.get("permissions")
        @permissions.setter
        def permissions(self, value: list[Permission]):
            if self.permissions is not None:
                logging.warning(f"Entire `permissions` section has been replaced for {self.name}.")
            self._src["permissions"] = value
            
        ### Additional properties that are not currently standard in AltSources ###
        
        @property 
        def absoluteVersion(self) -> str:
            return self._src.get("absoluteVersion")
        @absoluteVersion.setter
        def absoluteVersion(self, value: str):
            self._src["absoluteVersion"] = value
            
        @property 
        def sha256(self) -> str:
            return self._src.get("sha256")
        @sha256.setter
        def sha256(self, value: str):
            self._src["sha256"] = value
            
        @property 
        def appID(self) -> str:
            return self._src.get("appID")
        @appID.setter
        def appID(self, value: str):
            if not isinstance(value, str):
                raise ArgumentTypeError("AltSource.App.appID cannot be set to any type other than str.")
            if self._src.get("appID") is not None:
                logging.warning(f"App `appID` changed from {self._src['appID']} to {value}.")
            self._src["appID"] = value
            
    # End class App
    
    class Article:
        _requiredKeys = ["title", "identifier", "caption", "date"]
        
        def __init__(self, src: dict | None = None):
            if src is None:
                logging.info(f"Brand new AltSource.Article created. Please remember to set the following properties: {self._requiredKeys}")
                self._src = {"title": "Example Article Title", "identifier": "com.example.article", "caption": "Provoking example caption.", "date": current_altstore_datetime()}
            else:
                self._src = src
                missing_keys = self.missing_keys()
                if missing_keys:
                    logging.warning(f"Missing required AltSource.Article keys: {missing_keys}")
            
        def to_dict(self) -> dict[str]:
            ret = self._src
            ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
            return ret
        
        def missing_keys(self) -> list[str]:
            """Checks to see if the `Article` has all the required values and returns the missing keys.
            
            Note that if the list is empty, it will evaluate as False.

            Returns:
                list[str]: The list of required keys that are missing. If the `Article` is valid, the list will be empty.
            """
            missing_keys = list()
            for key in self._requiredKeys:
                if key not in self._src.keys():
                    missing_keys.append(key)
            return missing_keys
        
        def is_valid(self) -> bool:
            """Checks to see if the AltSource.Article is valid and contains all the required information.

            Returns:
                bool: True if the `Article` is a valid AltSource.Article.
            """
            return not self.missing_keys()
        
        @property 
        def title(self) -> str:
            return self._src.get("title")
        @title.setter
        def title(self, value: str):
            self._src["title"] = value
            
        @property 
        def name(self) -> str:
            return self._src.get("name")
        @name.setter
        def name(self, value: str):
            self._src["name"] = value
            
        @property 
        def newsID(self) -> str:
            return self._src.get("identifier")
        @newsID.setter
        def newsID(self, value: str):
            logging.warning(f"Article `identifier` changed from {self._src['identifier']} to {value}.")
            self._src["identifier"] = value
            
        @property 
        def caption(self) -> str:
            return self._src.get("caption")
        @caption.setter
        def caption(self, value: str):
            self._src["caption"] = value
            
        @property 
        def tintColor(self) -> str:
            return self._src.get("tintColor")
        @tintColor.setter
        def tintColor(self, value: str):
            self._src["tintColor"] = value
            
        @property 
        def imageURL(self) -> str:
            return self._src.get("imageURL")
        @imageURL.setter
        def imageURL(self, value: str):
            self._src["imageURL"] = value
            
        @property 
        def appID(self) -> str:
            return self._src.get("appID")
        @appID.setter
        def appID(self, value: str):
            self._src["appID"] = value
            
        @property 
        def date(self) -> str:
            return self._src.get("date")
        @date.setter
        def date(self, value: str):
            self._src["date"] = value
            
        @property 
        def notify(self) -> bool:
            return self._src.get("notify")
        @notify.setter
        def notify(self, value: bool):
            self._src["notify"] = value
            
        @property 
        def url(self) -> str:
            return self._src.get("url")
        @url.setter
        def url(self, value: str):
            self._src["url"] = value
    # End class Article
    
    _requiredKeys = ["name", "identifier", "apps"]
    
    def __init__(self, src: dict | None = None):
        if src is None:
            self._src = {"name": "ExampleSourceName", "identifier": "com.example.identifier", "apps": [], "version": 2}
            logging.info(f"Brand new AltSource created. Please remember to set the following properties: {self._requiredKeys}")
        else:
            self._src = src
            self._src["apps"] = [self.App(app) for app in src["apps"]]
            if "news" in self._src.keys():
                self._src["news"] = [self.Article(art) for art in src["news"]]
            self.version = 2 # set current API version
    
    def to_dict(self) -> dict[str]:
        ret = self._src
        ret["apps"] = [app.to_dict() for app in self.apps]
        if "news" in self._src.keys():
            ret["news"] = [art.to_dict() for art in self.news]
        ret = {k:v for (k,v) in ret.items() if ret.get(k) is not None}
        return ret
    
    def missing_keys(self) -> list[str]:
        """Checks to see if the `AltSource` has all the required values.
        
        Note that if the list is empty, it will evaluate as False.

        Returns:
            list[str]: The list of required keys that are missing. If the `AltSource` is valid, the list will be empty.
        """
        missing_keys = list()
        for key in self._requiredKeys:
            if key not in self._src.keys():
                missing_keys.append(key)
        return missing_keys
    
    def is_valid(self):
        return not self.missing_keys()
    
    @property 
    def name(self) -> str:
        return self._src.get("name")
    @name.setter
    def name(self, value: str):
        self._src["name"] = value
        
    @property 
    def identifier(self) -> str:
        return self._src.get("identifier")
    @identifier.setter
    def identifier(self, value: str):
        logging.warning(f"Source `identifier` changed from {self._src['identifier']} to {value}.")
        self._src["identifier"] = value
        
    @property 
    def sourceURL(self) -> str:
        return self._src.get("sourceURL")
    @sourceURL.setter
    def sourceURL(self, value: str):
        self._src["sourceURL"] = value
    
    @property 
    def apps(self) -> list[App]:
        return self._src.get("apps")
    @apps.setter
    def apps(self, value: list[App]):
        logging.warning("Entire `apps` section has been replaced.")
        self._src["apps"] = value
        
    @property 
    def news(self) -> list[Article]:
        return self._src.get("news")
    @news.setter
    def news(self, value: list[Article]):
        if self.news is not None:
            logging.warning("Entire `news` section has been replaced.")
        self._src["news"] = value
        
    # Start unofficial AltSource attributes.
    
    @property 
    def version(self) -> str:
        """Used to declare the AltSource API version.
        """
        return self._src.get("version")
    @version.setter
    def version(self, value: str):
        self._src["version"] = value
# End class AltSource

class AltSourceManager:
    def __init__(self, filepath: Path | str | None = None, sources_data: list[dict[str]] | None = None, alternate_data: dict[dict[str]] | None = None, prettify: bool = True):
        """Creates a new AltSourceManager instance to maintain an AltSource.

        If no filepath is provided, a brand new blank source is created.

        Args:
            filepath (Path | str | None, optional): The location of the source to be parsed. Defaults to None.
            sources_data (list | None, optional): A list of sources stored in a dictionary format to be used for adding/updating apps, see examples. Defaults to None.
            alternate_data (dict | None, optional): A dictionary containing preferred AltStore app metadata using the bundleID as the key. Defaults to None.
            prettify (bool, optional): If True, the saved json file will be nicely indented and formatted across multiple lines. Defaults to True.
        """
        self.src_data, self.alt_data, self.prettify = sources_data, alternate_data, prettify

        if filepath is None:
            self.path = Path.cwd / "altsource.json"
            self.src = AltSource()
        else:
            if not isinstance(filepath, Path):
                filepath = Path(filepath)
            self.path = filepath
            with open(self.path, "r", encoding="utf-8") as fp:
                self.src = AltSource(json.load(fp))

    def add(self):
        raise NotImplementedError()
        logging.info("x apps added, x news added.")

    def update(self):
        logging.info(f"Starting on {self.src.name}")
        existingAppIDs = [app.appID or app.bundleIdentifier for app in self.src.apps]
        existingNewsIDs = [article.newsID for article in self.src.news]
        updatedAppsCount = addedAppsCount = addedNewsCount = 0

        for data in self.src_data:
            try:
                parser = data["parser"](**data["kwargs"])

                # perform different actions depending on the type of file being parsed
                if isinstance(parser, AltSourceParser):
                    apps = parser.parse_apps(None if data.get("getAllApps") else data.get("ids"))
                    for app in apps:
                        bundleID = app.appID
                        if bundleID in existingAppIDs:
                            # save the old versions property to ensure old versions aren't lost even if the other AltSource isn't tracking them
                            old_vers = self.src.apps[existingAppIDs.index(bundleID)].versions
                            # version.parse() will be a lower value if the version is 'older'
                            if version.parse(app.versions[0].version) > version.parse(self.src.apps[existingAppIDs.index(bundleID)].versions[0].version):
                                updatedAppsCount += 1
                                old_vers.insert(0, app.versions[0])
                                app._update_old_version_util(old_vers[0])
                            app._src["versions"] = old_vers # use the _src property to avoid overwrite warnings
                            self.src.apps[existingAppIDs.index(bundleID)] = app # note that this actually updates the app regardless of whether the version is newer
                        else:
                            addedAppsCount += 1
                            self.src.apps.append(app)

                    if not data.get("ignoreNews"):
                        news = parser.parse_news(None if data.get("getAllNews") else data.get("ids"))
                        for article in news:
                            newsID = article.newsID
                            if newsID in existingNewsIDs:
                                self.src.news[existingNewsIDs.index(newsID)] = article # overwrite existing news article
                            else:
                                addedNewsCount += 1
                                self.src.news.append(article)

                elif isinstance(parser, GithubParser) or isinstance(parser, Unc0verParser):
                    ids = data.get("ids")
                    
                    if ids is None:
                        raise NotImplementedError("Support for updating without specified ids is not supported.")
                    if len(ids) > 1:
                        raise NotImplementedError("Support for parsing multiple ids from one GitHub release is not supported.") # TODO: Fix GithubParser class to be able to process multiple apps using ids to fetch them
                    
                    #fetch_ids = flatten_ids(ids)
                    app_ids = flatten_ids(ids, use_keys=False)
                    #id_conv_tbl = gen_id_parse_table(ids)
                    
                    for i, id in enumerate(app_ids):
                        if not isinstance(id, str):
                            raise ArgumentTypeError("Values in `ids` must all be of type `str`.")
                        if id not in existingAppIDs:
                            logging.warning(f"{id} not found in {self.src.name}. Create an app entry with this bundleID first.")
                            continue

                        app = self.src.apps[existingAppIDs.index(id)]
                        
                        # try to use absoluteVersion if the App contains it
                        if version.parse(app.versions[0].absoluteVersion if app.versions[0].absoluteVersion else app.versions[0].version) < version.parse(parser.version) or (parser.prefer_date and parse_github_datetime(app.versions[0].date) < parse_github_datetime(parser.versionDate)): 
                            metadata = parser.get_asset_metadata()
                            
                            new_ver = AltSource.App.Version()
                            new_ver.absoluteVersion = parser.version
                            new_ver.date = parser.versionDate
                            new_ver.localizedDescription = parser.versionDescription
                            new_ver.size = metadata.get("size")
                            new_ver.version = metadata.get("version") or new_ver.absoluteVersion
                            new_ver.downloadURL = metadata.get("downloadURL")
                            
                            if metadata["bundleIdentifier"] != app.bundleIdentifier:
                                logging.warning(app.name + " BundleID has changed to " + metadata["bundleIdentifier"])
                                app.bundleIdentifier = metadata["bundleIdentifier"]
                                new_ver.localizedDescription += "\n\nNOTE: BundleIdentifier changed in this version and automatic updates have been disabled until manual install occurs."

                            if app.appID is None:
                                app.appID = id
                            
                            app.versions.insert(0, new_ver)
                            app._update_old_version_util(new_ver)
                            updatedAppsCount += 1
                else:
                    raise NotImplementedError("The specified parser class is not supported.")
            except json.JSONDecodeError as err:
                logging.error(f"Unable to process {data.get('ids')}.")
                errstr = str(err).replace('\n', '\n\t') #indent newlines for prettier printing
                logging.error(f"{type(err).__name__}: {errstr[:300]}...") #only print first 300 chars
                continue
            except (requests.RequestException, requests.ConnectionError, GitHubError, AltSourceError) as err:
                logging.error(f"Unable to process {data.get('ids')}.")
                logging.error(f"{type(err).__name__}: {str(err)}")
                continue
            except StopIteration as err:
                logging.error(f"Unable to process {data.get('ids')}.")
                logging.error(f"{type(err).__name__}: Could not find download asset with matching criteria.")
                continue
            
            # end of for loop

        if self.alt_data is not None:
            self.alter_app_info()

        full_src = self.src.to_dict()
        with open(self.path, "w", encoding="utf-8") as fp:
            json.dump(full_src, fp, indent = 2 if self.prettify else None)
            fp.write("\n") # add missing newline to EOF
        logging.info(f"{updatedAppsCount} app(s) updated.")
        logging.info(f"{addedAppsCount} app(s) added, {addedNewsCount} news article(s) added.")

    def alter_app_info(self):
        """Uses the provided alternate source info to automatically modify the data in the json.
        
        Caution: this method bypasses the built-in safety and formatting checks.
        """
        for i in range(len(self.src.apps)):
            bundleID = self.src.apps[i].appID
            if bundleID in self.alt_data.keys():
                for key in self.alt_data[bundleID].keys():
                    if key == "permissions":
                        self.src.apps[i]._src[key] = [AltSource.App.Permission(perm) for perm in self.alt_data[bundleID][key]]
                    elif key == "versions":
                        self.src.apps[i]._src[key] = [AltSource.App.Version(ver) for ver in self.alt_data[bundleID][key]]
                    else:
                        self.src.apps[i]._src[key] = self.alt_data[bundleID][key]

class AltSourceParser:
    """A parser that allows the collection the apps and news articles from an AltSource.
    """
    def __init__(self, filepath: Path | str):
        """
        Args:
            filepath (Path | str): The location of the source to be parsed, strings can be a url or filepath.

        Raises:
            ArgumentTypeError: Occurs if the filepath is not of the accepted types or contains an invalid filepath or url.
        """
        if isinstance(filepath, Path) and filepath.exists():
            with open(filepath, "r", encoding="utf-8") as fp:
                self.src = AltSource(json.load(fp))
        elif isinstance(filepath, str) and is_url(filepath):
            self.src = AltSource(requests.get(filepath).json())
        else:
            try:
                path = Path(filepath)
                with open(path, "r", encoding="utf-8") as fp:
                    self.src = AltSource(json.load(fp))
            except Exception as err:
                raise ArgumentTypeError("Filepath must be a path-like object or a url.")

        if not self.src.is_valid():
            raise AltSourceError("Invalid source formatting.")

    def parse_apps(self, ids: list[str | dict[str, str]] | None = None) -> list[AltSource.App]:
        """Takes a provided list of ids that are `str` provided that `appID` is intended to be equal to `bundleIdentifier` or are type `dict` in the case that they are not the same value. The dict key will be the id being parsed from the other source, assumably the `bundleIdentifier` (but if an `appID` does exist, it will prioritize that) and the predetermined `appID` will be the value. It will then ensure every app has a unique `appID` before returning the list of Apps. This allows the user to change the appID of an app when they parse it.

        Args:
            ids (list[str | dict] | None, optional): _description_. Defaults to None.

        Returns:
            list[AltSource.App]: _description_
        """
        
        processed_apps, processed_keys = list(), list()
        fetch_ids = flatten_ids(ids)
        id_conv_tbl = gen_id_parse_table(ids)
        
        for app in self.src.apps:
            if app.is_valid():
                id = app.appID or app.bundleIdentifier
                if id in processed_keys: # appID / bundleID already exists in list of apps processed (meaning there's a duplicate)
                    index = processed_keys.index(id)
                    if version.parse(processed_apps[index].versions[0].version) > version.parse(app.versions[0].version):
                        continue
                    else:
                        processed_apps[index] = app
                elif ids is None or id in fetch_ids:
                    processed_apps.append(app)
                else:
                    continue # app is not going to be included
                
                if app.appID is None:
                    if ids is None or id in ids:
                        app.appID = app.bundleIdentifier
                    else:
                        app.appID = id_conv_tbl[app.bundleIdentifier]
                        
                processed_keys.append(id)
            else:
                logging.warning(f"Failed to parse invalid app: {app.name}")
            
        # determine if any listed keys were not found in the source
        if len(processed_keys) < len(fetch_ids):
            missing_ids = set([pid for pid in fetch_ids if pid not in processed_keys])
            logging.warning(f"Requested ids not found in AltSource ({self.src.name}): {missing_ids}")
        return processed_apps

    def parse_news(self, ids: list[str] | None = None) -> list[AltSource.Article]:
        processed_news = list()
        if self.src.news is None:
            return processed_news
        for article in self.src.news:
            if article.is_valid():
                if ids is None:
                    processed_news.append(article)
                elif article.newsID in ids:
                    processed_news.append(article)
        return processed_news

class Unc0verParser:
    def __init__(self, url: str = "https://unc0ver.dev/releases.json", ver_parse: Callable = lambda x: x.lstrip("v"), prefer_date: bool = False):
        """Create a new Unc0verParser object that can be used to generate an AltSource.App using the Unc0ver team's personal json release data.

        Args:
            url (str): Link to the Unc0ver API releases json. Defaults to "https://unc0ver.dev/releases.json".
            ver_parse (_type_, optional): A lambda function used as a preprocessor to the listed tag_version before comparing to the stored version. Defaults to lambda x:x.lstrip("v").
            prefer_date (bool, optional): Utilizes the published date to determine if there is an update. Defaults to False.
        """
        self.prefer_date, self.ver_parse = prefer_date, ver_parse
        releases = requests.get(url).json()

        # alter the release tags to match altstore version tags
        releases = [{k: ver_parse(v) if k == "tag_name" else v for (k, v) in x.items()} for x in releases]

        if prefer_date:
            self.data = sorted(releases, key=lambda x: parse_github_datetime(x["published_at"]))[-1] # only grab the most recent release
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

    def get_asset_metadata(self) -> dict[str]:
        """Returns a dictionary containing the downloadURL, size, bundleID, version
        """
        download_url = "https://unc0ver.dev" + self.data["browser_download_url"]
        ipa_path = download_tempfile(download_url)
        metadata = extract_altstore_metadata(ipa_path)
        metadata["downloadURL"] = download_url
        return metadata

class GithubParser:
    def __init__(self, url: str | None = None, repo_author: str | None = None, repo_name: str | None = None, ver_parse: Callable = lambda x: x.lstrip("v"), include_pre: bool = False, prefer_date: bool = False, asset_regex: str = r".*\.ipa", extract_twice: bool = False, upload_ipa_repo: Release | None = None):
        """Create a new GithubParser object that can be used to generate an AltSource.App.
        
        Supply either the api url explicitly or the repo_author and repo_name to automatically find the api url.

        Args:
            url (str | None, optional): Link to the GitHub API json. Defaults to None.
            repo_author (str | None, optional): The repo owner's username. Defaults to None.
            repo_name (str | None, optional): The name of the repo that contains the releases. Defaults to None.
            ver_parse (_type_, optional): A lambda function used as a preprocessor to the listed GitHub tag_version before comparing to the stored version. Defaults to lambda x:x.lstrip("v").
            include_pre (bool, optional): Flag to allow the inclusion of pre-releases, additional changes to `ver_parse` may be required. Defaults to False.
            prefer_date (bool, optional): Utilizes the GitHub published date to determine if there is an update. Defaults to False.
            asset_regex (str, optional): The regex used to match the IPA asset on the releases. Defaults to r".*\.ipa".
            extract_twice (bool, optional): Set True if the IPA has been enclosed in a zip file for distribution. Defaults to False.
            upload_ipa_repo (Release | None, optional): A github3.py Release object used to upload the ipa. Defaults to None.

        Raises:
            GitHubError: If there was an issue using the GitHub API to get the release info.
        """
        self.asset_regex, self.extract_twice, self.upload_ipa_repo, self.prefer_date = asset_regex, extract_twice, upload_ipa_repo, prefer_date
        if url is not None:
            releases = requests.get(url).json()
        elif repo_author is not None and repo_name is not None:
            releases = requests.get("https://api.github.com/repos/{0}/{1}/releases".format(repo_author, repo_name)).json()
        else:
            raise ValueError("Either the api url or both the repo name and author are required.")
        if isinstance(releases, dict):
            if releases.get("message") == "Not Found":
                raise GitHubError("Github Repo not found.")
            elif releases.get("message").startswith("API rate limit exceeded"):
                raise GitHubError("Github API rate limit has been exceeded for this hour.")
            else:
                raise GitHubError("Github API issue: " + releases.get("message"))

        #### Helper methods ####
        def match_asset(release):
            assets = list(filter(lambda x: re.fullmatch(self.asset_regex, x["name"]), release["assets"])) # filters assets to match asset_regex
            asset = sorted(assets, key=lambda x: parse_github_datetime(x["updated_at"]))[-1] # gets most recently updated ipa
            release["asset"] = asset # set asset in the release to only be most recently IPA found
            
        def alter_tag_name(release):
            release["tag_name"] = ver_parse(release["tag_name"])

        #### Parse the correct release ####
        if not include_pre:
            releases = list(filter(lambda x: x["prerelease"] != True, releases)) # filter out prereleases
        if prefer_date:
            # narrow down assets for all releases to make checking the asset timestamp easier
            for x in releases: match_asset(x)
            self.data = sorted(releases, key=lambda x: parse_github_datetime(x["asset"]["updated_at"]))[-1] # only grab the most recent release
            alter_tag_name(self.data)
        else:
            # alter the github release tags to match AltStore version tags
            for x in releases: alter_tag_name(x) 
            self.data = sorted(releases, key=lambda x: version.parse(x["tag_name"]))[-1] # only grab the release with the highest version
            match_asset(self.data)

    @property
    def version(self) -> str:
        return self.data["tag_name"]

    @property
    def versionDate(self) -> str:
        return self.data["asset"]["updated_at"]

    @property
    def versionDescription(self) -> str:
        return "# " + self.data["name"] + "\n\n" + self.data["body"]

    def get_asset_metadata(self) -> dict[str]:
        """Processes the most recently released ipa to get various internal metadata.

        Returns:
            dict: A dictionary containing the downloadURL, size, bundleID, version, and more.
        """
        download_url = self.data["asset"]["browser_download_url"]

        ipa_path = download_tempfile(download_url)
        payload_path = extract_ipa(ipa_path, self.extract_twice)
        if self.extract_twice:
            ipa_path = payload_path.parent / "temp2.ipa"
        plist_path = list(payload_path.rglob("Info.plist"))[0] # locate the Info.plist path within the extracted data
        metadata = extract_altstore_metadata(ipa_path=ipa_path, plist_path=plist_path)
        
        # Uploads the ipa to a separate GitHub repository after its been processed
        if self.upload_ipa_repo is not None:
            download_url = upload_ipa_github(ipa_path, self.upload_ipa_repo, name=metadata["bundleIdentifier"], ver=metadata["version"])
        
        metadata["downloadURL"] = download_url
        return metadata

class AltSourceError(Exception):
    """Base exception for AltSource parsing."""
    pass

class GitHubError(AltSourceError):
    """Occurs when there is an error accessing the GitHub API."""
    pass

class ArgumentTypeError(AltSourceError):
    """Occurs when an argument is not of the correct type."""
    pass
