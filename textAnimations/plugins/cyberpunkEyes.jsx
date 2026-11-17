// cyberpunk: a pre-comp of the three overhead shots (projects/cyberpunk/shot1-3.png) and their close-ups, nested at
// the end of Intro 1.
// 0-1.2 s: the three overheads as glitch cut-ups around the character, hard match-cut on the same composition, one
// exponential push into the face across them.
// 1.2 s: the one thermogram transition (orange/green LUT frames + exposure blow-out, as thermalCuts.jsx).
// 1.2-4.4 s: the close-ups as one glitch video, aligned on the eyes: the brain's core, then the girl in photo, anime and
// five Intro 1 styles, glitch-cut into each other, with the exponential push on the big cuts. No sigils.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/";
function img(n){ var p=ROOT+"projects/cyberpunk/"+n+".png"; return findFile(p)||app.project.importFile(new ImportOptions(new File(p))); }

// timed to matt's VO (assets/make_cyberpunk_flow.py, make_cyberpunk_closeups.py): the glitch push from frame 247, the
// thermogram on "now", the close-ups to "introducing", the outro (cyberpunk outro, VO-timed) after
var OPEN_END=247/30, PUSH_END=265/30, CLOSE_END=PUSH_END+183/30, OUTRO=findComp("cyberpunk outro").duration, DUR=CLOSE_END+OUTRO;
var old=findComp("cyberpunk"); if(old) old.remove();
var C=app.project.items.addComp("cyberpunk",1920,1080,1,DUR,30);
C.motionBlur=true;

// the opening: the realistic overhead as one locked-off shot she walks into (projects/cyberpunk/open_a/b/c.png, made
// by images/gen/make_cyberpunk_opening.py): her spot empty, then her standing there, then the crowd moved on around
// her, hard cuts 0.4 s apart under a slow zoom; then the glitch cut-up around her (assets/collage/
// cyberpunk_overhead_glitch.mp4, made by assets/make_cyberpunk_collage.py) while the push ramps exponentially into
// the thermogram match cut onto her face. [file, in, out]; all 1920x1080, her face at (960,427).
// generated clips are re-read from disk on every build (replace), so a regenerated clip comes in at its new length
function fresh(p){ var it=findFile(p); if(it){ it.replace(new File(p)); return it; } return app.project.importFile(new ImportOptions(new File(p))); }
function cut(n){ return fresh(ROOT+"textAnimations/assets/collage/cyberpunk_"+n+".mp4"); }
// the whole opening is one video now (assets/collage/cyberpunk_opening_flow.mp4, made by
// assets/make_cyberpunk_flow.py): her on her own layer, sharp, over the crowd cycling every frame through the photo,
// anime and light-being moments with a slow-shutter drag, zoom streaks, the light bending around her and noise; then
// the glitch slices around her and a clean tail into the thermogram
// the blue cyberpsycho lines (plugins/cyberpsycho) as their own layer above the flow, with the same push, so they stay
// locked to her; applyCyberpunk.jsx lifts this layer above the CRT so it stays clean blue
function mov(n){ return fresh(ROOT+"textAnimations/assets/collage/cyberpunk_"+n+".mov"); }
var OVER=[[cut("opening_flow"),"opening flow",0.0,PUSH_END],[mov("lines"),"cyberpsycho lines",0.0,PUSH_END]];
for (var i=0;i<OVER.length;i++){
  var o=[OVER[i][1],OVER[i][2],OVER[i][3],960,427], src=OVER[i][0];
  var L=C.layers.add(src); L.name=o[0];
  L.startTime=o[1]; L.inPoint=o[1]; L.outPoint=o[2]; L.motionBlur=true;
  var tr=L.property("Transform");
  tr.property("Anchor Point").setValue([o[3],o[4]]);
  var cover=Math.max(1920/src.width,1080/src.height)*100;
  // one zoom across the whole opening: a slow 15% creep while she walks in, then from the glitch on an exponential
  // push to 4x, slow then rushing, into the thermogram
  tr.property("Scale").expression=
    "var t=time,z;if(t<"+OPEN_END+")z=1+0.15*t/"+OPEN_END+";"+
    "else{var q=Math.min(1,(t-"+OPEN_END+")/"+(PUSH_END-OPEN_END).toFixed(2)+");z=1.15*Math.pow(4/1.15,q*q);}"+
    "var k="+cover.toFixed(4)+"*z;[k,k]";
  // the face slides to frame centre as the push grows; the edges always covered
  tr.property("Position").expression=
    "var k=scale[0]/100,c="+(cover/100).toFixed(5)+",u=Math.min(1,(k-c)/(c*1.5));"+
    "var x0=960+("+o[3]+"-width/2)*c,y0=540+("+o[4]+"-height/2)*c;"+
    "var x=x0+(960-x0)*u,y=y0+(540-y0)*u;"+
    "x=Math.min("+o[3]+"*k,Math.max(1920-(width-"+o[3]+")*k,x));y=Math.min("+o[4]+"*k,Math.max(1080-(height-"+o[4]+")*k,y));[x,y]";
}

// close-ups: one collage video (assets/collage/cyberpunk_closeups.mp4, made by assets/make_cyberpunk_closeups.py),
// every variation aligned on the point between her eyes at frame centre; its face cuts every 4 frames and the
// collage of strips and features builds on top. The only movement is one slow push in over the whole of it: nothing
// scales, moves or transitions on its cuts.
var CL=C.layers.add(cut("closeups")); CL.name="closeups";
CL.startTime=PUSH_END; CL.inPoint=PUSH_END; CL.outPoint=CLOSE_END;
CL.property("Transform").property("Scale").expression="var k=100+12*(time-inPoint)/(outPoint-inPoint);[k,k]";

// thin cyberpsycho lines in depth over her face (assets/make_cyberpunk_closeup_lines.py), kept clear of the face:
// each depth pushes at its own rate (far slowest, near fastest) so the camera moving in on her gives them parallax;
// applyCyberpunk.jsx lifts them above the CRT
var DEPTH=[["far",4],["mid",14],["near",38]];
for (var i=0;i<DEPTH.length;i++){
  var DL=C.layers.add(mov("lines_"+DEPTH[i][0])); DL.name="closeup lines "+DEPTH[i][0];
  DL.startTime=PUSH_END; DL.inPoint=PUSH_END; DL.outPoint=CLOSE_END;
  DL.property("Transform").property("Scale").expression="var k=100+"+DEPTH[i][1]+"*(time-inPoint)/(outPoint-inPoint);[k,k]";
}

// halfway through the close-ups, the Hermes Agent 8-bit wordmark in grayscale (projects/cyberpunk/hermes_logo_gray.png,
// from Wikimedia's Hermes_Agent_logo.webp) cuts in, pinned to the middle of the frame, still, over the collage
var LG=C.layers.add(img("hermes_logo_gray")); LG.name="hermes logo";
var LOGO_IN=PUSH_END+(CLOSE_END-PUSH_END)/2;
LG.startTime=LOGO_IN; LG.inPoint=LOGO_IN; LG.outPoint=CLOSE_END;
LG.property("Transform").property("Position").setValue([960,540]);
var lw=1150/LG.source.width*100; LG.property("Transform").property("Scale").setValue([lw,lw]);

// the outro: the "cyberpunk outro" pre-comp, built from layers by cyberpunkOutro.jsx (generated by
// assets/make_cyberpunk_outro_comp.py; run it first): flash, the Nous logo, the push and the back of her as one
// pre-comp per step with the cut-up pieces as masked stills, the busts reveal and the portraits. The CRT goes over it.
var OUC=findComp("cyberpunk outro");
if(!OUC) throw new Error("no 'cyberpunk outro' comp: run plugins/cyberpunkOutro.jsx first");
var OU=C.layers.add(OUC); OU.name="outro";
OU.startTime=CLOSE_END; OU.inPoint=CLOSE_END; OU.outPoint=DUR;

// the thermogram transition, once: the zoom from the overheads into the close-ups. Frames -2 orange, -1 green,
// 0 orange, +1 picture, +2 green, +3 orange, inside an exposure blow-out (as thermalCuts.jsx in Intro 1)
var CUTS="["+PUSH_END.toFixed(2)+"]";
var LOOK="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";
var X=C.layers.addSolid([0,0,0],"exposure cuts",1920,1080,1); X.adjustmentLayer=true; X.inPoint=0; X.outPoint=DUR;
var ex=X.property("Effects").addProperty("ec.color.exposure");
P(ex,"master/exposure").expression="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.3&&d<=0)p=(d+.3)/.3;else if(d>0&&d<.4)p=1-d/.4;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}th?0.35*env:3.6*env";
var LUTS={"thermal orange":["thermograph_orange","o"],"thermal green":["thermograph_green","g"]};
for (var n in LUTS){
  var T=C.layers.addSolid([0,0,0],n,1920,1080,1); T.adjustmentLayer=true; T.inPoint=0; T.outPoint=DUR;
  var lut=T.property("Effects").addProperty("ec.utility.applylut");
  P(lut,"lut").setValue(ROOT+"textAnimations/assets/luts/"+LUTS[n][0]+".cube");
  T.property("Transform").property("Opacity").expression=LOOK+"look==='"+LUTS[n][1]+"'?100:0";
}

// nested at the end of Intro 1, on top of its stack
var I=findComp("Intro 1");
var END_OF_INTRO=62.13; // Intro 1's own length before the cyberpunk shot was added after it
var was=byName(I,"cyberpunk"); if(was) was.remove();
var end=END_OF_INTRO;
I.duration=end+DUR;
var N=I.layers.add(C); N.name="cyberpunk"; N.startTime=end; N.inPoint=end; N.outPoint=end+DUR;
N.moveToBeginning();
writeLn("cyberpunk "+C.numLayers+" layers, "+DUR+" s; in Intro 1 at "+end.toFixed(2)+"-"+(end+DUR).toFixed(2));
