// Intro 1, 0-12 s: genre-swap match cuts and a PS2 lip-sync cutout.
// - Each swap (images/genre) is the SAME composition as the footage frame it was made from, re-imagined in another
//   genre (hyperreal photo, Magritte, Caravaggio oil, PS2 render); it cuts in for 6 frames where that frame plays.
//   Comp times come from the footage remaps: shot A linear(0..6 -> 0..5.146); shot B Pre-comp 49 linear(6..11.98 ->
//   0..3.05) into Pre-comp 51 (rotating 1: 0..1.567 -> 0..4.067; rotating 2: 1.533..3.9 -> 0..5.062).
// - The cutout: a window top left with her PS2 face cropped to the mouth, flapping open/closed on the VO words.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/images/genre/";
function img(n){ var p=DIR+n+".png"; return findFile(p)||app.project.importFile(new ImportOptions(new File(p))); }
var c=findComp("Intro 1"), F=1/30;
for (var k=c.numLayers;k>=1;k--) if(/^(genre |ps2 )/.test(c.layer(k).name)) c.layer(k).remove();
var girl=byName(c,"hermes girl intro");

// [image, comp time, frames]  — source frame in the comment
var SWAPS=[
 ["hill_hyperreal",3.78,6],   // HermesGirl.mp4 3.24
 ["glance_oil",6.75,6],       // rotating1 0.99
 ["glance_surreal",8.06,6],   // rotating1 2.73
 ["front_hyperreal",10.80,5], // rotating2 ~2.1 (front-on face)
 ["front_ps2",10.97,4]
];
for (var i=0;i<SWAPS.length;i++){
  var s=SWAPS[i], src=img(s[0]);
  var L=c.layers.add(src); L.name="genre "+s[0].replace(/_/g," "); L.moveBefore(girl);
  L.startTime=s[1]; L.inPoint=s[1]; L.outPoint=s[1]+s[2]*F;
  var cover=Math.max(1920/src.width,1080/src.height)*100;
  L.property("Transform").property("Scale").setValue([cover,cover]);
  writeLn(L.name+" "+s[1].toFixed(2)+"→"+L.outPoint.toFixed(2));
}

// the PS2 mouth: a 640x360 precomp framing the mouth of front_ps2, the open frame on top flapping with the VO
var M=findComp("ps2 mouth"); if(M) M.remove();
M=app.project.items.addComp("ps2 mouth",640,360,1,c.duration,30);
var closed=img("front_ps2"), open=img("front_ps2_open");
var W=closed.width, H=closed.height, sc=640/(0.30*W)*100;
var pos=[320-(0.515*W-W/2)*sc/100, 180-(0.745*H-H/2)*sc/100];
var LC=M.layers.add(closed); LC.property("Transform").property("Scale").setValue([sc,sc]); LC.property("Transform").property("Position").setValue(pos);
var LO=M.layers.add(open); LO.property("Transform").property("Scale").setValue([sc,sc]); LO.property("Transform").property("Position").setValue(pos);
// open while a word is being said, chattering every 3 frames like a PS2 jaw
LO.property("Transform").property("Opacity").expression=
  "var w=[[6.04,6.42],[6.42,7.2],[7.2,7.82],[7.82,8.92],[8.92,9.42],[10.32,10.4],[10.4,10.62],[10.62,11.02]];"+
  "var on=0;for(var i=0;i<w.length;i++)if(time>=w[i][0]&&time<w[i][1])on=1;on&&Math.floor(time*10)%2===0?100:0";

// in Intro 1: white-edged cutout window, top left, slightly tilted like a pasted-in clipping
// above the noir grade and the CRT colorize (still under its scanline grid and glow): it keeps its own PS2 colour, a clipping from another world
var FR=c.layers.addSolid([0.92,0.95,1],"ps2 cutout frame",660,380,1); FR.moveBefore(byName(c,"CC 2")); // above the grade and the CRT colorize, under its grid and glow
FR.inPoint=6.0; FR.outPoint=11.97;
FR.property("Transform").property("Position").setValue([380,250]);
FR.property("Transform").property("Rotation").setValue(-3);
var CU=c.layers.add(M); CU.name="ps2 cutout"; CU.moveBefore(FR);
CU.startTime=0; CU.inPoint=6.0; CU.outPoint=11.97;
CU.property("Transform").property("Position").setValue([380,250]);
CU.property("Transform").property("Rotation").setValue(-3);
// pops on with the cut at 6.00 and off before the card
FR.property("Transform").property("Scale").expression=CU.property("Transform").property("Scale").expression=
  "var t=time-inPoint;var s=t<0.1?100*Math.min(1,t/0.1)*1.08:100;[s,s]";
writeLn("ps2 cutout 6.00→11.97");


