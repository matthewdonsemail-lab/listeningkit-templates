// logPlayJourney: a camera that anticipates, overshoots and springs (pre-pan, post-pan, zoom overshoot),
// and a neon grid floor and ceiling in world space so the moves read as travel through a space.
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var J=findComp("logPlayJourney");
var cam=byName(J,"3D Camera").property("Transform");

// back-in-out: drifts back before it goes (pre-pan) and runs past the card before settling (post-pan)
var BIO="function bio(t){var s=2.4;t*=2;if(t<1)return .5*(t*t*((s+1)*t-s));t-=2;return .5*(t*t*((s+1)*t+s)+2);}";
var props=["Position","Point of Interest","Z Rotation"];
for (var i=0;i<props.length;i++){
  var p=cam.property(props[i]), e=p.expression;
  if(e.indexOf("function bio(")>=0) continue;
  e=BIO+e;
  // travel: back-eased path, a bigger pull-out mid-move
  e=e.replace("var p=ease((time-a)/(b-a)),","var q=Math.max(0,Math.min(1,(time-a)/(b-a))),p=bio(q),");
  e=e.replace("d=2000+300*Math.sin(Math.PI*p);turn=Math.sin(Math.PI*p)","d=2000+650*Math.sin(Math.PI*q);turn=Math.sin(Math.PI*q)");
  // arrival: zooms in past the card and springs back
  e=e.replace(/\.035\*ring/g,".06*ring").replace("d-=170*ring;","d-=380*ring;");
  // just before leaving: a small push in that the pull-out releases
  e=e.replace("d+=450*sm(7.85,8.3);","if(next)d-=150*sm(stop.depart-.22,stop.depart)*(1-sm(stop.depart,stop.depart+.1));d+=450*sm(7.85,8.3);");
  p.expression=e;
}

// neon grid floor and ceiling: world space, so camera travel gives parallax
var GRIDS=[["grid floor",1250],["grid ceiling",-650]];
for (var i=0;i<GRIDS.length;i++){
  var old=byName(J,GRIDS[i][0]); if(old) old.remove();
  var L=J.layers.addSolid([0,0,0],GRIDS[i][0],20000,9000,1); L.inPoint=0; L.outPoint=J.duration;
  L.threeDLayer=true;
  var tr=L.property("Transform");
  tr.property("X Rotation").setValue(90);
  tr.property("Position").setValue([6200,GRIDS[i][1],400]);
  var g=L.property("Effects").addProperty("ec.generate.grid");
  P(g,"width").setValue(260); P(g,"height").setValue(260); P(g,"border").setValue(4);
  P(g,"color").setValue([0.15,0.95,0.8,1]);
  L.property("Effects").addProperty("ADBE Glo2");
  L.blendingMode=BlendingMode.ADD;
  L.property("Transform").property("Opacity").setValue(i?35:60);
  L.moveToEnd();
}
for (var k=1;k<=J.numLayers;k++){ var l=J.layer(k); if(/grid|Camera/.test(l.name)) writeLn("  "+k+" ["+l.name+"] 3D="+l.threeDLayer); }
