from mpv import MPV
import os
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, RadioSet, RadioButton, Footer

urls = [
    'https://www.youtube.com/watch?v=jfKfPfyJRdk',  # Lofi Hip Hop
    'https://www.youtube.com/watch?v=E_XmwjgRLz8',  # Lofi Guitar
    'https://www.youtube.com/watch?v=sulgD9TQsTk'   # Lofi Christmas
]

class RadioPlayerApp(App):

    CSS_PATH = "App.css"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    def compose(self) -> ComposeResult:
        yield Label(open(os.path.join(os.path.dirname(__file__), "radioplayer_ascii.txt"), "r").read(), id="Title") # Load ASCII art from file
        yield Footer()
        with VerticalScroll():
            with Horizontal():
                    with RadioSet():
                        yield RadioButton("Lofi Hip Hop", id="op0")
                        yield RadioButton("Lofi Guitar", id="op1")
                        yield RadioButton("Lofi Christmas", id="op2")
            with Horizontal():
                yield Label(id="pressed")
            with Horizontal():
                yield Label(id="index")

    def action_quit(self):
        return super().action_quit()
    
    def on_mount(self) -> None:
        # create a single player for the app and reuse it
        self.radio = RadioPlayer()
    
    def on_radio_set_changed(self, event):
        # stop current playback and play the selected URL using the app's player
        self.radio.stop()
        self.radio.play(urls[int(event.pressed.id[-1])])
        
    
    


class RadioPlayer:
    def __init__(self):
        # keep a registry of instances so we can stop all if needed
        self.player = MPV(ytdl = True, vo='null', volume=50)  # disable video output
        RadioPlayer._instances.append(self)

    # registry for all created players
    _instances = []
    
    @classmethod
    def stop_all(cls):
        """Stop all tracked MPV instances."""
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


if __name__ == "__main__":
    app = RadioPlayerApp()
    app.run()





