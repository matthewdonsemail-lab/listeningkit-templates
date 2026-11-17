"""The launch film's process as an Excalidraw board (matt, 2026-11-16), for a video walking through how it was made:
four columns left to right, each picture with its caption:
  1 REFERENCES       the TikToks, trailers and edits he gave, the frames picked out of them
  2 PULLED OUT       what numpy extracted from them: the effect layers, the ECG line, the red-flash seeds, the
                     Edgerunners 2 line skeletons
  3 GENERATED        what the generators made from that: the red lines, the girl flash cuts, the UI elements, ...
  4 IN THE FILM      stills from the final cut, and frames from the final render
Pictures are shrunk to 1000 px JPEGs and embedded in the file. Writes
textAnimations/PROCESS_BOARD.excalidraw (open it at excalidraw.com: menu > Open, or drop the file on the page).
  python textAnimations/assets/make_process_board.py"""
import base64
import hashlib
import io
import json
import os
import random
import subprocess

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(TA, ".."))
REF = os.path.join(REPO, "projects", "opening", "ref")
YT = "https://www.youtube.com/watch?v="
WALK = "C:/Users/0/filmcraft/projects/effectcraftEditing"


def G(folder, *names):
    """the generated stills in projects/<folder> (the named ones, or every non-raw .png), for a sheet"""
    d = os.path.join(REPO, "projects", folder)
    if names:
        return [os.path.join(d, n + ".png") for n in names]
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".png") and "_raw" not in f]
COLS = [
    ("0  THE OPENER", [
        (REF + "/../../opening/ref/bigshort_stylesheet.png" if False else TA + "/assets/collage/process/opener_bigshort.jpg", "The Big Short: the reference for the guys' shots"),
        (TA + "/assets/collage/process/opener_shotref.jpg", "The reference edit for the opener's shots"),
        ("FRAME 0.4", "[00:00:00:00 - 00:00:00:23] The establishing shot: San Francisco, pushed in, handheld, morphing into the car window"),
        (TA + "/assets/collage/process/sun_ae_picked.jpg", "THE INFLUENCE: the red sun_ae TikTok, frames 177-224: faces multiplied and echoing outwards, red and white, glitch blocks, the cyberware HUD"),
        (TA + "/assets/collage/process/opener_psycho_steps.jpg", "[00:00:10:08 - 00:00:15:00] Each man in 12 steps into the look, and his matte (cut off his background)"),
        ("NOTE", "HOW THE CYBERPSYCHO CUT WORKS\n- 12 AI-generated steps per man, camera locked, into the red sun_ae look\n- each man cut out with GrabCut (the white mattes above): the effects stay on him\n- the frame split into quadrants that swap between his steps\n- rectangles of his face from other steps over his eyes, brows, mouth (large into small)\n- his eyes echoing outwards, different sizes\n- cyberpsycho lines drawn out of his eyes (cyberpsycho.py, new on twos)\n- the two men alternating on the beat from the drop"),
        (TA + "/assets/collage/process/opener_psycho_cut.jpg", "[00:00:10:08 - 00:00:15:00] The crazy cut itself"),
        (TA + "/assets/collage/process/eye_effect.jpg", "[opener 00:00:10:08, busts 00:00:30:22, girl 00:00:38:20] THE EYE EFFECT, isolated: the reference, then every scene that uses it (the two men, the busts, the girl): the shot, its eyes found, the echoes alone, on the shot"),
    ]),
    ("1  REFERENCES", [
        ("YT urV5GzXcXsQ", "Edgerunners 2 trailer (the red lines, the music's source)"),
        ("YT QBlPg818lGI", "Edgerunners 2 Teaser #2 (the red flash, the logo reveal)"),
        ("YT mV7451mcw-E", "The ECG line and the 1:05 lighting"),
        ("YT QiCYtUZkZVw", "Cyberpunk 2077 menu UI recreation"),
        (REF + "/tt_elements/elements_sheet.jpg", "TikTok 1: every frame, numbered, to pick effects from"),
        (REF + "/tt_elements2/elements_sheet.jpg", "TikTok 2: the same"),
        (REF + "/yellow_blue_scene.jpg", "The bright yellow and blue scene (TikTok 1, 244-247)"),
        (REF + "/yt_morph/ref_silhouette.png", "Trailer: the yellow silhouette shot"),
        (REF + "/yt_line/lighting_sheet.jpg", "The 1:05 lighting: silhouette, hard flat light"),
        (REF + "/cyberpunk_edits/boards/type_moves.jpg", "How the edits move their type"),
        (REF + "/cyberpunk_edits/QBlPg818lGI/at124_tear.jpg", "Edgerunners 2 Teaser #2, 1:24: the red flash"),
        (REF + "/cyberpunk_edits/urV5GzXcXsQ/lines_1029_sheet.jpg", "Edgerunners 2 trailer, 1020-1139: the red lines"),
        (REF + "/t2_outro_sheet.jpg", "Teaser #2 outro: the 3D logo reveal"),
        (REF + "/t1_arrows_sheet.jpg", "Trailer 1: the 3D arrow signs"),
        (REF + "/zdepth_ref/big.jpg", "Cyberpunk 2077 menu UI: layers at depth"),
    ]),
    ("2  PULLED OUT WITH NUMPY", [
        ("NOTE", "HOW THE NUMPY EXTRACTION WORKS\n- every frame read with OpenCV\n- masks by colour and brightness (HSV thresholds) pull out just the effect\n- the rest made transparent, written as PNG / ProRes 4444 layers\n- lines thinned to skeletons and traced into paths\n- those shapes and paths saved as SEEDS\n- generators then draw NEW variations from the seeds along a path or out of a matte (a face, a word, the eyes)"),
        (REF + "/tt_elements/assets/fx/layers_sheet.jpg", "TikTok effects split into layers (chroma, streaks, noise, lines)"),
        (REF + "/cyberpunk_edits/boards/00_extracted_fx_layers.jpg", "Trailer effects lifted onto transparent"),
        (REF + "/yt_line/line_sheet.jpg", "The ECG line from the Edgerunners 2 trailer's first second"),
        (TA + "/assets/collage/redflash_seeded.jpg", "Red flash: the teaser frames, their numpy seeds, new flashes from them"),
        (TA + "/plugins/redlines/redlines_sheet.jpg", "Red lines: trailer frames, numpy skeletons, generated cracks and slashes"),
    ]),
    ("3  GENERATED", [
        (TA + "/assets/collage/process/transition_howto.jpg", "[00:00:11:02, and every cut 00:00:00:23 - 00:00:37:13] One transition taken apart: shot A, shot B, the blend frames between"),
        ("NOTE", "HOW THE TRANSITIONS WORK\n- shot A runs on past the cut, shot B starts early\n- double exposure: one shot's dark shapes printed into the other's highlights\n- displacement: one shot pushes the other's pixels by its brightness\n- datamosh blocks, cut-in rectangles, echo trails, 1-frame flicks, a tint\n- a pixel-sort burst right on the cut\n- built from the clean render, then placed under the CRT / VHS"),
        (TA + "/assets/collage/ending_redlines_stills.jpg", "[00:00:37:13 - 00:00:58:09] Cracks and slashes on the ending's cards"),
        (TA + "/assets/collage/lines_animated_check.jpg", "A new drawing every frame"),
        (TA + "/assets/collage/girl_inserts_sheet.jpg", "[00:00:38:20 - 00:00:57:18] The girl: eye echoes, face cut-ins, slashes round her"),
        (TA + "/assets/ui3d/elements_sheet.jpg", "The menu UI elements, rebuilt"),
        (TA + "/assets/collage/ending_transitions_stills.jpg", "[00:00:37:28 - 00:00:58:09] Clip blends and red flashes between cards"),
        (TA + "/assets/collage/opening_camera_stills.jpg", "[00:00:00:00 - 00:00:10:08] Camera moves on the opener"),
    ]),
    ("4  IN THE FILM", [
        (TA + "/assets/collage/ending_crazy_stills.jpg", "[00:00:37:13 - 00:00:58:09] Giant words, flash cuts, thermogram"),
        (TA + "/assets/collage/ending_2d_stills.jpg", "[00:00:37:13 - 00:00:58:09] The ending: colour cards, lines round the letters"),
        (TA + "/assets/collage/endcard_seq_stills.jpg", "[00:00:58:09 - 00:01:05:12] The end card: Nous, Log, side by side"),
        ("FINAL", "Frames from the final render, each with its timecode"),
    ]),
    # matt, 2026-11-17: "outline how we did all of it, like all of the image generations"
    ("5  IMAGE GENERATIONS", [
        ("NOTE", "HOW THE STILLS WERE GENERATED (images/gen/make_*.py)\n- Nano Banana Pro / Gemini 3 Pro Image, through treg or Google's API with the\n  references sent inline (about $0.15 an image)\n- chained in rounds: the first image (the cast sheet, the standing girl) is the\n  reference for every later shot, so faces and clothes stay the same\n- camera, crop and pose locked across versions, so they cut and glitch in place\n- text on screens and boards left out, added as editable layers\n- the raw generation kept beside the cleaned one (_raw.png)"),
        (G("opening", "dawn_empty", "dawn_crowd", "dawn_light", "dawn_lookup", "split_cold"), "make_opening_dawn.py: the marble hall at dawn, the crowd, the light-beings, the split"),
        (G("opening/creation"), "make_opening_creation.py: the creation of AI, sunny and golden"),
        (G("opening/cast"), "make_opening_cast.py: the GPT-3 team in the Pioneer Building loft (cast sheet first, then every shot from it)"),
        (G("opening/gpt3"), "make_opening_gpt3.py / make_opening_carwindow.py: the building, the loft, the car window"),
        (G("opening/psycho/sam") + G("opening/psycho/dario"), "make_opening_psycho_speakers.py: the real clips in 12 steps each into the red sun_ae look"),
        (G("cyberpunk", "open_a", "open_b", "open_c", "open_d", "open_e", "open_f", "open_g", "shot1", "shot2", "shot3", "eyes1", "eyes2", "eyes3", "girl"), "make_cyberpunk_opening.py / make_cyberpunk_eyes.py: the cyberpunk shots and the eye close-ups that match-cut"),
        (G("cyberpunk/variants/eyes2"), "make_cyberpunk_variants.py: the same eyes in other styles (PS2, clay, oil, Magritte, ukiyo-e)"),
        (G("cyberpunk/outro", *["portrait_%d" % i for i in range(6)]) + G("cyberpunk/outro/styles"), "make_bust_styles.py: the six busts, then each one realistic, low-poly and 1-bit dither"),
        (REPO + "/projects/cyberpunk/outro/ensemble.png", "make_caricature_ensemble.py: the caricature ensemble"),
        (G("stamp", "s0_ots", "s1_feet", "s2_stand") + G("cyberpunk/outro", "stamp_girl_yellow"), "make_stamp_shots.py / make_yellow_woman.py: the stamp girl, and her on yellow"),
        (REPO + "/projects/cyberpunk/outro/inbetween_sheet.jpg", "make_girl_inbetweens.py: in-between shots of her in the 1:05 lighting"),
    ]),
    ("6  THE EFFECTCRAFT WALKTHROUGH", [
        ("NOTE", "HOW THE 20-MINUTE WALKTHROUGH WAS EDITED (FilmCraft)\n- an hour-long screen recording of matt explaining EffectCraft\n- the voice cleaned with RE-USE on a Colab T4, in three parts\n- the transcript turned into a cut list: 20 minutes, sentences kept whole\n- every pause of 0.30 s+ cut out (179 pauses down to 66)\n- every cut a J-cut: the voice comes in 8+ frames before the picture\n- bust-shot close-ups of matt on whole talking sentences\n- the intro built in EffectCraft: CRT, dark gradient, matt cut out above it,\n  words in the empty space, 8-bit letter swaps, deep glow, a riser, a flash\n- the launch film, the actual Big Short and 23 of this board's breakdowns cut in\n  where he talks about them\n- rendered as ProRes in 4 pieces, then x264 CRF 16: 1080p60, ~9.8 Mbps; .srt beside it"),
        ("VID " + WALK + "/introEC/intro_render.mp4 1 3.5 6 9 12 15.5", "[00:00:00 - 00:00:17] The intro, built in EffectCraft"),
        ("BD", "The breakdown inserts: this board's pictures and the reference videos, full screen where he talks about them"),
        ("VID " + WALK + "/renders/effectcraftEditing-20min-v15-hq.mp4 30 120 200 315 600 750 937 1060 1180 1250", "Frames from the final 20-minute render, each with its timecode"),
    ]),
]
W_IMG, GAP, COLW = 1000, 120, 1200


def jpeg(img):
    img = img.convert("RGB"); img.thumbnail((W_IMG, W_IMG * 2))
    b = io.BytesIO(); img.save(b, "JPEG", quality=82)
    return b.getvalue(), img.size


def frame_at(t):
    vid = os.path.join(TA, "renders", "launch_film_final_full.mp4")
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", vid, "-frames:v", "1", "-vf", "scale=1000:-2",
                        "-f", "image2", "-c:v", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def final_frames():
    vid = os.path.join(TA, "renders", "launch_film_final_full.mp4")
    ims = []
    for t in (2, 10.4, 16, 26, 28, 33, 40, 47, 59, 62.5):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", vid, "-frames:v", "1", "-vf", "scale=480:-2",
                            "-f", "image2", "-c:v", "png", "-"], capture_output=True)
        if r.stdout:
            im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
            f = int(round(t * 30)); dr = __import__("PIL.ImageDraw", fromlist=["x"]).Draw(im)
            dr.rectangle((0, 0, 120, 16), fill=(0, 0, 0)); dr.text((3, 2), "%02d:%02d:%02d:%02d" % (0, f // 1800, (f // 30) % 60, f % 30), fill=(255, 220, 0))
            ims.append(im)
    s = Image.new("RGB", (2 * 480, 5 * 270))
    for i, im in enumerate(ims):
        s.paste(im, ((i % 2) * 480, (i // 2) * 270))
    return s


def tile(ims, labels, cols, w=480):
    from PIL import ImageDraw
    th = []
    for im, lb in zip(ims, labels):
        im = im.convert("RGB"); im.thumbnail((w, w * 2))
        cell = Image.new("RGB", (w, round(w * 9 / 16)), (0, 0, 0))
        im.thumbnail(cell.size); cell.paste(im, ((w - im.width) // 2, (cell.height - im.height) // 2))
        if lb:
            dr = ImageDraw.Draw(cell); dr.rectangle((0, 0, 8 + 7 * len(lb), 16), fill=(0, 0, 0)); dr.text((3, 2), lb, fill=(255, 220, 0))
        th.append(cell)
    ch = th[0].height
    s = Image.new("RGB", (cols * w, -(-len(th) // cols) * ch), (255, 255, 255))
    for i, c in enumerate(th):
        s.paste(c, ((i % cols) * w, (i // cols) * ch))
    return s


def grab(vid, t, w=480):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", vid, "-frames:v", "1", "-vf", "scale=%d:-2" % w,
                        "-f", "image2", "-c:v", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def still_sheet(paths):
    paths = [p for p in paths if os.path.exists(p)]
    cols = 6 if len(paths) > 16 else 4 if len(paths) > 6 else 3 if len(paths) > 2 else len(paths)
    return tile([Image.open(p) for p in paths], [os.path.splitext(os.path.basename(p))[0] for p in paths], cols, 960 // cols * 2)


def video_sheet(spec):
    vid, *ts = spec.split()[1:]  # "VID <path without spaces> <seconds> ..."
    ts = [float(t) for t in ts]
    return tile([grab(vid, t) for t in ts], ["%02d:%02d:%02d" % (t // 3600, t // 60 % 60, t % 60) for t in ts], 2)


def breakdown_sheet():
    ins = json.load(open(WALK + "/breakdowns/inserts.json"))
    return tile([grab(i["file"], i["d"] / 2, 320) for i in ins], ["%d:%02d" % (i["t"] // 60, i["t"] % 60) for i in ins], 3, 320)


rnd = random.Random(1)
els, files = [], {}


def eid():
    return "%016x" % rnd.getrandbits(64)


def text(x, y, s, size):
    return {"id": eid(), "type": "text", "x": x, "y": y, "width": len(s) * size * 0.55, "height": size * 1.25,
            "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": None, "seed": rnd.randint(1, 2 ** 30), "version": 1, "versionNonce": rnd.randint(1, 2 ** 30),
            "isDeleted": False, "boundElements": None, "updated": 1, "link": None, "locked": False, "text": s,
            "fontSize": size, "fontFamily": 2, "textAlign": "left", "verticalAlign": "top", "containerId": None,
            "originalText": s, "lineHeight": 1.25, "baseline": int(size)}


def image(x, y, data, size):
    fid = hashlib.sha1(data).hexdigest()
    files[fid] = {"mimeType": "image/jpeg", "id": fid, "created": 1,
                  "dataURL": "data:image/jpeg;base64," + base64.b64encode(data).decode()}
    return {"id": eid(), "type": "image", "x": x, "y": y, "width": size[0], "height": size[1], "angle": 0,
            "strokeColor": "transparent", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 1,
            "strokeStyle": "solid", "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": rnd.randint(1, 2 ** 30), "version": 1, "versionNonce": rnd.randint(1, 2 ** 30), "isDeleted": False,
            "boundElements": None, "updated": 1, "link": None, "locked": False, "status": "saved", "fileId": fid,
            "scale": [1, 1]}


def note(x, y, s):
    t = text(x, y, s, 26)
    t["width"] = 1000; t["height"] = 33 * (s.count(chr(10)) + 1)
    return t


def embed(x, y, url):
    return {"id": eid(), "type": "embeddable", "x": x, "y": y, "width": 1000, "height": 562, "angle": 0,
            "strokeColor": "#1e1e1e", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 2,
            "strokeStyle": "solid", "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": None, "seed": rnd.randint(1, 2 ** 30), "version": 1, "versionNonce": rnd.randint(1, 2 ** 30),
            "isDeleted": False, "boundElements": None, "updated": 1, "link": url, "locked": False, "validated": True}


def arrow(x0, y0, x1):
    return {"id": eid(), "type": "arrow", "x": x0, "y": y0, "width": x1 - x0, "height": 0, "angle": 0,
            "strokeColor": "#e03131", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 4,
            "strokeStyle": "solid", "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 2}, "seed": rnd.randint(1, 2 ** 30), "version": 1,
            "versionNonce": rnd.randint(1, 2 ** 30), "isDeleted": False, "boundElements": None, "updated": 1,
            "link": None, "locked": False, "points": [[0, 0], [x1 - x0, 0]], "lastCommittedPoint": None,
            "startBinding": None, "endBinding": None, "startArrowhead": None, "endArrowhead": "arrow"}


els.append(text(0, -260, "HOW IT WAS MADE: THE LOG LAUNCH FILM AND THE EFFECTCRAFT WALKTHROUGH", 72))
for ci, (title, items) in enumerate(COLS):
    x = ci * (COLW + 200)
    els.append(text(x, -120, title, 48))
    y = 0
    for path, cap in items:
        if path == "NOTE":
            n = note(x, y, cap); els.append(n); y += n["height"] + GAP
            continue
        if isinstance(path, str) and path.startswith("YT "):
            els.append(text(x, y, cap, 26)); els.append(embed(x, y + 44, YT + path[3:])); y += 44 + 562 + GAP
            continue
        if isinstance(path, list):
            img = still_sheet(path)
        elif path == "BD":
            img = breakdown_sheet()
        elif path.startswith("VID "):
            img = video_sheet(path)
        else:
            img = final_frames() if path == "FINAL" else frame_at(float(path[6:])) if path.startswith("FRAME ") else Image.open(path)
        data, size = jpeg(img)
        els.append(text(x, y, cap, 26))
        els.append(image(x, y + 44, data, size))
        y += 44 + size[1] + GAP
    if ci < len(COLS) - 1:
        els.append(arrow(x + COLW - 60, -95, x + COLW + 160))
doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com", "elements": els,
       "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": files}
out = os.path.join(TA, "PROCESS_BOARD.excalidraw")
json.dump(doc, open(out, "w"))
print(out, len(els), "elements", len(files), "images", "%.1f MB" % (os.path.getsize(out) / 1e6))
