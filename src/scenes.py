"""Every drawing in the video. Variants copy a base drawing and add one thing, like a teenager would."""

from functools import lru_cache

import numpy as np

from characters import dentures, shark, steve, steves_mom_eye, stick
from paint import Canvas, H, W

SCENES = {}


def scene(fn):
    SCENES[fn.__name__] = fn
    return fn


def base(fn):
    """Memoised base drawing; callers get a fresh copy to draw on."""
    cached = lru_cache(None)(fn)

    def get(name):
        return cached().copy(name)
    return get


def water(c, seeds=((3, 3), (W - 4, 3), (3, H // 2), (W - 4, H // 2))):
    for p in seeds:
        c.fill(p, "turq", only_if="white")


def sand(c, y=478):
    xs = np.linspace(-20, W + 20, 9)
    c.stroke([(x, y + c.rng.normal(0, 10)) for x in xs], 6, smooth=True)
    c.fill((W // 2, H - 3), "sand", only_if="white")
    for x in c.rng.uniform(40, W - 40, 3):
        c.spray([(x, H - 30)], "brown", radius=14, density=40)


def house(c, x, y, s=1.0):
    """Steve's house: rectangle tool, polygon roof, a door that is also a rectangle."""
    c.rect((x, y, x + 150 * s, y + 110 * s), w=4, fill="red")
    c.polygon([(x - 15 * s, y), (x + 75 * s, y - 70 * s), (x + 165 * s, y)], w=4, fill="brown")
    c.rect((x + 55 * s, y + 50 * s, x + 95 * s, y + 110 * s), w=4, fill="gold")
    c.rect((x + 108 * s, y + 20 * s, x + 138 * s, y + 45 * s), w=3, fill="white")


# ---------------------------------------------------------------- intro
@base
def _title():
    c = Canvas("title")
    c.write("BABY SHARK", 90, 150, size=88, w=11, slant=-0.1)
    c.stroke([(180, 290), (480, 300), (790, 282)], 7, "red")
    return c


@scene
def title():
    return _title("title_a")


@scene
def title_by_me():
    c = _title("title_b")
    c.type("(the movie)", 400, 320, size=30)
    c.write("BY ME", 700, 420, size=36)
    return c


@base
def _ocean():
    c = Canvas("ocean")
    c.ellipse((820, -90, 1060, 150), w=4, fill="yellow")
    c.stroke([(-10, 170), (160, 150), (330, 178), (520, 150), (700, 175), (970, 155)], 6, smooth=True)
    c.fill((480, 400), "turq")
    c.label("THE OCEAN", 110, 30, (300, 260), size=40)
    return c


@scene
def ocean():
    return _ocean("ocean_a")


@scene
def ocean_wet():
    c = _ocean("ocean_b")
    c.write("(IT IS WET)", 480, 330, size=30)
    return c


@base
def _steve_intro():
    c = Canvas("steve_intro")
    sand(c)
    steve(c, 330, 330, 1.3)
    water(c)
    c.label("THIS IS STEVE", 470, 110, (390, 300), size=40)
    c.type("he is not in this song", 470, 200, size=26)
    return c


@scene
def steve_intro():
    return _steve_intro("steve_intro_a")


@scene
def steve_house():
    c = Canvas("steve_house")
    sand(c)
    house(c, 560, 320, 1.1)
    steve(c, 330, 380, 1.1)
    water(c)
    c.label("STEVES HOUSE", 520, 80, (640, 250), size=36)
    c.bubble("HI", 220, 250, tail=(300, 350), size=30)
    return c


# ---------------------------------------------------------------- the family, one at a time
def intro(who, label_xy, target, seed_extra=""):
    c = Canvas(f"intro_{who}{seed_extra}")
    sand(c)
    x = {"baby": 480, "mommy": 460, "daddy": 470, "grandma": 450, "grandpa": 470}[who]
    T = shark(c, who, x, 330, s={"baby": 1.0, "mommy": 1.6, "daddy": 1.9, "grandma": 1.6, "grandpa": 1.6}[who])
    water(c)
    c.label(who.upper(), *label_xy, target, size=44)
    return c, T


@base
def _baby():
    c, _ = intro("baby", (120, 60), (420, 280))
    return c


@scene
def baby_1():
    return _baby("baby_1")


@scene
def baby_2():
    c = _baby("baby_2")
    c.bubble("HI", 720, 180, tail=(600, 290), size=40)
    return c


@scene
def baby_3():
    c = _baby("baby_3")
    c.write("AGE: 2\n(IN SHARK)", 620, 110, size=34)
    return c


FRAME1 = (310, 130, 650, 430)


def photo(name, members, frame=FRAME1, old_frames=()):
    """Family photo: brown rectangle frame, the family squeezed inside, Steve outside it."""
    c = Canvas(name)
    for of in old_frames:
        c.rect(of, outline="brown", w=12)
        x0, y0, x1, y1 = of
        c.erase([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0 + 20)], w=22)
    c.rect(frame, outline="brown", w=12)
    for who, x, y, s in members:
        shark(c, who, x, y, s=s)
    fx = (frame[0] + frame[2]) // 2
    c.fill((frame[0] + 12, frame[1] + 12), "turq", only_if="white")
    c.fill((frame[2] - 12, frame[3] - 12), "turq", only_if="white")
    c.write("FAMILY PHOTO", fx - 150, 40, size=36)
    return c


@scene
def baby_4():
    c = photo("baby_4", [("baby", 480, 290, 0.8)])
    steve(c, 820, 470, 0.7, flip=True)
    return c


@base
def _mommy():
    c, _ = intro("mommy", (110, 50), (330, 290))
    c.label("BAG (WHY)", 90, 420, (440, 420), size=26)
    return c


@scene
def mommy_1():
    return _mommy("mommy_1")


@scene
def mommy_2():
    c = _mommy("mommy_2")
    c.bubble("HAVE YOU\nEATEN", 740, 150, tail=(600, 270), size=32)
    return c


@scene
def mommy_3():
    c = _mommy("mommy_3")
    shark(c, "baby", 830, 420, s=0.55, flip=True)
    c.bubble("NO", 830, 300, tail=(830, 390), size=30)
    return c


@scene
def mommy_4():
    c = photo("mommy_4", [("mommy", 480, 250, 0.8), ("baby", 470, 370, 0.5)])
    steve(c, 770, 450, 0.7, flip=True)
    c.bubble("HI", 850, 340, tail=(790, 425), size=26)
    return c


@base
def _daddy():
    c, _ = intro("daddy", (80, 40), (330, 280))
    return c


@scene
def daddy_1():
    return _daddy("daddy_1")


@scene
def daddy_2():
    c = _daddy("daddy_2")
    c.bubble("I AM\nTHE DAD", 780, 140, tail=(640, 270), size=34)
    return c


@scene
def daddy_3():
    c = _daddy("daddy_3")
    # a grill: rectangle, legs, three wobbly lines of not-smoke
    c.rect((720, 330, 880, 380), w=4, fill="gray")
    for x in (735, 865):
        c.stroke([(x, 380), (x, 470)], 5)
    c.write("GRILL", 740, 250, size=30)
    c.type("(underwater. does not work)", 640, 490, size=20)
    return c


@scene
def daddy_4():
    c = photo("daddy_4", [("mommy", 430, 250, 0.7), ("baby", 420, 370, 0.45), ("daddy", 610, 300, 0.95)])
    c.label("DOESNT FIT", 700, 450, (700, 350), size=24)
    steve(c, 180, 450, 0.7)
    c.bubble("IS THERE\nROOM", 150, 320, tail=(180, 425), size=24)
    return c


@base
def _grandma():
    c, _ = intro("grandma", (100, 40), (340, 250))
    return c


@scene
def grandma_1():
    return _grandma("grandma_1")


@scene
def grandma_2():
    c = _grandma("grandma_2")
    shark(c, "baby", 830, 430, s=0.55, flip=True)
    c.bubble("YOU LOOK\nTHIN", 760, 170, tail=(640, 280), size=32)
    return c


@scene
def grandma_3():
    c = _grandma("grandma_3")
    # the sweater: a lumpy freehand blob, red, no holes of any kind
    c.stroke([(700, 330), (760, 300), (840, 305), (900, 340), (880, 450), (720, 455)], 5, smooth=True, closed=True)
    c.fill((800, 380), "red", max_px=40000)
    c.stroke([(560, 360), (700, 300)], 4, "gray")
    c.stroke([(560, 380), (705, 340)], 4, "gray")
    c.label("SWEATER\n(NO ARM HOLES)", 560, 110, (790, 300), size=28)
    return c


FRAME2 = (170, 110, 790, 440)


@scene
def grandma_4():
    c = photo("grandma_4", [("mommy", 330, 230, 0.65), ("baby", 330, 360, 0.42), ("daddy", 540, 300, 0.8),
                            ("grandma", 690, 190, 0.5)], frame=FRAME2, old_frames=[FRAME1])
    steve(c, 870, 470, 0.6, flip=True)
    c.bubble("I ALSO HAVE\nA GRANDMA", 790, 500, size=20, shape="ellipse")
    return c


@base
def _grandpa():
    c, _ = intro("grandpa", (90, 40), (330, 260))
    return c


@scene
def grandpa_1():
    return _grandpa("grandpa_1")


@scene
def grandpa_2():
    c = _grandpa("grandpa_2")
    c.bubble("BACK IN MY DAY\nTHE OCEAN WAS\nBIGGER", 700, 140, tail=(640, 290), size=26)
    return c


@scene
def grandpa_3():
    c = _grandpa("grandpa_3")
    dentures(c, 760, 450, 1.2)
    c.label("HIS TEETH", 640, 250, (755, 425), size=32)
    return c


FRAME3 = (40, 100, 920, 460)


@scene
def grandpa_4():
    c = photo("grandpa_4", [("mommy", 200, 220, 0.6), ("baby", 200, 360, 0.42), ("daddy", 420, 300, 0.75),
                            ("grandma", 640, 200, 0.55), ("grandpa", 660, 370, 0.55)],
              frame=FRAME3, old_frames=[FRAME1, FRAME2])
    steve(c, 840, 250, 0.6, flip=True)
    c.write("(ADOPTED)", 750, 300, size=24)
    c.stroke([(790, 200), (890, 310)], 8, "red")
    c.stroke([(890, 205), (795, 305)], 8, "red")
    c.bubble("WHO IS\nTHAT", 820, 500, size=20, shape="ellipse")
    return c


# ---------------------------------------------------------------- let's go hunt
def lineup(c, y=320, s=0.62, legs=False, mood="smile", x0=120, gap=175, order=("grandpa", "grandma", "mommy", "baby", "daddy")):
    Ts = {}
    for i, who in enumerate(order):
        sc = s * (0.55 if who == "baby" else 1.2 if who == "daddy" else 1)
        Ts[who] = shark(c, who, x0 + i * gap, y + (25 if who == "baby" else 0), s=sc, legs=legs, mood=mood)
    return Ts


@scene
def hunt_1():
    c = Canvas("hunt_1")
    sand(c)
    Ts = lineup(c)
    sx, sy = Ts["daddy"](70, -30)
    c.stroke([(sx - 40, sy + 30), (sx + 60, sy - 50)], 6, "brown")
    c.polygon([(sx + 55, sy - 62), (sx + 80, sy - 62), (sx + 72, sy - 40)], w=3, fill="gray")
    water(c)
    c.polygon([(300, 110), (560, 110), (560, 80), (660, 140), (560, 200), (560, 170), (300, 170)], w=4, fill="white")
    c.type("LETS GO HUNT", 330, 125, size=28)
    return c


@scene
def hunt_2():
    c = Canvas("hunt_2")
    c.write("THE PLAN", 360, 30, size=48)
    c.ellipse((80, 330, 240, 420), w=4, fill="gray")
    c.write("OUR ROCK", 80, 440, size=26)
    xs = np.linspace(230, 700, 14)
    for i in range(len(xs) - 1):
        if i % 2 == 0:
            c.stroke([(xs[i], 360 - 120 * np.sin(i / 4)), (xs[i + 1], 360 - 120 * np.sin((i + 1) / 4))], 5, "red")
    house(c, 720, 250, 0.9)
    c.write("X", 760, 190, size=50, w=9, color="red")
    c.write("FOOD", 740, 400, size=30)
    return c


@scene
def hunt_3():
    c = Canvas("hunt_3")
    sand(c)
    Ts = lineup(c, y=330, s=0.55, x0=110, gap=160, order=("daddy", "mommy", "baby", "grandma", "grandpa"))
    water(c)
    c.bubble("WHAT ARE WE\nHUNTING", 770, 140, tail=Ts["grandpa"](60, -30), size=24)
    c.bubble("SHH", 180, 150, tail=Ts["daddy"](60, -30), size=30)
    return c


@scene
def hunt_4():
    c = Canvas("hunt_4")
    sand(c)
    house(c, 600, 300, 1.2)
    steve(c, 450, 400, 1.1)
    water(c)
    c.label("DINNER", 90, 250, (400, 390), size=40, color="red")
    c.bubble("I THOUGHT I\nWAS ADOPTED", 470, 170, tail=(460, 370), size=30)
    return c


# ---------------------------------------------------------------- run away
@base
def _mom():
    c = Canvas("steves_mom")
    c.ellipse((-200, -150, 1100, 700), w=6, fill="orange")
    steves_mom_eye(c, 420, 200, 1.4)
    c.stroke([(300, 440), (420, 470), (560, 445)], 14, "red", smooth=True)
    c.write("STEVES MOM", 600, 330, size=40)
    return c


@scene
def run_1():
    c = _mom("run_1")
    c.bubble("WHO IS HUNTING\nMY SON", 700, 470, size=24, shape="ellipse")
    return c


@scene
def run_2():
    c = Canvas("run_2")
    sand(c)
    Ts = lineup(c, y=340, s=0.55, legs=True, mood="scared", x0=130, gap=165,
                order=("baby", "mommy", "daddy", "grandma", "grandpa"))
    for y in (300, 340, 380):
        c.stroke([(5, y), (60, y + 5)], 4)
    water(c)
    c.label("LEGS (NEW)", 350, 90, Ts["daddy"](20, 55), size=34)
    c.write("RUN", 740, 80, size=60, color="red", w=9)
    return c


@scene
def run_3():
    c = Canvas("run_3")
    sand(c)
    shark(c, "grandpa", 420, 340, s=1.1, legs=True, flip=True, mood="flat")
    for y in (260, 300, 340):
        c.stroke([(850, y), (955, y - 4)], 4)
    water(c)
    c.bubble("GO ON\nWITHOUT ME", 250, 130, tail=(380, 290), size=30)
    c.write("(NOBODY WAITED)", 560, 440, size=24)
    return c


@scene
def run_4():
    c = _mom("run_4")
    dentures(c, 230, 390, 2.0)
    c.stroke([(120, 460), (170, 420)], 4)
    c.stroke([(110, 420), (165, 400)], 4)
    c.label("TEETH (THROWN)", 40, 40, (230, 360), size=30)
    c.write("OW", 640, 90, size=50, w=8)
    return c


# ---------------------------------------------------------------- safe at last
@base
def _cave():
    c = Canvas("cave")
    sand(c)
    c.rect((230, 170, 730, 470), w=4, fill="black")
    rng = c.rng
    for i in range(5):
        x, y = 290 + i * 90 + rng.normal(0, 10), 300 + rng.normal(0, 30)
        for dx in (0, 22):
            c.ellipse((x + dx - 6, y - 6, x + dx + 6, y + 6), w=0, outline=None, fill="white")
    water(c)
    c.label("CAVE", 780, 120, (720, 200), size=40)
    c.type("safe at last", 400, 110, size=30)
    return c


@scene
def safe_1():
    return _cave("safe_1")


@lru_cache(None)
def _inside():
    c = Canvas("inside")
    c.rect((0, 440, W, H), w=0, outline=None, fill="brown")
    c.rect((600, 80, 820, 240), w=5, fill="turq")  # window
    c.line((710, 80), (710, 240), w=5)
    c.rect((360, 300, 620, 320), w=4, fill="dkbrown")  # table
    for x in (380, 600):
        c.line((x, 320), (x, 440), w=6)
    c.rect((60, 60, 250, 150), w=4, fill="white")
    c.type("HOME SWEET\nHOME - STEVE", 75, 75, size=22)
    Ts = {}
    for who, x, y, s in [("daddy", 200, 360, 0.7), ("mommy", 250, 250, 0.55), ("grandma", 780, 320, 0.55),
                         ("grandpa", 800, 410, 0.55), ("baby", 120, 440, 0.4)]:
        Ts[who] = shark(c, who, x, y, s=s, flip=x > 500, mood="flat")
    steve(c, 490, 250, 0.9)
    return c, Ts


@scene
def safe_2():
    c, Ts = _inside_copy("safe_2")
    c.bubble("HELLO", 490, 120, tail=(490, 225), size=32)
    return c


def _inside_copy(name):
    c, Ts = _inside()
    return c.copy(name), Ts


@scene
def safe_3():
    c, Ts = _inside_copy("safe_3")
    for x in (400, 470, 540):
        c.ellipse((x, 280, x + 30, 300), w=3, fill="white")
    c.bubble("YOU LOOK\nTHIN", 820, 490, size=22, shape="ellipse")
    c.label("AWKWARD", 380, 40, (330, 180), size=32)
    return c


@scene
def safe_4():
    c, Ts = _inside_copy("safe_4")
    for x in (400, 470, 540):
        c.ellipse((x, 280, x + 30, 300), w=3, fill="white")
    c.ellipse((620, 110, 700, 170), w=3, fill="white")
    c.ellipse((645, 120, 675, 160), w=0, outline=None, fill="black")
    c.bubble("MOM WE HAVE\nGUESTS", 380, 110, tail=(470, 225), size=26)
    return c


# ---------------------------------------------------------------- it's the end
@scene
def end_1():
    c = Canvas("end_1")
    c.rect((0, 430, W, H), w=4, fill="brown")  # desk
    c.ellipse((250, 60, 710, 440), w=5, fill="white")  # fishbowl
    inner = SCENES["safe_4"]()
    c.paste_small(inner, (340, 170, 620, 327))
    c.stroke([(290, 170), (480, 160), (670, 172)], 4)
    c.label("THE OCEAN", 640, 40, (620, 190), size=34)
    return c


@scene
def end_2():
    c = Canvas("end_2")
    c.rect((0, 400, W, H), w=4, fill="brown")
    c.paste_small(SCENES["end_1"](), (560, 250, 900, 441))
    c.rect((100, 80, 480, 330), w=6, fill="black")
    c.rect((120, 100, 460, 310), w=0, outline=None, fill="white")
    c.rect((120, 100, 460, 118), w=0, outline=None, fill="winblue")
    c.type("untitled - Paint", 126, 101, size=13, color="white")
    c.paste_small(SCENES["safe_4"](), (135, 125, 445, 300))
    c.rect((250, 330, 330, 400), w=4, fill="gray")
    c.label("COMPUTER", 520, 60, (470, 150), size=34)
    return c


@base
def _teen():
    c = Canvas("teen")
    c.rect((0, 400, W, H), w=4, fill="brown")
    c.rect((430, 120, 760, 330), w=6, fill="black")
    c.rect((448, 138, 742, 312), w=0, outline=None, fill="white")
    c.paste_small(SCENES["safe_4"](), (455, 150, 735, 305))
    c.rect((560, 330, 630, 400), w=4, fill="gray")
    stick(c, 250, 120, 1.25, arm="type")
    c.label("ME", 60, 90, (220, 150), size=40)
    return c


@scene
def end_3():
    c = _teen("end_3")
    c.bubble("IM BORED", 230, 60, size=28)
    return c


@scene
def end_4():
    c = _teen("end_4")
    c.write("THE END", 330, 40, size=70, w=9, color="red")
    c.bubble("DINNER", 830, 190, size=30)
    c.write("(MY MOM)", 770, 270, size=20)
    return c


@scene
def save_dialog():
    c = Canvas("save_dialog", bg="black")
    c.rect((230, 170, 730, 370), w=2, fill="wingray")  # pasted in with Print Screen, like everyone did
    c.rect((230, 170, 730, 200), w=0, outline=None, fill="winblue")
    c.type("Paint", 240, 174, size=18, color="white")
    c.type("Do you want to save changes to Untitled?", 260, 225, size=20)
    for i, t in enumerate(["Save", "Don't Save", "Cancel"]):
        x = 330 + i * 125
        c.rect((x, 305, x + 110, 340), w=2, fill="white")
        c.type(t, x + 12, 312, size=17)
    c.polygon([(470, 318), (470, 348), (478, 341), (484, 355), (489, 353), (483, 339), (493, 338)],
              w=2, fill="white")
    return c


# ---------------------------------------------------------------- outro (not saved)
@base
def _void():
    c = Canvas("void")
    shark(c, "baby", 330, 300, s=0.9)
    return c


@scene
def outro_1():
    c = _void("outro_1")
    c.bubble("HELLO?", 330, 150, tail=(350, 260), size=32)
    return c


@base
def _void2():
    c = _void("void2")
    steve(c, 640, 310, 1.0, flip=True)
    return c


@scene
def outro_2():
    c = _void2("outro_2")
    c.bubble("HE DIDNT\nSAVE", 660, 160, tail=(640, 280), size=30)
    return c


@scene
def outro_3():
    c = _void2("outro_3")
    c.bubble("SO WE DONT\nEXIST", 280, 140, tail=(320, 260), size=26)
    c.bubble("CORRECT", 700, 450, tail=(650, 340), size=26)
    return c


@scene
def outro_4():
    c = _void2("outro_4")
    steves_mom_eye(c, 820, 110, 0.9)
    c.write("STEVE.\nDINNER.", 560, 400, size=40, w=6)
    return c


# ---------------------------------------------------------------- end card (silence)
@base
def _card():
    c = Canvas("card")
    c.write("THE END", 250, 150, size=100, w=11)
    return c


@scene
def card_1():
    return _card("card_1")


@scene
def card_2():
    c = _card("card_2")
    c.type("no sharks were harmed in the making of this video", 180, 330, size=24)
    c.write("STEVE WAS A BIT HARMED", 250, 380, size=26)
    return c


@scene
def card_3():
    c = _card("card_3")
    c.type("no sharks were harmed in the making of this video", 180, 330, size=24)
    c.write("STEVE WAS A BIT HARMED", 250, 380, size=26)
    c.type("made in paint", 780, 505, size=16)
    steve(c, 120, 470, 0.6)
    return c
