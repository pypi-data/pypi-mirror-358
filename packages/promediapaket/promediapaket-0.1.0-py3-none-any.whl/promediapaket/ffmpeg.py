from time import strptime, mktime
from subprocess import run
from pathlib import Path
from os import PathLike
from json import loads

from .utils import log


def ffprobe(file: PathLike | str) -> dict:
    if not Path(file).is_file():
        raise RuntimeError(f'"{file}" is not a file')
    ffprobe_out = loads(run(['ffprobe', file, '-print_format', 'json', '-show_streams', '-show_format'], capture_output=True).stdout)
    return ffprobe_out


def get_duration(ffprobe_data: dict) -> float:
    if 'format' in ffprobe_data:
        ffprobe_data = ffprobe_data['format']

    duration = 0
    if 'duration' in ffprobe_data:
        duration = ffprobe_data['duration']
    elif 'tags' in ffprobe_data and 'DURATION' in ffprobe_data['tags']:
        duration = ffprobe_data['tags']['DURATION']

    try:
        duration = float(duration)

    except ValueError:
        duration_seconds = duration.split('.')[0]
        duration_milliseconds = float('0.' + duration.split('.')[1])
        duration = mktime(strptime(duration_seconds, '%H:%M:%S')) + 2208992400 + duration_milliseconds

    return duration


def check_for_errors(video_file) -> int:
    ffprobe_out = ffprobe(video_file)
    if ffprobe_out['format']['format_name'] == 'webvtt':
        print("VERBOSE", "Subtitles can't be checked for errors.")
        return 0

    for stream in ffprobe_out['streams']:
        out_format = "yuv4mpegpipe" if stream['codec_type'] == "video" else "wav"

        ffmpeg_out = run([
            'ffmpeg', '-y', '-loglevel', 'error',
            '-i', video_file, '-c', 'copy',
            '-f', 'null', '/dev/null'
        ], capture_output=True)

        if ffmpeg_out.returncode:
            log("ERROR", f'FFmpeg Check Error failed. {video_file}')
            return 1

        elif ffmpeg_out.stderr:
            log("ERROR", f'FFmpeg Check Error failed. {video_file}')
            return 2

        ffmpeg_out = run([
            'ffmpeg', '-y', '-loglevel', 'error',
            '-i', video_file, '-t', '180',
            '-f', out_format, '/dev/null'
        ], capture_output=True)

        if ffmpeg_out.returncode:
            log("ERROR", f'FFmpeg Check Error failed. {video_file}')
            return 4

        elif ffmpeg_out.stderr:
            log("ERROR", f'FFmpeg Check Error failed. {video_file}')
            return 5

        video_duration = get_duration(ffprobe_out)
        ffmpeg_out = run([
            'ffmpeg', '-y', '-loglevel', 'error',
            '-ss', str(int(video_duration - 180)), '-i', video_file,
            '-f', out_format, '/dev/null'
        ], capture_output=True)

        if ffmpeg_out.returncode:
            log("ERROR", f'FFmpeg Check Error failed. {video_file}')
            return 6

        elif ffmpeg_out.stderr:

            ffmpeg_out = run([
                'ffmpeg', '-y', '-loglevel', 'error',
                '-i', video_file,
                '-f', out_format, '/dev/null'
            ], capture_output=True)

            if ffmpeg_out.returncode:
                log("ERROR", f'FFmpeg Check Error failed. {video_file}')
                return 7

            elif ffmpeg_out.stderr:
                log("ERROR", f'FFmpeg Check Error failed. {video_file}')
                return 8

    return 0
