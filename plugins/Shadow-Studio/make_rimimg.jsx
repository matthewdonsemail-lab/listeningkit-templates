var PROJ="C:/Users/0/AppData/Local/Temp/listeningkit-templates/projects/logoTiles";
var P=PROJ+"/logoTiles_crt.ecproj";
for (var i=app.project.numItems;i>=1;i--){var it=app.project.item(i); if(it instanceof CompItem && it.name==="rimImg") it.remove();}
var C=app.project.items.addComp("rimImg",1280,960,1,4,30);
C.bgColor=[0,0,0];
var jf=app.project.importFile(new ImportOptions(new File(PROJ+"/jason_cut.png")));
var L=C.layers.add(jf); L.name="jason";
var s=(700/jf.height)*100; L.property("Transform").property("Scale").setValue([s,s]);
L.property("Transform").property("Position").setValue([640,480]);
app.project.save(new File(P));
writeLn("rimImg layers="+C.numLayers);
