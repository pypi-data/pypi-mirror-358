import random
import time
from itertools import count as breakloop
import win32gui as g,win32api as a
import pyautogui

def sass_reply():
    sass_responses = [
        "Oh, you want my opinion? Nah.",
        "Let me think ... no.",
        "🩰💅💅💅💄💄💄",
        "I'm not here to hold your hand.",
        "If I had a penny for every time I heard that I'd be rich enough to ignore you.",
        "Your question is beyond my level of interest.",
    ]
    
    return random.choice(sass_responses)

def annoying_load():
    print("Loading...")
    time_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    time_list_2 = [15, 20]
    time.sleep(random.choice(time_list))
    print("Not Done!")
    time.sleep(1)
    print("Loading...")
    time.sleep(random.choice(time_list))
    print("Almost there...")
    time.sleep(random.choice(time_list))
    print("Just kidding, I'm not loading anything for you.")
    time.sleep(1)
    print("Or am I?")
    time.sleep(1)
    print("Loading... please wait.))")
    print("Oh.. and here's a picture of me:")
    time.sleep(1)
    print(""""

▒▒▒▒▒▒▒▒╧╧╧╧╧╧╧▒▒▒▒▒▒▒▒XXXXXXX▒XXXXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒▒╧░░░░░░░╧▒▒▒XXXXX║║║║║║║║║║║X▒╧╧╧╧╧╧╧▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒╧╧╧╧░░░░░░░░░╧XX║║║║║░░░░░░░░░░║╧╧░░░░░░╧╧╧╧╧▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒╧░░░╧╧░░░░░░░╧▒X║║░░░░░░░░░░░░░░╧║X░░░░░░░░░╧░╧▒▒XXXXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒╧░░░░░╧╧╧╧╧╧╧╧▒▒XX║░░░░░▓░░░▓░░░░░╧╧░░░░╧░░░░░░░XX░░░░X▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒X░░░XXXX▒▒▒▒▒▒▒▒X║░░█░░░░░░░█░░░░║X╧╧╧╧╧╧╧░░░░░░░░░XXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒X░░░░░░░X▒▒▒▒▒▒▒XX║░░░███████░░░░║║X▒▒▒▒▒▒╧╧X░░░░░░░░░░X▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
X░░░░░░░XX▒▒▒▒▒▒▒X║║║░░░░░░░░░░░║║XXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒XXX░░XXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
X░░░░░X░░X▒▒▒▒▒▒▒XXX║║║║║║║║║║║║XXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒XXX░░XXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒XX░░░XXXX▒▒▒▒▒▒▒▒▒XXXXXXXXXXXXXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒XXXXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒XXXX▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒███▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒███▒█▒▒█▒▒▒▒▒█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒███▒▒█▒▒▒▒████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒▒█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
""")
    print("Actually loading something, please wait...")
    time.sleep(random.choice(time_list_2))
    print("Really done now!")
    time.sleep(10) 
    print("Just kidding, I'm still loading.")
    print("""⋆˚🐝˖        ╱|、
                          (˚ˎ 。7          look, a bee!
                           |、˜〵          
                          じしˍ,)ノ """)

def crash():
    print("System crash imminent! Brace yourself!")
    time.sleep(2)
    print("Just kidding, but wouldn't that be fun?")
    time.sleep(1)
    print("Or would it? Who knows...")
    time.sleep(1)
    print("Please wait while microsoft tries to fix this.")
    time.sleep(2)
    print("Oooh they fixed it!")
    print("You have 10 seconds before the system crashes. (really crashes this time)")
    print("This is not a joke, I promise.")
    print("10")
    time.sleep(1)
    print("9")
    time.sleep(1)
    print("8")
    time.sleep(1)
    print("7")
    time.sleep(1)
    print("6")
    time.sleep(1)
    print("5")
    time.sleep(1)
    print("4")
    time.sleep(1)
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    time.sleep(1)
    print("SO LONG, SUCKER!")
    list(breakloop(0))

def matrix_overtake():
    print("Welcome to the Matrix!")
    print("This program will take over your screen with a Matrix-like effect.")
    print("Simply stop running this script to exit.")
    print("You have 5 seconds to prepare.")
    time.sleep(5)
    sym = "ｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕ"
    sym += "日ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂ💅💄🩰"
    sym += "0123456789010101100101001"

    dc = g.GetDC(0)
    font = g.LOGFONT()
    font.lfFaceName = "Consolas"
    fnt = g.CreateFontIndirect(font)
    g.SelectObject(dc, fnt)
    g.SetBkColor(dc, a.RGB(0, 0, 0))
    colors = [
        a.RGB(0, 255, 65),
        a.RGB(0, 59, 0),
        a.RGB(0, 143, 17)
    ]
    w = a.GetSystemMetrics(0)
    h = a.GetSystemMetrics(1)
    while True:
        x = random.randint(0, w) // 10 * 10
        to = random.randint(0, h)
        for y in range(0, to, 15):
            color = random.choice(colors)
            g.SetTextColor(dc, color)
            g.DrawText(dc,
                       random.choice(sym),
                       1,
                       (x, y, x + 20, y + 30), 0)

def crazy_mouse():
  x,y = pyautogui.position()
  
  x += random.randint(-250,250)
  y += random.randint(-250,250)
  
  pyautogui.moveTo(x,y,duration=0.0000000000001)