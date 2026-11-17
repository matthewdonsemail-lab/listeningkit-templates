// Intro 1: a thermograph LUT flicker on every cut (orange and green), inside the exposure ramp.
// LUTs: assets/luts/thermograph_*.cube (make_thermograph_luts.py).
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var c=findComp("Intro 1");
var CUTS="[6.00,11.97,16.97,19.27,22.00,24.97,32.73]";
// frames around each cut: -2 orange, -1 green, 0 orange, +1 picture, +2 green, +3 orange
var LOOK="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";

var olds=["thermal cuts","thermal orange","thermal green"];
for (var i=0;i<olds.length;i++){ var l=byName(c,olds[i]); if(l) l.remove(); }

// on top of everything, the CRT included: the flash is the graded LUT at full strength
var LUTS={"thermal orange":["thermograph_orange","o"],"thermal green":["thermograph_green","g"]};
for (var n in LUTS){
  var L=c.layers.addSolid([0,0,0],n,1920,1080,1); L.adjustmentLayer=true; L.inPoint=0; L.outPoint=c.duration;
  L.moveToBeginning();
  var lut=L.property("Effects").addProperty("ec.utility.applylut");
  P(lut,"lut").setValue("C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/luts/"+LUTS[n][0]+".cube");
  L.property("Transform").property("Opacity").expression=LOOK+"look==='"+LUTS[n][1]+"'?100:0";
}

// exposure ramp: blows out into and out of the cut, a light lift on the LUT frames so the heat reads
var X=byName(c,"exposure cuts"); var xfx=X.property("Effects");
for (var j=xfx.numProperties;j>=1;j--) if(xfx.property(j).name==="Thermal") xfx.property(j).remove();
var ENV="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.3&&d<=0)p=(d+.3)/.3;else if(d>0&&d<.4)p=1-d/.4;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}";
for (var j=1;j<=xfx.numProperties;j++) if(xfx.property(j).matchName==="ec.color.exposure") P(xfx.property(j),"master/exposure").expression=ENV+"th?0.35*env:3.6*env";
for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k); if(/thermal|CC 2|exposure cuts/.test(l.name)) writeLn("  "+k+" ["+l.name+"]"); }

