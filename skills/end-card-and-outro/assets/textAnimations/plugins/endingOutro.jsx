// The outro (matt, 2026-11-16), with assets/audio/launch_music_outro.wav (assets/make_outro_audio.py): the girl's last
// phrase stuttered on the beat, loops getting shorter, a glitch, a reverb tail. The end card follows it:
//   - both logos for the first two loops, then the Log mark drops out: the single Nous logo
//   - the Nous logo jumps on every loop restart (a scale pop, a sideways kick, a glitch frame), harder as they shorten
//   - on the glitch it glitches out (Digital Glitch full, slips) and cuts to black; the reverb plays over black
// The film (and "ending", "ending card") run to the end of the audio. Replaces endingTail.jsx; run instead of it.
//   File > Scripts > Run Script File... > plugins/endingOutro.jsx
var MUSIC="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/audio/launch_music_outro.wav";
var F=30, NEW_LF=65.4;
var LOOPS=[0,0.768,1.536,1.92,2.304,2.496,2.688,2.784,2.88,2.976,3.072,3.12,3.168,3.216], GLITCH=3.264, OUT=3.414;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function grow(C, add){ var old=C.duration; C.duration=old+add; for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(Math.abs(L.outPoint-old)<0.02) L.outPoint=C.duration; } }
var EC=findComp("ending card"), E=findComp("ending"), LF=findComp("launch film");
var ADD=NEW_LF-LF.duration;
if(ADD>0.01){ grow(EC, ADD); grow(E, ADD); grow(LF, ADD); }
for (var k=1;k<=LF.numLayers;k++){ var L=LF.layer(k);
  if(L.name==="ending"||L.name==="vo") L.outPoint=LF.duration;
  if(L.name==="music"){ var m=app.project.importFile(new ImportOptions(new File(MUSIC))); L.replaceSource(m,false); L.outPoint=LF.duration; }
  if(L.name==="fade out") L.remove(); }

// the end card
var lp="var L=["+LOOPS.join(",")+"],t=time,i=-1;for(var k=0;k<L.length;k++) if(t>=L[k]) i=k; var d=(i<0)?99:t-L[i];";
for (var k=1;k<=EC.numLayers;k++){ var L=EC.layer(k);
  if(L.name==="end log"){ L.outPoint=LOOPS[2]; }
  if(L.name==="end nous"){ L.outPoint=OUT;
    var sc=L.property("Transform").property("Scale"), base=sc.expression;
    // the card's own pop-in / push, its last statement turned into v
    var body=base||"value", cut=body.lastIndexOf(";"), pre=(cut>=0)?body.slice(0,cut+1):"", last=(cut>=0)?body.slice(cut+1):body;
    sc.expression=pre+"var v="+last+";"+lp+
      "var hit=(i>=2)?(0.06+0.012*i):0; var p=(d<0.06)?1+hit*(1-d/0.06):1; [v[0]*p, v[1]*p]";
    var po=L.property("Transform").property("Position"), pv=po.value;
    po.expression=lp+"var kick=(i>=2&&d<0.04)?((i%2)?1:-1)*(8+6*i):0; value+[kick,0]";
    var g=fx(L,"ec.vr.digitalglitch");
    P(g,2).expression=lp+"(time>="+GLITCH+")?100:((i>=2&&d<0.035)?Math.min(100,20+6*i):0)"; P(g,5).expression="time*700";
    var t=fx(L,"ADBE Turbulent Displace"); P(t,3).setValue(30); P(t,6).expression="time*900";
    P(t,2).expression="(time>="+GLITCH+")?160:0";
  }
  if(L.name==="black") L.outPoint=EC.duration;
}
writeLn("outro: film "+LF.duration.toFixed(2)+" s, Nous alone from "+LOOPS[2]+" s, glitch out at "+GLITCH+" s, reverb to the end");
