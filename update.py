import logging

from altparse import AltSourceManager, Parser, altsource_from_file

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

########################
## QUANTUM SOURCE
########################

sourcesData = [
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "ish-app", "repo_name": "ish", "prefer_date": True, "include_pre": True},
        "ids": ["app.ish.iSH"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "zhuowei", "repo_name": "WDBFontOverwrite"},
        "ids": ["com.worthdoingbadly.WDBRemoveThreeAppLimit"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "vcmi", "repo_name": "vcmi"},
        "ids": ["com.vcmi.VCMI"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "lonkelle", "repo_name": "deltroid"},
        "ids": ["com.rileytestut.Deltroid"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://altstore.oatmealdome.me"},
        "ids": ["me.oatmealdome.dolphinios-njb", "me.oatmealdome.DolphiniOS-njb-patreon-beta"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "quarksource.json"},
        "ids": ["com.libretro.RetroArchiOS11", "com.louisanslow.record", "org.scummvm.scummvm", "com.dry05.filzaescaped11-12", "com.virtualapplications.play"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://provenance-emu.com/apps.json"},
        "ids": ["org.provenance-emu.provenance"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://theodyssey.dev/altstore/odysseysource.json"},
        "ids": ["org.coolstar.odyssey"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "Odyssey-Team", "repo_name": "Taurine"},
        # "kwargs": {"filepath": "https://taurine.app/altstore/taurinestore.json"},
        "ids": ["org.coolstar.taurine"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://alt.getutm.app"},
        "ids": ["com.utmapp.UTM", "com.utmapp.UTM-SE"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://demo.altstore.io"},
        "ids": ["com.rileytestut.GBA4iOS"]
    },
    {
        "parser": Parser.ALTSOURCE,
        # "kwargs": {"repo_author": "flyinghead", "repo_name": "flycast"},
        "kwargs": {"filepath": "https://flyinghead.github.io/flycast-builds/altstore.json"},
        "ids": ["com.flyinghead.Flycast"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "iNDS-Team", "repo_name": "iNDS"},
        "ids": ["net.nerd.iNDS"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "yoshisuga", "repo_name": "MAME4iOS"},
        "ids": ["com.example.mame4ios"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "nspire-emus", "repo_name": "firebird"},
        "ids": ["com.firebird.firebird-emu"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "Wh0ba", "repo_name": "XPatcher"},
        "ids": ["com.wh0ba.xpatcher"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "litchie", "repo_name": "dospad"},
        "ids": ["com.litchie.idosgames"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "QuarkSources", "repo_name": "ppsspp-builder"},
        "ids": ["org.ppsspp.ppsspp"]
    },
    {
        "parser": Parser.UNC0VER,
        "kwargs": {"url": "https://unc0ver.dev/releases.json"},
        "ids": ["science.xnu.undecimus"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "ianclawson", "repo_name": "Delta-iPac-Edition"},
        "ids": ["com.ianclawson.DeltaPacEdition"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "zydeco", "repo_name": "minivmac4ios"},
        ## This is the previous kwargs required when this application was distributed as a zipped .ipa file ##
        # "kwargs": {"repo_author": "zydeco", "repo_name": "minivmac4ios", "asset_regex": r".*\.ipa\.zip", "extract_twice": True, "upload_ipa_repo": g_release},
        "ids": ["net.namedfork.minivmac"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "T-Pau", "repo_name": "Ready", "ver_parse": lambda x: x.replace("release-", "")},
        "ids": ["at.spiderlab.c64"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "yoshisuga", "repo_name": "activegs-ios"},
        "ids": ["com.yoshisuga.activeGS"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "zzanehip", "repo_name": "The-OldOS-Project"},
        "ids": ["com.zurac.OldOS"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "n3d1117", "repo_name": "appdb", "prefer_date": True},
        "ids": ["it.ned.appdb-ios"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://pokemmo.eu/altstore/"},
        "ids": ["eu.pokemmo.client"]
    }
]
alternateAppData = {
    "eu.pokemmo.client": {
        "beta": False
    },
    "com.flyinghead.Flycast": {
        "localizedDescription": "Flycast is a multi-platform Sega Dreamcast, Naomi and Atomiswave emulator derived from reicast.\nInformation about configuration and supported features can be found on TheArcadeStriker's [flycast wiki](https://github.com/TheArcadeStriker/flycast-wiki/wiki).",
        "screenshotURLs": ["https://i.imgur.com/47KjD5a.png", "https://i.imgur.com/MfhD1h1.png", "https://i.imgur.com/wO88IVP.png"]
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

src = altsource_from_file("quantumsource.json")
quantumsrc = AltSourceManager(src, sourcesData)
try:
    quantumsrc.update()
    quantumsrc.alter_app_info(alternateAppData)
    quantumsrc.save()
    quantumsrc.save(alternate_dir="dist/quantumsource.min.json",prettify=False)
except Exception as err:
    logging.error(f"Unable to update {quantumsrc.src.name}.")
    logging.error(f"{type(err).__name__}: {str(err)}")

########################
## ALTSTORE COMPLETE
########################

sourcesData = [
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://apps.altstore.io"},
        "ids": ["com.rileytestut.AltStore", "com.rileytestut.AltStore.Beta", "com.rileytestut.Delta", "com.rileytestut.Delta.Beta", "com.rileytestut.Clip", "com.rileytestut.Clip.Beta"],
        "getAllNews": True
    },
    {
        "parser": Parser.ALTSOURCE,
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

src = altsource_from_file("altstore-complete.json")
alt_complete = AltSourceManager(src, sourcesData)
try:
    alt_complete.update()
    alt_complete.alter_app_info(alternateAppData)
    alt_complete.save()
    alt_complete.save(alternate_dir="dist/altstore-complete.min.json",prettify=False)
except Exception as err:
    logging.error(f"Unable to update {alt_complete.src.name}.")
    logging.error(f"{type(err).__name__}: {str(err)}")

########################
## QUANTUM SOURCE++
########################

sourcesData = [
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "quarksource++.json"},
        "ids": ["com.crunchyroll.iphone", "com.duolingo.DuolingoMobile", "com.deezer.Deezer", "syto203.reddit.pp", "com.antique.Popcorn", "mediaboxhd.event.2", "comicreader.net.ios", "com.channelsapp.channels", "com.Lema.Michael.InstagramApp", "net.whatsapp.WhatsApp", "com.hotdog.popcorntime81.ios", "tv.twitch"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "quarksource-cracked.json"},
        "ids": ["com.grailr.CARROTweather", "com.wolframalpha.wolframalpha", "com.firecore.infuse", "com.stey", "com.luma-touch.LumaFusion"]
    },
    {
        "parser": Parser.GITHUB,
        #"kwargs": {"filepath": "https://altstore.enmity.app/"},
        "kwargs": {"repo_author": "enmity-mod", "repo_name": "tweak", "asset_regex": r"(?!.*(d|D)ev.*).*\.ipa"},
        "ids": ["com.hammerandchisel.discord"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://9ani.app/api/altstore"},
        "ids": ["com.marcuszhou.NineAnimator"]
    },
    {
        "parser": Parser.GITHUB,
        # ver_parse allows you to specify how to github tag should be processed before comparing to AltStore version tags
        "kwargs": {"repo_author": "Paperback-iOS", "repo_name": "app", "ver_parse": lambda x: x.replace("-r", ".").lstrip("v")},
        "ids": ["com.faizandurrani.paperback.ios"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "tatsuz0u", "repo_name": "EhPanda"},
        "ids": ["app.ehpanda"]
    },
    # {
    #    "parser": AltSourceParser,
    #    "kwargs": {"filepath": "https://raw.githubusercontent.com/ytjailed/ytjailed.github.io/main/apps.json"},
    #    "ids": ["com.google.ios.youtube", "com.atebits.Tweetie2"]
    # },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://raw.githubusercontent.com/WuXu1/wuxuslibrary/main/wuxu-complete%2B%2B.json"},
        "ids": ["com.spotify.client", "com.soundcloud.TouchApp","AlexisBarreyat.BeReal","com.zhiliaoapp.musically","com.errorerrorerror.animenow","jb.zini.tevi","com.toyopagroup.picaboo","com.microblink.PhotoMath"],
        "ignoreNews": True
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://repos.yattee.stream/alt/apps.json"},
        "ids": ["stream.yattee.app"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://qnblackcat.github.io/AltStore/apps.json"},
        "ids": ["com.burbn.instagram", "com.facebook.Facebook", "com.atebits.Tweetie2", "com.google.ios.youtube","com.reddit.Reddit"]
    }
]
alternateAppData = {
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

src = altsource_from_file("quantumsource++.json")
quantumsrc_plus = AltSourceManager(src, sourcesData)
try:
    quantumsrc_plus.update()
    quantumsrc_plus.alter_app_info(alternateAppData)
    quantumsrc_plus.save()
    quantumsrc_plus.save(alternate_dir="dist/quantumsource++.min.json",prettify=False)
except Exception as err:
    logging.error(f"Unable to update {quantumsrc_plus.src.name}.")
    logging.error(f"{type(err).__name__}: {str(err)}")
