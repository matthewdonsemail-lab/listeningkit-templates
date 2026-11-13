// Intro 1: the type and UI scenes sit in the blue-noir world instead of a black void.
// Behind each, one of the film's own stills: dark, blurred, pushing in slowly.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findItem(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it.name===n && !(it instanceof CompItem)) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var c=findComp("Intro 1");

// type04: off the white Strawberry page, heading in near-white, so it no longer needs the colour flip
var t4=findComp("type04");
byName(t4,"Strawberry dotted background").enabled=false;
var hs=byName(t4,"heading").property("Source Text"); var hd=hs.value; hd.fillColor=[0.88,0.93,1]; hs.setValue(hd);
var G=byName(c,"noir grade"), gfx=G.property("Effects");
gfx.property("Invert").property("blend").expression="100";
for (var j=1;j<=gfx.numProperties;j++) if(gfx.property(j).matchName==="ec.color.exposure") P(gfx.property(j),"master/exposure").expression="0";

// [scene layer, still, in, out, darkness (stops), blur]
var BGS=[["introCard","Blue Noir Headband Portraits.png",11.97,16.97,-1.4,16],
         ["logPlayJourney","Blue Noir Whisper Network.png",24.97,32.97,-2.2,28],
         ["type04","Midnight Blue Conspiracy.png",32.73,35.73,-2.6,24]];
for (var i=0;i<BGS.length;i++){
  var b=BGS[i], name="bg "+b[0];
  var old=byName(c,name); if(old) old.remove();
  var L=c.layers.add(findItem(b[1])); L.name=name;
  L.startTime=0; L.inPoint=b[2]; L.outPoint=b[3];
  L.moveAfter(byName(c,b[0]));
  var tr=L.property("Transform");
  tr.property("Scale").expression="var p=(time-inPoint)/(outPoint-inPoint);var s=[thisComp.width/width,thisComp.height/height];var k=Math.max(s[0],s[1])*(104+8*p);[k,k]";
  var fx=L.property("Effects");
  P(fx.addProperty("ec.blur.fastbox"),"radius").setValue(b[5]);
  P(fx.addProperty("ec.color.exposure"),"master/exposure").setValue(b[4]);
}
for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k); if(/^bg |introCard|type04|logPlayJourney/.test(l.name)) writeLn("  "+k+" ["+l.name+"] "+l.inPoint.toFixed(2)+"→"+l.outPoint.toFixed(2)); }

