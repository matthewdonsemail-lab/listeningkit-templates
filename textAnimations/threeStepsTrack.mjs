import {fileURLToPath} from 'node:url';
import {kit,stage} from './startCardMotion.mjs';

const white=[1,1,1],blue=[42/255,140/255,1],navy=[13/255,42/255,76/255];
const pale=[.95,.97,.99],muted=[.42,.50,.60],green=[.118,.557,.31];
export const stepsTrackDuration=9;
export const stepsTrackPartNames=['stepsAskDemo','stepsCodeDemo','stepsFlowDemo','stepsPlayDemo','stepsResultDemo','stepsCard1','stepsCard2','stepsCard3'];
const tasks=[['Read #marketing back a day','discordRead'],['Find a meme for the moment','memelordSearch'],['Check it fits the room','voice'],['Answer in the chat','discordSendLive'],['React to their thanks','discordReactLive']];
const asset=p=>fileURLToPath(new URL('./assets/'+p,import.meta.url)).replaceAll('\\','/');

function panel(k,dark=false){
  k.rect('Panel edge',560,368,1100,714,[.102,.373,.784],25);
  k.rect('Panel surface',560,360,1100,714,dark?[.051,.067,.09]:white,25);
}
function pop(k,n,start){
  k.ex(n,'transform/opacity',`time<${start}?0:100`);
  k.ex(n,'transform/position',`var v=value;[v[0],v[1]+24*(1-bk(${start},${start+.25})),0]`);
}
function group(k,n,names,x,y,start){
  k.cmd('layer.newNull',{name:n});k.set(n,'transform/position',[x,y,0]);
  for(const name of names){
    k.cmd('layer.setParent',{layers:[name],parent:n,compensate:true});
    // A parent null's opacity does not propagate to its children.
    k.ex(name,'transform/opacity',`time<${start}?0:100`);
  }
  k.ex(n,'transform/scale',`var s=90+10*bk(${start},${start+.28});[s,s,100]`);pop(k,n,start);
}

export function stepsTrackPartsSteps(){
  const all=[{command:'file.import',params:{paths:[asset('startCards/hermesAgent.png'),asset('platforms/discord.svg')]}}];
  let k=kit('stepsAskDemo',1120,740,stepsTrackDuration);panel(k);
  k.image('Hermes mark','hermesAgent.png',66,60,76);
  k.text('Agent name','Hermes Agent',112,60,33,navy,'Satoshi','Bold');
  k.rect('Header divider',560,108,1096,2,[.90,.93,.96],0);
  k.text('Session','growth-mates / #marketing',58,158,25,muted);
  k.rect('Your request',624,313,884,208,blue,25);
  k.text('Ask','/log  Read #marketing over the last day.\nWho needs help with ads?',220,314,37,white,'Satoshi','Bold');
  k.ex('Ask','text/sourceText','var s=String(value);s.slice(0,Math.floor(s.length*sm(.08,.65)))');
  k.rect('Reply bubble',481,493,850,96,pale,22);
  k.text('Reply','On it. Running the play with log.',85,493,35,navy);
  group(k,'Reply entrance',['Reply bubble','Reply'],481,493,.72);
  k.rect('Tool chip',397,616,680,68,[.90,.95,1],16);
  k.text('Tool label','●  log · discordRead',85,616,29,blue,'JetBrains Mono');
  group(k,'Tool entrance',['Tool chip','Tool label'],397,616,1.13);
  for(const n of ['Agent name','Ask','Reply'])k.control(n);all.push(...k.finish());

  k=kit('stepsCodeDemo',1120,740,stepsTrackDuration);panel(k,true);
  [57,89,121].forEach((x,i)=>k.rect('Window dot '+i,x,55,16,16,[.35,.39,.44],8));
  k.rect('File tab',268,55,184,52,[.13,.16,.20],10);
  k.text('File name','play.ts',208,55,28,[.8,.85,.91],'JetBrains Mono');
  k.rect('Code divider',560,98,1096,2,[.19,.23,.28],0);
  const lines=["export default definePlay('helpWithAds',",'  async (log) => {',...tasks.flatMap(([label,tool])=>['  // '+label,'  await log.'+tool+'()']),'})'];
  lines.forEach((line,i)=>{
    const y=146+i*43,n='Code line '+i;
    k.text('Line number '+i,String(i+1).padStart(2,'0'),41,y,23,[.36,.42,.49],'JetBrains Mono');
    k.text(n,line,104,y,28,line.includes('//')?[.55,.61,.67]:line.includes('await')?[.64,.80,1]:[.9,.94,.97],'JetBrains Mono');
    for(const name of [n,'Line number '+i])pop(k,name,i<2?0:.06+i*.047);
  });k.control('Code line 0','Play declaration');all.push(...k.finish());

  k=kit('stepsFlowDemo',1120,740,stepsTrackDuration);panel(k);
  k.rect('Running dot',64,60,16,16,green,8);
  k.text('Flow title','Running the play',92,60,34,navy,'Satoshi','Bold');
  k.rect('Flow divider',560,108,1096,2,[.9,.93,.96],0);
  tasks.forEach(([label,tool],i)=>{
    const y=178+i*101,start=.08+i*.15;
    k.rect('Task surface '+i,560,y,1008,86,pale,16);
    k.rect('Task icon tile '+i,99,y,52,52,[.87,.93,1],12);
    k.text('Task icon '+i,['#','✦','≈','↗','♡'][i],83,y,29,blue,'Satoshi','Bold');
    k.text('Task name '+i,label,145,y,31,navy,'Satoshi','Bold');
    k.text('Next '+i,'Next',938,y,26,muted);
    k.ex('Next '+i,'transform/opacity',`time<${start+.13}?100:0`);
    k.text('Done '+i,'✓ Done',910,y,27,green,'Satoshi','Bold');pop(k,'Done '+i,start+.13);
    k.text('Call '+i,tool,145,y+28,15,muted,'JetBrains Mono');
    k.ex('Call '+i,'transform/opacity','0'); // Tool names remain editable without crowding the website row.
  });k.text('Completion','All 5 steps checked.',58,692,25,green,'Satoshi','Bold');pop(k,'Completion',.92);
  k.control('Flow title');all.push(...k.finish());

  k=kit('stepsPlayDemo',1120,740,stepsTrackDuration);
  k.image('Code','stepsCodeDemo',560,370);
  k.image('Checked flow','stepsFlowDemo',560,370);
  k.cmd('layer.enableTimeRemap',{layers:['Checked flow'],value:true});
  k.ex('Checked flow','timeRemap','Math.max(0,time-.72)');
  k.set('Checked flow','transform/opacity',100);
  k.ex('Checked flow','transform/position','[560,370+800*(1-bk(.72,1.14)),0]');
  k.ex('Code','transform/scale','var p=Math.max(0,Math.min(1,(time-.70)/.42)),s=100*Math.max(0,1+1.8*p*p-2.8*p*p*p);[s,s,100]');
  k.cmd('essential.addProperty',{comp:'stepsPlayDemo',layer:'Checked flow',path:'transform/scale',name:'Flow size',as:'scale'});all.push(...k.finish());

  k=kit('stepsResultDemo',1120,740,stepsTrackDuration);panel(k);
  [['Who',60],['What log did',320],['Status',922]].forEach(([copy,x],i)=>k.text('Column '+i,copy,x,69,27,muted,'Satoshi','Bold'));
  k.rect('Table divider',560,115,1096,2,[.9,.93,.96],0);
  [['mila','answer about ads'],['deano','meme, shown inline'],['kai','answer about ads']].forEach(([who,what],i)=>{
    const y=215+i*133,start=.14+i*.21;
    k.rect('Row divider '+i,560,y+62,1008,2,[.93,.95,.97],0);
    k.text('Who '+i,who,60,y,37,navy,'Satoshi','Bold');
    k.text('What '+i,what,320,y,33,muted);
    k.rect('Status badge '+i,978,y,144,52,[.91,.97,.94],12);
    k.text('Sent '+i,'Sent',945,y,27,green,'Satoshi','Bold');
    group(k,'Result entrance '+i,['Who '+i,'What '+i,'Status badge '+i,'Sent '+i],560,y,start);
  });
  k.rect('Footer',560,645,1096,132,[.97,.98,.99],20);
  k.rect('Footer divider',560,579,1096,2,[.9,.93,.96],0);
  k.rect('Discord badge',341,645,72,72,blue,17);k.logo('discord',341,645,47,true);
  k.text('Landing','Landed on Discord',399,645,35,navy,'Satoshi','Bold');
  group(k,'Landed entrance',['Discord badge','Logo discord','Landing'],560,645,.88);
  k.control('Landing');all.push(...k.finish());

  const titles=['Ask your agent','log writes and runs the play','It lands on Discord'];
  const bodies=['The play: help people in\nyour Discord server.','5 steps, each one checked\nbefore the next.','Every message from your own\naccount, in your own voice.'];
  ['stepsAskDemo','stepsPlayDemo','stepsResultDemo'].forEach((demo,i)=>{
    k=kit('stepsCard'+(i+1),1200,1300,stepsTrackDuration);
    k.rect('Blue carrier edge',600,657,980,1220,[.102,.373,.784],36);
    k.rect('Blue carrier',600,645,980,1220,blue,36);
    k.cmd('effect.apply',{effect:'Gradient Ramp',layers:['Blue carrier']});
    k.set('Blue carrier','effects/#1/startColor',[.31,.65,1,1]);k.set('Blue carrier','effects/#1/endColor',[.122,.471,.941,1]);
    k.set('Blue carrier','effects/#1/start',[600,0]);k.set('Blue carrier','effects/#1/end',[600,1290]);
    k.image('Website demo',demo,600,443);
    k.cmd('layer.enableTimeRemap',{layers:['Website demo'],value:true});
    k.ex('Website demo','timeRemap',`Math.max(0,time-${i===0?.32:.47})`);
    k.text('Step number','Step '+(i+1),165,911,108,white,'Satoshi','Black');
    k.text('Step title',titles[i],165,1033,i===1?48:54,white,'Satoshi','Bold');
    k.text('Step description',bodies[i],165,1148,37,[.90,.96,1]);
    ['Step number','Step title','Step description'].forEach((n,j)=>{pop(k,n,.10+j*.07);k.control(n);});
    all.push(...k.finish());
  });
  k=kit('stepsTrackParts',1200,1300,stepsTrackDuration);k.image('Three-step preview','stepsCard1',600,650);
  k.cmd('essential.addProperty',{comp:'stepsTrackParts',layer:'Three-step preview',path:'transform/scale',name:'Card size',as:'scale'});
  all.push(...k.finish());return all;
}

export const stepsTrackStops=[
  {source:'stepsCard1',center:[360,540,0],arrival:.70,reveal:0},
  {source:'stepsCard2',center:[2160,540,-2800],arrival:3.70,reveal:2.85},
  {source:'stepsCard3',center:[360,540,-5600],arrival:6.70,reveal:5.85},
];
// The physical dolly retreats every frame. Native lens pushes provide the requested
// longer close approaches without reversing travel along the outward Z track.
export const outwardZExpression='-2300-110*time-3700*ramp5(2,3.65)-3700*ramp5(5.1,6.65)-800*ramp5(8.15,9)';
// time, look XYZ, magnification, orbit XY, roll. Deliberately wide horizontal swings.
export const stepsTrackCameraPoses=[
  [0,180,540,0,.42,-200,-55,-2.5],
  [.70,380,540,0,.69,120,-25,1.3],
  [1.55,440,540,0,.79,190,-20,2],
  [1.95,400,540,0,.83,100,-30,1.3],
  [2.43,520,540,-550,.30,-120,-100,-1.2],
  [2.92,1540,540,-1950,.33,-260,-110,-3.2],
  [3.50,2260,540,-2770,.63,-110,-50,-1.2],
  [4.22,2230,540,-2800,.76,100,-20,1.2],
  [4.82,2110,540,-2800,.83,-100,-30,-1.4],
  [5.36,2040,540,-3170,.30,120,-100,1.2],
  [5.95,960,540,-4620,.34,260,-110,3.2],
  [6.52,260,540,-5570,.63,110,-50,1.2],
  [7.25,290,540,-5600,.76,-100,-20,-1.2],
  [7.92,440,540,-5600,.83,100,-30,1.4],
  [8.30,350,540,-5610,.56,20,-65,.5],
  [9,-470,540,-5800,.24,-300,-105,-3],
];

// Solve a natural cubic at authoring time. Its native polynomial pieces share
// velocity AND acceleration, avoiding the sharp little lens/roll reversals.
export function stepsCameraSegments(){
  const p=stepsTrackCameraPoses,n=p.length,h=p.slice(1).map((v,i)=>v[0]-p[i][0]);
  const channels=[];
  for(let j=1;j<p[0].length;j++){
    const a=Array(n).fill(0),b=Array(n).fill(0),c=Array(n).fill(0),d=Array(n).fill(0);
    b[0]=b[n-1]=1;
    for(let i=1;i<n-1;i++){
      a[i]=h[i-1];b[i]=2*(h[i-1]+h[i]);c[i]=h[i];
      d[i]=6*((p[i+1][j]-p[i][j])/h[i]-(p[i][j]-p[i-1][j])/h[i-1]);
    }
    for(let i=1;i<n;i++){const q=a[i]/b[i-1];b[i]-=q*c[i-1];d[i]-=q*d[i-1];}
    const m=Array(n).fill(0);m[n-1]=d[n-1]/b[n-1];
    for(let i=n-2;i>=0;i--)m[i]=(d[i]-c[i]*m[i+1])/b[i];
    channels.push(h.map((dt,i)=>[p[i][j],(p[i+1][j]-p[i][j])/dt-dt*(2*m[i]+m[i+1])/6,m[i]/2,(m[i+1]-m[i])/(6*dt)]));
  }
  return h.map((dt,i)=>[p[i][0],dt,channels.map(v=>v[i])]);
}
const cameraMath='function ramp5(a,b){var p=Math.max(0,Math.min(1,(time-a)/(b-a)));return p*p*p*(10+p*(-15+6*p));}function cameraSample(t,k){var i=0;while(i<k.length-1&&t>k[i][0]+k[i][1])i++;var s=Math.max(0,Math.min(k[i][1],t-k[i][0])),out=[];for(var j=0;j<k[i][2].length;j++){var c=k[i][2][j];out.push(c[0]+s*(c[1]+s*(c[2]+s*c[3])));}return out;}';

export function stepsFlowRefinementSteps(){
  const k=kit('stepsPlayDemo',1120,740,stepsTrackDuration);k.steps.length=0;
  k.cmd('comp.open',{comp:'stepsPlayDemo'});
  k.ex('Checked flow','transform/opacity','100');
  k.ex('Checked flow','transform/position','[560,370+800*(1-bk(.72,1.14)),0]');
  k.ex('Code','transform/scale','var p=Math.max(0,Math.min(1,(time-.70)/.42)),s=100*Math.max(0,1+1.8*p*p-2.8*p*p*p);[s,s,100]');
  return k.steps;
}

export function stepsTrackSceneSteps(){
  const k=stage('logThreeStepsTrack',stepsTrackDuration),{cmd,set,ex}=k;
  k.steps.unshift({command:'effect.plugins.load',params:{folder:'C:/Users/0/AppData/Roaming/EffectCraft/Plug-ins'}});
  cmd('layer.setSwitch',{layers:['Studio gradient'],switch:'video',value:false});
  k.image('Built dither background','ditherGradientBackground',960,540);
  k.three('Built dither background');
  cmd('essential.set',{layer:'Built dither background',control:'Wipe',value:61});
  cmd('essential.set',{layer:'Built dither background',control:'Pixel Size',value:5});
  ex('Built dither background','essential/eg149','61+4*Math.sin(time*.32)');
  // A real world-space backdrop behind the entire track. Overscan covers the
  // widest camera swing; the smaller source cells preserve readable dithering.
  ex('Built dither background','transform/scale','[3000,3000,100]');
  ex('Built dither background','transform/position','[1150+450*Math.sin(time*.20),540+180*Math.sin(time*.24),6500]');
  cmd('layer.enableTimeRemap',{layers:['Built dither background'],value:true});
  ex('Built dither background','timeRemap','Math.min(time*.45,4.9)');
  cmd('layer.timing',{layers:['Built dither background'],in:0,out:stepsTrackDuration});
  cmd('layer.arrange',{layers:['Built dither background'],to:'back'});
  stepsTrackStops.forEach((stop,i)=>{
    const n='Step '+(i+1)+' · complete card';k.plane(n,stop.source,stop.center,null,92);
    set(n,'transform/anchor',[600,650,0]);set(n,'transform/orientation',[0,i===1?-3:3,0]);
    const next=stepsTrackStops[i+1];
    const exit=next?next.arrival-.18:8.15;
    const popScale=`var u=Math.max(0,time-${stop.arrival-.36}),base=92-52*Math.exp(-4.4*u)*(Math.cos(8.7*u)+4.4/8.7*Math.sin(8.7*u)),s=base*(time<=${stop.reveal}?0:bk(${stop.reveal},${stop.reveal+.28})),strain=(base-92)/92,p=Math.max(0,Math.min(1,(time-${exit})/.68));s*=Math.max(0,1+1.8*p*p-2.8*p*p*p);`;
    ex(n,'transform/scale',popScale+'[s*(1-.06*strain),s*(1+.06*strain),100]');
    ex(n,'transform/rotation',`var u=Math.max(0,time-${stop.arrival-.36});${i===1?1:-1}*.8*Math.exp(-4.4*u)*Math.sin(8.7*u)`);
    ex(n,'transform/opacity','100');
    cmd('layer.enableTimeRemap',{layers:[n],value:true});
    ex(n,'timeRemap',`Math.max(0,time-${stop.reveal})`);
  });
  stepsTrackStops.slice(0,-1).forEach((stop,i)=>{
    const next=stepsTrackStops[i+1],a=stop.center,b=next.center,way=Math.sign(b[0]-a[0]);
    const start=[a[0]+440*way,680,a[2]+90],end=[b[0]-440*way,680,b[2]+90];
    // Reveal only once the camera has retreated behind the complete connection;
    // drawing a world-space stroke through the camera's near plane causes a flare.
    const dx=end[0]-start[0],dz=end[2]-start[2],len=Math.hypot(dx,dz),n='Step handoff '+(i+1),begin=next.reveal;
    cmd('layer.newShape',{kind:'none',name:n});
    cmd('shape.newPath',{layer:n,vertices:[[0,0],[len*.28,-120],[len*.72,-120],[len,0]],inTangents:[[0,0],[-len*.12,0],[-len*.12,0],[-len*.12,0]],outTangents:[[len*.12,0],[len*.12,0],[len*.12,0],[0,0]],space:'layer',fill:false,stroke:blue,strokeWidth:7});
    k.three(n);set(n,'transform/position',start);set(n,'transform/rotationY',-Math.atan2(dz,dx)*180/Math.PI);
    set(n,'contents/group/contents/stroke/cap',1);cmd('layer.addShapeItem',{layer:n,kind:'trim'});
    ex(n,'contents/trim/end',`100*sm(${begin},${next.arrival-.04})`);
    ex(n,'contents/trim/start',`100*sm(${next.arrival+.10},${next.arrival+.65})`);
    ex(n,'transform/opacity',`time<${begin}||time>${next.arrival+.65}?0:100`);
  });
  const clock=cameraMath+`var v=cameraSample(time,${JSON.stringify(stepsCameraSegments())}),z=${outwardZExpression};`;
  k.cam(clock+'[v[0]+v[4],v[1]+v[5],z]',clock+'[v[0],v[1],v[2]]',clock+'v[6]');
  ex('3D Camera','cameraOptions/zoom',clock+'Math.max(100,(v[2]-z)*v[3])');
  cmd('essential.addProperty',{comp:'logThreeStepsTrack',layer:'3D Camera',path:'cameraOptions/zoom',name:'Track framing'});
  return k.finish();
}
