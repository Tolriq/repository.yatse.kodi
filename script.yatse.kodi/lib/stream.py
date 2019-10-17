# -*- coding: utf-8 -*-
import lib.utils as utils

if utils.is_python_3():
    from urllib.parse import unquote
else:
    from urllib import unquote


def run(argument):
    utils.play_items([argument_to_meta_data(argument)], argument['play_action'])


def argument_to_meta_data(argument):
    meta_data = {}
    if 'thumbnail' in argument:
        meta_data['thumbnail'] = unquote(argument['thumbnail'])
    if 'title' in argument:
        meta_data['title'] = unquote(argument['title'])
    if 'description' in argument:
        meta_data['description'] = unquote(argument['description'])
    if 'genre' in argument:
        meta_data['categories'] = unquote(argument['genre'])
    if 'artist' in argument:
        meta_data['artist'] = unquote(argument['artist'])
    if 'album' in argument:
        meta_data['album'] = unquote(argument['album'])
    if 'track_number' in argument:
        meta_data['track_number'] = int(argument['track_number'])
    if 'artist' in argument:
        meta_data['artist'] = unquote(argument['artist'])
    if 'media_type' in argument:
        meta_data['media_type'] = argument['media_type']
    if 'mime_type' in argument:
        meta_data['mime_type'] = argument['mime_type']
    if 'data' in argument:
        meta_data['url'] = unquote(argument['data'])
    return meta_data
