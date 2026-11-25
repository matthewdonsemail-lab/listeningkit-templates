var PROJ="C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/logoTiles/logoTiles_crt.ecproj";
var OUTDIR="C:/Users/0/AppData/Roaming/EffectCraft/Presets";
function mkdir(p){ var f=new Folder(p); if(!f.exists) f.create(); }
mkdir(OUTDIR);
app.newProject();
var C=app.project.items.addComp("p",1920,1080,1,2,30);
var L=C.layers.addSolid([0.5,0.5,0.5],"s",1920,1080,1);
app.executeCommand("effect.plugins.load", {path:"C:/Users/0/AppData/Roaming/EffectCraft/Plug-ins/shadow_studio.wasm"});

function setP(E,p){
  function s(n,v){ try{ E.property(n).setValue(v); }catch(e){ writeLn("  !"+n+" "+e.message); } }
  s("Shadow Type",p.type); s("Angle",p.angle); s("Distance",p.distance); s("Softness",p.softness);
  s("Color",p.color); s("Blend Mode",p.blend); s("Opacity Start",p.opacity); s("Opacity End",p.fall);
}

var PRESETS=[
 ["Inner Lighting",{type:2,angle:90,distance:40,softness:70,color:[1,1,1,1],blend:2,opacity:100,fall:0},{type:2,angle:270,distance:40,softness:70,color:[0,0,0,1],blend:0,opacity:60,fall:0}],
 ["Rim Lighting",{type:3,angle:90,distance:14,softness:30,color:[1,1,1,1],blend:2,opacity:100,fall:0},{type:3,angle:90,distance:14,softness:30,color:[0,0,0,1],blend:0,opacity:50,fall:0}],
 ["Glowing Edge",{type:3,angle:90,distance:22,softness:60,color:[1,1,1,1],blend:2,opacity:100,fall:20},{type:3,angle:90,distance:22,softness:60,color:[0,0,0,1],blend:0,opacity:30,fall:0}],
 ["Full Lighting",{type:1,angle:90,distance:30,softness:45,color:[1,1,1,1],blend:1,opacity:100,fall:40},{type:0,angle:270,distance:60,softness:55,color:[0,0,0,1],blend:0,opacity:75,fall:40}],
 ["Colorized Highlight",{type:1,angle:120,distance:26,softness:36,color:[1,0.55,0.15,1],blend:3,opacity:100,fall:50},{type:0,angle:300,distance:40,softness:40,color:[0,0,0,1],blend:0,opacity:55,fall:40}]
];

for (var i=0;i<PRESETS.length;i++){
  var name=PRESETS[i][0];
  for (var k=L.effects.numProperties;k>=1;k--) L.effects.property(k).remove();
  var EH=L.effects.addProperty("Shadow Studio"); EH.name="Shadow Studio (Highlight)"; setP(EH,PRESETS[i][1]);
  var ES=L.effects.addProperty("Shadow Studio"); ES.name="Shadow Studio (Shadow)"; setP(ES,PRESETS[i][2]);
  L.selected=true;
  EH.selected=true; ES.selected=true;
  var res=app.executeCommand("anim.savePreset",{path:OUTDIR+"/"+name+".ecpreset",name:name});
  writeLn(name+" -> "+(res===false||res===undefined?"?":JSON.stringify(res)));
}
writeLn("done");
