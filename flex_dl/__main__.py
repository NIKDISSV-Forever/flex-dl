from __future__ import annotations

import argparse
from typing import Callable

from flex_dl import FlexClient
from flex_dl.error import MapKeyError


def _help_nested_format(exc: MapKeyError):
    to_visit = {(): exc.format_map}
    available = []
    while to_visit:
        path, value = to_visit.popitem()
        items = None
        if isinstance(value, dict):
            items = value.items()
        elif isinstance(value, (list, tuple)):
            items = enumerate(value)
        if items is not None:
            for k, v in items:
                to_visit[path + (k,)] = v
        if path:
            available.append(f"{path[0]}{''.join([f'[{p}]' for p in path[1:]])}: {type(value).__name__}")
    available.sort(key=lambda v: (v[0], len(v), v))
    print('\n'.join(available))
    import sys
    print(exc, file=sys.stderr)


def _filter(expr: str) -> Callable[[int], bool]:
    expr = expr.strip()
    if neg := expr.startswith('!'):
        expr = expr.removeprefix('!')
    if expr and expr != '*':
        if expr.startswith('*'):
            func = range(*[int(i) for i in expr[1:].split(',')[:3]]).__contains__
        else:
            func = {int(i) for i in expr.split(',')}.__contains__
    else:
        return lambda _: not neg
    if neg:
        return lambda v: not func(v)
    return func


def episodes_filter_str(rules: str) -> Callable[[int, int], bool]:
    """
    expr1|expr2|...
    expr = N1:N2 (N1 - season, N2 - episode)
    N/!N: digit / *[start,[stop,step]] / n1,n2,n...
    """
    filters = ()
    for rule in rules.split('|'):
        match rule.strip().split(':', 1):
            case vs, vep:
                filters += (lambda s, e, _s=_filter(vs), _e=_filter(vep): _s(s) and _e(e)),
    return lambda s, e: any([f(s, e) for f in filters])


def main():
    """Download films/series from flex-kino.com"""
    parser = argparse.ArgumentParser()
    parser.add_argument('slug', help='flex-kino.com title slug')
    parser.add_argument('-f', '--format', help='download format')
    parser.add_argument('-s', '--series',
                        help='series ("*[start,[stop,step]]:...|..." for range or list in format "s1,s2...:e1,e2|..."',
                        type=episodes_filter_str, default=lambda _, _2: True)
    parser.add_argument('-v', '--studio', default='0', help='studio name, slug, #id or index')
    parser.add_argument('-o', '--out', help='outfile',
                        default="{f[original_name]}/{e[season]:0>2}/{e[series]:0>2}.%(ext)s")
    parser.add_argument('-e', '--exe', default='yt-dlp', help='yt-dlp executable')
    parser.add_argument('-x', default=False, action='store_true', help='multithread yt-dlp run')
    parser.add_argument('-l', default=False, action='store_true', help='print commands only')
    args, add = parser.parse_known_args()
    exe = args.exe
    if args.x:
        exe = f'start {exe}'
    with FlexClient(print_only=args.l, executable=exe) as client:
        try:
            client.download(args.slug, args.out, args.format, filter_episodes=args.series, add=add)
        except MapKeyError as e:
            _help_nested_format(e)


if __name__ == '__main__':
    main()
