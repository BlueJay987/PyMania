# PyMania Parser
from pathlib import Path

def checkFileType(path):
    file = Path(path)
    if file.suffix != ".osu" and file.suffix != ".pymm":
        raise TypeError("map file must be .osu or .pymm!")
    
    with open(path, "r") as map:
        format = map.readline().strip("\ufeff")
        format = format.strip()
        if format != "osu file format v128":
            raise TypeError("osu file format must be v128!")

def parseMap(mapPath):
    """Parses a .osu beatmap into a useable format for PyMania to use."""
    #! Notes:
    # map must be osu file format v128

    # file structure:

    # standard note:
    # 0,192,500,1,0,1:0:0:100:
    # [0]: lane the note is is (0:1, 128:2, 256:3, 384:4)
    # [192]: useless, ignore it
    # [500]: ms the note will be hit
    # [1]: indicates this is a standard note
    # [0,1:0:0:100:] also pointless, ignore

    # hold note:
    # 0,192,6500,128,0,7000:1:0:0:100:
    # [0]: lane the note is is (0:1, 128:2, 256:3, 384:4)
    # [192]: useless, ignore it
    # [6500]: ms the note will be hit
    # [128]: indicates this is a hold note
    # [0]: pointless
    # [7000]: ms the note will be LET GO
    # [:1:0:0:100:]: pointless

    # notes start at line "[HitObjects]"
    checkFileType(mapPath)
    noteList = []
    with open(mapPath, "r") as map:
        readingNotes = False
        for line in map:
            line = line.strip()
            if line == "[HitObjects]":
                readingNotes = True
                continue
            if readingNotes:
                dataList = line.split(",")

                # grab each piece
                lane = int(dataList[0])
                # convert to simpler numbers
                if lane == 0:
                    lane = 1
                elif lane == 128:
                    lane = 2
                elif lane == 256:
                    lane = 3
                elif lane == 384:
                    lane = 4

                hit = int(dataList[2])

                ntype = int(dataList[3])
                # convert to easier
                if ntype == 128:
                    ntype = "hold"
                    release = int(dataList[5].split(":")[0])
                else:
                    ntype = "std"
                    release = None
                #print(f"lane:{lane}, hit:{hit}, type:{ntype}, release:{release}")


                # construct note dict
                noteDict = {
                    "Type": ntype,
                    "Lane": lane,
                    "Hit": hit
                }
                if release:
                    noteDict["Release"] = release
                
                noteList.append(noteDict)
    return noteList


if __name__ == "__main__":
    print(parseMap("/media/pi/BackupFD/PyMania/testmap/metronome - testmap1 (BlueJay987) [e].osu"))