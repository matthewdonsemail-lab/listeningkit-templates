var PROJ="C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/logoTiles";
var P=PROJ+"/logoTiles_crt.ecproj";
function findComp(n){ for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem&&it.name===n) return it;} return null; }
var C=findComp("jasonHero");
if(!C){ writeLn("no comp"); }
else {
  var L=null; for(var i=1;i<=C.numLayers;i++){ var x=C.layer(i); if(x.name==="jason") L=x; }
  if(!L){ writeLn("no jason layer"); }
  else {
    for(var k=L.effects.numProperties;k>=1;k--) L.effects.property(k).remove();   // strip all effects
    writeLn("effects left: "+L.effects.numProperties);
    app.executeCommand("effect.plugins.load",'{"path":"C:/Users/0/AppData/Roaming/EffectCraft/Plug-ins/shadow_studio.wasm"}');
    var E=L.effects.addProperty("Shadow Studio");
    E.name="Shadow Studio (Rim)";
    E.property("Shadow Type").setValue(3);   // Rim
    E.property("Angle").setValue(90);
    E.property("Distance").setValue(18);
    E.property("Softness").setValue(34);
    E.property("Color").setValue([1,1,1,1]);
    E.property("Blend Mode").setValue(2);    // Screen
    E.property("Opacity Start").setValue(100);
    E.property("Opacity End").setValue(0);
    writeLn("applied rim; effects now: "+L.effects.numProperties);
    app.project.save(new File(P));
  }
}
