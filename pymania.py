import pygame
from pygame.locals import *
import sys
import parser
import argparse


pygame.init()

#~ PyGame VARS
WINDOWWIDTH = 1920
WINDOWHEIGHT = 1080
window = pygame.display.set_mode((1920,1080))
clock = pygame.time.Clock()
FPS = 120


#~ GAME VARS

# get map/audio from arguments
parse = argparse.ArgumentParser(description="Run PyMania.")
parse.add_argument("--audioPath", type=str, help="Path to audio file.", default="maps/Aresene's Bazaar/audio.mp3")
parse.add_argument("--mapPath", type=str, help="Path to map file.", default="maps/Aresene's Bazaar/Aresene's Bazaar  [Normal].osu")
args = parse.parse_args()

# store args, or use defaults
AUDIO = args.audioPath
MAP = args.mapPath

SCROLLSPEED = 1.3 # i wouldn't go above 2.5
VOLUME = 0.1 # between 0.0-1.0 (this is LOUD, stay low)
GLOBALINPUTOFFSET = 0 # offsets all inputs by this value. may not be needed

NOTEWIDTH = 120
NOTEHEIGHT = 30
NOTECOLORS = {
    1: (255, 92, 30),  # orange
    2: (50, 200, 255),  # cyan 
    3: (255, 50, 255),  # magenta
    4: (255, 50, 50),   # red
}
JUDGEMENTY = 930

# JUDGEMENT VALUES
# all in ms
MISSJUDGE = 80

# JUDGEMENT COLORS
# Perfect: (0, 158, 245)
# Good: (27, 212, 0)
# OK: (245, 225, 0)
# Miss: (255, 0, 0)

#~ Classes

class Note():
    """class for note objects"""
    def __init__(self, noteDict: dict):
        # grab stuff from dict
        # info about noteDict found in parser.py
        self.lane = noteDict["Lane"]
        self.hitTime = noteDict["Hit"]
        self.type = noteDict["Type"]
        if self.type == "hold":
            self.releaseTime = noteDict["Release"]
            self.holdLength = 0
            self.wasHit = False
        
        self.yPos = 0

    
    def drawNote(self):
        """draw the note on screen"""
        noteColor = NOTECOLORS[self.lane]
        sinceSpawn = (getSongTime() - (self.hitTime - JUDGEMENTY/SCROLLSPEED)+NOTEHEIGHT)
        if sinceSpawn >= 0:
            self.yPos = (sinceSpawn*SCROLLSPEED)
            if self.type == "std":
                pygame.draw.rect(window, noteColor, (self.lane*NOTEWIDTH+(NOTEWIDTH*5),self.yPos, NOTEWIDTH, NOTEHEIGHT))
            else:
                self.holdLength = ((self.releaseTime - self.hitTime) * SCROLLSPEED) + NOTEHEIGHT
                pygame.draw.rect(window, noteColor, (self.lane*NOTEWIDTH+(NOTEWIDTH*5),self.yPos-(self.holdLength-NOTEHEIGHT), NOTEWIDTH, self.holdLength))

class KeyIndicator():
    def __init__(self, lane):
        self.lane = lane
        keys = {
            1: K_d,
            2: K_f,
            3: K_j,
            4: K_k,
        }
        self.key = keys[self.lane]

        self.color = (0, 0, 0)
    
    def update(self, judgement):
        pressedKeys = pygame.key.get_pressed()
        if pressedKeys[self.key]:
            if judgement == "Perfect":
                self.color = (0, 158, 245)
            elif judgement == "Good":
                self.color = (27, 212, 0)
            elif judgement == "Ok":
                self.color = (245, 225, 0)
            elif judgement == "Miss":
                self.color = (255, 0, 0)
        else:
            self.color = (0,0,0)
        
        pygame.draw.rect(window, self.color, (self.lane*NOTEWIDTH+(NOTEWIDTH*5), JUDGEMENTY+4, NOTEWIDTH, WINDOWHEIGHT-JUDGEMENTY))

class PlayerStats():
    """class to handle scoring data"""
    def __init__(self):
        """init function"""
        self.score = 0
        self.accuracy = 0.00 # is a %
        self.combo = 0

        #hit type counters (HT counters)
        self.perfects = 0
        self.goods = 0
        self.oks = 0
        self.misses = 0

        # fonts for blit
        self.scoreFont = pygame.font.Font("fonts/Azonix-1VB0.otf", 55)
        self.htFont = pygame.font.Font("fonts/Azonix-1VB0.otf", 50)
        self.comboFont = pygame.font.Font("fonts/Azonix-1VB0.otf", 105)
        
    def draw(self, surface):
        """draw HUD."""
        
        # draw score
        scoreText = self.scoreFont.render(f"{self.score}", True, (255,255,255)) # white
        scoreRect = scoreText.get_rect()
        scoreRect.midright = (WINDOWWIDTH//3,scoreRect.height*1.2)
        surface.blit(scoreText, scoreRect)

        # draw combo
        comboText = self.comboFont.render(f"x{self.combo}", True, (255,255,255)) # white
        comboRect = comboText.get_rect()
        comboRect.center = (WINDOWWIDTH//2,WINDOWHEIGHT//2)
        surface.blit(comboText, comboRect)

        # draw acc
        accText = self.scoreFont.render(f"{self.accuracy:.2f}%", True, (255,255,255)) # white
        accRect = accText.get_rect()
        accRect.midleft = (WINDOWWIDTH//1.5,accRect.height*1.2)
        surface.blit(accText, accRect)

        # draw HTs
        missText = self.htFont.render(f"Miss: {self.misses}", True, (255,0,0)) # miss color
        missRect = missText.get_rect()
        missRect.midleft = (WINDOWWIDTH//1.5,WINDOWHEIGHT//2+missRect.height*2)
        surface.blit(missText, missRect)

        okText = self.htFont.render(f"Ok: {self.oks}", True, (245, 225, 0)) # ok color
        okRect = okText.get_rect()
        okRect.midleft = (WINDOWWIDTH//1.5,WINDOWHEIGHT//2+okRect.height)
        surface.blit(okText, okRect)

        goodText = self.htFont.render(f"Good: {self.goods}", True, (27, 212, 0)) # good color
        goodRect = goodText.get_rect()
        goodRect.midleft = (WINDOWWIDTH//1.5,WINDOWHEIGHT//2)
        surface.blit(goodText, goodRect)

        perfectText = self.htFont.render(f"Perfect: {self.perfects}", True, (0, 158, 245)) # perfect color
        perfectRect = okText.get_rect()
        perfectRect.midleft = (WINDOWWIDTH//1.5,WINDOWHEIGHT//2-perfectRect.height)
        surface.blit(perfectText, perfectRect)          

    def addNoteHit(self, judgement):
        """take in a note judgement, and add to score and HT counters"""
        if judgement == "Perfect":
            self.score += 300
            self.perfects += 1
            self.increaseCombo()
        elif judgement == "Good":
            self.score += 100
            self.goods += 1
            self.increaseCombo()
        elif judgement == "Ok":
            self.score += 50
            self.oks += 1
            self.increaseCombo()
        elif judgement == "Miss":
            self.misses += 1
            self.breakCombo()
            pass
        self.calcAcc()

    def calcAcc(self):
        """take in the amt of notes hit, calculate the max score, and
        generate a percentage for accuracy
        """
        totalHits = self.perfects + self.goods + self.oks + self.misses
        maxPossScore = totalHits*300 # score if all perfects
        self.accuracy = round((self.score/maxPossScore)*100, 2) # looks like 90.34%
    
    def increaseCombo(self):
        """increases combo."""
        self.combo += 1

    def breakCombo(self):
        """break the combo."""
        self.combo = 0

class DebugText():
    """prints some simple debug text. only using in development."""
    def __init__(self):
        self.font = pygame.font.Font("fonts/Azonix-1VB0.otf", 55)

    def draw(self, x, y, text, surface):
        debug = self.font.render(text, True, (255,255,255))
        rect = debug.get_rect()
        rect.midleft = (x, y)
        surface.blit(debug, rect)

class ResultScreen():
    """shows and calculates the results screen at the end"""
    def __init__(self, stats: PlayerStats):
        self.grade = ""
        self.gradeColor = ()
        self.stats = stats

        self.gradeFont = pygame.font.Font("fonts/Azonix-1VB0.otf", 400)
        self.basicFont = pygame.font.Font("fonts/Azonix-1VB0.otf", 70)
        self.statFont = pygame.font.Font("fonts/Azonix-1VB0.otf", 85)
        self.htFont = pygame.font.Font("fonts/Azonix-1VB0.otf", 70)
    
    def calculate(self):
        """calculates all stuff needed for displaying"""
        if self.stats.accuracy >= 99:
            self.grade = "SS"
            self.gradeColor = (252, 18, 225)
        elif self.stats.accuracy >= 94:
            self.grade = "S"
            self.gradeColor = (10, 237, 245)
        elif self.stats.accuracy >= 90:
            self.grade = "A"
            self.gradeColor = (0, 247, 21)
        elif self.stats.accuracy >= 80:
            self.grade = "B"
            self.gradeColor = (245, 237, 7)
        elif self.stats.accuracy >= 70:
            self.grade = "C"
            self.gradeColor = (250, 143, 2)
        else:
            self.grade = "F"
            self.gradeColor = (252, 36, 8)
    
    def draw(self, surface):
        """draw the results screen"""
        self.calculate()

        gradeText = self.gradeFont.render(self.grade, True, self.gradeColor)
        gradeRect = gradeText.get_rect()
        gradeRect.center = (WINDOWWIDTH//2, WINDOWHEIGHT//2)
        surface.blit(gradeText, gradeRect)

        accLText = self.basicFont.render("Accuracy", True, (255,255,255))
        accLRect = accLText.get_rect()
        accLRect.center = (WINDOWWIDTH//2, accLRect.height*1.5)
        surface.blit(accLText, accLRect)

        accText = self.statFont.render(f"{self.stats.accuracy:.2f}%", True, (255,255,255))
        accRect = accText.get_rect()
        accRect.center = (WINDOWWIDTH//2, WINDOWHEIGHT//5)
        surface.blit(accText, accRect)

        scoreLText = self.basicFont.render("Score", True, (255,255,255))
        scoreLRect = scoreLText.get_rect()
        scoreLRect.center = (WINDOWWIDTH//2, WINDOWHEIGHT-(scoreLRect.height*4.5))
        surface.blit(scoreLText, scoreLRect)

        scoreText = self.statFont.render(f"{self.stats.score}", True, (255,255,255))
        scoreRect = scoreText.get_rect()
        scoreRect.center = (WINDOWWIDTH//2, WINDOWHEIGHT//1.25)
        surface.blit(scoreText, scoreRect)

        # HTs
        missText = self.htFont.render(f"Miss: {self.stats.misses}", True, (255,0,0)) # miss color
        missRect = missText.get_rect()
        missRect.midleft = (WINDOWWIDTH//1.5,WINDOWHEIGHT//2+missRect.height*2)
        surface.blit(missText, missRect)

        okText = self.htFont.render(f"Ok: {self.stats.oks}", True, (245, 225, 0)) # ok color
        okRect = okText.get_rect()
        okRect.midleft = (WINDOWWIDTH//1.5,WINDOWHEIGHT//2+okRect.height)
        surface.blit(okText, okRect)

        goodText = self.htFont.render(f"Good: {self.stats.goods}", True, (27, 212, 0)) # good color
        goodRect = goodText.get_rect()
        goodRect.midleft = (WINDOWWIDTH//1.5,WINDOWHEIGHT//2)
        surface.blit(goodText, goodRect)

        perfectText = self.htFont.render(f"Perfect: {self.stats.perfects}", True, (0, 158, 245)) # perfect color
        perfectRect = okText.get_rect()
        perfectRect.midleft = (WINDOWWIDTH//1.5,WINDOWHEIGHT//2-perfectRect.height)
        surface.blit(perfectText, perfectRect)   



#~ Global Funcs

def getSongTime():
    """
    get current song time in ms.
    this only exists because the pygame command is too damn long.
    """
    return pygame.mixer.music.get_pos()


def drawLaneBorders():
    """draws the lane borders."""
    pygame.draw.line(window, (255,255,255), (WINDOWWIDTH//2+(NOTEWIDTH*2), 0), (WINDOWWIDTH//2+(NOTEWIDTH*2), WINDOWHEIGHT), 4)
    pygame.draw.line(window, (255,255,255), (WINDOWWIDTH//2-(NOTEWIDTH*2), 0), (WINDOWWIDTH//2-(NOTEWIDTH*2), WINDOWHEIGHT), 4)


def drawJudgementLine():
    """take a wild guess."""
    pygame.draw.line(window, (255,255,255), (WINDOWWIDTH//2-(NOTEWIDTH*2), JUDGEMENTY), (WINDOWWIDTH//2+(NOTEWIDTH*2), JUDGEMENTY), 4)

def calcJudgements(offset, keys, lane):
    """take in a hit offset, and returns a judgement string."""
    # Perfect: <= 32ms
    # Good: 33-70ms
    # Ok: 71-120ms
    # Miss: anything greater

    # JUDGEMENT COLORS
    # Perfect: (0, 158, 245)
    # Good: (27, 212, 0)
    # OK: (245, 225, 0)
    # Miss: (255, 0, 0)
    offset = abs(offset)-GLOBALINPUTOFFSET

    if offset <= 25:
        return "Perfect"
    elif offset <= 55:
        return "Good"
    elif offset <= MISSJUDGE:
        return "Ok"
    else:
        return "Miss"

# load and play song, and load notes
pygame.mixer.music.set_volume(VOLUME)
pygame.mixer.music.load(AUDIO)
pygame.time.delay(700)
pygame.mixer.music.play()

# I LEARNED HOW TO DO THESE COOL ONE-LINERS
# create our list of note classes
noteList = [Note(note) for note in parser.parseMap(MAP)]

# make all 4 key indicators
keyIndicators = [KeyIndicator(i+1) for i in range(4)]

# make a playerstat
stat = PlayerStats()

# each key represents the corresponding lane
# values can only be 2 things: the songtime the key was pressed (in ms) or None (key released)
currentHitKeys = {
    1:None,
    2:None,
    3:None,
    4:None,
}

debug = DebugText()
judgement = ""


drawJudgementLine()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == KEYDOWN:
            if event.key == K_d:
                currentHitKeys[1] = getSongTime()
            elif event.key == K_f:
                currentHitKeys[2] = getSongTime()
            elif event.key == K_j:
                currentHitKeys[3] = getSongTime()
            elif event.key == K_k:
                currentHitKeys[4] = getSongTime()
            # allows quitting with escape 
            elif event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

        elif event.type == KEYUP:
            if event.key == K_d:
                currentHitKeys[1] = None
            elif event.key == K_f:
                currentHitKeys[2] = None
            elif event.key == K_j:
                currentHitKeys[3] = None
            elif event.key == K_k:
                currentHitKeys[4] = None

    # draw bg always
    window.fill("BLACK")

    # check if music is playing
    if pygame.mixer.music.get_busy():
        drawJudgementLine()
        # draw all notes
        for note in noteList:
            note.drawNote()
            
            if currentHitKeys[note.lane] is not None:
                if abs(currentHitKeys[note.lane] - note.hitTime) <= 75:
                    judgement = calcJudgements(currentHitKeys[note.lane] - note.hitTime, keyIndicators, note.lane-1)

                    #print(f"{judgement} {currentHitKeys[note.lane]}:{note.hitTime}") # debug

                    if note.type == "std":
                        stat.addNoteHit(judgement) # add judment to stat calculations
                        noteList.remove(note) # delete note
                    elif note.type == "hold" and not note.wasHit:
                        stat.addNoteHit(judgement)
                        note.wasHit = True

                else:
                    judgement = None
                    keyIndicators[note.lane-1].color = (255, 255, 255)
            
            # count unhit notes as misses, both std and LN
            if getSongTime() - note.hitTime > MISSJUDGE:
                if note.type == "std":
                    stat.addNoteHit("Miss")
                    noteList.remove(note)

                elif note.type == "hold" and not note.wasHit:
                    stat.addNoteHit("Miss")
                    noteList.remove(note)
                    #debug.draw(200, 200, str(note.yPos), window)
            
            # count as miss if LN isn't held the whole duration
            if note.type == "hold" and getSongTime() < note.releaseTime-MISSJUDGE and getSongTime() > note.hitTime+MISSJUDGE and currentHitKeys[note.lane] is None and note.wasHit:
                stat.addNoteHit("Miss")
                noteList.remove(note)
        
        # update key indicators            
        for indic in keyIndicators:
            indic.update(judgement)

        # draw borders and stats
        drawLaneBorders()
        stat.draw(window)
    else: # if the music ended
        # show results screen
        pygame.time.delay(500)
        results = ResultScreen(stat)
        results.draw(window)


    # update stuff
    pygame.display.update()
    clock.tick(FPS)