// Intro 1: each story still becomes its random cut-up collage video (assets/collage, made by make_collage_shots.py).
// Replaces the still in place (keeps its timing, push and drift); the separate variant flashes and patch layers go.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/";
var MAP=[["img 1 log ingests","01_log_ingests"],["img 2 every conversation","02_every_conversation"],
 ["img 3 youve ever had","03_youve_ever_had"],["img 4 a voice profile","05_a_voice_profile"],["img 5 of you","06_of_you"],
 ["img 6 local models","07_local_models"],["img 7 re rank","08_re_rank"],["img 8 embed","09_embed"],
 ["img 9 vector search","10_vector_search"],["img 10 the way you actually","11_the_way_you_actually"],
 ["img 11 talk","12_talk"],["img 12 time back","13_time_back"],["shot only moat","Blue_Noir_Only_Moat"]];
var c=findComp("Intro 1");
for (var k=c.numLayers;k>=1;k--) if(/^(var|patch) /.test(c.layer(k).name)) c.layer(k).remove();
for (var i=0;i<MAP.length;i++){
  var L=byName(c,MAP[i][0]); if(!L){ writeLn("missing "+MAP[i][0]); continue; }
  var p=DIR+MAP[i][1]+".mp4", src=findFile(p)||app.project.importFile(new ImportOptions(new File(p)));
  var tin=L.inPoint, tout=L.outPoint;
  L.replaceSource(src,false);
  L.startTime=tin; L.inPoint=tin; L.outPoint=tout;
  L.property("Transform").property("Anchor Point").setValue([src.width/2,src.height/2]); // the old still's anchor stays after a swap
  // the cover scale follows the new source size; the push (and the moat shot's own scale) stays
  var sc=L.property("Transform").property("Scale");
  sc.expression=sc.expression.replace(/var k=[0-9.]+\*/,"var k=Math.max(thisComp.width/width,thisComp.height/height)*100*");
  writeLn(MAP[i][0]+" -> "+MAP[i][1]+".mp4 "+tin.toFixed(2)+"→"+tout.toFixed(2));
}

