from __future__ import annotations

import json
import os
import urllib.request
from http.client import HTTPResponse
from pathlib import Path
from typing import Callable

from flex_dl import _regex
from flex_dl.error import MapKeyError

__all__ = ('API_URL', 'TRAILERS', 'FlexClient')
API_URL = 'https://flex-kino.com/api/v4/films/{slug}/'
TRAILERS = 'https://flex-kino.com/api/v4/trailers/?torrent_id={id}'
_CDN_URL = '{cdn}/TVShows/S%02d/E%02d/{file}'


class FlexClient:
    def __init__(self, *, print_only: bool, executable: str):
        self.print_only = print_only
        self.executable = executable

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        pass

    @staticmethod
    def _jsonify(url: str) -> dict[str]:
        resp: HTTPResponse
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode())

    def _parse_film(self, slug: str):
        return self._jsonify(API_URL.format(slug=slug))

    def _get_trailers(self, id_: int) -> dict[str]:
        return self._jsonify(TRAILERS.format(id=id_))

    @staticmethod
    def _any_matches(url: str) -> tuple[str, str] | None:
        if m := _regex.CDN_URL_RE.match(url):
            path, file = m.groups()
        elif m := _regex.FUCKING_MKV.match(url):
            path, file = m.groups()
        else:
            return
        return path, file

    def _get_url_format(self, id_: int) -> str:
        path = file = None
        for trailer in self._get_trailers(id_)['results']:
            if m := self._any_matches(trailer['trailer_stream'] or trailer['trailer_url']):
                path, file = m
        if path is file is None:
            raise Exception('The URL was not found, the API may have changed.')
        return _CDN_URL.format(cdn=path, file=file)

    def runner(self, *command: str):
        cmd = ' '.join([f'"{i}"' for i in command])
        cmd = f"{self.executable} {cmd}"
        if self.print_only:
            print(cmd)
        else:
            os.system(cmd)

    def download(self, slug: str, out: str, file_format: str, *,
                 filter_episodes: Callable[[int, int], bool], add: list[str]):
        if file_format:
            format_ = ['-f', file_format]
            if '+' in file_format:
                format_ += ['--video-multistreams', '--audio-multistreams']
        else:
            format_ = []
        film = self._parse_film(slug)
        url_format = self._get_url_format(film['id'])
        for season in film['list']:
            for episode in season['series']:
                if not filter_episodes(s := episode['season'], e := episode['series']):
                    continue
                episode['label'] = episode['label'].strip()
                format_map = {'f': film, 's': season, 'e': episode}
                try:
                    out_path = out.format_map(format_map)
                except KeyError as e:
                    raise MapKeyError(*e.args, at=out, format_map=format_map)
                Path(out_path).parent.mkdir(parents=True, exist_ok=True)
                self.runner(url_format % (s, e), '-o', out_path, *format_, *add)
