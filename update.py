from sourceUtil import AltSourceManager, AltSourceParser, GithubParser

sourcesData = [
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://techmunchies.net/.netlify/functions/altstore"},
        "ids": ["org.ppsspp.ppsspp"], # Optional: Loads only the apps and news with an id (or appID in case of news) listed here. If missing or set to None, all apps and news will be loaded
        "ignoreNews": True, # Optional: Overrides everything else to prevent loading the news
        "getAllNews": False, # Optional: You can get all news regardless of ids
        "getAllApps": False # Optional: You can also get all apps regardless of ids, although not recommended
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://altstore.oatmealdome.me"},
        "ids": ["me.oatmealdome.dolphinios-njb", "me.oatmealdome.DolphiniOS-njb-patreon-beta"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "quarksource.json"},
        "ids": ["science.xnu.undecimus", "net.hollr.Provenance4", "com.libretro.dist.ios.RetroArch", "com.louisanslow.record", "org.scummvm.scummvm", "net.namedfork.minivmac", "com.dry05.filzaescaped11-12", "com.virtualapplications.play"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://theodyssey.dev/altstore/odysseysource.json"},
        "ids": ["org.coolstar.odyssey"]
    },
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "https://taurine.app/altstore/taurinestore.json"},
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
        "kwargs": {"repo_author": "Provenance-Emu", "repo_name": "Provenance"},
        "ids": ["com.provenance-emu.provenance"]
    },
    {
        "parser": GithubParser,
        "kwargs": {"repo_author": "brandonplank", "repo_name": "flappybird"},
        "ids": ["org.brandonplank.flappybird15"]
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
    }
]
alternateAppData = {
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
    }
}

quantumsrc = AltSourceManager("quantumsource.json", sourcesData, alternateAppData, prettify=False) # if prettify is true, output will have indents and newlines
try:
    quantumsrc.update()
except Exception as err:
    print("Unable to update Quantum Source.")
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
    print("Unable to update AltStore Complete.")
    print(f"{type(err).__name__}: {str(err)}")

sourcesData = [
    {
        "parser": AltSourceParser,
        "kwargs": {"filepath": "quarksource++.json"},
        "ids": ["com.google.ios.youtube", "com.crunchyroll.iphone", "com.duolingo.DuolingoMobile", "com.deezer.Deezer", "com.spotify.client", "com.atebits.Tweetie2", "syto203.reddit.pp", "com.antique.Popcorn-iOS", "mediaboxhd.event.2", "comicreader.net.ios", "com.channelsapp.channels", "com.burbn.instagram", "com.Lema.Michael.InstagramApp", "net.whatsapp.WhatsApp", "com.hotdog.popcorntime81.ios", "tv.twitch"]
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
    }
]

quantumsrc_plus = AltSourceManager("quantumsource++.json", sourcesData, prettify=False)
try:
    quantumsrc_plus.update()
except Exception as err:
    print("Unable to update Quantum Source Plus.")
    print(f"{type(err).__name__}: {str(err)}")
