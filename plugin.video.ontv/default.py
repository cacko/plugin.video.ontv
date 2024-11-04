# -*- coding: utf-8 -*-

from __future__ import division

from pathlib import Path
import sys
import xbmcaddon
import xbmcplugin
import logging
import xbmc
import xbmcgui
from resources.lib import main
from resources.lib.api import Api as Client
from resources.lib.favourites import Favourites
from resources.lib.models import Settings, ITEM_MODE, main_menu, Stream
from urllib.parse import parse_qs
from difflib import get_close_matches as gcm
import requests
requests.urllib3.disable_warnings()

plugin_handle = int(sys.argv[1])
ADDON = xbmcaddon.Addon(id='plugin.video.ontv')
profile_dir = Path(main.DIR_USERDATA)

Client.register(
    Settings(
        username=ADDON.getSetting('ontv_username'),
        password=ADDON.getSetting('ontv_password'),
        host=ADDON.getSetting('ontv_host'),
        http_port=ADDON.getSetting('ontv_http_port'),
        https_port=ADDON.getSetting('ontv_https_port')
    ),
    profile_dir
)
Favourites.register(profile_dir)

def get_Score(st: Stream, query: str):
    qr_tokens = query.lower().split(" ")
    tokens = st.name.lower().split(" ")
    return (sum([len(gcm(qr, tokens, cutoff=0.80)) for qr in qr_tokens]), st)


def get_params():
    parsed = parse_qs(sys.argv[2][1:])
    return {k: v[0] for k, v in parsed.items()}


params = get_params()
content_type = None
content_id = params.get("id")
name = params.get("name")
mode = ITEM_MODE(params.get("mode", ""))

logging.debug(sys.argv[2])
logging.debug(params)

match (mode):
    case ITEM_MODE.MAIN:
        main.createMainMenu(main_menu)
    case ITEM_MODE.CATEGORIES:
        main.createCategoryMenu(Client.categories.get_data())
    case ITEM_MODE.CATEGORY:
        main.createStreamsMenu(Client.streams.get_data(category_id=content_id))
    case ITEM_MODE.FAVOURITES:
        main.createStreamsMenu(Favourites.items)
    case ITEM_MODE.ADD_FAVOURITE:
        Favourites.add(content_id)
    case ITEM_MODE.REM_FAVOURITE:
        Favourites.remove(content_id)
    case ITEM_MODE.SEARCH:
        keyboard = xbmc.Keyboard('', "type")
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText()
            with_scores = map(lambda st: get_Score(st, query), Client.streams.get_data())
            valid_scores = [(sc, st) for sc, st in with_scores if sc > 0]
            streams = list(map(lambda sc: sc[1], sorted(valid_scores, key=lambda sc: sc[0], reverse=True)))
            main.createStreamsMenu(streams[:24])
    case ITEM_MODE.REFRESH:
        dialog = xbmcgui.DialogProgress()
        dialog.create("onTV")
        for pct, txt in Client.reload():
            dialog.update(pct, txt)
        dialog.close()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
