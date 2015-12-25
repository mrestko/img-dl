# img-dl

## Description

img-dl is a command line script for downloading albums.

    img-dl.py [-h] URL [PATH]

## Example

```bash
$ ./img-dl.py http://imgur.com/a/XbUFk
```

## ToDo

Currently there is basic support of Imgur. I hope to expand this to provide better support for animated images. (Currently we force download of WebM files as gif which is stupid but easier to code.)

Longer term, I would like to expand to support other popular image hosts in the vein of youtube-dl.

## License

MIT License