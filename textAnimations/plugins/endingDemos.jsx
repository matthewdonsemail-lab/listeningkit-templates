// The launch film's ending (matt, 2026-11-15): product demos and scenes no other film uses (the 3D ones in "Product
// Demos" and the exposition / title cards), cut to the
// recorded VO (projects/cyberpunk/audio_words.json) from the end of cyberpunk (37.43 s) to the end card. Builds the comp
// "ending" (folder "ending parts", with "ending card") and nests it in "launch film" after cyberpunk, which it makes
// longer for the card. Thermogram flashes (as cyberpunk's match cut) on the bigger switches. Rebuilt in place.
//   effectcraft-cli --project textAnimations.ecproj script plugins/endingDemos.jsx --save
// See ENDING.md.
var F=30, ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/";
var START=37.43, END=61.30;                    // launch film seconds: cyberpunk ends at 37.43; the VO at 58.30
var SHOTS=[ // comp, from, to (launch film s), where in it to start (s), the line. Only scenes no other film uses
  // (matt: not the demos Intro 1 already has, logReply/Inbox/ThreeSteps/PlayJourney)
  ["logAgentDemo",      37.43, 44.22, 0.0, "Humans can tell when you use AI. Log systematically defeats that by becoming you."],
  ["expositionStudy",   44.22, 48.40, 0.0, "There are opportunities across every conversation you've ever had."],
  ["logResearchDepth",  48.40, 52.72, 2.5, "Log helps you find them, speak with them, and win the people over."],
  ["askHermes",         52.72, 55.58, 0.8, "For whatever you do, for whatever you want."],
  ["logListeningDemo",  55.58, 58.30, 4.5, "All locally, because that's what counts."],
  ["ending card",       58.30, END,   0.0, "(end card)"]
];
var THERMAL=[37.43, 48.40, 55.58, 58.30];      // launch film seconds

function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var FOLDER=null; for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof FolderItem && it.name==="ending parts") FOLDER=it; }
if(!FOLDER) FOLDER=app.project.items.addFolder("ending parts");
function comp(name,dur){ var c=findComp(name);
  if(c){ for (var k=c.numLayers;k>=1;k--) c.layer(k).remove(); c.duration=dur; return c; }
  c=app.project.items.addComp(name,1920,1080,1,dur,F); c.parentFolder=FOLDER; return c; }

// --- the end card: LOG, then the credit line, on black
var CD=END-58.30;
var K=comp("ending card",CD);
function text(c,str,size,y,font,color){ var t=c.layers.addText(str); t.name=str;
  try{ var td=t.property("Source Text").value; td.font=font; td.fontSize=size; td.fillColor=color; td.applyFill=true; td.applyStroke=false;
       td.justification=ParagraphJustification.CENTER_JUSTIFY; t.property("Source Text").setValue(td); }catch(x){}
  t.property("Transform").property("Position").setValue([960,y]); t.startTime=0; t.inPoint=0; t.outPoint=CD; return t; }
var logo=text(K,"LOG",260,560,"Satoshi-Black",[1,1,1]);
var sc=logo.property("Transform").property("Scale");
sc.setValueAtTime(0,[60,60]); sc.setValueAtTime(8/F,[106,106]); sc.setValueAtTime(14/F,[100,100]);
var cred=text(K,"by ListeningKit \u00D7 Nous Research",54,690,"Satoshi-Medium",[0.66,0.8,1]);
var op=cred.property("Transform").property("Opacity"); op.setValueAtTime(10/F,0); op.setValueAtTime(20/F,100);

// --- the ending: the demos in order
var E=comp("ending",END-START);
for (var i=0;i<SHOTS.length;i++){ var s=SHOTS[i], src=findComp(s[0]); if(!src) throw new Error("no comp "+s[0]);
  var L=E.layers.add(src); L.name=s[0];
  var a=s[1]-START, b=s[2]-START;
  L.startTime=a-s[3]; L.inPoint=a; L.outPoint=b;
  try{ L.collapseTransformation=false; }catch(x){}
}
// thermogram flashes on top: frames -2 orange, -1 green, 0 orange, +1 picture, +2 green, +3 orange, in an exposure blow-out
var cuts=[]; for (var i=0;i<THERMAL.length;i++) cuts.push((THERMAL[i]-START).toFixed(4));
var CUTS="["+cuts.join(",")+"]";
var LOOK="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";
var X=E.layers.addSolid([0,0,0],"exposure cuts",1920,1080,1); X.adjustmentLayer=true; X.startTime=0; X.inPoint=0; X.outPoint=E.duration;
P(X.property("Effects").addProperty("ec.color.exposure"),"master/exposure").expression="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.3&&d<=0)p=(d+.3)/.3;else if(d>0&&d<.4)p=1-d/.4;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}th?0.35*env:3.6*env";
X.moveToBeginning();
var LUTS={"thermal orange":["thermograph_orange","o"],"thermal green":["thermograph_green","g"]};
for (var n in LUTS){ var T=E.layers.addSolid([0,0,0],n,1920,1080,1); T.adjustmentLayer=true; T.startTime=0; T.inPoint=0; T.outPoint=E.duration;
  P(T.property("Effects").addProperty("ec.utility.applylut"),"lut").setValue(ROOT+"textAnimations/assets/luts/"+LUTS[n][0]+".cube");
  T.property("Transform").property("Opacity").expression=LOOK+"look==='"+LUTS[n][1]+"'?100:0"; T.moveToBeginning(); }

// --- into the launch film, after cyberpunk; longer for the card
var LF=findComp("launch film"); if(!LF) throw new Error("no launch film");
var old=byName(LF,"ending"); if(old) old.remove();
LF.duration=END;
var N=LF.layers.add(E); N.name="ending"; N.startTime=START; N.inPoint=START; N.outPoint=END;
var cy=byName(LF,"cyberpunk"); if(cy) N.moveBefore(cy);
var vo=byName(LF,"vo"), mu=byName(LF,"music"); if(vo) vo.outPoint=END; if(mu) mu.outPoint=END;
writeLn("ending: "+SHOTS.length+" shots, "+START+"-"+END+" s; launch film now "+LF.duration.toFixed(2)+" s");
for (var k=1;k<=LF.numLayers;k++){ var l=LF.layer(k); writeLn("  "+k+" ["+l.name+"] "+l.inPoint.toFixed(2)+"-"+l.outPoint.toFixed(2)); }
