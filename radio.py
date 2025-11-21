import os
import threading
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, RadioSet, RadioButton, Footer, Sparkline
import subprocess
import sys
import signal


urls = [
    'https://www.youtube.com/watch?v=jfKfPfyJRdk',  # Lofi Hip Hop
    'https://www.youtube.com/watch?v=E_XmwjgRLz8',  # Lofi Guitar
    'https://www.youtube.com/watch?v=sulgD9TQsTk',   # Lofi Christmas
]

padding_sparkline = len(urls) + 1

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]


class RadioPlayerApp(App):

    CSS_PATH = "App.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:

        # ASCII-Title
        yield Label(
            open(os.path.join(os.path.dirname(__file__), "radioplayer_ascii.txt"), "r").read(),
            id="Title"
        )

        # NEUE ZEILE: direkt unter ASCII-Art
        with Horizontal(id="top_row"):
            with RadioSet(id="radio_set"):
                yield RadioButton("Lofi Hip Hop", id="op0")
                yield RadioButton("Lofi Guitar", id="op1")
                yield RadioButton("Lofi Christmas", id="op2")

            yield Sparkline(
                data,
                summary_function=max,
                id="spark",
            )

        # Restliche Anzeige
        with VerticalScroll():
            with Horizontal():
                yield Label(id="pressed")
            with Horizontal():
                yield Label(id="index")

        yield Footer()

    def action_quit(self):
        RadioPlayer.stop(self.radio)
        return super().action_quit()

    def on_mount(self) -> None:
        self.radio = RadioPlayer()

        sparkline_widget = self.query_one("#spark")
        sparkline_widget.styles.margin = (padding_sparkline)

        


    def on_radio_set_changed(self, event):
        self.radio.stop()
        self.radio.play(urls[int(event.pressed.id[-1])])


class RadioPlayer:
    def __init__(self):
        self.process = None

    def play(self, url: str):
        self.stop()  # Stop any current track

        # Command to extract audio and pipe to ffplay
        command = [
            "yt-dlp",
            "-x",                 # Extract audio
            "--audio-format", "mp3",
            "-o", "-",             # Output to stdout
            url
        ]

        ffplay_command = [
            "ffplay",
            "-nodisp",            # No video display
            "-autoexit",          # Exit when done
            "-i", "pipe:0",       # Read from stdin
            "-loglevel", "quiet"  # Suppress ffplay messages
        ]

        # Start yt-dlp process
        yt_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        # Start ffplay process reading from yt-dlp stdout
        self.process = subprocess.Popen(
            ffplay_command,
            stdin=yt_process.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Detach stdout so yt-dlp closes when ffplay exits
        yt_process.stdout.close()


    def stop(self):
        if self.process:
            try:
                self.process.send_signal(signal.SIGTERM)
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

if __name__ == "__main__":
    app = RadioPlayerApp()
    app.run()#
