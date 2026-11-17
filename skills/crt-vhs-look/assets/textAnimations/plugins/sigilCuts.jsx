// Intro 1: a 5-frame abstract sigil cutaway on each cut (images/sigils, file name = cut time), the idea of the VO
// at that point. Full frame, one dropped frame for a flicker, a small scale pop; under the grade, CRT and thermal flash, above the cut noise.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/images/sigils/";
var FILES=["s0600_hourglass","s1197_eye","s1927_lone_node","s2200_two_faces","s2497_radial_network","s3340_inward_spiral",
           "s3667_index","s3800_voiceprint","s4025_lattice","s4345_mouth","s4545_mirror","s4970_key","s5290_door","s5470_moat"];
var c=findComp("Intro 1"), F=1/30;
for (var k=c.numLayers;k>=1;k--) if(/^sig /.test(c.layer(k).name)) c.layer(k).remove();
var above=byName(c,"exposure cuts"); // above the cut noise/blur so the thin lines survive
for (var i=0;i<FILES.length;i++){
  var p=DIR+FILES[i]+".png", src=findFile(p)||app.project.importFile(new ImportOptions(new File(p)));
  var t=parseInt(FILES[i].substr(1,4),10)/100;
  var L=c.layers.add(src); L.name="sig "+FILES[i].substr(6).replace(/_/g," ");
  L.moveBefore(above); L.startTime=t; L.inPoint=t; L.outPoint=t+5*F;
  var cover=Math.max(1920/src.width,1080/src.height)*100;
  L.property("Transform").property("Scale").expression=
    "var f=Math.round((time-inPoint)*30);var k="+cover.toFixed(4)+"*(1.0+0.025*f);[k,k]";
  L.property("Transform").property("Opacity").expression="Math.round((time-inPoint)*30)===2?0:100";
  writeLn(L.name+" "+t.toFixed(2)+"→"+L.outPoint.toFixed(2));
}

