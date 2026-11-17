import {fileURLToPath} from 'node:url';
import {readFileSync} from 'node:fs';
import {kit,stage} from './startCardMotion.mjs';

const blue=[.165,.549,1],navy=[.051,.165,.298],muted=[.36,.46,.58],paper=[.94,.97,1];
const asset=n=>fileURLToPath(new URL('./assets/research/'+n,import.meta.url)).replaceAll('\\','/');
export const researchPartNames=['researchTerminal','researchSources','researchDecision','researchShortlist'];
export const researchDuration=8;

function header(k,logo,subtitle){
  k.rect('Panel edge',700,559,1280,754,[.73,.85,.99],26);
  k.rect('Panel surface',700,550,1280,750,[1,1,1],26,[.8,.88,.98]);
  k.image('Service logo',logo,123,235,logo==='subq.svg'?112.5:10.546875);
  k.cmd('effect.apply',{effect:'Tint',layers:['Service logo']});
  k.set('Service logo','effects/#1/black',[...blue,1]);k.set('Service logo','effects/#1/white',logo==='treg.svg'?[1,1,1,1]:[...blue,1]);
  k.text('Service title',subtitle,178,233,38,navy,'Satoshi','Bold');
  k.rect('Header divider',700,291,1190,2,[.86,.91,.97],0);
  k.text('Demo provenance','Illustrative data · adapted from the Treg motion study',106,885,21,muted);
  k.control('Service title');
}
function row(k,i,y,build){
  const names=[];
  const rect=(...args)=>{names.push(args[0]);return k.rect(...args);};
  const text=(...args)=>{names.push(args[0]);return k.text(...args);};
  build(rect,text);
  const n='Row '+i+' motion';k.cmd('layer.newNull',{name:n});k.set(n,'transform/position',[700,y,0]);
  for(const name of names)k.cmd('layer.setParent',{layers:[name],parent:n,compensate:true});
  k.ex(n,'transform/scale',`var s=86+14*bk(${.18+i*.12},${.5+i*.12});[s,s,100]`);
  k.ex(n,'transform/opacity',`time<${.18+i*.12}?0:100`);
  k.ex(n,'transform/position',`[700,${y}+28*(1-bk(${.18+i*.12},${.5+i*.12})),0]`);
}
export function hermesAgentTerminalSteps(){
  const k=kit('hermesAgentTerminal',1400,1000,researchDuration);
  const logo=fileURLToPath(new URL('./assets/startCards/hermesAgent.png',import.meta.url)).replaceAll('\\','/');
  k.cmd('file.import',{paths:[logo]});
  k.rect('Terminal shell',700,550,1280,750,[.063,.094,.126],25,[.25,.34,.44]);
  k.rect('Terminal chrome',700,209,1276,64,[.09,.137,.18],24);
  k.rect('Chrome seam',700,240,1275,2,[.21,.29,.37],0);
  k.image('Hermes mark','hermesAgent.png',120,207,65);
  k.text('Agent title','Hermes Agent',164,207,32,[.94,.97,1],'Satoshi','Bold');
  k.text('Workspace','log / research',1030,207,24,[.58,.69,.8],'JetBrains Mono');
  k.rect('Prompt surface',700,344,1170,128,[.09,.16,.23],18,[.18,.33,.48]);
  k.text('Prompt','› Find growth leaders at Series A startups\n  in San Francisco.',140,342,33,[.83,.93,1],'JetBrains Mono');
  k.ex('Prompt','text/sourceText','var s=String(value);s.slice(0,Math.floor(s.length*sm(.08,.58)))');
  k.rect('Tool surface',700,559,1170,224,[.075,.12,.165],18,[.18,.27,.35]);
  k.text('Tool','● treg · catalog_search',141,485,32,[.42,.71,1],'JetBrains Mono');
  k.text('Tool arguments','people search · company context · source signals',168,539,27,[.58,.71,.83],'JetBrains Mono');
  k.text('Tool result','✓ Source context collected',168,610,32,[.52,.89,.77],'JetBrains Mono');
  k.text('Next tool','SubQ · compare against the target profile',141,729,29,[.76,.86,.96],'JetBrains Mono');
  k.rect('Session state',700,825,1170,72,[.10,.22,.34],16);
  k.text('Reply','Context attached. Ready to review.',141,825,32,[.58,.8,1],'JetBrains Mono');
  for(const [names,start]of [[['Tool surface','Tool','Tool arguments'],.43],[['Tool result'],.68],[['Next tool','Session state','Reply'],.88]])
    for(const n of names){k.ex(n,'transform/opacity',`time<${start}?0:100`);k.ex(n,'transform/position',`var v=value;[v[0],v[1]+22*(1-bk(${start},${start+.24})),0]`);}
  for(const n of ['Prompt','Tool','Tool result','Next tool','Reply'])k.control(n);
  return k.finish();
}
export function researchPartsSteps(){
  const all=[{command:'file.import',params:{paths:['treg.svg','subq.svg','hunter.png','prospeo.png','crustdata.png'].map(asset)}}];
  let k=kit('researchTerminal',1400,1000,researchDuration);
  k.image('Hermes terminal','hermesAgentTerminal',700,500);
  k.cmd('layer.enableTimeRemap',{layers:['Hermes terminal'],value:true});
  k.ex('Hermes terminal','timeRemap','Math.min(time*1.3,7.95)');
  k.cmd('essential.addProperty',{comp:'researchTerminal',layer:'Hermes terminal',path:'transform/scale',name:'Terminal size',as:'scale'});all.push(...k.finish());

  k=kit('researchSources',1400,1000,researchDuration);header(k,'treg.svg','People search · source results');
  ['hunter','prospeo','crustdata'].forEach((v,i)=>{
    const x=275+i*420,w=readFileSync(asset(v+'.png')).readUInt32BE(16);k.rect('Provider '+i,x,348,380,70,paper,15);k.image('Provider logo '+i,v+'.png',x-145,348,44/w*100);
    k.text('Provider name '+i,['Hunter','Prospeo','Crustdata'][i],x-104,348,28,navy,'Satoshi','Bold');
  });
  const leads=[['Mira Chen','Head of Growth','Hiring a growth team'],['Alex Kim','VP Growth','Launching a product'],['Ravi Shah','Head of Growth','Expanding outbound'],['Leah Park','Growth Lead','Building a growth team']];
  leads.forEach(([name,role,signal],i)=>{const y=460+i*105;row(k,i,y,(rect,text)=>{
    rect('Result '+i,700,y,1190,90,i%2?paper:[.975,.985,1],13);
    text('Name '+i,name,133,y,32,navy,'Satoshi','Bold');text('Role '+i,role,435,y,29,muted);text('Signal '+i,signal,820,y,28,blue);
  });});all.push(...k.finish());

  k=kit('researchDecision',1400,1000,researchDuration);header(k,'subq.svg','Read the context. Keep the matches.');
  k.rect('Rule surface',700,350,1190,72,paper,15);k.text('Matching rule','Growth role + Series A + San Francisco',133,350,32,blue,'Satoshi','Bold');
  leads.forEach(([name,role,signal],i)=>{const y=460+i*105,keep=i!==1;row(k,i,y,(rect,text)=>{
    rect('Decision '+i,700,y,1190,90,keep?[.9,.95,1]:[.97,.975,.98],13);
    text('Candidate '+i,name,133,y,32,navy,'Satoshi','Bold');text('Evidence '+i,keep?signal:'Outside the target stage',435,y,28,muted);
    text('Match '+i,keep?'✓ Match':'— Skip',1080,y,30,keep?blue:muted,'Satoshi','Bold');
  });});
  k.rect('Scan line',700,415,1180,3,blue,1);k.ex('Scan line','transform/position','[700,415+395*sm(.2,1.1),0]');
  k.ex('Scan line','transform/opacity','time<1.18?55:0');all.push(...k.finish());

  k=kit('researchShortlist',1400,1000,researchDuration);header(k,'treg.svg','Your shortlist · with the reasons attached');
  [leads[0],leads[2],leads[3]].forEach(([name,role,signal],i)=>{const y=420+i*136;row(k,i,y,(rect,text)=>{
    rect('Shortlist '+i,700,y,1190,114,paper,16);text('Shortlisted name '+i,name,143,y-20,34,navy,'Satoshi','Bold');
    text('Shortlisted context '+i,role+' · '+signal,143,y+26,26,muted);rect('Ready badge '+i,1190,y,150,48,blue,12);text('Ready '+i,'Ready',1146,y,27,[1,1,1],'Satoshi','Bold');
  });});
  k.rect('Next step',700,820,1190,64,blue,16);k.text('Next step label','Keep the source. Let Hermes take the next step.',143,820,31,[1,1,1],'Satoshi','Bold');
  all.push(...k.finish());
  k=kit('researchParts',1400,1000,researchDuration);k.image('Research component preview','researchSources',700,500);
  k.cmd('essential.addProperty',{comp:'researchParts',layer:'Research component preview',path:'transform/scale',name:'Panel size',as:'scale'});
  all.push(...k.finish());return all;
}

export function brandBlueGradientSteps(){
  const k=kit('brandBlueGradient',1920,1080,12);
  k.cmd('layer.newSolid',{name:'Brand blue',color:'#2A8CFF',width:1920,height:1080});
  k.cmd('effect.apply',{effect:'Gradient Ramp',layers:['Brand blue']});
  k.set('Brand blue','effects/#1/startColor',[.37,.69,1,1]);k.set('Brand blue','effects/#1/endColor',[.07,.34,.82,1]);
  k.ex('Brand blue','effects/#1/start','[400+130*Math.sin(time*.22),-150]');
  k.ex('Brand blue','effects/#1/end','[1350+100*Math.sin(time*.18),1280]');
  for(const [path,name]of [['startColor','Light blue'],['endColor','Deep blue']])
    k.cmd('essential.addProperty',{comp:'brandBlueGradient',layer:'Brand blue',path:'effects/#1/'+path,name});
  return k.finish();
}

export const researchCameraStops=[
  {center:[960,540,0],arrival:.5,depart:1.25},
  {center:[2740,140,850],arrival:2.25,depart:3.25},
  {center:[1280,1640,-380],arrival:4.25,depart:5.25},
  {center:[3380,1150,1100],arrival:6.25,depart:7.5},
];

// Time-aware Hermite tangents keep velocity continuous across the authored poses.
// A pose stores time, look target XYZ, focal distance, orbit XY and roll.
const spline=`function sample(t,k){if(t<=k[0][0])return k[0].slice(1);if(t>=k[k.length-1][0])return k[k.length-1].slice(1);var i=0;while(i<k.length-2&&t>k[i+1][0])i++;var a=k[i],b=k[i+1],l=k[Math.max(0,i-1)],r=k[Math.min(k.length-1,i+2)],dt=b[0]-a[0],p=(t-a[0])/dt,p2=p*p,p3=p2*p,out=[];for(var j=1;j<a.length;j++){var m0=.65*(b[j]-l[j])/(b[0]-l[0]),m1=.65*(r[j]-a[j])/(r[0]-a[0]);out.push((2*p3-3*p2+1)*a[j]+(p3-2*p2+p)*dt*m0+(-2*p3+3*p2)*b[j]+(p3-p2)*dt*m1);}return out;}`;
export {spline as motionSplineExpression};
export const researchFocusScale=[[-.32,70],[-.16,89],[.025,108],[.16,89],[.31,94],[.48,92]];

export function researchCameraPoses(){
  const poses=[],add=(time,c,d,ox,oy,roll)=>poses.push([time,...c,d,ox,oy,roll]);
  const at=(c,v,s)=>c.map((x,j)=>x+v[j]*s);
  add(0,[920,560,-15],2580,-65,-50,-1.1);
  researchCameraStops.forEach((stop,i)=>{
    const c=stop.center,previous=researchCameraStops[Math.max(0,i-1)].center;
    const incoming=i?c.map((v,j)=>v-previous[j]):researchCameraStops[1].center.map((v,j)=>v-c[j]);
    const dir=Math.sign(incoming[0])||1,a=stop.arrival;
    add(a-.25,at(c,incoming,-.012),2380,-40*dir,-60,-.8*dir);
    add(a,at(c,incoming,.024),2080,70*dir,-25,1.8*dir);
    add(a+.14,at(c,incoming,-.012),2280,-20*dir,-45,-.9*dir);
    add(a+.32,at(c,incoming,.006),2140,25*dir,-35,.45*dir);
    if(i<3){
      const next=researchCameraStops[i+1].center,v=next.map((x,j)=>x-c[j]),way=Math.sign(v[0])||1,d=stop.depart;
      add(d-.22,at(c,v,-.035),2050,-80*way,-28,-1.6*way);
      add(d,at(c,v,.025),2650,20*way,-85,.7*way);
      const wide=at(c,v,.24);wide[1]-=110*way;
      add(d+.30,wide,3620,120*way,-105,2.3*way);
      const push=at(c,v,.66);push[1]-=75*way;
      add(d+.56,push,3270,90*way,-70,1.7*way);
    }else{
      add(7.2,at(c,incoming,.012),2090,90,-15,1.25);
      add(7.5,[c[0]+160,c[1]-75,c[2]],2450,120,-55,2.2);
      add(8,[c[0]+490,c[1]-190,c[2]+200],3220,160,-80,3);
    }
  });
  return poses.sort((a,b)=>a[0]-b[0]);
}

export function researchDepthSteps(){
  const k=stage('logResearchDepth',researchDuration),{cmd,set,ex,plane,cam}=k;
  cmd('layer.setSwitch',{layers:['Studio gradient'],switch:'video',value:false});
  cmd('layer.addItem',{item:'brandBlueGradient',position:[960,540]});cmd('layer.rename',{layer:'brandBlueGradient',name:'Brand blue background'});
  cmd('layer.arrange',{layers:['Brand blue background'],to:'back'});
  const arrivals=researchCameraStops.map(s=>s.arrival);
  researchPartNames.forEach((source,i)=>{
    const n=['Ask in the terminal','Treg source context','SubQ decision','Hermes shortlist'][i],arrival=arrivals[i];
    plane(n,source,researchCameraStops[i].center,null,92);set(n,'transform/orientation',[0,i%2?-4:4,i%2?1:-1]);
    set(n,'transform/anchor',[700,550,0]);
    // Every focus uses the same 70 → 108 → 89 → 94 → 92 spring.
    const pop=spline+`var s=sample(time-${arrival},${JSON.stringify(researchFocusScale)})[0]*bk(${i*.045},${.28+i*.045}),strain=(s-92)/92;`;
    ex(n,'transform/scale',pop+'[s*(1-.12*strain),s*(1+.12*strain),100]');
    ex(n,'transform/orientation',`var a=time-${arrival},j=a<0?0:Math.exp(-a*7)*Math.sin(a*20);[0,${i%2?-4:4}+2.5*j,${i%2?1:-1}+1.2*j]`);
    cmd('layer.enableTimeRemap',{layers:[n],value:true});ex(n,'timeRemap',`Math.max(0,(time-${Math.max(0,arrival-.4)})*1.7)`);
    cmd('layer.timing',{layers:[n],in:0,out:researchDuration});
    ex(n,'transform/opacity',i===3?'100':`100*(1-sm(${arrivals[i+1]+.15},${arrivals[i+1]+.45}))`);
  });
  researchCameraStops.slice(0,-1).forEach((stop,i)=>{
    const a=stop.center,next=researchCameraStops[i+1],b=next.center,way=Math.sign(b[0]-a[0])||1;
    const start=[a[0]+380*way,a[1]+80,a[2]+180],end=[b[0]-380*way,b[1]+80,b[2]+180];
    const dx=end[0]-start[0],dz=end[2]-start[2],dy=end[1]-start[1],length=Math.hypot(dx,dz),begin=stop.depart-.18;
    const n='White connection '+(i+1)+' draw';cmd('layer.newShape',{kind:'none',name:n});
    cmd('shape.newPath',{layer:n,vertices:[[0,0],[length*.25,dy*.15-80*way],[length*.75,dy*.85-80*way],[length,dy]],inTangents:[[0,0],[-length*.12,0],[-length*.12,0],[-length*.12,0]],outTangents:[[length*.12,0],[length*.12,0],[length*.12,0],[0,0]],space:'layer',fill:false,stroke:[1,1,1],strokeWidth:5});
    k.three(n);set(n,'transform/position',start);set(n,'transform/rotationY',-Math.atan2(dz,dx)*180/Math.PI);
    set(n,'contents/group/contents/stroke/cap',1);cmd('layer.addShapeItem',{layer:n,kind:'trim'});
    ex(n,'contents/trim/end',`100*sm(${begin},${next.arrival-.04})`);
    ex(n,'contents/trim/start',`100*sm(${next.arrival+.10},${next.arrival+.64})`);
    ex(n,'transform/opacity',`time<${begin}||time>${next.arrival+.64}?0:88`);
  });
  const clock=spline+`var v=sample(time,${JSON.stringify(researchCameraPoses())});`;
  cam(clock+'[v[0]+v[4],v[1]+v[5],v[2]-v[3]]',clock+'[v[0],v[1],v[2]]',clock+'v[6]');
  cmd('essential.addProperty',{comp:'logResearchDepth',layer:'3D Camera',path:'cameraOptions/zoom',name:'Depth framing'});
  return k.finish();
}
