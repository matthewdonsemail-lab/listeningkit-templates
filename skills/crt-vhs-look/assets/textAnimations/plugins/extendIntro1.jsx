// Intro 1, 33.40 → 57.15: the rest of the VO, Blue Noir image slides cut against the 3D demo precomps.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findItem(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it.name===n && !(it instanceof CompItem)) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
function eachProp(g,fn){ for (var j=1;j<=g.numProperties;j++){ var p=g.property(j); if(p.propertyType===PropertyType.PROPERTY) fn(p); else eachProp(p,fn); } }
var ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/";
function asset(path){ var n=path.split("/").pop(); return findItem(n)||app.project.importFile(new ImportOptions(new File(ROOT+path))); }

// ---- 1: the demo precomps on the noir look: no floating captions, no light backgrounds, the circuit wall behind
var wallSrc=asset("textAnimations/assets/nickjayk/circuit_wall.mp4");
var DEMOS=["logAgentDemo","logInboxDemo","logReplyDemo","logResearchDepth","logThreeStepsTrack"];
for (var d=0;d<DEMOS.length;d++){
  var D=findComp(DEMOS[d]);
  var off=["Motion caption","Studio gradient","Brand blue background","Built dither background"];
  for (var i=0;i<off.length;i++){ var l=byName(D,off[i]); if(l) l.enabled=false; }
  var old=byName(D,"circuit wall"); if(old) old.remove();
  // centre of what the camera looks at, over the comp
  var poi=byName(D,"3D Camera").property("Transform").property("Point of Interest"), s=[0,0,0], n=9;
  for (var k=0;k<n;k++){ var v=poi.valueAtTime(D.duration*k/(n-1),false); s[0]+=v[0]/n; s[1]+=v[1]/n; s[2]+=v[2]/n; }
  var W=D.layers.add(wallSrc); W.name="circuit wall"; W.inPoint=0; W.outPoint=D.duration;
  W.timeRemapEnabled=true; W.property("Time Remap").expression="time%4"; W.outPoint=D.duration;
  W.threeDLayer=true;
  W.property("Transform").property("Position").setValue([s[0],s[1],s[2]+4200]);
  W.property("Transform").property("Scale").setValue([400,400,400]);
  W.property("Transform").property("Opacity").setValue(35);
  W.blendingMode=BlendingMode.ADD; W.moveToEnd();
  writeLn(DEMOS[d]+": captions/backgrounds off, circuit wall at "+[Math.round(s[0]),Math.round(s[1]),Math.round(s[2]+2600)]);
}

// ---- 2: the new section of Intro 1
var c=findComp("Intro 1");
var OLD_END=c.duration, END=57.15;
c.duration=END;
for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k); if(l.outPoint>=OLD_END-0.01) l.outPoint=END; }
byName(c,"vo").outPoint=END;
byName(c,"type04").outPoint=33.40; // hard cut on "Log"
var tb=byName(c,"bg type04"); if(tb) tb.outPoint=33.40;
var tg=byName(c,"fx dot globe"); if(tg) tg.outPoint=33.40;

var under=byName(c,"Adjustment Layer 1");
// [name, kind, source, in, out, slide] — image slides drift sideways and push in; demos are time-remapped
var SHOTS=[
 ["shot ingest","img","images/Blue Noir Ingest.png",33.40,36.67,1],      // Log ingests every conversation you've ever had
 ["shot inbox","comp","logInboxDemo",36.67,38.00,[2.4,4.4]],              // indexes them
 ["shot voiceprint","img","images/Blue Noir Voiceprint.png",38.00,40.25,-1], // builds a voice profile of you
 ["shot research","comp","logResearchDepth",40.25,43.45,[3.4,7.6]],       // local models re-rank, embed and vector search
 ["shot vector space","img","images/Blue Noir Vector Space.png",43.45,45.45,1], // the way you actually talk
 ["shot reply","comp","logReplyDemo",45.45,49.70,[2.6,7.6]],              // so Hermes speaks like you … to who it matters
 ["shot three steps","comp","logThreeStepsTrack",49.70,54.70,[1.6,8.4]],  // an official Hermes plugin, built to give you your time back
 ["shot only moat","img","images/Blue Noir Only Moat.png",54.70,END,-1]   // because the only moat is you
];
for (var i=0;i<SHOTS.length;i++){
  var sh=SHOTS[i]; var o=byName(c,sh[0]); if(o) o.remove();
  var src=sh[1]==="img"?asset(sh[2]):findComp(sh[2]);
  var L=c.layers.add(src); L.name=sh[0]; L.moveAfter(under);
  L.startTime=sh[3]; L.inPoint=sh[3];
  if(sh[1]==="comp"){
    L.timeRemapEnabled=true;
    L.property("Time Remap").expression="linear(time,inPoint,outPoint,"+sh[5][0]+","+sh[5][1]+")";
  } else {
    // the camera slide: a slow lateral drift with a push, eased, the still overscanned to cover
    var dir=sh[5];
    L.property("Transform").property("Scale").expression=
      "var p=ease(time,inPoint,outPoint,0,1);var k=Math.max(thisComp.width/width,thisComp.height/height)*(106+7*p);[k,k]";
    L.property("Transform").property("Position").expression=
      "var p=ease(time,inPoint,outPoint,0,1);["+"thisComp.width/2+("+dir+")*(55-110*p),thisComp.height/2+8-16*p]";
  }
  L.outPoint=sh[4];
}

// THE ONLY MOAT IS YOU, word by word on the VO
var T=byName(c,"moat words"); if(T) T.remove();
T=c.layers.addText("THE ONLY MOAT IS YOU"); T.name="moat words"; T.moveBefore(byName(c,"shot only moat"));
T.inPoint=55.10; T.outPoint=END;
var st=T.property("Source Text"), td=st.value;
td.font="Satoshi"; td.fauxBold=true; td.fontSize=120; td.fillColor=[0.86,0.93,1]; td.justification=ParagraphJustification.CENTER_JUSTIFY; td.tracking=40;
st.setValue(td);
st.expression="var w=[['THE',55.10],['ONLY',55.30],['MOAT',55.64],['IS',56.14],['YOU.',56.56]],s='';for(var i=0;i<w.length;i++)if(time>=w[i][1])s+=(s?' ':'')+w[i][0];s";
T.property("Transform").property("Position").setValue([960,930]);
T.property("Effects").addProperty("ADBE Glo2");

// ---- 3: the cuts and the UI-only CRT settings
var CUTS="[6.00,11.97,19.27,22.00,24.97,32.73,33.40,36.67,38.00,40.25,43.45,45.45,49.70,54.70]";
var UIRANGE="((time>=24.97&&time<33.40)||(time>=36.67&&time<38.00)||(time>=40.25&&time<43.45)||(time>=45.45&&time<54.70))";
var changed=0;
for (var k=1;k<=c.numLayers;k++){
  eachProp(c.layer(k),function(p){
    if(!p.expression) return; var e=p.expression, e0=e;
    e=e.replace(/var cuts=\[[0-9.,]+\]/g,"var cuts="+CUTS);
    e=e.split("time>=24.97").join(UIRANGE);
    if(e!==e0){ p.expression=e; changed++; }
  });
}
writeLn("expressions updated: "+changed);
// CC 2 stays as the plug-in built it
byName(c,"CC 2").property("Transform").property("Opacity").expression="";
// light-grey card text on white clips under the CRT stack: headroom on the demo shots themselves
var HEAD={"shot research":-1.5,"shot reply":-1.3,"shot three steps":-1.5,"shot inbox":-0.6};
for (var n in HEAD){ var e=byName(c,n).property("Effects").addProperty("ec.color.exposure"); P(e,"master/exposure").setValue(HEAD[n]); }
for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k); if(/^shot |moat|type04|vo$/.test(l.name)) writeLn("  "+k+" ["+l.name+"] "+l.inPoint.toFixed(2)+"→"+l.outPoint.toFixed(2)); }





