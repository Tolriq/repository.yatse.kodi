# -*- coding: utf-8 -*-
import urllib

import utils


def run(argument):
    utils.play_items([argument_to_meta_data(argument)], argument['play_action'])


def argument_to_meta_data(argument):
    meta_data = {}
    if 'thumbnail' in argument:
        meta_data['thumbnail'] = urllib.unquote(argument['thumbnail'])
    if 'title' in argument:
        meta_data['title'] = urllib.unquote(argument['title'])
    if 'description' in argument:
        meta_data['description'] = urllib.unquote(argument['description'])
    if 'genre' in argument:
        meta_data['categories'] = urllib.unquote(argument['genre'])
    if 'artist' in argument:
        meta_data['artist'] = urllib.unquote(argument['artist'])
    if 'album' in argument:
        meta_data['album'] = urllib.unquote(argument['album'])
    if 'track_number' in argument:
        meta_data['track_number'] = int(argument['track_number'])
    if 'artist' in argument:
        meta_data['artist'] = urllib.unquote(argument['artist'])
    if 'media_type' in argument:
        meta_data['media_type'] = argument['media_type']
    if 'mime_type' in argument:
        meta_data['mime_type'] = argument['mime_type']
    if 'data' in argument:
        meta_data['url'] = urllib.unquote(argument['data'])
    return meta_data
