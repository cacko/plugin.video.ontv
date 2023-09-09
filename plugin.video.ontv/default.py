# -*- coding: utf-8 -*-

from __future__ import division

from pathlib import Path
import sys
import xbmcaddon
import xbmcplugin
import logging
from resources.lib import main
from resources.lib.api import Api as Client
from resources.lib.models import API_INFO, ITEM_MODE, main_menu
from urllib.parse import parse_qs

plugin_handle = int(sys.argv[1])
ADDON = xbmcaddon.Addon(id='plugin.video.ontv')
profile_dir = Path(main.DIR_USERDATA)

Client.register(
    API_INFO(
        username=ADDON.getSetting('ontv_username'),
        password=ADDON.getSetting('ontv_password'),
        host=ADDON.getSetting('ontv_host'),
        http_port=ADDON.getSetting('ontv_http_port'),
        https_port=ADDON.getSetting('ontv_https_port')
    ),
    profile_dir
)


def get_params():
    parsed = parse_qs(sys.argv[2][1:])
    return {k: v[0] for k, v in parsed.items()}


params = get_params()
content_type = None
content_id = params.get("id")
name = params.get("name")
mode = ITEM_MODE(params.get("mode", ""))
iconimage = params.get("iconimage")
description = None
keyword = None

logging.debug(sys.argv[2])
logging.debug(params)

match (mode):
    case ITEM_MODE.MAIN:
        main.createMainMenu(main_menu)
    case ITEM_MODE.CATEGORIES:
        main.createCategoryMenu(Client.categories)
    case ITEM_MODE.CATEGORY:
        main.createStreamsMenu(
            list(filter(lambda s: s.category_id == content_id, Client.streams))
        )

xbmcplugin.endOfDirectory(int(sys.argv[1]))
