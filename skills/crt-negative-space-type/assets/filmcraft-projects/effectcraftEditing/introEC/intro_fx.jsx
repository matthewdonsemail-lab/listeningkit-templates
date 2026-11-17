// The cold open's effects (matt, 2026-11-16), on comp "intro" as intro_base.jsx left it. Run before applyIntroCRT.jsx.
//   - "red lines": lines/l_NNN.png (make_intro_lines.py), a new drawing every frame, over the cards' gradient, under
//     the cards' letters where they weave
//   - "screen thermal": the plate in the thermograph LUTs on some cards (orange on 3, 5, 8; green on 6), under the
//     gradient and the type, so the screen reads as a heat map
//   - "cut displace": a Turbulent Displace hit on every card change (3 frames either side), the plate tearing
//   - "exposure cuts" / "thermal orange" / "thermal green": the launch film's thermogram transition on every card
//     change (frames -2 orange, -1 green, 0 orange, +2 green, +3 orange inside an exposure blow-out), on top of all
// Rerun replaces them.
var D="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/";
var LUTD="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/luts/";
var F=30;
var STARTS=[0,68,83,176,221,290,344,351,437,481];
var CUTS="["+STARTS.slice(1).map(function(f){return (f/F).toFixed(4);}).join(",")+"]";
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function Pp(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
var DUR=C.duration;
var MINE=["red lines","screen thermal orange","screen thermal green","cut displace","exposure cuts","thermal orange","thermal green"];
for (var i=0;i<MINE.length;i++){ var l=byName(C,MINE[i]); if(l) l.remove(); }
function adj(name){ var A=C.layers.addSolid([0,0,0],name,1920,1080,1); A.adjustmentLayer=true; A.startTime=0; A.inPoint=0; A.outPoint=DUR; return A; }
var plate=byName(C,"plate"), grad=byName(C,"left gradient");

// the screen as a heat map on some cards: just above the plate
var HELD={"screen thermal orange":["thermograph_orange",[[83,176],[221,290],[351,437]]],"screen thermal green":["thermograph_green",[[290,344]]]};
for (var n in HELD){
  var T=adj(n); var lut=fx(T,"ec.utility.applylut"); Pp(lut,"lut").setValue(LUTD+HELD[n][0]+".cube");
  var R=JSON.stringify(HELD[n][1]);
  T.property("Transform").property("Opacity").expression="var r="+R+",f=Math.round(time*30),on=0;for(var i=0;i<r.length;i++)if(f>=r[i][0]&&f<r[i][1])on=1;on?100:0";
  T.moveBefore(plate);
}
// the plate tears on every card change
var X=adj("cut displace"); var td=fx(X,"ADBE Turbulent Displace");
P(td,3).setValue(160); P(td,6).expression="time*400";
P(td,2).expression="var cuts="+CUTS+",a=0;for(var i=0;i<cuts.length;i++){var d=Math.abs(time-cuts[i])*30;if(d<=3)a=Math.max(a,(1-d/4)*220);}a";
X.moveBefore(plate);
// the red lines, over the gradient, under the cards
var o=new ImportOptions(new File(D+"lines/l_000.png")); o.sequence=true;
var seq=app.project.importFile(o); seq.mainSource.conformFrameRate=F;
var RLn=C.layers.add(seq); RLn.name="red lines"; RLn.startTime=0; RLn.inPoint=0; RLn.outPoint=DUR;
RLn.moveBefore(grad);
// the thermogram transition on every card change, on top of everything
var LOOK="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";
var E=adj("exposure cuts"); var ex=fx(E,"ec.color.exposure");
Pp(ex,"master/exposure").expression="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.15&&d<=0)p=(d+.15)/.15;else if(d>0&&d<.25)p=1-d/.25;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}th?0.35*env:2.4*env";
E.moveToBeginning();
var LUTS={"thermal orange":["thermograph_orange","o"],"thermal green":["thermograph_green","g"]};
for (var n2 in LUTS){
  var T2=adj(n2); var lut2=fx(T2,"ec.utility.applylut"); Pp(lut2,"lut").setValue(LUTD+LUTS[n2][0]+".cube");
  T2.property("Transform").property("Opacity").expression=LOOK+"look==='"+LUTS[n2][1]+"'?100:0";
  T2.moveToBeginning();
}
for (var k=1;k<=C.numLayers;k++) writeLn("  "+k+" "+C.layer(k).name);
