import altSourceParser

sourcesData = [
    {
        "url": "https://techmunchies.net/.netlify/functions/altstore",
        "ids": ["org.ppsspp.ppsspp"],
        "ignoreNews": True
    },
    {
        "url": "https://altstore.oatmealdome.me",
        "ids": ["me.oatmealdome.dolphinios-njb", "me.oatmealdome.DolphiniOS-njb-patreon-beta"]
    },
    {
        "url": "https://quarksources.github.io/quarksource.json",
        "ids": ["net.nerd.iNDS", "com.example.mame4ios", "science.xnu.undecimus", "ru.nonamedude.iTorrent", "com.rileytestut.GBA4iOS", "com.provenance-emu.provenance", "net.hollr.Provenance4", "com.libretro.dist.ios.RetroArch", "org.brandonplank.flappybird", "com.louisanslow.record", "org.scummvm.scummvm", "com.osy86.UTM", "net.namedfork.minivmac", "com.dry05.filzaescaped11-12", "com.wh0ba.xpatcher", "com.virtualapplications.play"]
    },
    {
        "url": "https://theodyssey.dev/altstore/odysseysource.json",
        "ids": ["org.coolstar.odyssey"]
    },
    {
        "url": "https://alt.getutm.app",
        "ids": ["com.utmapp.UTM"]
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
    }
}

altSourceParser.combineSources("quantumsource.json", sourcesData, alternateAppData)

sourcesData = [
    {
        "url": "https://apps.altstore.io",
        "ids": ["com.rileytestut.AltStore", "com.rileytestut.AltStore.Beta", "com.rileytestut.Delta", "com.rileytestut.Delta.Beta", "com.rileytestut.Clip", "com.rileytestut.Clip.Beta"],
        "getAllNews": True,
        "getAllApps": False # This is also an option, although not recommended
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

altSourceParser.combineSources("altstore-complete.json", sourcesData, alternateAppData)
