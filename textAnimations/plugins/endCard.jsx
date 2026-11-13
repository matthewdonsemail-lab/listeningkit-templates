// Intro 1 end card: after "...the only moat is you." hard cut to the Nous logo and the Log mark side by side,
// big, each popping in with an overshoot (Log a beat after Nous) and pushing in slowly together.
// Assets: assets/endcard (nous_logo_white.png = the Nous logo as white line art, log_mark.svg = the Log logo without its blue square).
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function eachProp(g,fn){ for (var j=1;j<=g.numProperties;j++){ var p=g.property(j); if(p.propertyType===PropertyType.PROPERTY) fn(p); else eachProp(p,fn); } }
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/endcard/";
var c=findComp("Intro 1");
var T0=57.15, END=62.15;

var OLD=c.duration;
if(OLD<END-0.01){
  c.duration=END;
  for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k);
    if(l.name!=="vo" && l.inPoint<=6 && l.outPoint>=OLD-0.05) l.outPoint=END; }
}
for (var k=c.numLayers;k>=1;k--) if(/^end /.test(c.layer(k).name)) c.layer(k).remove();

function logo(name,file,tin,h,x){
  var src=findFile(DIR+file)||app.project.importFile(new ImportOptions(new File(DIR+file)));
  var L=c.layers.add(src); L.name=name; L.moveBefore(byName(c,"CC 2")); // above the CRT colorize: true colours, under its grid and glow
  L.startTime=T0; L.inPoint=tin; L.outPoint=END;
  var base=h/src.height*100;
  // pops in past full size and settles; the push runs over the whole card so both move together
  L.property("Transform").property("Scale").expression=
    "var t=time-inPoint,b="+base.toFixed(3)+";var p=Math.min(1,t/0.35),u=p-1;var o=1+2.6*u*u*u+1.6*u*u;"+
    "var k=b*(0.8+0.2*o)*(1+0.05*(time-"+T0+")/"+(END-T0)+");[k,k]";
  L.property("Transform").property("Position").expression=
    "var s=1+0.05*(time-"+T0+")/"+(END-T0)+";[960+("+x+"-960)*s,540]";
  return L;
}
// side by side: Nous card (portrait, 1464x2040) left, Log mark right
logo("end nous","nous_logo_white.png",T0,700,600);
logo("end log","log_mark.svg",T0+0.40,760,1320);

// one cut into the card (57.15) keeps the exposure ramp + thermal flash; the old Nous→Log cut at 59.65 goes
var changed=0;
for (var k=1;k<=c.numLayers;k++) eachProp(c.layer(k),function(p){
  if(!p.expression) return;
  var e=p.expression.split(",59.65").join("");
  if(e.indexOf("var cuts=[")>=0 && e.indexOf("57.15")<0) e=e.replace(/var cuts=\[([0-9.,]+)\]/g,"var cuts=[$1,57.15]");
  if(e!==p.expression){ p.expression=e; changed++; }
});
writeLn("end card "+T0+"→"+END+"; cut expressions updated: "+changed);

