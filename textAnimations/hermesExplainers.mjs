import {pagePushSteps,textEntranceSteps} from './iCanDo.mjs';
export const explainerNames=['askHermes','socialActions','yourControl'];
const navy=[13/255,42/255,76/255],blue=[42/255,140/255,1],pale=[.9,.95,1];
export function explainerSteps(comp){
  const steps=[{command:'comp.new',params:{name:comp,width:1920,height:1080,frameRate:30,duration:4.2,background:'#FFFEFC',open:true}}];
  const set=(layer,path,value)=>steps.push({command:'prop.set',params:{layer,path,value}});
  const expr=(layer,path,expression)=>steps.push({command:'prop.setExpression',params:{layer,path,expression}});
  const pop=(start)=>`var p=Math.max(0,Math.min(1,(time-${start})/.45));var u=p-1;var q=Math.max(0,Math.min(1,(time-(thisComp.duration-.22))/.2));var s=100*(1+2.8*u*u*u+1.8*u*u)*(1-q*q*(3-2*q));[s,s,100]`;
  const rect=(name,x,y,w,h,colour,start)=>{steps.push({command:'layer.newShape',params:{kind:'rounded',name,size:[w,h],fill:colour,position:[x,y]}});set(name,'contents/group/contents/rect/roundness',24);expr(name,'transform/scale',pop(start));};
  const text=(name,copy,x,y,size,start,sticker=false)=>{
    steps.push({command:'layer.newText',params:{name,text:copy,font:sticker?'Schoolbell':'Satoshi',style:sticker?'Regular':'Black',size,fill:sticker?blue:navy,position:[x,y],justify:'center',...(sticker?{stroke:[1,1,1],applyStroke:true,strokeWidth:16,strokeOverFill:false}:{})}});
    expr(name,'transform/anchor','var r=sourceRectAtTime(2,false);[r.left+r.width/2,r.top+r.height/2,0]');
    steps.push(...textEntranceSteps(name,start,.45));
    expr(name,'transform/scale',pop(start));
    if(sticker){
      steps.push({command:'layer.style.stroke',params:{layers:[name]}});set(name,'layerStyles/stroke/color',[...navy,1]);set(name,'layerStyles/stroke/size',5);
      steps.push({command:'layer.style.outerGlow',params:{layers:[name]}});set(name,'layerStyles/outerGlow/color',[...blue,1]);set(name,'layerStyles/outerGlow/opacity',45);set(name,'layerStyles/outerGlow/size',24);set(name,'transform/rotation',-2);
    }
    steps.push({command:'essential.addProperty',params:{comp,layer:name,path:'text/sourceText',name:copy}});
  };
  steps.push({command:'file.import',params:{paths:[new URL('./assets/strawberry-background.svg',import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1')]}});
  steps.push({command:'layer.addItem',params:{item:'strawberry-background.svg',position:[960,540]}});
  text('step',comp==='askHermes'?'01 / ASK':comp==='socialActions'?'02 / ACT':'03 / STAY IN CONTROL',960,170,38,.1);
  if(comp==='askHermes'){
    text('headline','Tell Hermes',960,365,118,.16);
    text('highlight','what you need.',960,520,146,.3,true);
    rect('prompt card',960,760,1420,154,pale,.38);
    text('prompt','Read my DMs. Who needs a reply?',960,760,62,.52);
  }else if(comp==='socialActions'){
    text('headline','One agent.',960,330,104,.14);
    ['Read','Reply','Post'].forEach((word,i)=>{rect('action card '+i,450+i*510,555,460,240,pale,.24+i*.13);text('action '+i,word,450+i*510,555,134,.34+i*.13,true);});
    text('subtext','Across your connected accounts.',960,790,60,.72);
  }else{
    text('accounts','Your accounts.',960,340,114,.14);
    text('voice','Your voice.',960,515,156,.28,true);
    text('control','Your call.',960,700,118,.42);
    rect('approval line',960,845,980,6,blue,.5);
    text('approval','Nothing sends until you approve.',960,905,45,.62);
  }
  steps.push(...pagePushSteps(),{command:'essential.setName',params:{comp,name:comp}},{command:'comp.close',params:{comp}});
  return steps;
}
export function blueSweepSteps(){
  const comp='blueSweep',steps=[{command:'comp.new',params:{name:comp,width:1920,height:1080,frameRate:30,duration:.8,open:true}}];
  // Transparent except for the moving panels; the main brand-blue panel covers the cut.
  [[-180,[13/255,42/255,76/255]],[0,[.69,.84,1]],[190,blue]].forEach(([offset,fill],i)=>{
    const name='sweep '+i;
    steps.push({command:'layer.newShape',params:{kind:'rounded',name,size:[2680,1800],fill,position:[-2100,540]}});
    steps.push({command:'prop.set',params:{layer:name,path:'transform/rotation',value:-9}});
    steps.push({command:'prop.setExpression',params:{layer:name,path:'transform/position',expression:`function smooth(p){p=Math.max(0,Math.min(1,p));return p*p*(3-2*p);}var x=time<.32?-2100+3060*smooth(time/.32):960+3400*smooth((time-.32)/.48);[x+${offset},540,0]`}});
  });
  steps.push({command:'essential.addProperty',params:{comp,layer:'sweep 2',path:'contents/group/contents/fill/color',name:'Sweep colour'}},{command:'essential.setName',params:{comp,name:'Blue diagonal sweep'}},{command:'comp.close',params:{comp}});return steps;
}
