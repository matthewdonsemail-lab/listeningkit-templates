import {fileURLToPath} from 'node:url';
import {kit} from './startCardMotion.mjs';

export const expositionNames=['expositionEars','expositionPremise','expositionPositioning','expositionStudy'];
const blue=[42/255,140/255,1],navy=[13/255,42/255,76/255];
const path=n=>fileURLToPath(new URL('./assets/exposition/'+n,import.meta.url)).replaceAll('\\','/');
const outro=(duration)=>`var m;try{m=thisComp.marker.key("out");}catch(e){m=null;}var a=m?m.time:${duration-.48},d=m&&m.duration>0?m.duration:.48,p=Math.max(0,Math.min(1,(time-a)/d)),s=100*Math.max(0,1+1.8*p*p-2.8*p*p*p);[s,s,100]`;

function cue(k,name,start,duration){
  k.cmd('layer.addMarker',{layers:[name],time:start,comment:'words'});
  k.cmd('markers.set',{layer:name,index:0,duration});
  k.cmd('layer.addTextAnimator',{layer:name,properties:['opacity'],name:'Spoken words'});
  k.cmd('layer.addTextSelector',{layer:name,animator:1,kind:'expression'});
  k.set(name,'text/animators/animator/properties/opacity',0);
  k.set(name,'text/animators/animator/selectors/expressionSelector/basedOn',2);
  k.ex(name,'text/animators/animator/selectors/expressionSelector/amount','var m=thisLayer.marker.key("words"),gap=textTotal>1?m.duration/(textTotal-1):0,a=time<m.time+(textIndex-1)*gap?100:0;[a,a,a]');
}
function line(k,name,copy,y,size,start,span,sticker=false){
  k.text(name,copy,310,y,size,sticker?blue:navy,sticker?'Schoolbell':'Satoshi','Black');
  // Fit settled text once. Word visibility never changes its layout or anchor.
  k.ex(name,'transform/scale','var r=sourceRectAtTime(thisComp.duration-.6,false),s=Math.min(100,1320/Math.max(1,r.width)*100);[s,s,100]');
  if(sticker){
    const textStep=k.steps.find(s=>s.command==='layer.newText'&&s.params.name===name);
    Object.assign(textStep.params,{stroke:[1,1,1],applyStroke:true,strokeWidth:8,strokeOverFill:false});
    k.cmd('layer.style.stroke',{layers:[name]});k.set(name,'layerStyles/stroke/color',[...navy,1]);k.set(name,'layerStyles/stroke/size',2.5);
    k.cmd('layer.style.outerGlow',{layers:[name]});k.set(name,'layerStyles/outerGlow/color',[...blue,1]);k.set(name,'layerStyles/outerGlow/opacity',20);k.set(name,'layerStyles/outerGlow/size',12);
    k.set(name,'transform/rotation',-1);
  }
  cue(k,name,start,span);k.control(name);
}

export function expositionSteps(name){
  if(name==='expositionEars'){
    const k=kit(name,1920,1080,5);
    k.cmd('file.import',{paths:Array.from({length:8},(_,i)=>path('ear'+(i+1)+'.webp'))});
    // Four anchored edge accents, with the other four source options in Assets.
    [[1,-35,270,88,-9],[3,1950,230,86,11],[5,10,920,78,8],[7,1920,930,86,-9]].forEach(([id,x,y,scale,rotation],i)=>{
      const n='Ear '+id;k.image(n,'ear'+id+'.webp',x,y,scale);
      k.ex(n,'transform/position',`[${x}+4*Math.sin(time*.5+${i}),${y}+6*Math.sin(time*.6+${i}),0]`);
      k.ex(n,'transform/rotation',`${rotation}+.7*Math.sin(time*.4+${i})`);
      k.ex(n,'transform/scale',`var s=${scale}*(1+.008*Math.sin(time*.5+${i}));[s,s,100]`);
    });
    k.cmd('essential.addProperty',{comp:name,layer:'Ear 1',path:'transform/position',name:'Upper left ear'});
    return k.finish();
  }
  if(name==='expositionStudy'){
    const k=kit(name,1920,1080,9);
    k.image('Premise','expositionPremise',960,540);k.cmd('layer.timing',{layers:['Premise'],in:0,out:5});
    k.image('Positioning','expositionPositioning',960,540);k.cmd('layer.timing',{layers:['Positioning'],start:5,in:5,out:9});
    k.cmd('comp.addMarker',{time:0,comment:'Premise · website copy / provisional narration timing'});
    k.cmd('comp.addMarker',{time:5,comment:'Positioning · full-screen read'});
    k.cmd('essential.addProperty',{comp:name,layer:'Premise',path:'transform/scale',name:'Premise size',as:'scale'});
    return k.finish();
  }
  const duration=name==='expositionPremise'?5:4,k=kit(name,1920,1080,duration);
  k.steps.unshift({command:'effect.plugins.load',params:{folder:'C:/Users/0/AppData/Roaming/EffectCraft/Plug-ins'}});
  k.image('Quiet dither','ditherGradientBackground',960,540,108);
  k.cmd('essential.set',{layer:'Quiet dither',control:'Wipe',value:88});
  k.ex('Quiet dither','essential/eg149','88+1.5*Math.sin(time*.4)');
  k.cmd('layer.enableTimeRemap',{layers:['Quiet dither'],value:true});k.ex('Quiet dither','timeRemap','Math.min(time*.5,4.9)');
  k.image('Ear frame','expositionEars',960,540);
  if(name==='expositionPremise'){
    line(k,'Premise subject','Your (potential) customers',326,108,.10,.48);
    line(k,'Premise situation','are moaning about something',486,108,.72,.60);
    line(k,'Premise context','on social media.',695,194,1.40,.45,true);
  }else{
    line(k,'Positioning lead','The best tool for',335,132,.10,.45);
    line(k,'Positioning category','social media',552,205,.66,.28,true);
    line(k,'Positioning finish','marketing.',756,205,1.10,0,true);
  }
  k.cmd('layer.newNull',{name:'Type block'});k.set('Type block','transform/position',[960,540,0]);
  for(const n of name==='expositionPremise'?['Premise subject','Premise situation','Premise context']:['Positioning lead','Positioning category','Positioning finish'])
    k.cmd('layer.setParent',{layers:[n],parent:'Type block',compensate:true});
  k.ex('Type block','transform/scale',outro(duration));k.ex('Ear frame','transform/scale',outro(duration));
  k.cmd('comp.addMarker',{time:duration-.48,comment:'out'});k.cmd('markers.set',{index:0,duration:.48});
  k.cmd('layer.newAdjustment',{name:'Quiet page push'});k.cmd('effect.apply',{effect:'ec.distort.transform',layers:['Quiet page push']});
  k.set('Quiet page push','effects/#1/anchor',[960,540]);k.set('Quiet page push','effects/#1/position',[960,540]);
  k.ex('Quiet page push','effects/#1/scaleHeight','100+2*time/thisComp.duration');
  k.ex('Quiet page push','effects/#1/rotation','-.2*time/thisComp.duration');
  return k.finish();
}
