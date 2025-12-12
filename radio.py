from mpv import MPV
import os
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container, Center
from textual.widgets import Label, RadioSet, RadioButton, Footer, Sparkline, Button, Input, Collapsible, Checkbox
import time
import threading
import random
import math 
from textual_slider import Slider
import json

data = []

urls_file = os.path.join(os.path.dirname(__file__), "urls.json")
with open(urls_file, "r") as f:
    urls = json.load(f)

# urls is now a list of dicts


print(urls)

class RadioPlayerApp(App):

    CSS_PATH = "App.css"
    current_song = 0

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        
        try:
            ascii_art = open(os.path.join(os.path.dirname(__file__), "radioplayer_ascii.txt"), "r").read()
        except FileNotFoundError:
            ascii_art = "RADIO PLAYER"

        # Main Wrapper
        with Container(id="main_container"):
            
            yield Label(ascii_art, id="Title")

            # ROW 1
            with Horizontal(classes="row"):
                
                # Left Box: Radio
                with Vertical(classes="box"):
                    yield Label("STATION", classes="box-label")
                    with RadioSet(id="radio_set"):
                        for i in range(len(urls)):
                            yield RadioButton(urls[i]["name"],id = "op" + str(i) )
                            

                        

                # Right Box: Sparkline
                with Vertical(classes="box"):
                    yield Label("VISUALIZER", classes="box-label")
                    with Center():
                        yield Sparkline(
                            data,
                            summary_function=max,
                            id="spark",
                        )

            # ROW 2
            with Horizontal(classes="row"):
                
                # Left Box: Volume
                with Vertical(classes="box"):
                    yield Label("LOUDNESS", classes="box-label")
                    with Center():
                        yield Slider(min=0, max=100, step=1, value=50, id="volume_slider")

                # Right Box: Pause
                with Vertical(classes="box"):
                    yield Label("PLAYBACK", classes="box-label")
                    with Center():
                        yield Button("||", id="pause_button")

            # Row 3: Add playlist items
            with Horizontal(classes="row"):
                with Vertical(classes="box", id="add_station_box"):
                    yield Label("ADD STATION", classes="box-label")
                    yield Input(id="name_input", placeholder="Enter station name here")
                    yield Input(id="url_input", placeholder="Enter stream URL here")
                    with Center():
                        yield Button("Add", id="add_button")


            # You have to add it into the box of the add and ohter things
        with Collapsible():
            with Vertical(id = "collapsible_content"):
                yield Button("Remove Selected Stations", id="remove_button")
                for i in range(len(urls)):
                    yield Checkbox(f"{urls[i]['name']}", value=False, id=f"chk{i}")
                
                
            
            
        yield Footer()

    def on_mount(self) -> None:
        self.radio = RadioPlayer()
        self.set_interval(0.2, self.update_sparkline)

    def update_sparkline(self):
        spark = self.query_one("#spark")
        spark.data = list(self.radio.spark_data)

    def on_slider_changed(self, event: Slider.Changed) -> None:
        new_vol = event.value
        self.radio.player.volume = new_vol

    def on_radio_set_changed(self, event):
        self.radio.stop()
        selected_index = int(event.radio_set.pressed_index)
        self.current_song = urls[selected_index]["url"]
        self.radio.play(self.current_song)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "pause_button":
            if self.radio.player.pause:
                self.radio.player.pause = False
                event.button.label = "||"
            else:
                self.radio.player.pause = True
                event.button.label = "▶"

        elif button_id == "add_button":
            if len(self.query_one("#name_input").value) > 0 and len(self.query_one("#url_input").value) > 0:
                new_name = self.query_one("#name_input").value
                new_url = self.query_one("#url_input").value
                urls.append({"name": new_name, "url": new_url})
                with open(urls_file, "w") as f:
                    json.dump(urls, f, indent=4)
                radio_set = self.query_one("#radio_set")
                radio_set.mount(RadioButton(new_name, id="op" + str(len(urls)-1)))
                collapese = self.query_one("#collapsible_content")
                collapese.mount(Checkbox(f"{new_name}", value=False, id=f"chk{len(urls)-1}"))
                self.query_one("#name_input").value = ""
                self.query_one("#url_input").value = ""
        elif button_id == "remove_button":
    # determine which checkboxes are checked
            indices_to_remove = []
            for i in range(len(urls)):
                radio_stations_to_remove = self.query_one(f"#op{i}")
                list_to_remove = self.query_one(f"#chk{i}")
                list_to_remove.remove()
                radio_stations_to_remove.remove()
            for i in range(len(urls)):
                chk = self.query_one(f"#chk{i}")
                if chk.value:                     # remove CHECKED ones
                    indices_to_remove.append(i)

            # remove from data model
            for idx in sorted(indices_to_remove, reverse=True):
                del urls[idx]

            # write updated json
            with open(urls_file, "w") as f:
                json.dump(urls, f, indent=4)

            for i in range(len(urls)):
                pass
class RadioPlayer:
    def __init__(self):
        self.player = MPV(ytdl=True, vo='null', volume=50)
        self.spark_data = [0] * 40
        self.running = False

    def play(self, url):
        self.player.play(url)
        self.running = True
        threading.Thread(target=self._sparkline_update_loop, daemon=True).start()

    def stop(self):
        self.running = False
        try:
            self.player.stop()
        except:
            pass

    def _sparkline_update_loop(self):
        while self.running:
            pos = math.sin(time.time() * 3) * 10 + random.randint(1, 15)
            if pos < 0: pos = 0
            self.spark_data.pop(0)
            self.spark_data.append(int(pos))
            time.sleep(0.1)

if __name__ == "__main__":
    app = RadioPlayerApp()
    app.run()