from mpv import MPV
import os
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, RadioSet, RadioButton, Footer, Sparkline
import subprocess


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
        return super().action_quit()

    def on_mount(self) -> None:
        self.radio = RadioPlayer()

        sparkline_widget = self.query_one("#spark")
        sparkline_widget.styles.margin = (padding_sparkline)

        


    def on_radio_set_changed(self, event):
        self.radio.stop()
        self.radio.play(urls[int(event.pressed.id[-1])])
        self.radio.get_loudness(urls[int(event.pressed.id[-1])])


class RadioPlayer:
    _instances = []

    def __init__(self):
        self.player = MPV(ytdl=True, vo='null', volume=50)
        RadioPlayer._instances.append(self)

    @classmethod
    def stop_all(cls):
        for inst in list(cls._instances):
            try:
                inst.player.stop()
                if hasattr(inst.player, "terminate"):
                    inst.player.terminate()
            except Exception:
                pass
        cls._instances.clear()

    def play(self, url):
        self.player.play(url)
        print("Playing radio stream...")

    def stop(self):
        try:
            self.player.stop()
        except Exception:
            pass

    def set_volume(self, vol):
        self.player.volume = vol

    def change_volume(self, delta):
        self.player.volume += delta

    def get_loudness(self, input_stream):
        pass


if __name__ == "__main__":
    app = RadioPlayerApp()
    app.run()
