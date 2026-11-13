// Intro 1, 33.40-57.15: her story with the shadow as the clone, cut against the 3D demos, with speed ramps.
// Images: images/shadow (the shadow-clone shots) and images/beats (kept). Style rules: RESEARCH/NEO_NOIR_SHOT_STYLE.md.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
function eachProp(g,fn){ for (var j=1;j<=g.numProperties;j++){ var p=g.property(j); if(p.propertyType===PropertyType.PROPERTY) fn(p); else eachProp(p,fn); } }
var IMG="C:/Users/0/.buzz/REPOS/listeningkit-templates/images/";
function img(rel){ var p=IMG+rel; return findFile(p)||app.project.importFile(new ImportOptions(new File(p))); }
var c=findComp("Intro 1");
var END=c.duration;

// the story: [file, in, out]
var STORY=[
 ["shadow/01_log_ingests.png",33.40,34.64],          // Log ingests — her shadow huge behind her
 ["shadow/02_every_conversation.png",34.64,35.68],   // every conversation — screen light through blinds, bars over her eyes
 ["beats/03_youve_ever_had.png",35.68,36.67],        // you've ever had — her eyes
 ["shadow/05_a_voice_profile.png",38.00,39.22],      // builds a voice profile — her shadow turns and studies her
 ["shadow/06_of_you.png",39.22,40.25],               // of you — two shadows: the clone is born
 ["beats/07_local_models.png",40.25,41.20],          // Local models — overhead, the ring of screens
 ["shadow/08_re_rank.png",41.20,41.82],              // re-rank — her shadow pulls one card out of line
 ["beats/09_embed.png",41.82,42.54],                 // embed — a drop of light in her palm
 ["beats/10_vector_search.png",42.54,43.45],         // vector search — the chart over her eye
 ["beats/11_the_way_you_actually.png",43.45,44.38],  // the way you actually — her lips
 ["shadow/12_talk.png",44.38,45.45],                 // talk — her lips shut, the shadow speaks
 ["shadow/13_time_back.png",52.90,54.70]             // give you your time back — she walks out, the shadow keeps working
];
for (var k=c.numLayers;k>=1;k--) if(/^img /.test(c.layer(k).name)) c.layer(k).remove();
var under=byName(c,"Adjustment Layer 1");
for (var i=0;i<STORY.length;i++){
  var s=STORY[i], src=img(s[0]);
  var L=c.layers.add(src); L.name="img "+(i+1)+" "+s[0].split("/")[1].replace(/^\d+_|\.png$/g,"").replace(/_/g," ");
  L.moveAfter(under); L.startTime=s[1]; L.inPoint=s[1]; L.outPoint=s[2];
  var cover=Math.max(1920/src.width,1080/src.height)*100;
  // speed ramp on the push: snaps into motion on the cut, then settles (ease-out expo)
  L.property("Transform").property("Scale").expression=
    "var t=Math.min(1,(time-inPoint)/(outPoint-inPoint));var e=1-Math.pow(2,-8*t);var k="+cover.toFixed(4)+"*(1.02+0.07*e);[k,k]";
  L.property("Transform").property("Position").expression=
    "var t=Math.min(1,(time-inPoint)/(outPoint-inPoint));var e=1-Math.pow(2,-8*t);[960+"+(i%2?22:-22)+"*(1-2*e),540]";
}

// demos: speed ramps — whip in fast, slow into the payoff and hold on it
var DEMOS=[["shot inbox",36.67,38.00,2.0,4.6],["shot reply",45.45,49.70,1.6,7.8],["shot three steps",49.70,52.90,1.2,8.2]];
for (var i=0;i<DEMOS.length;i++){
  var d=DEMOS[i], L=byName(c,d[0]); if(!L) continue;
  L.inPoint=d[1]; L.outPoint=d[2];
  L.property("Time Remap").expression=
    "var t=Math.min(1,Math.max(0,(time-inPoint)/(outPoint-inPoint)));var e=1-Math.pow(1-t,3);"+d[3]+"+("+d[4]+"-"+d[3]+")*e";
}

// cuts: thermal + exposure on every scene/demo change, now including 52.90
var CUTS="[6.00,11.97,19.27,22.00,24.97,32.73,33.40,36.67,38.00,40.25,43.45,45.45,49.70,52.90,54.70]";
var UI_OLD="((time>=24.97&&time<33.40)||(time>=36.67&&time<38.00)||(time>=45.45&&time<54.70))";
var UI_NEW="((time>=24.97&&time<33.40)||(time>=36.67&&time<38.00)||(time>=45.45&&time<52.90))";
var changed=0;
for (var k=1;k<=c.numLayers;k++) eachProp(c.layer(k),function(p){
  if(!p.expression) return; var e=p.expression, e0=e;
  e=e.replace(/var cuts=\[[0-9.,]+\]/g,"var cuts="+CUTS); e=e.split(UI_OLD).join(UI_NEW);
  if(e!==e0){ p.expression=e; changed++; }
});
writeLn("expressions updated: "+changed);
for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k); if(/^img |^shot /.test(l.name)) writeLn("  ["+l.name+"] "+l.inPoint.toFixed(2)+"→"+l.outPoint.toFixed(2)); }
