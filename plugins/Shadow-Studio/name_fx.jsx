var P="C:/Users/0/AppData/Local/Temp/listeningkit-templates/projects/logoTiles/logoTiles_crt.ecproj";
function fc(n){for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i);if(it instanceof CompItem&&it.name===n)return it;}return null;}
var C=fc("rimImg"); var L=null;
for(var i=1;i<=C.numLayers;i++) if(C.layer(i).name==="jason") L=C.layer(i);
L.effects.property(1).name="Shadow Studio 2 (Highlight)";
L.effects.property(2).name="Shadow Studio 2 (Shadow)";
L.effects.property(2).property("Angle").setValue(177);
app.project.save(new File(P));
writeLn("named: "+L.effects.property(1).name+" / "+L.effects.property(2).name);
