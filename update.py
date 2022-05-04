from sourceUtil import AltSourceManager, AltSourceParser, GithubParser, Unc0verParser
import os
from github3 import login
from github3.exceptions import GitHubError, ResponseError

try:
  g_repo, g_release = None, None
  token = os.environ["GITHUB_TOKEN"]
  gh = login(token=token)
  g_repo = gh.repository_with_id(321891219)
  g_release = g_repo.latest_release()
except KeyError as err:
  print(f"Could not find GitHub Token.")
  print(f"{type(err).__name__}: {str(err)}")
except GitHubError as err:
  print(f"Github Authentication failed.")
  print(f"{type(err).__name__}: {str(err)}")

sourcesData = [
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://altstore.oatmealdome.me"},
        "ids": ["me.oatmealdome.dolphinios-njb", "me.oatmealdome.DolphiniOS-njb-patreon-beta"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "quarksource.json"},
        "ids": ["com.libretro.dist.ios.RetroArch", "com.louisanslow.record", "org.scummvm.scummvm", "com.dry05.filzaescaped11-12", "com.virtualapplications.play"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://provenance-emu.com/apps.json"},
        "ids": ["org.provenance-emu.provenance"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://theodyssey.dev/altstore/odysseysource.json"},
        "ids": ["org.coolstar.odyssey"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "Odyssey-Team", "repo_name": "Taurine"},
        #"kwargs": {"filepath": "https://taurine.app/altstore/taurinestore.json"},
        "ids": ["com.odysseyteam.taurine"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://alt.getutm.app"},
        "ids": ["com.utmapp.UTM", "com.utmapp.UTM-SE"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://demo.altstore.io"},
        "ids": ["com.rileytestut.GBA4iOS"]
    },
    {
        "parser": AltSourceParser,
        #"kwargs": {"repo_author": "flyinghead", "repo_name": "flycast"},
        "kwargs": {"filepath": "https://flyinghead.github.io/flycast-builds/altstore.json"},
        "ids": ["com.flyinghead.Flycast"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "iNDS-Team", "repo_name": "iNDS"},
        "ids": ["net.nerd.iNDS"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "yoshisuga", "repo_name": "MAME4iOS"},
        "ids": ["com.example.mame4ios"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "brandonplank", "repo_name": "flappybird"},
        "ids": ["org.brandonplank.flappybird15"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "nspire-emus", "repo_name": "firebird"},
        "ids": ["com.firebird.firebird-emu"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "Wh0ba", "repo_name": "XPatcher"},
        "ids": ["com.wh0ba.xpatcher"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "litchie", "repo_name": "dospad"},
        "ids": ["com.litchie.idosgames"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "QuarkSources", "repo_name": "ppsspp-builder"},
        "ids": ["org.ppsspp.ppsspp"]
    },
    {
        "parser": Unc0verParser,
        "kwargs": {"url": "https://unc0ver.dev/releases.json"},
        "ids": ["science.xnu.undecimus"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "ianclawson", "repo_name": "Delta-iPac-Edition"},
        "ids": ["com.ianclawson.DeltaPacEdition"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "zydeco", "repo_name": "minivmac4ios", "asset_regex": r".*\.ipa\.zip", "extract_twice": True,
          "upload_ipa_kwargs": {"github_release": g_release, "name": "minivmac4ios"}
        },
        "ids": ["net.namedfork.minivmac"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "T-Pau", "repo_name": "Ready", "ver_parse": lambda x: x.replace("release-", "")},
        "ids": ["at.spiderlab.c64"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "yoshisuga", "repo_name": "activegs-ios"},
        "ids": ["com.yoshisuga.activeGS"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "zzanehip", "repo_name": "The-OldOS-Project"},
        "ids": ["com.zurac.OldOS"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "n3d1117", "repo_name": "appdb"},
        "ids": ["it.ned.appdb-ios"]
    }
]
alternateAppData = {
    "com.flyinghead.Flycast": {
      "localizedDescription": "Flycast is a multi-platform Sega Dreamcast, Naomi and Atomiswave emulator derived from reicast.\nInformation about configuration and supported features can be found on TheArcadeStriker's [flycast wiki](https://github.com/TheArcadeStriker/flycast-wiki/wiki).",
      "screenshotURLs": []
    },
    "org.ppsspp.ppsspp": {
        "tintColor": "#21486b",
        "subtitle": "PlayStation Portable games on iOS.",
        "screenshotURLs": [
            "https://i.imgur.com/CWl6GgH.png",
            "https://i.imgur.com/SxmN1M0.png",
            "https://i.imgur.com/sGWgR6z.png",
            "https://i.imgur.com/AFKTdmZ.png"
        ],
        "iconURL": "https://i.imgur.com/JP0Fncv.png"
    },
    "com.rileytestut.GBA4iOS": {
        "iconURL": "https://i.imgur.com/SBrqO9g.png",
        "screenshotURLs": [
            "https://i.imgur.com/L4H0yM3.png",
            "https://i.imgur.com/UPGYLVr.png",
            "https://i.imgur.com/sWpUAii.png",
            "https://i.imgur.com/UwnDXRc.png"
          ]
    },
    "org.provenance-emu.provenance": {
        "localizedDescription": "Provenance is a multi-system emulator frontend for a plethora of retro gaming systems. You can keep all your games in one place, display them with cover art, and play to your heart's content.\n\nSystems Supported:\n\n• Atari\n  - 2600\n  - 5200\n  - 7800\n  - Lynx\n  - Jaguar\n• Bandai\n  - WonderSwan / WonderSwan Color\n• NEC\n  - PC Engine / TurboGrafx-16 (PCE/TG16)\n  - PC Engine Super CD-ROM² System / TurboGrafx-CD\n  - PC Engine SuperGrafx\n  - PC-FX\n• Nintendo\n  - Nintendo Entertainment System / Famicom (NES/FC)\n  - Famicom Disk System\n  - Super Nintendo Entertainment System / Super Famicom (SNES/SFC)\n  - Game Boy / Game Boy Color (GB/GBC)\n  - Virtual Boy\n  - Game Boy Advance (GBA)\n  - Pokémon mini\n• Sega\n  - SG-1000\n  - Master System\n  - Genesis / Mega Drive\n  - Game Gear\n  - CD / MegaCD\n  - 32X\n• SNK\n  - Neo Geo Pocket / Neo Geo Pocket Color\n• Sony\n  - PlayStation (PSX/PS1)",
        "tintColor": "#1c7cf3",
        "permissions": [
            {
              "type": "camera",
              "usageDescription": "Used for album artwork."
            },
            {
              "type": "photos",
              "usageDescription": "Provenance can set custom artworks from your photos or save screenshots to your photos library."
            },
            {
              "type": "music",
              "usageDescription": "This will let you play your imported music on Spotify."
            },
            {
              "type": "bluetooth",
              "usageDescription": "Provenance uses Bluetooth to support game controllers."
            },
            {
              "type": "background-fetch",
              "usageDescription": "Provenance can continue running while in the background."
            },
            {
              "type": "background-audio",
              "usageDescription": "Provenance can continue playing game audio while in the background."
            }
        ]
    }
}

quantumsrc = AltSourceManager("quantumsource.json", sourcesData, alternateAppData, prettify=False) # if prettify is true, output will have indents and newlines
try:
    quantumsrc.update()
except Exception as err:
    print(f"Unable to update {quantumsrc.name}.")
    print(f"{type(err).__name__}: {str(err)}")

sourcesData = [
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://apps.altstore.io"},
        "ids": ["com.rileytestut.AltStore", "com.rileytestut.AltStore.Beta", "com.rileytestut.Delta", "com.rileytestut.Delta.Beta", "com.rileytestut.Clip", "com.rileytestut.Clip.Beta"],
        "getAllNews": True
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://alpha.altstore.io"},
        "ids": ["com.rileytestut.AltStore.Alpha", "com.rileytestut.Delta.Alpha"],
        "getAllNews": True
    }
]
alternateAppData = {
    "com.rileytestut.AltStore.Beta": {
        "name": "AltStore (Beta)",
        "beta": False
    },
    "com.rileytestut.Delta.Beta": {
        "name": "Delta (Beta)",
        "beta": False
    },
    "com.rileytestut.Clip.Beta": {
        "name": "Clip (Beta)",
        "beta": False
    }
}

alt_complete = AltSourceManager("altstore-complete.json", sourcesData, alternateAppData, prettify=False)
try:
    alt_complete.update()
except Exception as err:
    print(f"Unable to update {alt_complete.name}.")
    print(f"{type(err).__name__}: {str(err)}")

sourcesData = [
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "quarksource++.json"},
        "ids": ["com.crunchyroll.iphone", "com.duolingo.DuolingoMobile", "com.deezer.Deezer", "com.spotify.client", "syto203.reddit.pp", "com.antique.Popcorn-iOS", "mediaboxhd.event.2", "comicreader.net.ios", "com.channelsapp.channels", "com.Lema.Michael.InstagramApp", "net.whatsapp.WhatsApp", "com.hotdog.popcorntime81.ios", "tv.twitch"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "quarksource-cracked.json"},
        "ids": ["com.grailr.CARROTweather", "com.wolframalpha.wolframalpha", "com.firecore.infuse", "com.stey", "com.luma-touch.LumaFusion"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://9ani.app/api/altstore"},
        "ids": ["com.marcuszhou.NineAnimator"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "Paperback-iOS", "repo_name": "app", "ver_parse": lambda x: x.replace("-r", ".").lstrip("v")}, #ver_parse allows you to specify how to github tag should be processed before comparing to AltStore version tags
        "ids": ["com.faizandurrani.paperback.ios"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "tatsuz0u", "repo_name": "EhPanda"},
        "ids": ["app.ehpanda"]
    },
    #{
    #    "parser": AltSourceParser,
    #    "kwargs": {"filepath": "https://raw.githubusercontent.com/ytjailed/ytjailed.github.io/main/apps.json"},
    #    "ids": ["com.google.ios.youtube", "com.atebits.Tweetie2"]
    #},
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://repos.yattee.stream/alt/apps.json"},
        "ids": ["stream.yattee.app"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://qnblackcat.github.io/AltStore/apps.json"},
        "ids": ["com.burbn.instagram", "com.facebook.Facebook", "com.google.ios.youtubecercubelegacy", "com.atebits.Tweetie2", "com.google.ios.youtubecercube", "com.google.ios.youtube"]
    }
]
alternateAppData = {
    "com.google.ios.youtubecercube": {
        "permissions": [
            {
              "type": "camera",
              "usageDescription": "This lets you create videos using the app."
            },
            {
              "type": "photos",
              "usageDescription": "This lets you upload videos you've already created."
            },
            {
              "type": "bluetooth",
              "usageDescription": "YouTube needs bluetooth access to scan for nearby Cast devices."
            },
            {
              "type": "contacts",
              "usageDescription": "Your contacts will be sent to YouTube servers to help you find friends to share videos with."
            },
            {
              "type": "network",
              "usageDescription": "Access to your network allows YouTube to discover and connect to devices such as your TV."
            },
            {
              "type": "music",
              "usageDescription": "This lets you add your own audio files to your videos."
            },
            {
              "type": "microphone",
              "usageDescription": "This lets you include audio with your videos and search using your voice."
            },
            {
              "type": "location",
              "usageDescription": "Makes it easier for you to attach location information to your videos and live streams and allows for features such as improved recommendations and ads."
            },
            {
              "type": "background-fetch",
              "usageDescription": "YouTube can continue running while in the background."
            },
            {
              "type": "background-audio",
              "usageDescription": "YouTube can continue playing audio while in the background."
            }
        ]
    },
    "com.google.ios.youtube": {
        "permissions": [
            {
              "type": "camera",
              "usageDescription": "This lets you create videos using the app."
            },
            {
              "type": "photos",
              "usageDescription": "This lets you upload videos you've already created."
            },
            {
              "type": "bluetooth",
              "usageDescription": "YouTube needs bluetooth access to scan for nearby Cast devices."
            },
            {
              "type": "contacts",
              "usageDescription": "Your contacts will be sent to YouTube servers to help you find friends to share videos with."
            },
            {
              "type": "network",
              "usageDescription": "Access to your network allows YouTube to discover and connect to devices such as your TV."
            },
            {
              "type": "music",
              "usageDescription": "This lets you add your own audio files to your videos."
            },
            {
              "type": "microphone",
              "usageDescription": "This lets you include audio with your videos and search using your voice."
            },
            {
              "type": "location",
              "usageDescription": "Makes it easier for you to attach location information to your videos and live streams and allows for features such as improved recommendations and ads."
            },
            {
              "type": "background-fetch",
              "usageDescription": "YouTube can continue running while in the background."
            },
            {
              "type": "background-audio",
              "usageDescription": "YouTube can continue playing audio while in the background."
            }
        ]
    }
}

quantumsrc_plus = AltSourceManager("quantumsource++.json", sourcesData, alternateAppData, prettify=False)
try:
    quantumsrc_plus.update()
except Exception as err:
    print(f"Unable to update {quantumsrc_plus.name}.")
    print(f"{type(err).__name__}: {str(err)}")
