from pathlib import Path

from PySide6.QtCore import (
    QObject,
    QProcess,
    Signal,
)

from media import find_executable


class GifConverter(QObject):

    progress_changed = Signal(int)

    status_changed = Signal(str)

    finished = Signal(
        bool,
        str
    )

    def __init__(self):

        super().__init__()

        self.process = None

        self.output_path = None

        self.total_duration = 0.0

    def start(
        self,
        input_path,
        output_path,
        fps=20,
        width=640,
        height=0,
        start=0,
        end=0,
        loop_forever=True,
    ):

        ffmpeg = find_executable(
            "ffmpeg"
        )

        if not ffmpeg:

            self.finished.emit(
                False,
                "FFmpeg could not be found."
            )

            return

        self.output_path = str(
            output_path
        )

        if end > start:

            self.total_duration = (
                end - start
            )

        else:

            self.total_duration = 2.0

        scale = self.build_scale(
            width,
            height
        )

        video_filter = (
            f"fps={fps},"
            f"{scale},"
            "split[s0][s1];"
            "[s0]palettegen="
            "max_colors=256[p];"
            "[s1][p]paletteuse="
            "dither=sierra2_4a"
        )

        args = [
            "-y",

            "-ss",
            str(start),

            "-i",
            str(input_path),
        ]

        if end > start:

            args.extend([
                "-t",
                str(
                    end - start
                ),
            ])

        args.extend([
            "-vf",
            video_filter,

            "-loop",
            (
                "0"
                if loop_forever
                else "-1"
            ),

            "-progress",
            "pipe:1",

            "-nostats",

            str(output_path),
        ])

        self.process = QProcess(
            self
        )

        self.process.setProcessChannelMode(
            QProcess.SeparateChannels
        )

        self.process.readyReadStandardOutput.connect(
            self.read_progress
        )

        self.process.readyReadStandardError.connect(
            self.read_error
        )

        self.process.finished.connect(
            self.on_finished
        )

        self.process.errorOccurred.connect(
            self.on_error
        )

        self.status_changed.emit(
            "Starting FFmpeg..."
        )

        self.process.start(
            ffmpeg,
            args
        )

    def build_scale(
        self,
        width,
        height
    ):

        if width and height:

            return (
                f"scale={width}:{height}:"
                "flags=lanczos"
            )

        if width:

            return (
                f"scale={width}:-1:"
                "flags=lanczos"
            )

        if height:

            return (
                f"scale=-1:{height}:"
                "flags=lanczos"
            )

        return (
            "scale=iw:ih"
        )

    def read_progress(self):

        if not self.process:
            return

        data = bytes(
            self.process.readAllStandardOutput()
        ).decode(
            errors="ignore"
        )

        for line in data.splitlines():

            if line.startswith(
                "out_time_ms="
            ):

                try:

                    microseconds = int(
                        line.split(
                            "=",
                            1
                        )[1]
                    )

                    seconds = (
                        microseconds
                        / 1_000_000
                    )

                    if self.total_duration:

                        percent = int(
                            (
                                seconds
                                / self.total_duration
                            )
                            * 100
                        )

                        percent = max(
                            0,
                            min(
                                99,
                                percent
                            )
                        )

                        self.progress_changed.emit(
                            percent
                        )

                        self.status_changed.emit(
                            f"Converting... "
                            f"{percent}%"
                        )

                except ValueError:
                    pass

            elif line == "progress=end":

                self.progress_changed.emit(
                    100
                )

    def read_error(self):

        if self.process:

            self.process.readAllStandardError()

    def on_error(
        self,
        error
    ):

        self.status_changed.emit(
            "FFmpeg process error."
        )

    def on_finished(
        self,
        exit_code,
        exit_status
    ):

        output = (
            Path(
                self.output_path
            )
            if self.output_path
            else None
        )

        success = (
            exit_code == 0
            and output is not None
            and output.exists()
            and output.stat().st_size > 0
        )

        if success:

            self.progress_changed.emit(
                100
            )

            self.status_changed.emit(
                "Conversion complete!"
            )

            self.finished.emit(
                True,
                str(output)
            )

        else:

            self.status_changed.emit(
                "Conversion failed."
            )

            self.finished.emit(
                False,
                "FFmpeg failed to create the GIF."
            )

        self.process = None

    def cancel(self):

        if self.process:

            self.status_changed.emit(
                "Cancelling..."
            )

            self.process.kill()

            self.process = None

            self.progress_changed.emit(
                0
            )

            self.status_changed.emit(
                "Conversion cancelled."
            )