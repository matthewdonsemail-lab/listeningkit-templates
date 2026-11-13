// Intro 1: one background behind every 3D demo shot, in screen space so camera moves can't push it off:
// her dark room wall with blind-bars of screen light (images/demo_bg_room.png) and dust drifting in the beam.
// The backdrops inside the demo precomps go off (they drifted with the 3D camera).
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function asset(p){ return findFile(p)||app.project.importFile(new ImportOptions(new File(p))); }
var ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/";
var DEMOS=["logInboxDemo","logReplyDemo","logThreeStepsTrack"];
for (var d=0;d<DEMOS.length;d++){ var D=findComp(DEMOS[d]); var b=byName(D,"backdrop")||byName(D,"circuit wall"); if(b) b.enabled=false; }

var c=findComp("Intro 1");
for (var k=c.numLayers;k>=1;k--) if(/^demo (bg|dust) /.test(c.layer(k).name)) c.layer(k).remove();
var room=asset(ROOT+"images/demo_bg_room.png"), dust=asset(ROOT+"textAnimations/assets/nickjayk/dust_beam.mp4");
var SHOTS=["shot inbox","shot reply","shot three steps"];
for (var i=0;i<SHOTS.length;i++){
  var S=byName(c,SHOTS[i]); if(!S) continue;
  var B=c.layers.add(room); B.name="demo bg "+SHOTS[i].slice(5); B.moveAfter(S);
  B.startTime=S.inPoint; B.inPoint=S.inPoint; B.outPoint=S.outPoint;
  var cover=Math.max(1920/room.width,1080/room.height)*100;
  // slow push and a drift against the demo camera, so the room has depth behind the cards
  B.property("Transform").property("Scale").expression=
    "var p=ease(time,inPoint,outPoint,0,1);var k="+cover.toFixed(4)+"*(1.06+0.05*p);[k,k]";
  B.property("Transform").property("Position").expression=
    "var p=ease(time,inPoint,outPoint,0,1);["+"960+"+(i%2?30:-30)+"*(1-2*p),540]";
  var U=c.layers.add(dust); U.name="demo dust "+SHOTS[i].slice(5); U.moveBefore(B);
  U.startTime=S.inPoint; U.inPoint=S.inPoint;
  U.timeRemapEnabled=true; U.property("Time Remap").expression="(time-inPoint)%4"; U.outPoint=S.outPoint;
  U.blendingMode=BlendingMode.ADD; U.property("Transform").property("Opacity").setValue(70);
  writeLn(SHOTS[i]+": room + dust "+S.inPoint.toFixed(2)+"→"+S.outPoint.toFixed(2));
}
