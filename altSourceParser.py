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
        if ids is None or article.get("appID") in ids:
            news.append(article)
    return news

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

def combineSourcesV1(fileName: str, primarySource: dict, sourcesData: list, alternateAppData: dict = None):
    apps = []
    news = []
    for data in sourcesData:
        try:
            response = requests.get(data["url"])
            src = json.loads(response.text)
        except Exception as e:
            print("Error fetching source: " + data["url"] + "\n" + str(e) + "\nUsing existing data instead.")
            with open(fileName, "r") as file:
                src = json.load(file)
            # This method still doesn't work quite right. If I turn them False, I might get less apps than intended. If I turn them True, I am guaranteed duplicate apps.
            data["getAllApps"] = False
            data["getAllNews"] = False
        try:
            # Parse apps first
            readApps = parseAltSourceApps(src, None if data.get("getAllApps") else data["ids"])
            if alternateAppData is not None:
                readApps = alterAppInfo(readApps, alternateAppData)
            apps.append(readApps)
            # Then parse news if wanted
            if not data.get("ignoreNews"):
                news.append(parseAltSourceNews(src, None if data.get("getAllNews") else data["ids"]))
        except Exception as e:
            print("Error parsing source: " + data["url"] + "\n" + str(e) + "\nUpdate aborted.")
            return

    primarySource["apps"] = apps
    primarySource["news"] = news

    # Should probably do some evaluating to see if there were actually any changes made.
    with open(fileName, "w") as file:
        json.dump(primarySource, file)
        print(primarySource["name"] + " successfully updated.")

def combineSources(fileName: str, sourcesData: list, alternateAppData: dict = None, prettify: bool = False):
    primarySource: dict = {}
    with open(fileName, "r") as file:
        primarySource = json.load(file)
    existingAppIDs = parseIdentifiers(primarySource["apps"], "bundleIdentifier")
    existingNewsIDs = parseIdentifiers(primarySource["news"], "identifier")
    for data in sourcesData:
        try:
            response = requests.get(data["url"])
            src = json.loads(response.text)
        except Exception as e:
            print("Error fetching source: " + data["url"] + "\n{}: ".format(type(e).__name__) + str(e) + "\nUpdates to this source will not be processed.")
            continue
        try:
            # Parse the apps, and perform any data alterations
            readApps = parseAltSourceApps(src, None if data.get("getAllApps") else data["ids"])
            if alternateAppData is not None:
                readApps = alterAppInfo(readApps, alternateAppData)
            # Insert each app into the correct location: Either the position of the existing app with matching bundleID, or add to the end of the list
            for app in readApps:
                bundleID = app["bundleIdentifier"]
                if bundleID in existingAppIDs:
                    primarySource["apps"][existingAppIDs.index(bundleID)] = app # overwrite existing application
                else:
                    primarySource["apps"].append(app)
            # Then do the same process with the news
            if not data.get("ignoreNews"):
                readNews = parseAltSourceNews(src, None if data.get("getAllNews") else data["ids"])
                for article in readNews:
                    newsID = article["identifier"]
                    if newsID in existingNewsIDs:
                        primarySource["news"][existingNewsIDs.index(newsID)] = article # overwrite existing application
                    else:
                        primarySource["news"].append(article)

        except Exception as e:
            print("Error parsing source: " + data["url"] + "\n" + str(e) + "\nUpdates to this source will not be processed.")
            continue

    # Should probably do some evaluating to see if there were actually any changes made.
    with open(fileName, "w") as file:
        json.dump(primarySource, file, indent = 2 if prettify else None)
        file.write("\n") # add missing newline to EOF
        print(primarySource["name"] + " successfully updated.")
