import json
import requests

def parseAltSourceApps(src: dict, ids: list = None) -> list:
    apps = []
    for app in src["apps"]:
        if ids is None or app["bundleIdentifier"] in ids:
            apps.append(app)
    return apps

def parseAltSourceNews(src: dict, ids: list = None) -> list:
    news = []
    for article in src["news"]:
        if ids is None or article.get("appID") in ids or article.get("identifier") in ids:
            news.append(article)
    return news

def validApp(app: dict) -> bool:
    requiredKeys = ["name", "bundleIdentifier", "developerName", "version", "versionDate", "downloadURL", "localizedDescription", "iconURL", "size"]
    for key in requiredKeys:
        if key not in app:
            return False
    return True

def validNews(article: dict) -> bool:
    requiredKeys = ["title", "identifier", "caption", "date"]
    for key in requiredKeys:
        if key not in article:
            return False
    return True

def alterAppInfo(apps: list, altAppData: dict) -> list:
    for i in range(len(apps)):
        bundleID = apps[i]["bundleIdentifier"]
        if bundleID in altAppData.keys():
            for key in altAppData[bundleID].keys():
                apps[i][key] = altAppData[bundleID][key]
    return apps

# Reads through a list of dicts and grabs value of the specified key from each
def parseIdentifiers(lst: list, key: str) -> list:
    ids = []
    for item in lst:
        ids.append(item[key])
    return ids

def combineSourcesIntoOne(fileName: str, sourceName: str, sourceIdentifier: str, sourceURL: str, sourcesData: list, alternateAppData: dict = None, prettify: bool = False):
    primarySource = {
        "name": sourceName,
        "identifier": sourceIdentifier,
        "sourceURL": sourceURL,
        "apps": [],
        "news": [],
        "userInfo": {}
    }
    for data in sourcesData:
        try:
            response = requests.get(data["url"])
            src = json.loads(response.text)
        except (json.JSONDecodeError, requests.RequestException) as e:
            print("Error fetching source: " + data["url"] + "\n{}: ".format(type(e).__name__) + str(e) + "\nThis source will not be processed.")
            continue
        # Parse the apps, and perform any data alterations
        readApps = parseAltSourceApps(src, None if data.get("getAllApps") else data.get("ids"))
        if alternateAppData is not None:
            readApps = alterAppInfo(readApps, alternateAppData)
        # Insert each app into the primary source
        for app in readApps:
            # Validate app to make sure all required arguments are found
            if not validApp(app):
                print("App invalid: " + app.get("bundleIdentifier"))
                continue
            primarySource["apps"].append(app)
        # Then do the same process with the news
        if not data.get("ignoreNews"):
            readNews = parseAltSourceNews(src, None if data.get("getAllNews") else data.get("ids"))
            for article in readNews:
                if not validNews(article):
                    print("News invalid: " + article.get("identifier"))
                    continue
                primarySource["news"].append(article)

    # Should probably do some evaluating to see if there were actually any changes made.
    with open(fileName, "w") as file:
        json.dump(primarySource, file, indent = 2 if prettify else None)
        file.write("\n") # add missing newline to EOF
        print(primarySource["name"] + " successfully created.")

def updateFromSources(fileName: str, sourcesData: list, alternateAppData: dict = None, prettify: bool = False):
    primarySource: dict = {}
    with open(fileName, "r") as file:
        primarySource = json.load(file)
    existingAppIDs = parseIdentifiers(primarySource["apps"], "bundleIdentifier")
    existingNewsIDs = parseIdentifiers(primarySource["news"], "identifier")
    for data in sourcesData:
        try:
            response = requests.get(data["url"])
            src = json.loads(response.text)
        except (json.JSONDecodeError, requests.RequestException) as e:
            print("Error fetching source: " + data["url"] + "\n{}: ".format(type(e).__name__) + str(e) + "\nUpdates to this source will not be processed.")
            continue
        # Parse the apps, and perform any data alterations
        readApps = parseAltSourceApps(src, None if data.get("getAllApps") else data.get("ids"))
        if alternateAppData is not None:
            readApps = alterAppInfo(readApps, alternateAppData)
        # Insert each app into the correct location: Either the position of the existing app with matching bundleID, or add to the end of the list
        for app in readApps:
            # Validate app to make sure all required arguments are found
            if not validApp(app):
                print("App invalid: " + app.get("bundleIdentifier"))
                continue
            bundleID = app["bundleIdentifier"]
            if bundleID in existingAppIDs:
                primarySource["apps"][existingAppIDs.index(bundleID)] = app # overwrite existing app
            else:
                primarySource["apps"].append(app)
        # Then do the same process with the news
        if not data.get("ignoreNews"):
            readNews = parseAltSourceNews(src, None if data.get("getAllNews") else data.get("ids"))
            for article in readNews:
                if not validNews(article):
                    print("News invalid: " + article.get("identifier"))
                    continue
                newsID = article["identifier"]
                if newsID in existingNewsIDs:
                    primarySource["news"][existingNewsIDs.index(newsID)] = article # overwrite existing news article
                else:
                    primarySource["news"].append(article)

    # Should probably do some evaluating to see if there were actually any changes made.
    with open(fileName, "w") as file:
        json.dump(primarySource, file, indent = 2 if prettify else None)
        file.write("\n") # add missing newline to EOF
        print(primarySource["name"] + " successfully updated.")
