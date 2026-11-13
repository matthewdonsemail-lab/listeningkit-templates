// Intro 1: particle-built background elements in the style of nickjaykdesign.com
// (assets/nickjayk, made by make_elements.py), around the type and UI scenes.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findItem(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it.name===n && !(it instanceof CompItem)) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var c=findComp("Intro 1");
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/nickjayk/";
function asset(f){ return findItem(f)||app.project.importFile(new ImportOptions(new File(DIR+f))); }

// [layer name, file, in, out, sits above (the scene) or under, opacity, scale]
var EL=[["fx warp tunnel","warp_tunnel.mp4",11.97,16.97,"under:introCard",75,100],
        ["fx code rain","code_rain.mp4",24.97,32.97,"under:logPlayJourney",40,100],
        ["fx hud frame","hud_frame.png",24.97,32.97,"over:logPlayJourney",85,100],
        ["fx dot globe","dot_globe.mp4",32.73,35.73,"under:type04",70,125]];
for (var i=0;i<EL.length;i++){
  var e=EL[i]; var old=byName(c,e[0]); if(old) old.remove();
  var L=c.layers.add(asset(e[1])); L.name=e[0];
  L.startTime=e[2]; L.inPoint=e[2]; L.outPoint=e[3];
  if(/\.mp4$/.test(e[1])){ L.timeRemapEnabled=true; L.property("Time Remap").expression="(time-inPoint)%4"; L.outPoint=e[3]; }
  var rel=e[4].split(":"), scene=byName(c,rel[1]);
  if(rel[0]==="under") L.moveAfter(scene); else L.moveBefore(scene);
  if(rel[0]==="under") L.blendingMode=BlendingMode.ADD;
  L.property("Transform").property("Opacity").setValue(e[5]);
  L.property("Transform").property("Scale").setValue([e[6],e[6]]);
}
for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k); if(/^fx |^bg |introCard|type04|logPlayJourney/.test(l.name)) writeLn("  "+k+" ["+l.name+"] "+l.inPoint.toFixed(2)+"→"+l.outPoint.toFixed(2)); }
