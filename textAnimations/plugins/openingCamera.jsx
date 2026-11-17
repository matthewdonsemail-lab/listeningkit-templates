// Camera moves on the opener's shots (matt, 2026-11-16), so they read as real shots: on the picture layer inside each
// shot's precomp, as expressions (edit the numbers at the top of each):
//   00 aerial            a slow push in on the city, handheld shake; morphs into 01 (turbulent dissolve, 6 frames)
//   01 car window        a push in on the Pioneer Building sign, handheld
//   02 Sam at the desk   a push in, handheld
//   06 sama3             a push in to his eyes, a rack focus (soft to sharp), handheld
//   08 through the blinds  a push in on him, a rack focus, handheld
//   10 his face          a pull out from his face, handheld
//   11 the other guy     a pull out from his face, handheld; then the cyberpsycho clip as before
// Rerun replaces them.   File > Scripts > Run Script File... > plugins/openingCamera.jsx
var F=30;
// shot: [push amount (negative = pull out), target x, y in the shot comp, frames, rack focus]
var SHOTS={
  "opening 00 aerial":[0.14, 900, 350, 23, false],
  "opening 01 carwindow_moving_raw":[0.22, 960, 620, 25, false],
  "opening 02 Cinematic Close-Up of Sam Altman":[0.16, 700, 380, 16, false],
  "opening 06 sama3":[0.38, 660, 230, 25, true],
  "opening 08 Through the Blinds_ Focused Tech Workspace":[0.24, 840, 460, 34, true],
  "opening 10 Through the Blinds, Wired In Silence":[-0.45, 660, 400, 28, false],
  "opening 11 Intense Gaze Before the Chalkboard":[-0.45, 1240, 440, 27, false]};
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function pic(C){ for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(L.enabled && !(L.source instanceof CompItem)) return L; } return C.layer(1); }
var n=0;
for (var name in SHOTS){ var C=findComp(name); if(!C) continue; var s=SHOTS[name], L=pic(C);
  var e=L.property("Effects"); for (var q=e.numProperties;q>=1;q--) if(/^cam /.test(e.property(q).name)) e.property(q).remove();
  var dur=(s[3]/F).toFixed(4), amt=s[0];
  // the move: scale about the target, eased; a push goes 1 -> 1+amt, a pull out 1-amt -> 1
  var K="var u=ease(time,0,"+dur+",0,1); var k="+(amt>=0?("1+"+amt+"*u"):("1+"+(-amt)+"*(1-u)"))+";";
  // handheld: a few slow sines, a little rotation
  var SH="var sx=6*Math.sin(time*2.3+1.1)+3*Math.sin(time*5.7)+1.5*Math.sin(time*11.3+2); var sy=5*Math.sin(time*1.9+0.4)+2.5*Math.sin(time*6.1+1.7)+1.2*Math.sin(time*12.7);";
  L.property("Transform").property("Scale").expression=K+"[value[0]*k, value[1]*k]";
  L.property("Transform").property("Position").expression=K+SH+"var T=["+s[1]+","+s[2]+"]; [T[0]+(value[0]-T[0])*k+sx, T[1]+(value[1]-T[1])*k+sy]";
  L.property("Transform").property("Rotation").expression="value+0.25*Math.sin(time*1.7+0.6)+0.1*Math.sin(time*4.9)";
  if(s[4]){ var b=fx(L,"ADBE Camera Lens Blur"); b.name="cam focus"; P(b,5).setValue(1);
    P(b,1).expression="var u=time/"+dur+"; u<0.12?16:(u<0.45?16*(1-ease(u,0.12,0.45,0,1)):1.2*Math.abs(Math.sin(time*3)))"; }
  n++;
}
// the morph from 00 into 01: 01 comes in 6 frames early, dissolving through a turbulent warp on both
var O=findComp("opening");
var a=null, c=null; for (var k=1;k<=O.numLayers;k++){ if(O.layer(k).name==="opening 00 aerial") a=O.layer(k); if(O.layer(k).name==="opening 01 carwindow_moving_raw") c=O.layer(k); }
if(a && c){ var M=6/F, cut=c.inPoint; if(Math.abs(cut-23/F)<0.01){ c.inPoint=cut-M; }
  cut=23/F;
  var ea=a.property("Effects"); for (var q=ea.numProperties;q>=1;q--) if(/^cam /.test(ea.property(q).name)) ea.property(q).remove();
  var ec=c.property("Effects"); for (var q=ec.numProperties;q>=1;q--) if(/^cam /.test(ec.property(q).name)) ec.property(q).remove();
  var ta=fx(a,"ADBE Turbulent Displace"); ta.name="cam morph"; P(ta,3).setValue(140); P(ta,6).expression="time*120";
  P(ta,2).expression="linear(time,"+(cut-M).toFixed(4)+","+cut.toFixed(4)+",0,160)";
  var tc=fx(c,"ADBE Turbulent Displace"); tc.name="cam morph"; P(tc,3).setValue(140); P(tc,6).expression="time*120";
  P(tc,2).expression="linear(time,"+(cut-M).toFixed(4)+","+(cut+3/F).toFixed(4)+",160,0)";
  c.property("Opacity").expression="linear(time,"+(cut-M).toFixed(4)+","+cut.toFixed(4)+",0,100)";
  if(c.index>a.index) c.moveBefore(a);
}
writeLn("opening: camera moves on "+n+" shots, aerial morphs into the car window");
