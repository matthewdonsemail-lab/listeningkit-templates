// Intro 1, 33.40 → 45.45 reworked:
// - each image line is 2-4 hard-cut crops of one image on the VO words (like 16-24 s), large, slight movement,
//   lit out of the dark (chiaroscuro) so the crop is the point
// - the research demo is out (it doesn't say "re-rank, embed, vector search"); Vector Space crops say it
// - code rain and HUD off; each 3D demo gets its own backdrop; demo colours dulled to read through the CRT
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findItem(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it.name===n && !(it instanceof CompItem)) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
function eachProp(g,fn){ for (var j=1;j<=g.numProperties;j++){ var p=g.property(j); if(p.propertyType===PropertyType.PROPERTY) fn(p); else eachProp(p,fn); } }
var ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/";
function asset(path){ var n=path.split("/").pop(); return findItem(n)||app.project.importFile(new ImportOptions(new File(ROOT+path))); }
var c=findComp("Intro 1");

// out: the single-image slides, the research demo, code rain, HUD, and any earlier crops
var gone=["shot ingest","shot voiceprint","shot vector space","shot research","fx code rain","fx hud frame"];
for (var i=0;i<gone.length;i++){ var g=byName(c,gone[i]); if(g) g.remove(); }
for (var k=c.numLayers;k>=1;k--) if(/^img /.test(c.layer(k).name)) c.layer(k).remove();

// crops: [image, in, out, centre x, centre y (0-1 of the image), zoom (1 = covers the frame), word]
var A="images/Blue Noir Ingest.png", B="images/Blue Noir Voiceprint.png", C="images/Blue Noir Vector Space.png";
var CROPS=[
 [A,33.40,34.64,0.50,0.50,1.12,"Log ingests"],
 [A,34.64,35.68,0.73,0.45,2.6,"every conversation"],     // the ring of messages
 [A,35.68,36.67,0.52,0.31,3.0,"you've ever had"],        // her face in the screen light
 [B,38.00,38.48,0.50,0.34,2.2,"builds"],                 // her hair breaking into particles
 [B,38.48,39.22,0.82,0.45,2.6,"a voice profile"],        // the waveform
 [B,39.22,40.25,0.20,0.50,3.2,"of you"],                 // her eye
 [C,40.25,41.20,0.50,0.50,1.08,"Local models"],
 [C,41.20,41.82,0.56,0.31,3.2,"re-rank"],                // one cluster
 [C,41.82,42.54,0.75,0.53,3.0,"embed"],                  // another
 [C,42.54,43.45,0.47,0.52,2.3,"vector search"],          // her, looking up into it
 [B,43.45,44.38,0.23,0.72,3.6,"the way you actually"],   // her lips
 [B,44.38,45.45,0.72,0.45,1.7,"talk"]                    // the voice, wide
];
var under=byName(c,"Adjustment Layer 1");
for (var i=0;i<CROPS.length;i++){
  var r=CROPS[i], src=asset(r[0]);
  var L=c.layers.add(src); L.name="img "+(i+1)+" "+r[6]; L.moveAfter(under);
  L.startTime=r[1]; L.inPoint=r[1]; L.outPoint=r[2];
  var cover=Math.max(1920/src.width,1080/src.height)*100;
  // slight movement: a 4% push and a small drift, the crop point held at the centre and the edges always covered
  L.property("Transform").property("Scale").expression=
    "var p=ease(time,inPoint,outPoint,0,1);var k="+cover.toFixed(4)+"*"+r[5]+"*(1+0.04*p);[k,k]";
  L.property("Transform").property("Position").expression=
    "var p=ease(time,inPoint,outPoint,0,1);var k=scale[0]/100,w=width*k,h=height*k;"+
    "var x=960-("+r[3]+"-0.5)*w+"+(i%2?14:-14)+"*(1-2*p),y=540-("+r[4]+"-0.5)*h;"+
    "x=Math.min(w/2,Math.max(1920-w/2,x));y=Math.min(h/2,Math.max(1080-h/2,y));[x,y]";
  // chiaroscuro: the point lit, the rest falling to black
  var v=L.property("Effects").addProperty("ec.stylize.ccvignette");
  P(v,"amount").setValue(r[5]>1.5?85:65); P(v,"angleOfView").setValue(70);
}
writeLn("crops: "+CROPS.length);

// each 3D demo gets its own backdrop, darker
var BACK={"logInboxDemo":"code_rain.mp4","logReplyDemo":"dot_globe.mp4","logThreeStepsTrack":"warp_tunnel.mp4"};
for (var n in BACK){
  var D=findComp(n), W=byName(D,"circuit wall"); if(!W) continue;
  W.replaceSource(asset("textAnimations/assets/nickjayk/"+BACK[n]),false);
  W.property("Transform").property("Opacity").setValue(60);
  writeLn(n+": backdrop "+BACK[n]);
}

// duller colours on the 3D scenes so the UI reads through the CRT
var DULL=["logPlayJourney","shot inbox","shot reply","shot three steps"];
for (var i=0;i<DULL.length;i++){
  var L=byName(c,DULL[i]); if(!L) continue;
  var fx=L.property("Effects");
  for (var j=fx.numProperties;j>=1;j--) if(fx.property(j).name==="Dull") fx.property(j).remove();
  var h=fx.addProperty("ADBE HUE SATURATION"); h.name="Dull";
  h.property("Master Saturation").setValue(-55);
  h.property("Master Lightness").setValue(-10);
}

// the UI-only CRT settings follow the new shot list (no research shot any more)
var OLDUI="((time>=24.97&&time<33.40)||(time>=36.67&&time<38.00)||(time>=40.25&&time<43.45)||(time>=45.45&&time<54.70))";
var NEWUI="((time>=24.97&&time<33.40)||(time>=36.67&&time<38.00)||(time>=45.45&&time<54.70))";
var changed=0;
for (var k=1;k<=c.numLayers;k++) eachProp(c.layer(k),function(p){ if(p.expression&&p.expression.indexOf(OLDUI)>=0){ p.expression=p.expression.split(OLDUI).join(NEWUI); changed++; } });
writeLn("UI ranges updated: "+changed);
for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k); if(/^img |^shot /.test(l.name)) writeLn("  ["+l.name+"] "+l.inPoint.toFixed(2)+"→"+l.outPoint.toFixed(2)); }

