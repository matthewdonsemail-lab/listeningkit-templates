// Rebuild only the launch film's end card (comp "ending card", 58.30 s on): the Nous logo and the Log mark side by side,
// as Intro 1's end card (plugins/endCard.jsx), on black. Same card endingTerminal.jsx builds; this touches nothing else.
//   File > Scripts > Run Script File... > plugins/launchEndCard.jsx
var F=30, ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/", ECDIR=ROOT+"textAnimations/assets/endcard/";
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function T(L,n){ return L.property("Transform").property(n); }
var K=findComp("ending card"); if(!K) throw new Error("no comp 'ending card': run plugins/endingTerminal.jsx first");
var CD=K.duration;
for (var k=K.numLayers;k>=1;k--) K.layer(k).remove();
var KB=K.layers.addSolid([0,0,0],"black",1920,1080,1); KB.startTime=0; KB.inPoint=0; KB.outPoint=CD;
function endLogo(name,file,tin,h,x){
  var src=null; for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===(ECDIR+file).toLowerCase()) src=it; }
  if(!src) src=app.project.importFile(new ImportOptions(new File(ECDIR+file)));
  var L=K.layers.add(src); L.name=name; L.startTime=0; L.inPoint=tin; L.outPoint=CD;
  var base=h/src.height*100;
  T(L,"Scale").expression="var t=time-inPoint,b="+base.toFixed(3)+";var p=Math.min(1,t/0.35),u=p-1;var o=1+2.6*u*u*u+1.6*u*u;"+
    "var k=b*(0.8+0.2*o)*(1+0.05*time/"+CD.toFixed(3)+");[k,k]";
  T(L,"Position").expression="var s=1+0.05*time/"+CD.toFixed(3)+";[960+("+x+"-960)*s,540]";
  return L; }
endLogo("end nous","nous_logo_white.png",0,700,600);
endLogo("end log","log_mark.svg",0.40,760,1320);
writeLn("ending card: Nous logo + Log mark");
