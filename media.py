import os
import shutil
import subprocess
from pathlib import Path


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".webm",
    ".m4v",
    ".flv",
    ".wmv",
}

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
}


def find_executable(name):
    """Find FFmpeg/FFprobe through PATH or common Windows locations."""

    # First: normal PATH lookup
    found = shutil.which(name)

    if found:
        return found

    executable = f"{name}.exe"

    locations = []

    local_app_data = os.environ.get(
        "LOCALAPPDATA"
    )

    program_files = os.environ.get(
        "PROGRAMFILES"
    )

    if local_app_data:
        locations.append(
            Path(local_app_data)
            / "Microsoft"
            / "WinGet"
            / "Packages"
        )

    if program_files:
        locations.extend([
            Path(program_files)
            / "ffmpeg"
            / "bin",

            Path(program_files)
            / "FFmpeg"
            / "bin",
        ])

    locations.append(
        Path("C:/ffmpeg/bin")
    )

    for location in locations:

        if not location.exists():
            continue

        try:

            matches = list(
                location.rglob(executable)
            )

            if matches:
                return str(
                    matches[0]
                )

        except OSError:
            pass

    return None


def is_video(path):
    return (
        Path(path).suffix.lower()
        in VIDEO_EXTENSIONS
    )


def is_image(path):
    return (
        Path(path).suffix.lower()
        in IMAGE_EXTENSIONS
    )


def is_supported(path):
    return (
        is_video(path)
        or is_image(path)
    )


def get_media_info(path):

    ffprobe = find_executable(
        "ffprobe"
    )

    if not ffprobe:

        raise RuntimeError(
            "ffprobe could not be found.\n\n"
            "Make sure FFmpeg is installed."
        )

    command = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "v:0",

        "-show_entries",
        "stream=width,height,r_frame_rate",

        "-show_entries",
        "format=duration",

        "-of",
        "default=noprint_wrappers=1",

        str(path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=15,
    )

    if result.returncode != 0:

        raise RuntimeError(
            result.stderr.strip()
            or "ffprobe failed."
        )

    info = {
        "width": None,
        "height": None,
        "fps": None,
        "duration": None,
    }

    for line in result.stdout.splitlines():

        if "=" not in line:
            continue

        key, value = line.split(
            "=",
            1
        )

        if key == "width":

            try:
                info["width"] = int(
                    value
                )
            except ValueError:
                pass

        elif key == "height":

            try:
                info["height"] = int(
                    value
                )
            except ValueError:
                pass

        elif key == "duration":

            try:
                info["duration"] = float(
                    value
                )
            except ValueError:
                pass

        elif key == "r_frame_rate":

            try:

                numerator, denominator = (
                    value.split("/")
                )

                denominator = float(
                    denominator
                )

                if denominator:

                    info["fps"] = (
                        float(numerator)
                        / denominator
                    )

            except (
                ValueError,
                ZeroDivisionError,
            ):
                pass

    return info


def format_duration(seconds):

    if seconds is None:
        return "Unknown"

    seconds = max(
        0,
        int(seconds)
    )

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    seconds = seconds % 60

    if hours:

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

    return (
        f"{minutes:02d}:"
        f"{seconds:02d}"
    )