// Breathing room for the outro (matt, 2026-11-16): the music ran out (59.75 s) before the film did and the end card
// was only 3 s, so it all stopped too fast. This:
//   - lengthens the end card to 6 s ("ending card" comp, the "ending" comp and the "launch film" each +3 s; every
//     layer that ran to the old end now runs to the new one, so the CRT etc. carry on)
//   - swaps the music for assets/audio/launch_music_tail.wav (the same track, its last bar looped under an echo and
//     faded out over 4.6 s, ending at 64.2 s: made with ffmpeg, see the commit)
//   - adds "fade out" on top of the launch film: to black over the last 1.5 s
// Run once (a rerun adds another 3 s).   File > Scripts > Run Script File... > plugins/endingTail.jsx
var ADD=3, F=30, MUSIC="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/audio/launch_music_tail.wav";
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function grow(C, add){ var old=C.duration; C.duration=old+add;
  for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(Math.abs(L.outPoint-old)<0.02) L.outPoint=C.duration; } }
var EC=findComp("ending card"), E=findComp("ending"), LF=findComp("launch film");
grow(EC, ADD); grow(E, ADD);
var oldLF=LF.duration; grow(LF, ADD);
for (var k=1;k<=LF.numLayers;k++){ var L=LF.layer(k);
  if(L.name==="ending") L.outPoint=LF.duration;
  if(L.name==="music"){ var m=app.project.importFile(new ImportOptions(new File(MUSIC))); L.replaceSource(m,false); L.outPoint=LF.duration; }
  if(L.name==="vo") L.outPoint=LF.duration; }
for (var k=LF.numLayers;k>=1;k--) if(LF.layer(k).name==="fade out") LF.layer(k).remove();
var fo=LF.layers.addSolid([0,0,0],"fade out",LF.width,LF.height,1); fo.startTime=0; fo.inPoint=LF.duration-1.5; fo.outPoint=LF.duration;
fo.property("Opacity").expression="linear(time, outPoint-1.5, outPoint, 0, 100)"; fo.moveToBeginning();
writeLn("launch film "+oldLF.toFixed(2)+" -> "+LF.duration.toFixed(2)+" s; end card "+EC.duration+" s; music with a tail, fade to black over 1.5 s");
