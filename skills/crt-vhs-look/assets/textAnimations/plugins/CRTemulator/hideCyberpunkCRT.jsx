// cyberpunk: switch the CRT layers off for quick previews. To bring the CRT back exactly as it was, run
// applyCyberpunk.jsx again (it rebuilds the CRT with Posterize Time off).
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
var CRT=["Global Scale","Lens Distortions","Monitor","CRT Glow","CRT Effects","Channel Blur","CC","Posterize Time","Position Flicker",
         "CRT_LINE","CRT_LINE 2","CRT Mask","Glitches","Distortions","Glow","CC 2","CRT ExposureFIX"];
var c=findComp("cyberpunk"), n=0;
for (var k=1;k<=c.numLayers;k++){ var l=c.layer(k);
  for (var j=0;j<CRT.length;j++) if(l.name===CRT[j] && l.enabled){ l.enabled=false; n++; } }
writeLn("CRT off: "+n+" layers");
