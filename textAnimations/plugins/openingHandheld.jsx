// The opening's camera, measured from The Big Short's first minute (projects/opening/ref/bigshort_camera.json):
//   faces    handheld: about 6 px of shake at ~1.7 Hz, a 0.2 degree wobble, a slow 1.2 %/s push in
//   screens  crash push-ins: about 25 %/s zoom with a drift (~150 px/s) and a heavier shake on top (drift softened to 70 px/s so the message stays in frame)
// As expressions on the shot layers of the "opening" comp, so the numbers stay editable. The outside shots (aerial,
// car window) and the cyberpsycho clip keep their own motion. Rerunning replaces the expressions.
var FACES=["02","06","07","08","10","11"], SCREENS=["03","04","05","09"];
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
// smooth handheld noise without wiggle(): a few incommensurate sines per axis, seeded per layer
function shake(seed,hz,amp){ return "var s="+seed+",t=time*"+hz+";"+
  "var nx=Math.sin(t*6.283+s)*0.55+Math.sin(t*2.71*6.283+s*1.7)*0.3+Math.sin(t*0.53*6.283+s*0.3)*0.4;"+
  "var ny=Math.sin(t*6.283*1.13+s*2.1)*0.55+Math.sin(t*3.07*6.283+s*0.9)*0.3+Math.sin(t*0.47*6.283+s*1.3)*0.4;"+
  "var A="+amp+";"; }
var c=findComp("opening"), out=[];
for (var k=1;k<=c.numLayers;k++){ var L=c.layer(k), m=L.name.match(/^opening (\d\d) /); if(!m) continue;
  var id=m[1], tr=L.property("Transform"), seed=k*1.37;
  if(FACES.join(",").indexOf(id)>=0){
    tr.property("Position").expression=shake(seed,1.7,6)+"value+[nx*A,ny*A]";
    tr.property("Rotation").expression=shake(seed+5,1.2,0.25)+"value+nx*A";
    tr.property("Scale").expression="var z=1+0.012*(time-inPoint);[value[0]*z,value[1]*z]";
    out.push(L.name+": handheld");
  } else if(SCREENS.join(",").indexOf(id)>=0){
    tr.property("Position").expression=shake(seed,2.2,14)+"var d=time-inPoint;value+[-70*d+nx*A,-25*d+ny*A]";
    tr.property("Rotation").expression=shake(seed+3,1.4,0.6)+"value+nx*A";
    tr.property("Scale").expression="var z=Math.pow(1.25,time-inPoint);[value[0]*z,value[1]*z]";
    out.push(L.name+": crash push-in");
  } }
writeLn(out.join("\n"));
