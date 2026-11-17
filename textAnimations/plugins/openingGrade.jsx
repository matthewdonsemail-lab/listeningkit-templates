// The opening's grade, per shot (assets/make_opening_luts.py): sunny gold on the shots outside and in the car (the
// aerial and the car window), The Big Short's cold blue-grey on every shot inside. One Apply LUT effect on each shot
// layer of the "opening" comp; rerunning replaces it.
var ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/luts/";
var SUNNY=["aerial","carwindow"];
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
var c=findComp("opening"), n=0, s=0;
for (var k=1;k<=c.numLayers;k++){ var L=c.layer(k); if(L.name.indexOf("opening ")!==0) continue;
  var E=L.property("Effects"); for (var j=E.numProperties;j>=1;j--) if(E.property(j).name==="Grade") E.property(j).remove();
  var sunny=false; for (var q=0;q<SUNNY.length;q++) if(L.name.indexOf(SUNNY[q])>=0) sunny=true;
  var fx=E.addProperty("ec.utility.applylut"); fx.name="Grade";
  fx.property("lut").setValue(ROOT+(sunny?"sunny_gold":"bigshort_cold")+".cube"); n++; if(sunny) s++; }
writeLn("graded "+n+" shots: "+s+" sunny, "+(n-s)+" cold");
