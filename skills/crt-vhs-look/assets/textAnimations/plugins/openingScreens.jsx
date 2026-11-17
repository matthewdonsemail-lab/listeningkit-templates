// The opening's computer screens, built in EffectCraft instead of generated (matt, 2026-11-15), in the Big Short's
// macro-on-a-monitor look: each one a flat UI pre-comp of live text and shapes ("screen ui ..."), with the RGB subpixel
// grid (assets/opening/pixelgrid.png) over it, then tilted in 3D under a camera with depth of field ("screen 3D ...")
// so only the message is sharp. Each 3D comp goes into its shot pre-comp in place of the generated still (the still is
// switched off, not deleted). Also lets the colour through the opening's VHS look, so the Big Short LUT reads blue.
// Rebuilt in place; rerun after changing the text.
var F=30, ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/";
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
function foot(rel){ var p=ROOT+rel; var it=findFile(p); if(it){ it.replace(new File(p)); return it; } return app.project.importFile(new ImportOptions(new File(p))); }
var FOLDER=null; for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof FolderItem && it.name==="opening screens") FOLDER=it; }
if(!FOLDER) FOLDER=app.project.items.addFolder("opening screens");
// the flat screens are bigger than the frame (SW x SH), the 1920x1080 layout sat in the middle (offset OX, OY), so the
// tilted screen always fills the frame (matt: no black bars at the top and bottom)
var SW=3840, SH=2700, OX=960, OY=810;
function comp(name,dur,big){ var c=findComp(name);
  if(c && big && (c.width!==SW||c.height!==SH)){ c.remove(); c=null; }
  if(c){ for (var k=c.numLayers;k>=1;k--) c.layer(k).remove(); c.duration=dur; return c; }
  c=app.project.items.addComp(name,big?SW:1920,big?SH:1080,1,dur,F); c.parentFolder=FOLDER; return c; }
function T(L,n){ return L.property("Transform").property(n); }
function rect(c,name,x,y,w,h,fill,stroke,r){ var L=c.layers.addShape(); L.name=name;
  var g=L.property("Contents").addProperty("ADBE Vector Group"), C=g.property("Contents");
  var rc=C.addProperty("ADBE Vector Shape - Rect"); rc.property("Size").setValue([w,h]); try{ rc.property("Roundness").setValue(r||0); }catch(e){}
  if(fill){ var f=C.addProperty("ADBE Vector Graphic - Fill"); f.property("Color").setValue(fill); }
  if(stroke){ var s=C.addProperty("ADBE Vector Graphic - Stroke"); s.property("Color").setValue(stroke); s.property("Stroke Width").setValue(3); }
  T(L,"Position").setValue([x+OX,y+OY]); return L; }
function page(c,col){ var L=rect(c,"page",SW/2-OX,SH/2-OY,SW,SH,col); return L; }
// a text line; typed on from 'from' seconds at 'cps' characters a second when given
function text(c,name,str,x,y,size,col,from,cps,weight){ var L=c.layers.addText(str); L.name=name;
  var st=L.property("Source Text"), td=st.value; td.fontSize=size; td.fillColor=col; td.applyFill=true; td.applyStroke=false;
  try{ td.font=weight||"Inter"; }catch(e){} td.justification=ParagraphJustification.LEFT_JUSTIFY; st.setValue(td);
  T(L,"Position").setValue([x+OX,y+OY]);
  // typed on: a hard left-to-right wipe across the line, char by char in time (EffectCraft ignores source text expressions)
  if(from!==undefined && cps){ var w=L.property("Effects").addProperty("ec.transition.linearwipe"); w.name="typing";
    w.property("Wipe Angle").setValue(270); w.property("Feather").setValue(0);
    var tc=w.property("Transition Completion"), n=str.length, d=n/cps;
    tc.setValueAtTime(Math.max(0,from-0.01),100);
    for (var q=1;q<=n;q++) tc.setValueAtTime(from+q/cps,100-100*q/n); }
  return L; }
function cursor(c,x,y,h,from){ var L=rect(c,"cursor",x,y,4,h,[0.12,0.16,0.2]);
  T(L,"Opacity").expression='Math.floor(time*2.5)%2?0:100'; return L; }
function grid(c){ var L=c.layers.add(foot("assets/opening/pixelgrid.png")); L.name="subpixel grid"; L.blendingMode=BlendingMode.MULTIPLY; T(L,"Opacity").setValue(70);
  T(L,"Position").setValue([SW/2,SH/2]); T(L,"Scale").setValue([SW/19.2,SH/10.8]); return L; }
var INK=[0.12,0.16,0.2], SOFT=[0.55,0.6,0.66], LINE=[0.79,0.83,0.87], PAGE=[0.96,0.97,0.98], GREEN=[0.84,0.94,0.86];

// --- the flat UIs
// the chat: one screen for both shots. The question types into the input box and sends at SPLIT seconds (the cut
// between the two shots); then it sits as a sent bubble and the reply types in under it
function uiChat(dur,split){ var c=comp("screen ui chat",dur,true); c.bgColor=PAGE; page(c,PAGE);
  var sent=rect(c,"sent bubble",1150,330,1060,130,[0.9,0.93,0.97],null,22); T(sent,"Opacity").expression='time<'+split+'?0:100';
  var st=text(c,"sent","my names sam whats your name?",660,352,64,INK); T(st,"Opacity").expression='time<'+split+'?0:100';
  var rb=rect(c,"reply bubble",900,560,1220,170,GREEN,null,22); T(rb,"Opacity").expression='time<'+(split+0.05)+'?0:100';
  text(c,"reply","My name is ChatGPT.",340,590,88,INK,split+0.08,36);
  rect(c,"input box",960,850,1560,190,[1,1,1],LINE,18);
  var q=text(c,"question","my names sam whats your name?",240,872,68,INK,0.08,36); T(q,"Opacity").expression='time<'+split+'?100:0';
  var cu=cursor(c,0,850,74); T(cu,"Position").expression='var t=thisComp.layer("question");var r=t.sourceRectAtTime(time);[t.position[0]+r.left+r.width+10,850+'+OY+']';
  T(cu,"Opacity").expression='time>='+split+'?0:(Math.floor(time*2.5)%2?0:100)';
  rect(c,"send",1610,970,170,60,[0.06,0.64,0.5],null,10);
  grid(c); return c; }
function uiTrust(dur){ var c=comp("screen ui trust",dur,true); c.bgColor=PAGE; page(c,PAGE);
  rect(c,"input box",960,380,1500,180,[1,1,1],LINE,18);
  text(c,"question","Can I trust you?",300,410,96,INK,0.05,22);
  text(c,"ai label","AI:",300,620,54,SOFT);
  rect(c,"answer bubble",560,780,560,170,GREEN,null,22);
  // "Maybe." comes back after the question is typed (0.78 s) and sent (the mouse-click insert)
  var a=text(c,"answer","Maybe.",360,810,100,INK); T(a,"Opacity").expression='time<0.95?0:100';
  T(c.layer("answer bubble"),"Opacity").expression='time<0.95?0:100';
  grid(c); return c; }
function uiPlayground(dur){ var c=comp("screen ui playground",dur,true); c.bgColor=[1,1,1]; page(c,[1,1,1]);
  rect(c,"sidebar",110,540,220,1080,[0.95,0.96,0.97]);
  text(c,"title","Playground",300,120,46,INK,undefined,undefined,"Inter");
  rect(c,"header line",1070,170,1700,2,LINE);
  rect(c,"prompt area",900,560,1180,700,[1,1,1],LINE,10);
  text(c,"prompt","Write a tagline for an ice cream shop.",340,290,40,INK,0.05,30);
  text(c,"completion","",340,350,40,[0.06,0.5,0.4]);
  var labels=[["Model",250],["davinci",300],["Temperature",400],["0.7",400],["Maximum length",500],["64",500],["Top P",600],["1",600]];
  for (var i=0;i<labels.length;i++){ var right=(i%2===1); text(c,"setting "+i,labels[i][0],right?1830:1560,labels[i][1],30,right?INK:SOFT); }
  for (var j=0;j<3;j++) rect(c,"slider "+j,1700,430+j*100,280,4,LINE);
  rect(c,"submit",400,960,150,54,[0.06,0.64,0.5],null,8);
  text(c,"submit text","Submit",352,970,26,[1,1,1]);
  grid(c); return c; }

// --- each flat UI tilted in 3D under a camera, focus on the message, a slow push like a macro on a monitor
function screen3D(name,ui,rotY,rotX,focus,scale,dur,offset){ var c=comp("screen 3D "+name,dur); c.bgColor=[0,0,0];
  var L=c.layers.add(ui); L.name=ui.name; L.threeDLayer=true; L.startTime=-(offset||0); L.inPoint=0; L.outPoint=dur;
  T(L,"Anchor Point").setValue([focus[0]+OX,focus[1]+OY,0]); // the message sits at the frame centre, in focus
  T(L,"Position").setValue([960,540,0]);
  T(L,"Scale").setValue([scale,scale,scale]);
  try{ T(L,"Y Rotation").setValue(rotY); T(L,"X Rotation").setValue(rotX); }catch(e){ try{ T(L,"Orientation").setValue([rotX,rotY,0]); }catch(e2){} }
  var cam=c.layers.addCamera("camera",[960,540]);
  var co=cam.property("Camera Options");
  co.property("Zoom").setValue(1600);
  co.property("Depth of Field").setValue(1);
  co.property("Focus Distance").setValue(1600);
  co.property("Aperture").setValue(130);
  co.property("Blur Level").setValue(100);
  var cp=T(cam,"Position"); cp.setValueAtTime(0,[960,540,-1600]); cp.setValueAtTime(c.duration,[960,540,-1480]);
  co.property("Focus Distance").setValueAtTime(0,1600); co.property("Focus Distance").setValueAtTime(c.duration,1480);
  return c; }

// --- into the shots, in place of the generated stills. The two chat shots are two camera angles on one screen: the
// first on the input box as the question types, the second on the reply, the screen's time running on across the cut
// [shot comp, screen name, Y rotation, X rotation, the point held in focus at frame centre, scale %]
var C4=findComp("opening 04 Pixelated Chat Input Close-Up (1)"), C5=findComp("opening 05 gpt32");
var chat=uiChat(C4.duration+C5.duration, C4.duration);
var SHOTS=[["opening 03 gpt3",uiPlayground(findComp("opening 03 gpt3").duration),"playground",-18,8,[900,420],72,0],
           ["opening 04 Pixelated Chat Input Close-Up (1)",chat,"chat, the question",-22,7,[760,850],78,0],
           ["opening 05 gpt32",chat,"chat, the reply",16,-5,[900,500],80,C4.duration],
           ["opening 09 Can I Trust You_ Maybe",uiTrust(findComp("opening 09 Can I Trust You_ Maybe").duration),"trust",-20,7,[760,600],74,0]];
// the two separate screens the chat replaces
var OLD=["screen ui prompt","screen ui reply","screen 3D prompt","screen 3D reply"];
var done=[];
for (var i=0;i<SHOTS.length;i++){ var sh=SHOTS[i], sc=findComp(sh[0]);
  var s3=screen3D(sh[2],sh[1],sh[3],sh[4],sh[5],sh[6],sc.duration,sh[7]);
  for (var k=sc.numLayers;k>=1;k--){ var L=sc.layer(k); if(L.source===s3 || (L.source && L.source.name && L.source.name.indexOf("screen 3D")===0)) L.remove(); else L.enabled=false; }
  var N=sc.layers.add(s3); N.name=s3.name; N.startTime=0; N.inPoint=0; N.outPoint=sc.duration;
  done.push(sh[0]+" <- "+s3.name); }
for (var o=0;o<OLD.length;o++){ var oc=findComp(OLD[o]); if(oc){ oc.remove(); done.push("removed "+OLD[o]); } }

// --- the VHS look keeps colour, so the shots' Big Short LUT (and the sunny one) come through
var op=findComp("opening"), vhs=null; for (var k=1;k<=op.numLayers;k++) if(op.layer(k).name==="VHS look") vhs=op.layer(k);
if(vhs){ var E=vhs.property("Effects");
  for (var j=1;j<=E.numProperties;j++){ var e=E.property(j);
    if(e.name==="Tint") e.property("Amount to Tint").setValue(0);
    if(e.name==="Hue/Saturation") e.property("Master Saturation").setValue(-4); } done.push("VHS look: tint 0, saturation -4"); }
writeLn(done.join("\n"));
