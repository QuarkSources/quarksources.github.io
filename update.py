import altSourceParser

sourcesData = [
    {
        "url": "https://techmunchies.net/.netlify/functions/altstore",
        "ids": ["org.ppsspp.ppsspp"], # Optional: Loads only the apps and news with an id (or appID in case of news) listed here. If missing or set to None, all apps and news will be loaded
        "ignoreNews": True, # Optional: Overrides everything else to prevent loading the news
        "getAllNews": False, # Optional: You can get all news regardless of ids
        "getAllApps": False # Optional: You can also get all apps regardless of ids, although not recommended
    },
    {
        "url": "https://altstore.oatmealdome.me",
        "ids": ["me.oatmealdome.dolphinios-njb", "me.oatmealdome.DolphiniOS-njb-patreon-beta"]
    },
    {
        "url": "https://quarksources.github.io/quarksource.json",
        "ids": ["net.nerd.iNDS", "com.example.mame4ios", "science.xnu.undecimus", "ru.nonamedude.iTorrent", "com.provenance-emu.provenance", "net.hollr.Provenance4", "com.libretro.dist.ios.RetroArch", "org.brandonplank.flappybird", "com.louisanslow.record", "org.scummvm.scummvm", "net.namedfork.minivmac", "com.dry05.filzaescaped11-12", "com.wh0ba.xpatcher", "com.virtualapplications.play"]
    },
    {
        "url": "https://theodyssey.dev/altstore/odysseysource.json",
        "ids": ["org.coolstar.odyssey"]
    },
    {
        "url": "https://alt.getutm.app",
        "ids": ["com.utmapp.UTM"]
    },
    {
        "url": "https://demo.altstore.io",
        "ids": ["com.rileytestut.GBA4iOS"]
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

altSourceParser.updateFromSources("quantumsource.json", sourcesData, alternateAppData, prettify=False) # if prettify is true, output will have indents and newlines

sourcesData = [
    {
        "url": "https://apps.altstore.io",
        "ids": ["com.rileytestut.AltStore", "com.rileytestut.AltStore.Beta", "com.rileytestut.Delta", "com.rileytestut.Delta.Beta", "com.rileytestut.Clip", "com.rileytestut.Clip.Beta"],
        "getAllNews": True
    },
    {
        "url": "https://alpha.altstore.io",
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

altSourceParser.updateFromSources("altstore-complete.json", sourcesData, alternateAppData)

sourcesData = [
    {
        "url": "https://quarksources.github.io/quarksource%2B%2B.json",
        "ids": ["com.google.ios.youtube", "com.crunchyroll.iphone", "com.duolingo.DuolingoMobile", "com.deezer.Deezer", "com.spotify.client", "com.atebits.Tweetie2", "syto203.reddit.pp", "com.FaizanDurrani.Paperback", "com.antique.Popcorn-iOS", "mediaboxhd.event.2", "comicreader.net.ios", "com.channelsapp.channels", "com.burbn.instagram", "com.Lema.Michael.InstagramApp", "net.whatsapp.WhatsApp"]
    },
    {
        "url": "https://quarksources.github.io/quarksource-cracked.json",
        "ids": ["com.grailr.CARROTweather", "com.wolframalpha.wolframalpha", "com.firecore.infuse", "com.stey", "com.luma-touch.LumaFusion"]
    },
    {
        "url": "https://9ani.app/api/altstore",
        "ids": ["com.marcuszhou.NineAnimator"]
    }
]

altSourceParser.updateFromSources("quantumsource++.json", sourcesData)
