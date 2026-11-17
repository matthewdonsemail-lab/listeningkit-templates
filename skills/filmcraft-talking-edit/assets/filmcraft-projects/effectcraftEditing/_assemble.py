"""one-off: assemble edit_config.py from the databroker generic logic (_generic.py) and this recording's parts"""
import os
from _parts import CUT_PHRASES, DROP, FIXES, HEADER, HOOK, QUICK, KEEP_20
VARIANT = os.environ.get('VARIANT', '')
if VARIANT == '20min':
    DROP = set(range(703)) - KEEP_20

g = open("_generic.py", encoding="utf8").read()
g = g.replace("@@CUT_PHRASES@@", CUT_PHRASES)
g = g.replace("@@HOOK_PHRASES@@", HOOK.rstrip("\n"))
body = ("# ---- body: every sentence in the recording's order (sentences.txt) minus DROP: restarts, repeats, filler,\n"
        "# garbled lines and the stretches where he is clicking through the demo without talking ----\n"
        "DROP = " + repr(sorted(DROP)) + "\nBODY = [k for k in range(len(SENTS)) if k not in set(DROP)]")
g = g.replace("@@BODY@@", body)
g = g.replace("@@QUICK@@", "QUICK = " + repr(sorted(QUICK)) + "\n")
g = g.replace("@@FIXES@@\n", FIXES)
start = g.index("# ---- body: sentence indices kept")
g = g[:start] + g[g.index("# ---- body: every sentence"):] if "# ---- body: every sentence" in g[start:] else g
g = g.replace('the hype, the one person paid, the jokes, the credits, the cost, the commissions; ends on "Yummy, yummy." and\n'
              '# hands over to the start of the recording.',
              "no timeline, one prompt, can't tell it's AI, guessing is over, never pay for plugins, it's templates; ends\n"
              "# on \"the greatest upgrade we'll ever have\" and hands over to the body.")
g = g.replace("@@", "").replace("TAG = \"-v1\"", ("TAG = \"" + os.environ.get("TAG", "-20min") + "\"") if VARIANT == "20min" else "TAG = \"-v2\"")
open("edit_config.py", "w", encoding="utf8").write(HEADER + g)
print("wrote edit_config.py")
