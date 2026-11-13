import {readFileSync} from 'node:fs';
import {textEntranceSteps,pagePushSteps} from './iCanDo.mjs';
const {platforms}=JSON.parse(readFileSync(new URL('./platforms.json',import.meta.url),'utf8'));
export function websitesSceneSteps(){
  const steps=[];
  const set=(layer,path,value)=>steps.push({command:'prop.set',params:{layer,path,value}});
  const expr=(layer,path,expression)=>steps.push({command:'prop.setExpression',params:{layer,path,expression}});
  const asset=file=>new URL('./assets/'+file,import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1');
  steps.push({command:'file.import',params:{paths:[asset('strawberry-background.svg')]}});
  steps.push({command:'layer.addItem',params:{item:'strawberry-background.svg',position:[960,540]}});
  steps.push({command:'layer.rename',params:{layer:'strawberry-background.svg',name:'Strawberry dotted background'}});
  const lines=[['headline','Log lets Hermes',74,370],['bridge','work natively on',100,495],['highlight','your favourite socials.',104,635]];
  lines.forEach(([name,text,size,y],i)=>{
    const sticker=name==='highlight';
    steps.push({command:'layer.newText',params:{name,text,font:sticker?'Schoolbell':'Satoshi',style:sticker?'Regular':'Black',size,fill:sticker?[.165,.549,1]:[.051,.165,.298],justify:'left',position:[475,y],...(sticker?{stroke:[1,1,1],applyStroke:true,strokeWidth:10,strokeOverFill:false}:{})}});
    expr(name,'transform/anchor','var r=sourceRectAtTime(1.6,false);[r.left,r.top+r.height/2,0]');
    steps.push(...textEntranceSteps(name,.1+i*.14,.45));
    const out=`var q=Math.max(0,Math.min(1,(time-(thisComp.duration-0.85+${i*.1}))/.42));var leave=2.8*q*q*q-1.8*q*q;`;
    expr(name,'transform/position',out+`var p=Math.max(0,Math.min(1,(time-${.1+i*.14})/.45)),u=p-1,enter=1+2.8*u*u*u+1.8*u*u;[475,${y}-100*(1-enter)+1000*leave,0]`);
    expr(name,'transform/scale',`var p=Math.max(0,Math.min(1,(time-${.1+i*.14})/.45));var u=p-1;var s=100*(1+2.8*u*u*u+1.8*u*u);[s,s,100]`);
    if(sticker){
      steps.push({command:'layer.style.stroke',params:{layers:[name]}});
      set(name,'layerStyles/stroke/color',[.051,.165,.298,1]);
      set(name,'layerStyles/stroke/size',3);
      steps.push({command:'layer.style.outerGlow',params:{layers:[name]}});
      set(name,'layerStyles/outerGlow/blendMode',0);
      set(name,'layerStyles/outerGlow/color',[.165,.549,1,1]);
      set(name,'layerStyles/outerGlow/opacity',25);
      set(name,'layerStyles/outerGlow/size',16);
      set(name,'transform/rotation',-2);
    }
    steps.push({command:'essential.addProperty',params:{comp:'type11',layer:name,path:'text/sourceText',name:text}});
  });
  // Fixed scattered edge positions: repeatable, airy, and clear of the central headline.
  const positions=[
    [90,90],[285,185],[75,310],[280,405],[105,535],[285,650],[80,765],[265,875],[100,1015],
    [1830,110],[1635,205],[1845,320],[1640,415],[1815,545],[1635,655],[1840,775],[1655,885],[1820,1010],
    [490,100],[700,240],[930,75],[1150,220],[1380,90],[1460,265],
    [480,860],[700,1000],[940,830],[1160,985],[1390,850],[1530,1010],
  ];
  positions.forEach(([x,y],i)=>{
    const p=platforms[i%platforms.length],file=p.id+'.svg',icon=`surround ${i+1} ${p.label}`,card=`logo card ${i+1}`;
    const size=[72,84,64,80,76][i%5],start=.1+((i*11)%positions.length)*.025;
    const tilt=[-6,4,-3,7,0][i%5];
    steps.push({command:'layer.newShape',params:{kind:'rounded',name:card,size:[size+40,size+40],fill:[.92,.96,1],position:[x,y]}});
    set(card,'contents/group/contents/rect/roundness',22);
    // Gentle breathing starts after entrance; each card/logo pair shares its own phase.
    const scale=(delay,base,isIcon=false)=>`var p=Math.max(0,Math.min(1,(time-${delay})/.4));var u=p-1;var t=Math.max(0,time-${start+.47});var breath=1+0.06*Math.sin(2*Math.PI*t/2.4+${(i%7)*.55})*Math.min(t/.4,1);var q=Math.max(0,Math.min(1,(time-(thisComp.duration-.85+${((i*11)%positions.length)*.012+(isIcon?0:.04)}))/.4));var leave=2.8*q*q*q-1.8*q*q;var s=${base}*(1+2.8*u*u*u+1.8*u*u)*breath*(1-leave);[s,s,100]`;
    expr(card,'transform/scale',scale(start,100));
    set(card,'transform/rotation',tilt);
    steps.push({command:'file.import',params:{paths:[asset('platforms/'+file)]}});
    steps.push({command:'layer.addItem',params:{item:file,position:[x,y]}});
    steps.push({command:'layer.rename',params:{layer:file,name:icon}});
    steps.push({command:'layer.setSwitch',params:{layers:[icon],switch:'collapse',value:true}});
    set(icon,'transform/rotation',tilt);
    expr(icon,'transform/scale',scale(start+2/30,size/104*100,true));
  });
  steps.push(...pagePushSteps());
  return steps;
}
