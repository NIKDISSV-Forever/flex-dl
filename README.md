# flex-dl
Download videos from kino-flex.ru

# Install
> pip install [flex_dl-0.1.0-py3-none-any.whl](https://github.com/NIKDISSV-Forever/flex-dl/releases)

# Usage 
> python -m flex_dl -h

```
usage: flex_dl [-h] [-f FORMAT] [-s SERIES] [-v STUDIO] [-o OUT] [-e EXE] [-x] [-l] slug

positional arguments:
  slug                  flex-kino.com title slug

options:
  -h, --help            show this help message and exit
  -f FORMAT, --format FORMAT
                        download format
  -s SERIES, --series SERIES
                        series ("*[start,[stop,step]]:...|..." for range or list in format "s1,s2...:e1,e2|..."
  -v STUDIO, --studio STUDIO
                        studio name, slug, #id or index
  -o OUT, --out OUT     outfile
  -e EXE, --exe EXE     yt-dlp executable
  -x                    multithread yt-dlp run
  -l                    print commands only
```
