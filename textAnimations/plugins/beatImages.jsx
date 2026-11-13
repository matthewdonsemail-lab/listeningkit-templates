// Intro 1, 33.40-45.45: the 12 beat slots get their own generated image (images/beats), full frame,
// a slight push and drift each, like the 16-24 s stills.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findItem(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it.name===n && !(it instanceof CompItem)) return it;} return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/images/beats/";
var FILES=["01_log_ingests","02_every_conversation","03_youve_ever_had","04_builds","05_a_voice_profile","06_of_you",
           "07_local_models","08_re_rank","09_embed","10_vector_search","11_the_way_you_actually","12_talk"];
var c=findComp("Intro 1");
for (var k=1;k<=c.numLayers;k++){
  var L=c.layer(k), m=/^img (\d+) /.exec(L.name); if(!m) continue;
  var i=parseInt(m[1],10)-1, f=FILES[i]+".png";
  var src=findItem(f)||app.project.importFile(new ImportOptions(new File(DIR+f)));
  L.replaceSource(src,false);
  var cover=Math.max(1920/src.width,1080/src.height)*100;
  L.property("Transform").property("Scale").expression=
    "var p=ease(time,inPoint,outPoint,0,1);var k="+cover.toFixed(4)+"*(1.03+0.05*p);[k,k]";
  L.property("Transform").property("Position").expression=
    "var p=ease(time,inPoint,outPoint,0,1);["+"960+"+(i%2?18:-18)+"*(1-2*p),540+6*(1-2*p)]";
  P(L.property("Effects").property(1),"amount").setValue(35);
  L.name="img "+(i+1)+" "+FILES[i].slice(3).replace(/_/g," ");
  writeLn(L.name+" "+L.inPoint.toFixed(2)+"→"+L.outPoint.toFixed(2));
}
