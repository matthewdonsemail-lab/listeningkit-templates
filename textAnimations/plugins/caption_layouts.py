"""Editorial layout for each caption in Intro 1: stacked lines, the key word huge, connectives small,
the block fitted to the shot's negative space. One entry per caption window (same order as make_captions.SHOTS
windows that have words). Each line: (words, x, y, size, justify). Words must match the VO in order.
Sizes: 44-50 connectives (wide tracking), 90-300 key words (tight tracking). x/y are the baseline anchor."""
S, M = 46, 90  # small, mid
LAYOUTS = [
    # 0-2.3 hill, sky above her
    [("WE WERE", 120, 170, S, "L"), ("PROMISED", 110, 300, 125, "L"), ("A FUTURE WHERE", 124, 360, S, "L")],
    # 2.3-4.8 hill
    [("AI", 1620, 300, 230, "R"), ("WOULD DO SO", 1620, 365, S, "R"), ("MUCH MORE.", 1620, 480, 110, "R")],
    # 4.8-6.0 hill
    [("INSTEAD,", 300, 200, S, "L"), ("WE'RE SAT", 300, 330, 120, "L")],
    # 6.0-9.8 her head fills the frame: opposite corners
    [("HERE", 1810, 110, S, "R"), ("WORKING", 1810, 215, 100, "R"), ("HARDER", 1810, 320, 100, "R"),
     ("AND LONGER.", 1810, 378, S, "R")],  # top right: the PS2 cutout holds the top left
    # 9.8-11.97 head turn, face centre
    [("NOT ANY", 960, 95, 52, "C"), ("LONGER.", 960, 260, 170, "C")],
    # 16.97-19.27 headband portraits, dark bottom band
    [("HERMES", 100, 1030, 190, "L"), ("WAS BUILT TO WORK", 116, 860, S, "L")],
    # 19.27-20.40 whisper network, black top right
    [("ON ITS", 1810, 150, 60, "R"), ("OWN.", 1810, 340, 210, "R")],
    # 20.40-22.00
    [("IT JUST NEVER HAD", 1810, 140, S, "R"), ("A NATIVE", 1810, 275, 130, "R")],
    # 22.00-23.40 conspiracy, dark lower left
    [("WAY TO", 120, 780, S, "L"), ("BE YOU.", 110, 965, 190, "L")],
    # 23.40-24.97
    [("NOW IT WORKS", 120, 800, S, "L"), ("NATIVELY", 110, 965, 160, "L")],
    # 24.97-26.94 X card, left of it
    [("WITH EVERY SOCIAL", 140, 150, S, "L"), ("YOU OWN.", 135, 275, 120, "L")],
    # 33.40-34.64 laptop, black top left beside her shadow
    [("LOG", 110, 310, 270, "L"), ("INGESTS EVERY", 120, 380, 50, "L")],
    # 34.64-35.68 blinds, dark lower right
    [("CONVERSATION", 1820, 905, 120, "R"), ("YOU'VE", 1820, 975, 50, "R")],
    # 35.68-36.67 eyes, below
    [("EVER", 960, 880, 50, "C"), ("HAD,", 960, 1045, 170, "C")],
    # 36.67-38.00 inbox demo, below the cards
    [("INDEXES", 960, 950, 130, "C"), ("THEM AND", 960, 1020, S, "C")],
    # 38.00-39.22 her shadow studies her: black above her head, top left
    [("BUILDS A", 120, 105, S, "L"), ("VOICE", 110, 210, 100, "L"), ("PROFILE", 110, 310, 100, "L")],
    # 39.22-40.25 two shadows, empty right half
    [("OF", 1540, 430, 60, "C"), ("YOU.", 1540, 660, 260, "C")],
    # 40.25-41.20 ring of screens: diagonal across the black corners
    [("LOCAL", 110, 190, 120, "L"), ("MODELS", 1810, 1000, 120, "R")],
    # 41.20-41.82 card shadows, dark lower left
    [("RE-RANK,", 110, 1010, 200, "L")],
    # 41.82-42.54 palm, black above
    [("EMBED", 960, 240, 210, "C"), ("AND", 960, 310, S, "C")],
    # 42.54-43.45 chart, dark lower left
    [("VECTOR", 120, 790, 50, "L"), ("SEARCH", 110, 945, 170, "L"), ("THE", 120, 1010, S, "L")],
    # 43.45-44.38 her lips, black right
    [("WAY YOU", 1800, 420, 52, "R"), ("ACTUALLY", 1800, 565, 150, "R")],
    # 44.38-45.45 the shadow speaks, dark lower right
    [("TALK.", 1350, 1010, 300, "C")],
    # 45.45-47.40 reply demo, right of the card
    [("SO HERMES", 1810, 400, S, "R"), ("SPEAKS", 1810, 510, M, "R"), ("LIKE YOU,", 1810, 610, M, "R")],
    # 47.40-49.70
    [("WHEN IT MATTERS,", 1810, 380, S, "R"), ("TO WHO IT", 1810, 440, S, "R"), ("MATTERS.", 1810, 555, 100, "R")],
    # 49.70-52.90 three steps, right of the card
    [("AN OFFICIAL", 1810, 400, S, "R"), ("HERMES", 1810, 490, 80, "R"), ("PLUGIN,", 1810, 580, 80, "R"),
     ("BUILT TO", 1810, 640, S, "R")],
    # 52.90-54.70 she walks out: black ceiling, the shadow at the desk below
    [("GIVE YOU", 110, 150, S, "L"), ("YOUR TIME", 110, 300, 150, "L"), ("BACK,", 110, 440, 150, "L")],
]

