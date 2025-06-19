import tkinter as tk
from tkinter import filedialog
import subprocess
import sys
import os
from pathlib import Path


class MapSelector(tk.Tk):
    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
    
        self.title("PyMania Loader")
        self.configure(bg="#191919")
        self.geometry("400x400")
        self.resizable(False, False)

        self.mapPath = None
        self.mapPathVar = tk.StringVar(value=str(self.mapPath))
        self.audioPath = None
        self.audioPathVar = tk.StringVar(value=str(self.audioPath))

        self.createWidgets()



    
    def createWidgets(self):
        """creates all the widgets to display"""
        title = tk.Label(
            text="PyMania Loader",
            font=("Courier", 20),
            bg="#191919",
            fg="white",
        )
        title.pack(pady=20)

        mapfilelabel = tk.Label(
            text="Map",
            font=("Courier", 15),
            bg="#191919",
            fg="white",
        )
        mapfilelabel.pack()

        mapPathlabel = tk.Label(
            textvariable=self.mapPathVar,
            font=("Courier", 10),
            bg="#191919",
            fg="magenta",
        )
        mapPathlabel.pack()

        mapButton = tk.Button(
            text="Select",
            width=10,
            height=2,
            font=("Courier", 12),
            command=self.getMapPath,
            anchor="center",
            bg="#3B82F6",
        )
        mapButton.pack(pady=10)

        audioPathlabel = tk.Label(
            textvariable=self.audioPathVar,
            font=("Courier", 10),
            bg="#191919",
            fg="magenta",
        )
        audioPathlabel.pack()

        playButton = tk.Button(
            text="Play Map",
            width=15,
            height=3,
            font=("Courier", 20),
            command=self.launch,
            anchor="center",
            bg="#3B82F6",
        )
        playButton.pack(pady=30)

    def getMapPath(self):
        """returns the filepath of the map, as well as automatically fetching the audio too."""
        filetypes = (
            ("Map Files", "*.osu *.pymm"),
            ("All Files", "*.*")
        )
        self.mapPath = filedialog.askopenfilename(filetypes=filetypes)
        self.mapPathVar.set(os.path.basename(self.mapPath))

        # using the map path, find the audio path
        mapdir = Path(self.mapPath).parent

        for i in [".mp3", ".ogg", ".wav"]:
            filename = f"audio{i}"
            audio = mapdir / filename
            if audio.exists():
                self.audioPath = audio
                self.audioPathVar.set(os.path.basename(self.audioPath))

    def launch(self):
        """launches PyMania"""
        command = [sys.executable, "pymania.py", "--audioPath", self.audioPath, "--mapPath", self.mapPath]

        subprocess.Popen(command)


if __name__ == "__main__":
    app = MapSelector()
    app.mainloop()