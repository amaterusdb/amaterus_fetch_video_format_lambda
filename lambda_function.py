import logging
from logging import getLogger

from yt_dlp import YoutubeDL

logger = getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context: dict) -> dict:
    url = event.get("Url")
    if not isinstance(url, str) or len(url) == 0:
        return {
            "result": "error",
            "message": "Bad Request",
        }

    ydl_opts = {
        "cachedir": False,
        "extractor_args": {
            "youtube": {
                "player-client": "web",
                "skip": ["dash", "hls", "translated_subs"],
            },
        },
    }
    with YoutubeDL(params=ydl_opts) as ydl:
        raw_info = ydl.extract_info(url=url, download=False)
        info = ydl.sanitize_info(raw_info)

    duration = info.get("duration")
    if not isinstance(duration, int):
        return {
            "result": "error",
            "message": "Invalid duration",
        }

    extractor = info.get("extractor")
    if not isinstance(extractor, str):
        return {
            "result": "error",
            "message": "Invalid extractor",
        }

    info_formats = info.get("formats")
    if not isinstance(info_formats, list) or len(info_formats) == 0:
        return {
            "result": "error",
            "message": "No available format found",
        }

    ret_formats = []
    for format in info_formats:
        if not isinstance(format, dict):
            return {
                "result": "error",
                "message": "Unexpected state",
            }

        # extractor specific format id
        format_id = format.get("format_id")
        if not isinstance(format_id, str):
            logger.warn(f"Invliad format id. Skipping: {format_id}")
            continue

        filesize = format.get("filesize")
        if not isinstance(filesize, int):
            filesize = None

        protocol = format.get("protocol")
        if not isinstance(protocol, str):
            protocol = None

        acodec = format.get("acodec")
        if not isinstance(acodec, str):
            acodec = None

        vcodec = format.get("vcodec")
        if not isinstance(vcodec, str):
            vcodec = None

        width = format.get("width")
        if not isinstance(width, int):
            width = None

        height = format.get("height")
        if not isinstance(height, int):
            height = None

        fps = format.get("fps")
        if not isinstance(fps, float):
            fps = None

        ret_formats.append(
            {
                "format_id": format_id,
                "filesize": filesize,
                "protocol": protocol,
                "acodec": acodec,
                "vcodec": vcodec,
                "width": width,
                "height": height,
                "fps": fps,
            }
        )

    return {
        "result": "success",
        "duration": duration,
        "extractor": extractor,
        "formats": ret_formats,
    }
