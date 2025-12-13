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
# writes json to global variable "urls"


class RadioPlayerApp(App):

    CSS_PATH = "App.css"
    current_song = 0

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        
        try:
            ascii_art = open(os.path.join(os.path.dirname(__file__), "radioplayer_ascii.txt"), "r").read()  #reads ascii for title
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

            # Row 4: Manage Stations
            with Horizontal(classes="row"):
                with Vertical(classes="box", id="manage_stations_box"):
                    # The Collapsible widget itself acts as the container for the remove functionality.
                    with Collapsible(title="Manage Stations"):
                        with Vertical(id="collapsible_content"):
                            yield Button("Remove Selected Stations", id="remove_button")
                            for i in range(len(urls)):
                                yield Checkbox(f"{urls[i]['name']}", value=False, id=f"chk{i}")


        yield Footer()

    def on_mount(self) -> None:
        self.radio = RadioPlayer()
        self.set_interval(0.2, self.update_sparkline)  #updates sparkline every 0.2 seconds

    def update_sparkline(self):
        spark = self.query_one("#spark")
        spark.data = list(self.radio.spark_data) #updates sparkline data

    def on_slider_changed(self, event: Slider.Changed) -> None: #volume change event
        new_vol = event.value
        self.radio.player.volume = new_vol

    def on_radio_set_changed(self, event): #radio station change event
        self.radio.stop()
        selected_index = int(event.radio_set.pressed_index)
        self.current_song = urls[selected_index]["url"]
        self.radio.play(self.current_song)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "pause_button": #pause button event
            if self.radio.player.pause:
                self.radio.player.pause = False
                event.button.label = "||"
            else:
                self.radio.player.pause = True
                event.button.label = "▶"

        elif button_id == "add_button":
            if len(self.query_one("#name_input").value) > 0 and len(self.query_one("#url_input").value) > 0: # check if its empty
                new_name = self.query_one("#name_input").value #gets input values
                new_url = self.query_one("#url_input").value
                urls.append({"name": new_name, "url": new_url}) #adds to urls list
                radio_set = self.query_one("#radio_set")
                radio_set.mount(RadioButton(new_name, id="op" + str(len(urls)-1))) #adds new radio button
                collapese = self.query_one("#collapsible_content")
                collapese.mount(Checkbox(f"{new_name}", value=False, id=f"chk{len(urls)-1}")) #adds new checkbox
                self.query_one("#name_input").value = "" #clears input fields
                self.query_one("#url_input").value = ""
                with open(urls_file, "w") as f:
                    json.dump(urls, f, indent=4) #writes updated urls to json file
                self.notify(f"Station '{new_name}' added successfully.")
            else: 
                self.notify("Please enter both a station name and URL.")
                
        elif button_id == "remove_button":
            # Find which checkboxes are checked and get their indices.
            indices_to_remove = []
            for i in range(len(urls)):
                # Use query instead of query_one to avoid errors if an ID is missing.
                checkbox = self.query(f"#chk{i}").first()
                if checkbox and checkbox.value:
                    indices_to_remove.append(i)

            # If nothing is selected, there's nothing to do.
            if not indices_to_remove:
                return

            # Remove widgets and data, iterating backwards to avoid index shifting issues.
            for idx in sorted(indices_to_remove, reverse=True):
                # Remove the widgets from the UI
                self.query(f"#op{idx}").first().remove()
                self.query(f"#chk{idx}").first().remove()
                # Remove the station from our data list
                del urls[idx]

            # Write the updated station list back to the JSON file.
            with open(urls_file, "w") as f:
                json.dump(urls, f, indent=4)

            self.notify("Selected stations have been removed.")
class RadioPlayer:
    def __init__(self):
        self.player = MPV(ytdl=True, vo='null', volume=50)
        self.spark_data = [0] * 40
        self.running = False

    def play(self, url):
        self.player.play(url)
        self.running = True
        threading.Thread(target=self._sparkline_update_loop, daemon=True).start()  #starts the sparkline thread

    def stop(self):
        self.running = False
        try:
            self.player.stop()
        except:
            pass

    def _sparkline_update_loop(self):
        while self.running:
            pos = math.sin(time.time() * 3) * 10 + random.randint(1, 15)  #simulate audio levels
            if pos < 0: pos = 0
            self.spark_data.pop(0)
            self.spark_data.append(int(pos))
            time.sleep(0.1)  #update every 0.1 seconds

if __name__ == "__main__":
    app = RadioPlayerApp()
    app.run()