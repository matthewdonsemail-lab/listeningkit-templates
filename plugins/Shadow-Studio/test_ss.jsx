var OUT="C:/Users/0/AppData/Local/hermes/cache/scratch/ss_test.ecproj";
app.newProject();
var C=app.project.items.addComp("t",400,400,1,2,30);
C.layers.addSolid([1,1,1],"bg",400,400,1);
var jf=app.project.importFile(new ImportOptions(new File("C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/logoTiles/jason_cut.png")));
var L=C.layers.add(jf);
var s=(300/jf.height)*100; L.property("Transform").property("Scale").setValue([s,s]);
L.property("Transform").property("Position").setValue([200,200]);
effect.plugins.load({path:"C:/Users/0/AppData/Roaming/EffectCraft/Plug-ins/shadow_studio.wasm"});
var E=L.effects.addProperty("Shadow Studio");
try{E.property("Shadow Type").setValue(0);}catch(e){}
try{E.property("Angle").setValue(135);}catch(e){}
try{E.property("Distance").setValue(40);}catch(e){}
try{E.property("Softness").setValue(20);}catch(e){}
try{E.property("Opacity Start").setValue(100);}catch(e){}
try{E.property("Opacity End").setValue(100);}catch(e){}
app.project.save(new File(OUT));
writeLn("test fx="+L.effects.numProperties);
