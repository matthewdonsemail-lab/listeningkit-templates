// 1) "Log by ListeningKit" holds to its last frame and hard-cuts at 16.97 on the music: no title exit, no ramp.
// 2) logPlayJourney: the grid floor/ceiling out, a particle circuit wall (assets/nickjayk/circuit_wall.mp4) in.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findItem(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it.name===n && !(it instanceof CompItem)) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function eachProp(g,fn){ for (var j=1;j<=g.numProperties;j++){ var p=g.property(j); if(p.propertyType===PropertyType.PROPERTY) fn(p); else eachProp(p,fn); } }

// --- 1: the card's "out" markers past its end, so the title is still up when the cut lands
var ic=findComp("introCard");
for (var k=1;k<=ic.numLayers;k++){
  var mk=ic.layer(k).property("Marker"); if(!mk) continue;
  for (var j=mk.numKeys;j>=1;j--){
    var v=mk.keyValue(j); if(v.comment!=="out") continue;
    mk.removeKey(j); mk.setValueAtTime(ic.duration+1,v);
    writeLn("introCard/"+ic.layer(k).name+": out marker → "+(ic.duration+1));
  }
}
// and 16.97 off every cut list (exposure ramp, noise, thermal LUTs)
var c=findComp("Intro 1");
var cutLayers=["exposure cuts","thermal orange","thermal green"];
for (var i=0;i<cutLayers.length;i++){
  var L=byName(c,cutLayers[i]); if(!L) continue;
  eachProp(L,function(p){ if(p.expression && p.expression.indexOf("16.97,")>=0){ p.expression=p.expression.split("16.97,").join(""); writeLn(cutLayers[i]+": "+p.name+" no longer cuts at 16.97"); } });
}

// --- 2: circuit wall in world space far behind the cards, so the camera's travel gives it parallax
var J=findComp("logPlayJourney");
var gone=["grid floor","grid ceiling","circuit wall"];
for (var i=0;i<gone.length;i++){ var g=byName(J,gone[i]); if(g) g.remove(); }
var src=findItem("circuit_wall.mp4")||app.project.importFile(new ImportOptions(new File("C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/nickjayk/circuit_wall.mp4")));
var W=J.layers.add(src); W.name="circuit wall"; W.inPoint=0; W.outPoint=J.duration;
W.timeRemapEnabled=true; W.property("Time Remap").expression="time%4"; W.outPoint=J.duration;
W.threeDLayer=true;
W.property("Transform").property("Position").setValue([6200,540,2600]);
W.property("Transform").property("Scale").setValue([300,300,300]);
W.property("Transform").property("Opacity").setValue(70);
W.blendingMode=BlendingMode.ADD;
W.moveToEnd();
writeLn("circuit wall in logPlayJourney at layer "+W.index);
