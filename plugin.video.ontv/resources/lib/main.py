# -*- coding: utf-8 -*-

import logging

from resources.lib.api import Api as Client
from resources.lib.favourites import Favourites
from resources.lib.models import (
    ITEM_MODE,
    Category,
    Stream,
    MenuItem
)
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import xbmcvfs
import html
from urllib.parse import urlencode
import sys
import os
from requests.packages import urllib3

urllib3.disable_warnings()


ADDON = xbmcaddon.Addon(id='plugin.video.ontv')


def tp(path):
    return xbmcvfs.translatePath(path)


def unescape(string):
    return html.unescape(string)


def GetAddonInfo():
    addon_info = {}
    addon_info["id"] = addonid
    addon_info["addon"] = xbmcaddon.Addon(addonid)
    addon_info["language"] = addon_info["addon"].getLocalizedString
    addon_info["version"] = addon_info["addon"].getAddonInfo("version")
    addon_info["path"] = addon_info["addon"].getAddonInfo("path")
    addon_info["profile"] = tp(addon_info["addon"].getAddonInfo('profile'))
    return addon_info


addonid = "plugin.video.ontv"
addoninfo = GetAddonInfo()
DIR_USERDATA = tp(addoninfo["profile"])
icondir = 'resource://resource.images.ontv/media/'
cookie_jar = None
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0'
headers = {'User-Agent': user_agent}


if (not os.path.exists(DIR_USERDATA)):
    os.makedirs(DIR_USERDATA)


def translation(id):
    return xbmcaddon.Addon(addonid).getLocalizedString(id)


def AddMenuEntry(
        name: str,
        id: str,
        mode: ITEM_MODE,
        iconimage=None,
        description=None
):
    if not iconimage:
        iconimage = "DefaultFolder.png"
    listitem_url = f"{sys.argv[0]}?"
    params = dict(
        id=id,
        mode=mode,
        name=name,
        iconimage=iconimage,
        description=description
    )
    listitem_url = f"{sys.argv[0]}?{urlencode(params, encoding='utf-8')}"
    listitem = xbmcgui.ListItem(label=name, label2=description)
    vinfo: xbmc.InfoTagVideo = listitem.getVideoInfoTag()
    listitem.setArt({'icon': 'DefaultFolder.png', 'thumb': iconimage})

    match mode:
        case ITEM_MODE.STREAM:
            vinfo.setTitle(name)
            action_params = dict(
                id=str(id),
                name='Remove favourite' if Favourites.is_in(id) else 'Add favourite',
                mode=ITEM_MODE.REM_FAVOURITE if Favourites.is_in(id) else ITEM_MODE.ADD_FAVOURITE
            )
            action_url = f"{sys.argv[0]}?{urlencode(action_params)}"
            logging.warning(action_url)
            listitem.addContextMenuItems([
                (action_params.get("name"), f"RunPlugin({action_url})")
            ])
            listitem.setContentLookup(False)
            listitem_url = Client.stream_url(id)
            listitem.setPath(Client.stream_url(id))
            listitem.setProperty("IsPlayable", 'true')
            listitem.setMimeType("video/mp2t")
            listitem.setProperty('inputstream', 'inputstream.ffmpegdirect')
            listitem.setProperty('inputstream.ffmpegdirect.stream_mode=timeshift', 'true')
            listitem.setProperty('inputstream.ffmpegdirect.is_realtime_stream', 'true')
            listitem.setProperty("IsFolder", 'false')
        case ITEM_MODE.CATEGORY:
            vinfo.setTitle(name)
            listitem.setProperty("IsPlayable", 'false')
            listitem.setPath(listitem_url)
            listitem.setProperty("IsFolder", 'true')

    listitem.setProperty("Property(Addon.Name)", "onTV")
    xbmcplugin.addDirectoryItem(
        handle=int(sys.argv[1]),
        url=listitem_url,
        listitem=listitem,
        isFolder=mode != ITEM_MODE.STREAM
    )
    xbmcplugin.setContent(int(sys.argv[1]), 'videos')
    return True


def createMainMenu(menu: list[MenuItem]):
    logging.debug(menu)
    for it in menu:
        AddMenuEntry(
            name=it.name,
            id=0,
            mode=it.mode
        )


def createCategoryMenu(categories: list[Category]):
    logging.debug(categories)
    for ct in sorted(categories, key=lambda ct: ct.category_name):
        AddMenuEntry(
            name=ct.category_name.encode('ascii', 'ignore').decode(),
            id=ct.category_id,
            mode=ITEM_MODE.CATEGORY,
        )


def createStreamsMenu(streams: list[Stream]):
    for st in sorted(streams, key=lambda st: st.name):
        AddMenuEntry(
            name=st.name.encode('ascii', 'ignore').decode(),
            id=st.stream_id,
            mode=ITEM_MODE.STREAM,
            iconimage=st.stream_icon
        )
