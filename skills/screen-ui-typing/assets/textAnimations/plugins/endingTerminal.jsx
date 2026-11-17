// The launch film's ending (matt, 2026-11-15): a new native 3D composition built on the Hermes Agent terminal
// (hermesAgentTerminal, Agent Windows). Four copies of the terminal, each saying one line of the VO, stand as 3D
// cards on the research scene's dark circuit background; the camera flies card to card on the VO. The prompt types
// out on each card, then the terminal's own rows pop in (its reveal expressions, shifted to after the typing).
// "find them, speak with them, win the people over" cuts to logResearchDepth, then back to the cards; then the end card.
// Builds (folder "ending parts"): "ending card", "ending terminal 1-4", "ending"; nests "ending" in "launch film"
// from the end of cyberpunk (37.43 s) and makes the film longer for the card. Rebuilt in place. See ENDING.md.
//   effectcraft-cli --project textAnimations.ecproj script plugins/endingTerminal.jsx --save
var F=30, ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/";
var START=37.43, END=61.30, DUR=END-START;
function L0(t){ return t-START; }            // launch film seconds -> this comp's

// the four cards: when (launch film s), where in the world, and what the terminal says
var CARDS=[
  {from:37.43, to:44.22, pos:[960,540,0], tilt:6, type:1.3, text:{
    "Workspace":"log / voice",
    "Prompt":"\u203A Reply to my DMs. Make it sound like me,\r  not like AI.",
    "Tool":"\u25CF log \u00B7 clone_voice",
    "Tool arguments":"your messages \u00B7 your phrasing \u00B7 your timing",
    "Tool result":"\u2713 Writing as you",
    "Next tool":"log \u00B7 twitterDms \u00B7 draft 6 replies",
    "Reply":"6 replies ready. Nobody can tell."}},
  {from:44.22, to:48.40, pos:[3300,280,-1700], tilt:-6, type:1.0, text:{
    "Workspace":"log / conversations",
    "Prompt":"\u203A Who in my conversations is worth\r  following up with?",
    "Tool":"\u25CF log \u00B7 index_conversations",
    "Tool arguments":"X \u00B7 Discord \u00B7 Slack \u00B7 Instagram \u00B7 LinkedIn",
    "Tool result":"\u2713 Every conversation you've ever had",
    "Next tool":"SubQ \u00B7 rank by who's ready",
    "Reply":"38 opportunities waiting on you."}},
  {from:52.72, to:55.58, pos:[700,820,-3500], tilt:6, type:0.8, text:{
    "Workspace":"log / plays",
    "Prompt":"\u203A Find customers. Hire a designer.\r  Book me on podcasts.",
    "Tool":"\u25CF log \u00B7 run_play",
    "Tool arguments":"customers \u00B7 hires \u00B7 investors \u00B7 podcasts",
    "Tool result":"\u2713 Running on every platform",
    "Next tool":"log \u00B7 reply in your voice",
    "Reply":"Whatever you want, done your way."}},
  {from:55.58, to:58.30, pos:[3100,520,-5300], tilt:-6, type:0.7, text:{
    "Workspace":"log / this machine",
    "Prompt":"\u203A Where does my data go?",
    "Tool":"\u25CF log \u00B7 local",
    "Tool arguments":"your laptop \u00B7 no cloud \u00B7 no upload",
    "Tool result":"\u2713 Everything stays on this machine",
    "Next tool":"Hermes Agent \u00B7 running locally",
    "Reply":"All local. That's what counts."}}
];
var RESEARCH={from:48.40, to:52.72, at:2.5};   // logResearchDepth, from its 2.5 s
var CARD_AT=58.30;                              // the end card
var THERMAL=[37.43, 48.40, 52.72, 58.30];       // thermogram flashes (launch film s)
var ZOOM=2058.7, DIST=1950;                     // the camera (as logResearchDepth's), its distance to a card

function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFoot(name){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.name===name) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var FOLDER=null; for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof FolderItem && it.name==="ending parts") FOLDER=it; }
if(!FOLDER) FOLDER=app.project.items.addFolder("ending parts");
function comp(name,dur){ var c=findComp(name);
  if(c){ for (var k=c.numLayers;k>=1;k--) c.layer(k).remove(); c.duration=dur; return c; }
  c=app.project.items.addComp(name,1920,1080,1,dur,F); c.parentFolder=FOLDER; return c; }
function T(L,n){ return L.property("Transform").property(n); }

// --- the four terminal cards: copies of hermesAgentTerminal with new words, the prompt typed, the rows after it
var SRC=findComp("hermesAgentTerminal"); if(!SRC) throw new Error("no hermesAgentTerminal");
var cards=[];
for (var i=0;i<CARDS.length;i++){ var cd=CARDS[i], name="ending terminal "+(i+1);
  var old=findComp(name); if(old) old.remove();
  var C=SRC.duplicate(); C.name=name; C.parentFolder=FOLDER;
  var off=cd.type+0.15;
  for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k), tr=L.property("Transform"), ps=["Position","Opacity","Anchor Point","Scale"];
    for (var j=0;j<ps.length;j++){ var p=tr.property(ps[j]); if(p && p.expression) p.expression=p.expression.replace(/\btime\b/g,"(time-"+off.toFixed(2)+")"); } }
  for (var ln in cd.text){ var L=byName(C,ln); if(!L) continue; var st=L.property("Source Text"), v=st.value;
    if(ln==="Prompt"){ var full=cd.text[ln], n=Math.ceil(cd.type*F/3);
      for (var s=0;s<=n;s++){ var d=st.value; d.text=full.substring(0,Math.round(full.length*s/n)); st.setValueAtTime(s*3/F,d); } }
    else { v.text=cd.text[ln]; st.setValue(v); } }
  cards.push(C); }

// --- the end card: LOG, then the credit line, on black
var CD=END-CARD_AT, K=comp("ending card",CD);
var KB=K.layers.addSolid([0,0,0],"black",1920,1080,1); KB.startTime=0; KB.inPoint=0; KB.outPoint=CD;
function text(c,str,size,y,font,color){ var t=c.layers.addText(str); t.name=str;
  try{ var td=t.property("Source Text").value; td.font=font; td.fontSize=size; td.fillColor=color; td.applyFill=true; td.applyStroke=false;
       td.justification=ParagraphJustification.CENTER_JUSTIFY; t.property("Source Text").setValue(td); }catch(x){}
  T(t,"Position").setValue([960,y]); t.startTime=0; t.inPoint=0; t.outPoint=CD; return t; }
// the Nous logo and the Log mark side by side, as Intro 1's end card (plugins/endCard.jsx): each pops in past full size
// and settles (Log a beat after Nous), and both push in slowly together
var ECDIR=ROOT+"textAnimations/assets/endcard/";
function endLogo(name,file,tin,h,x){
  var src=null; for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===(ECDIR+file).toLowerCase()) src=it; }
  if(!src) src=app.project.importFile(new ImportOptions(new File(ECDIR+file)));
  var L=K.layers.add(src); L.name=name; L.startTime=0; L.inPoint=tin; L.outPoint=CD;
  var base=h/src.height*100;
  T(L,"Scale").expression="var t=time-inPoint,b="+base.toFixed(3)+";var p=Math.min(1,t/0.35),u=p-1;var o=1+2.6*u*u*u+1.6*u*u;"+
    "var k=b*(0.8+0.2*o)*(1+0.05*time/"+CD.toFixed(3)+");[k,k]";
  T(L,"Position").expression="var s=1+0.05*time/"+CD.toFixed(3)+";[960+("+x+"-960)*s,540]";
  T(L,"Opacity").expression="time<inPoint?0:100";
  return L; }
endLogo("end nous","nous_logo_white.png",0,700,600);
endLogo("end log","log_mark.svg",0.40,760,1320);

// --- the scene
var old=findComp("ending demos"); if(old) old.remove();
var E=comp("ending",DUR);
// background, as logResearchDepth: the brand blue, its studio gradient, the circuit wall far behind (looped)
function stack(src,len,setup){ if(!(len>0.5)) len=DUR;  // a solid or still has no length of its own: one layer
  for (var t0=0;t0<DUR;t0+=len){ var L=E.layers.add(src); L.startTime=t0; L.inPoint=t0; L.outPoint=Math.min(t0+len,DUR); setup(L); } }
var RD=findComp("logResearchDepth");
var NAVY=[0.035,0.07,0.13];  // the research scene's dark navy
var base=E.layers.addSolid(NAVY,"navy",1920,1080,1); base.startTime=0; base.inPoint=0; base.outPoint=DUR;
var cw=byName(RD,"circuit wall"); if(cw) stack(cw.source,cw.source.duration,function(L){ L.name="circuit wall"; L.threeDLayer=true;
  L.blendingMode=cw.blendingMode; T(L,"Opacity").setValue(35); T(L,"Scale").setValue([700,700,700]); T(L,"Position").setValue([2000,600,6000]); });
// the cards in the world
for (var i=0;i<CARDS.length;i++){ var cd=CARDS[i], L=E.layers.add(cards[i]); L.name="terminal "+(i+1); L.threeDLayer=true;
  try{ L.collapseTransformation=false; }catch(x){}
  L.startTime=L0(cd.from); L.inPoint=0; L.outPoint=DUR;
  T(L,"Position").setValue(cd.pos); T(L,"Orientation").setValue([0,cd.tilt,0]); }
// the camera: a slow push on each card while it speaks, a fluid swing to the next before its line
var cam=E.layers.addCamera("3D Camera",[960,540]);
try{ cam.property("Camera Options").property("Zoom").setValue(ZOOM); }catch(x){}
// as an expression (setting a key on every frame is far too slow in the CLI): each card's pose pushes in slowly while it
// speaks; SWING s before a card's line the camera swings to it with a smootherstep
var SWING=0.8, cardsJ=[];
for (var i=0;i<CARDS.length;i++) cardsJ.push("["+L0(CARDS[i].from).toFixed(3)+","+L0(CARDS[i].to).toFixed(3)+","+CARDS[i].pos.join(",")+","+(CARDS[i].tilt>0?1:-1)+"]");
var CAMX="var C=["+cardsJ.join(",")+"],D="+DIST+",S="+SWING+";"
 +"function ease(x){x=Math.max(0,Math.min(1,x));return x*x*x*(x*(x*6-15)+10);}"
 +"function pose(c,u,poi){u=Math.max(0,Math.min(1,u));var d=D*(1-0.07*u);return poi?[c[2],c[3],c[4]]:[c[2]-c[5]*260*(1-0.3*u),c[3]-50,c[4]-d];}"
 +"function at(poi){var i=0;for(var k=0;k<C.length;k++)if(time>=C[k][0]-S+0.15)i=k;var c=C[i],cur=pose(c,(time-c[0])/(c[1]-c[0]),poi);"
 +"if(i>0&&time<c[0]+0.15&&c[0]-C[i-1][1]<0.01){var p=pose(C[i-1],1,poi),w=ease((time-(c[0]+0.15-S))/S);return [p[0]+(cur[0]-p[0])*w,p[1]+(cur[1]-p[1])*w,p[2]+(cur[2]-p[2])*w];}return cur;}";
cam.property("Transform").property("Position").expression=CAMX+"at(false)";
cam.property("Transform").property("Point of Interest").expression=CAMX+"at(true)";
// logResearchDepth for "find them, speak with them, win the people over"
var R=E.layers.add(RD); R.name="logResearchDepth"; R.startTime=L0(RESEARCH.from)-RESEARCH.at; R.inPoint=L0(RESEARCH.from); R.outPoint=L0(RESEARCH.to);
R.moveToBeginning();
var RB=E.layers.addSolid(NAVY,"navy under research",1920,1080,1); RB.startTime=0; RB.inPoint=R.inPoint; RB.outPoint=R.outPoint; RB.moveAfter(R);
var KC=E.layers.add(K); KC.name="ending card"; KC.startTime=L0(CARD_AT); KC.inPoint=L0(CARD_AT); KC.outPoint=DUR; KC.moveToBeginning();
// thermogram flashes on top: frames -2 orange, -1 green, 0 orange, +1 picture, +2 green, +3 orange, in an exposure blow-out
var cuts=[]; for (var i=0;i<THERMAL.length;i++) cuts.push(L0(THERMAL[i]).toFixed(4));
var CUTS="["+cuts.join(",")+"]";
var LOOK="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";
var X=E.layers.addSolid([0,0,0],"exposure cuts",1920,1080,1); X.adjustmentLayer=true; X.startTime=0; X.inPoint=0; X.outPoint=DUR;
P(X.property("Effects").addProperty("ec.color.exposure"),"master/exposure").expression="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.3&&d<=0)p=(d+.3)/.3;else if(d>0&&d<.4)p=1-d/.4;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}th?0.35*env:3.6*env";
X.moveToBeginning();
var LUTS={"thermal orange":["thermograph_orange","o"],"thermal green":["thermograph_green","g"]};
for (var n in LUTS){ var Th=E.layers.addSolid([0,0,0],n,1920,1080,1); Th.adjustmentLayer=true; Th.startTime=0; Th.inPoint=0; Th.outPoint=DUR;
  P(Th.property("Effects").addProperty("ec.utility.applylut"),"lut").setValue(ROOT+"textAnimations/assets/luts/"+LUTS[n][0]+".cube");
  T(Th,"Opacity").expression=LOOK+"look==='"+LUTS[n][1]+"'?100:0"; Th.moveToBeginning(); }

// --- into the launch film, after cyberpunk; longer for the card
var LF=findComp("launch film"); if(!LF) throw new Error("no launch film");
var was=byName(LF,"ending"); if(was) was.remove();
LF.duration=END;
var N=LF.layers.add(E); N.name="ending"; N.startTime=START; N.inPoint=START; N.outPoint=END;
var cy=byName(LF,"cyberpunk"); if(cy) N.moveBefore(cy);
var vo=byName(LF,"vo"), mu=byName(LF,"music"); if(vo) vo.outPoint=END; if(mu) mu.outPoint=END;
writeLn("ending: 4 terminal cards + logResearchDepth + end card, "+START+"-"+END+" s; launch film "+LF.duration.toFixed(2)+" s");
for (var k=1;k<=LF.numLayers;k++){ var l=LF.layer(k); writeLn("  "+k+" ["+l.name+"] "+l.inPoint.toFixed(2)+"-"+l.outPoint.toFixed(2)); }
