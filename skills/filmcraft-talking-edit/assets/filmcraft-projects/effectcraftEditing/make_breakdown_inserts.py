"""The launch film's breakdowns as full-screen inserts for the walkthrough (matt, 2026-11-17: "we have other reference
material that we can show, like the actual breakdowns of what I was doing ... right now we're just cutting into them"):
the process board's pictures (textAnimations/PROCESS_BOARD.excalidraw, make_process_board.py / make_process_sheets.py)
and the reference videos they came from, each cut to where he talks about it in the 20-minute edit.
Every insert is 1920x1080, 60 fps, picture only, on black: pictures that fit are fitted, wide strips pan left to right
at a readable height, tall sheets pan top to bottom. Writes breakdowns/bd_NN.mp4 and breakdowns/inserts.json
(edit time, length, file, what he says) for build_v14.py.
  python make_breakdown_inserts.py"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:/Users/0/.buzz/REPOS/listeningkit-templates"
T, R = REPO + "/textAnimations", REPO + "/projects/opening/ref"
OUT = os.path.join(HERE, "breakdowns")
os.makedirs(OUT, exist_ok=True)
# (edit time s, length s, source, mode, mode arg, what he's saying)
#   fit; panx: strip height in px; pany: (start, end) fraction of the sheet's height; video: source in-point s
INSERTS = [
    (183.0, 4.0, R + "/shotref.mp4", "video", 30.0, "I love watching reference material"),
    (190.0, 3.8, T + "/assets/collage/process/opener_bigshort.jpg", "fit", None, "take my favourite media and find the shots I like"),
    (194.5, 3.5, T + "/assets/collage/process/opener_shotref.jpg", "fit", None, "with Claude Code you can automate the fuck out of this"),
    (283.0, 4.5, T + "/assets/collage/opening_camera_stills.jpg", "fit", None, "pass through the reference image, a counted 45-degree angle"),
    (486.0, 5.0, T + "/plugins/redlines/redlines_sheet.jpg", "fit", None, "NumPy pulls out the skeleton, a seed of this path"),
    (512.0, 6.0, T + "/assets/collage/process/eye_effect.jpg", "pany", (0.0, 0.45), "this is just done with Python ... the effect around the eyes"),
    (563.0, 5.0, T + "/assets/collage/process/opener_psycho_steps.jpg", "panx", 640, "12 variation shots, the subject off the background"),
    (585.0, 5.0, T + "/assets/collage/process/eye_effect.jpg", "pany", (0.5, 1.0), "OpenCV plots out where the eyes are ... 3 echoes"),
    (618.0, 5.0, T + "/assets/collage/process/opener_psycho_cut.jpg", "fit", None, "rectangles cropped in random intervals from 12 variations"),
    (647.0, 4.0, R + "/sun_ae/tiktok_7658403141708172558.mp4", "video", 5.5, "this TikTok, the sun_ae one"),
    (652.0, 3.5, T + "/assets/collage/process/sun_ae_picked.jpg", "fit", None, "multiple faces, red and white glitch box, the cyberware HUD"),
    (794.0, 3.5, R + "/cyberpunk_edits/urV5GzXcXsQ/video.mp4", "video", 43.5, "this is from Cyberpunk itself"),
    (798.0, 4.5, R + "/cyberpunk_edits/urV5GzXcXsQ/lines_1029_sheet.jpg", "pany", (0.0, 1.0), "turn it into a map ... a seed ... a generator"),
    (826.5, 4.5, R + "/yt_line/line_sheet.jpg", "fit", None, "the trailer ... a small white line, this is the skeleton"),
    (836.0, 5.0, T + "/assets/collage/ending_redlines_stills.jpg", "panx", 700, "create these cracks ... slashes around the subject"),
    (866.0, 5.0, T + "/assets/collage/girl_inserts_sheet.jpg", "fit", None, "going around it, the area of the object to create a line"),
    (947.0, 5.0, R + "/tt_elements/tiktok_7705499377023995169.mp4", "video", 0.0, "throughout the TikTok videos, they achieve these effects"),
    (958.0, 5.0, R + "/tt_elements/assets/fx/layers_sheet.jpg", "fit", None, "break a transition down into each RGB layer"),
    (999.0, 4.0, R + "/cyberpunk_edits/boards/00_extracted_fx_layers.jpg", "fit", None, "take these different effects, NumPy, isolated paths"),
    (1005.0, 6.5, T + "/assets/collage/process/transition_howto.jpg", "panx", 560, "shot A runs past the cut, shot B starts early"),
    (1231.0, 4.0, R + "/tt_elements/elements_sheet.jpg", "pany", (0.0, 1.0), "these are obviously the TikTok frames"),
    (1237.0, 4.5, R + "/tt_elements/assets/fx/layers_sheet.jpg", "fit", None, "the chroma streaks, the noise, the lines"),
    (1249.0, 3.0, T + "/assets/collage/ending_transitions_stills.jpg", "fit", None, "really interesting transitions like these"),
]
FIT = "scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black"
ENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-r", "60", "-an"]
meta = []
for i, (t, d, src, mode, arg, said) in enumerate(INSERTS):
    out = os.path.join(OUT, "bd_%02d.mp4" % i)
    if mode == "video":
        inp = ["-ss", str(arg), "-t", str(d), "-i", src]
        vf = FIT + ",fps=60"
    else:
        inp = ["-loop", "1", "-framerate", "60", "-t", str(d), "-i", src]
        if mode == "fit":
            vf = FIT
        elif mode == "panx":
            vf = ("scale=-2:%d:flags=lanczos,crop=1920:%d:'(iw-1920)*t/%s':0,"
                  "pad=1920:1080:0:(oh-ih)/2:black" % (arg, arg, d))
        else:
            a, b = arg
            vf = "scale=1920:-2:flags=lanczos,crop=1920:1080:0:'(ih-1080)*(%s+%s*t/%s)'" % (a, b - a, d)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-vf", vf, "-frames:v", str(round(d * 60)), *ENC, out], check=True)
    meta.append({"t": t, "d": d, "file": out.replace("\\", "/"), "src": src, "said": said})
    print("%7.1f  %4.1fs  %s" % (t, d, os.path.basename(src)))
json.dump(meta, open(os.path.join(OUT, "inserts.json"), "w"), indent=1)
print(len(meta), "inserts in", OUT)
