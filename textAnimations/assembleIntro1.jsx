// Update the saved edit in place. Keep the existing opening, introCard timing and adjustment effects.
// Run: effectcraft-cli --project textAnimations.ecproj script assembleIntro1.jsx
function findComp(name) {
  for (var i=1;i<=app.project.numItems;i++) {
    var item=app.project.item(i);
    if (item instanceof CompItem && item.name===name) return item;
  }
  throw new Error('Missing composition: '+name);
}
function sourceLayer(comp,name) {
  for(var i=1;i<=comp.numLayers;i++) {
    var l=comp.layer(i);
    try { if(l.source.name===name) return l; } catch(e) {}
  }
  return null;
}
var main=findComp('Intro 1'), websites=findComp('type11'), platforms=findComp('type04');
var extraNames=['logPlayJourney'];
var extras=[];for(var i=0;i<extraNames.length;i++)extras.push(findComp(extraNames[i]));
var intro=sourceLayer(main,'introCard');
if(!intro) throw new Error('Intro 1 must already contain introCard');
var adjustment=null;
for(var i=1;i<=main.numLayers;i++) if(main.layer(i).adjustmentLayer) {adjustment=main.layer(i);break;}
if(!adjustment) throw new Error('Intro 1 must already have an adjustment layer');

// Replace the rejected typography and wipe instances only. Their library sources remain available.
for(var i=main.numLayers;i>=1;i--){
  var old=main.layer(i),sourceName='';try{sourceName=old.source.name;}catch(e){}
  if(['askHermes','socialActions','yourControl','blueSweep','logAgentDemo','logInboxDemo','logReplyDemo','logListeningDemo'].indexOf(sourceName)!==-1)old.remove();
}

var start11=intro.outPoint;
var l11=sourceLayer(main,'type11') || main.layers.add(websites);
l11.name='type11';l11.startTime=start11;l11.inPoint=start11;l11.outPoint=start11+websites.duration;
l11.moveAfter(adjustment);
var start04=l11.outPoint;
var l04=sourceLayer(main,'type04') || main.layers.add(platforms);
l04.name='type04';l04.startTime=start04;l04.inPoint=start04;l04.outPoint=start04+platforms.duration;
l04.moveAfter(adjustment);
if(main.duration<l04.outPoint) main.duration=l04.outPoint;
var sceneLayers=[intro,l11,l04],end=l04.outPoint;
var totalEnd=end;for(var i=0;i<extras.length;i++)totalEnd+=extras[i].duration;
if(main.duration<totalEnd)main.duration=totalEnd;
for(var i=0;i<extras.length;i++){
  var l=sourceLayer(main,extras[i].name)||main.layers.add(extras[i]);
  l.name=extras[i].name;l.startTime=end;l.inPoint=end;l.outPoint=end+extras[i].duration;
  l.moveAfter(adjustment);end=l.outPoint;sceneLayers.push(l);
}
main.workAreaStart=0;main.workAreaDuration=end;
adjustment.outPoint=l04.outPoint;
// This typography scene already owns its dotted background and page motion.
// Preserve the legacy grade for other shots without dithering its letters/logo tiles.
adjustment.property('Opacity').expression='';
adjustment.property('Opacity').setValue(100);
main.duration=end;

var effects=adjustment.property('Effects'),zoom=null;
var gradeBypass='var l=thisComp.layer("type11");time>=l.inPoint&&time<l.outPoint?0:value';
for(var i=1;i<=effects.numProperties;i++){
  var grade=effects.property(i),mix=grade.property('Mix with Original');
  if(mix&&(grade.name.indexOf('Halftone')!==-1||grade.name.indexOf('Pixel Sort')!==-1))mix.expression=gradeBypass;
}
for(var i=1;i<=effects.numProperties;i++) if(effects.property(i).name==='Cut zoom'||effects.property(i).name==='Cut motion') zoom=effects.property(i);
if(!zoom) zoom=effects.addProperty('ADBE Geometry2');
zoom.name='Cut motion';
zoom.property('Anchor Point').setValue([main.width/2,main.height/2]);
zoom.property('Position').setValue([main.width/2,main.height/2]);
zoom.property('Uniform Scale').setValue(true);
zoom.property('Sampling').setValue(2); // JSX popup values are one-based: Bicubic.
// Small directional follow-through carries the cut; the UI state change carries the story.
var clock='var names=["introCard","type11","type04","logPlayJourney"];var amount=0,shift=0;for(var i=0;i<names.length;i++){var p=(time-thisComp.layer(names[i]).inPoint+.16)/.44;if(p>=0&&p<=1){var a=Math.pow(Math.sin(Math.PI*p),4);amount+=a;shift+=Math.sin(2*Math.PI*p)*a;}}';
zoom.property('Scale Height').expression=clock+'100+2.5*amount';
zoom.property('Position').expression=clock+'[960+30*shift,540]';
zoom.property('Rotation').expression=clock+'.25*shift';
var blur=null;for(var i=1;i<=effects.numProperties;i++)if(effects.property(i).name==='Cut directional blur')blur=effects.property(i);
if(!blur)blur=effects.addProperty('ADBE Motion Blur');
blur.name='Cut directional blur';
blur.property('Direction').setValue(90);
blur.property('Blur Length').expression=clock+'8*amount';
adjustment.moveToBeginning();
main.time=l04.outPoint+1.75;
main.openInViewer();
app.project.save();
var summary=[];for(var i=0;i<sceneLayers.length;i++)summary.push({comp:sceneLayers[i].name,inPoint:sceneLayers[i].inPoint,outPoint:sceneLayers[i].outPoint});
writeLn(JSON.stringify({sequence:summary,adjustment:adjustment.name,workAreaEnd:end}));
