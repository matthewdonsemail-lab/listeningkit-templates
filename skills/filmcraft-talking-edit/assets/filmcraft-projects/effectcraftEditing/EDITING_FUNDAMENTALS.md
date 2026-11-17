# How matt edits now: the fundamentals (from the EffectCraft walkthrough)

Pulled from the 67.5 min Cap recording of 2026-11-16 (`transcript.md`, AssemblyAI). Times are in the source recording.
It's the spine of the video: what he does, in the order he explains it. Every point is something he said.

## The core idea

**Then: hours on the timeline by hand. Now: you say what's in your head, with references, and Claude Code builds it in EffectCraft.**

- EffectCraft is After Effects decompiled and free: same compositions, precomps, keyframes, expressions and cameras, driven from code instead of the timeline (0:02, 0:27, 56:05).
- "I did not touch the timeline basically once" on the Log launch trailer (1:31, 18:35, 26:33, 65:13).
- His subtitle plugin (rim light, deep glow, Animation Composer, synced to the timeline) used to need After Effects. In EffectCraft it took one prompt (2:54–3:32).
- It took a day and a half, where it used to take a week. The next one will take half a day, because the process is written down in a GitHub repo (64:44–65:12).

## Why he can say it

- 13 years editing, self-taught from YouTube by taking apart videos he liked at 14 (1:04, 1:56).
- A degree in digital video production at Salford, where he learned nothing (1:48).
- He's worked as a videographer and on sets, and edited for creators (4:25, 17:17).
- 20–21K views on his competition trailers in the last few days (0:52).

## The fundamentals, in order

### 1. Use frontier models, and don't one-shot
- Use Claude Code Max, Codex or Hermes Agent on the Nous Portal. Anything weaker takes 10 times longer and wastes tokens (5:23–5:49).
- "Make me this video, make no mistakes" doesn't work. Learn the fundamentals and guide it (5:56, 57:31).

### 2. Always start from a reference
- Take your favourite media and find the shots you like (6:15–6:32).
- His references:
  - the Cyberpunk Edgerunners 2 trailers and teasers;
  - the Nathan Fielder documentary, with faces close and boxed in for unease (6:39–8:54);
  - the opening of The Big Short, with push-ins on Burry and fast cuts to the families behind the numbers (11:34–14:49).
- Automate the gathering. Claude Code downloads the trailers, finds the exact time points and pulls every frame. He picks the frames he wants (6:32, 15:16–15:32).

### 3. Pick references for the story, not the look
- The product sounds scary: an AI that becomes you on every platform. So the film borrows from scenes about a pivotal moment that hurts people (9:38–10:14).
- The setting: the Pioneer Building and the ChatGPT 3.5 API, the first commercial access. That's paired with The Big Short's "there is a problem" moment (10:18–11:45, 22:57–24:28).
- The cast: Sam Altman and Dario Amodei, set against the Hermes girl, who stands for local models and ownership (25:37–26:01).

### 4. Generate the stills, then give them a camera
- First stills come from ChatGPT images, then the rest come through Treg, because it's cheap (20:13, 49:52).
- He shot on a laptop in Vietnam with no camera, so the camera is EffectCraft's (16:23–16:40).
- Give the camera a perspective and a focal length. Ask for a "45-degree counter angle with depth of field", then cut to a closer 25-degree push-in, so the timing varies (17:31–18:23).

### 5. Rebuild the UI: screenshot to HTML to precomp
- The old GPT-3.5 Playground is gone from the internet.
- So the screenshot goes to Opus, which makes HTML; the HTML becomes a precomp in EffectCraft, in one prompt (19:04–20:04).
- The typing is just a trim path revealing the text. Then add an angle, depth of field, and a focus pull onto "Sam" (21:16–22:14).

### 6. Make people caricatures: the cyberpsycho eyes
- His reference is the sun_ae TikTok and David going cyberpsycho in Edgerunners: the eyes bulge out to show someone losing it (29:00–30:21, 37:56–38:22).
- Turn one base shot into 12 variations of the same character as a monster (39:10–39:58).
- GrabCut takes the subject off the background, onto its own layer (39:22).
- OpenCV finds the eyes and cuts them out in boxes. Three echoes of each eye step outwards with fast scale and position changes (39:58–40:33).
- Rectangles are cropped at random intervals, rotating through the 12 variations. The two men are match-cut at eye level (41:01–43:21).

### 7. References become generators, not copies
- You don't have the project file. Don't guess by eye. "That shit is over" (36:33–36:59).
- From a screenshot, NumPy pulls out the skeleton. That becomes a seed path, which becomes a generator making new variations of the same look (37:02, 46:48–47:18).
- Red lines go around the subject using the depth map, as cracks and slashes. The same paths wrap the text on the cards (47:31–49:44).

### 8. Layer it: lots of small elements
- It's not one effect. It's many small elements across the composition (46:07–46:31).
- The stack: eye effect, then CRT, then the rectangle cuts of the eyes, then the NumPy generator (50:14).
- The CRT is rebuilt from CRT Animator as an EffectCraft plugin (44:18–45:24).
- Text sits under the CRT, which gives it the emulsion look (49:05).

### 9. Transitions done with maths
- Take a reference transition apart into its RGB layers and timings (chroma streaks, noise, lines), and use it as a displacement map (52:31–53:19, 63:42–64:14).
- Shot A runs out past the cut and shot B starts early, as a double exposure. Add a pixel sort, datamosh rectangles, echo trails, one-frame flicks and a tint (54:27–54:53).
- Stack copies of things you know until they become something new (53:35–54:03).

### 10. Plugins: recreate, don't install
- After Effects plugins don't load in EffectCraft.
- Screenshot the plugin or pack and get Claude Code to recreate it: the CRT emulator, a LUT pack with an exposure ramp, Red Giant-style tools (55:04–56:18).
- An After Effects ZXP is just JSX. Get Claude Code to port it into a WASM plugin (51:23).

### 11. Taste is the job: templates aren't editing
- The "AI can edit" videos are templates baked into skills. That isn't editing (58:59–61:34).
- Every project in his 14 years has been different. The taste is where the editing shows (61:38–62:04).
- AI still can't compose a shot on its own. You make skills out of how you work (62:23–62:46).

### 12. Speak it, don't type it
- Talking is more creative. Close your eyes and say what you see, with the references beside you (62:53–63:23).

## The close
- "We're cooked as creative people, or it's the greatest upgrade we'll ever have. I'm in that camp" (65:18).
- Calls to action:
  - join the ArtCraft Discord;
  - a community is coming, so leave a comment;
  - message him for agency work;
  - ListeningKit "bends social media" for service businesses, startups and solopreneurs, run from your own harness (65:50–67:17).
