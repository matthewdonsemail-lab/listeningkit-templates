// Native editable platform reel, with the slide/hold motion from the reference.
import {readFileSync,writeFileSync} from 'node:fs';
const {platforms}=JSON.parse(readFileSync(new URL('./platforms.json',import.meta.url),'utf8'));
export const platformCues=[0.17,0.58,0.96,1.21,1.46,1.79,2.04];
export function textEntranceSteps(layer,start,duration){
  const path='text/animators/animator';
  const back='function back(p){p=Math.max(0,Math.min(1,p));var u=p-1;return 1+2.8*u*u*u+1.8*u*u;}';
  return [
    {command:'layer.addTextAnimator',params:{layer,properties:['scale'],name:'Typewriter overshoot'}},
    {command:'layer.addTextSelector',params:{layer,animator:1,kind:'expression'}},
    {command:'prop.set',params:{layer,path:path+'/properties/scale',value:[0,0,100]}},
    {command:'prop.set',params:{layer,path:'text/moreOptions/anchorGrouping',value:0}},
    {command:'prop.set',params:{layer,path:'text/moreOptions/groupingAlignment',value:[0,-50]}},
    {command:'prop.setExpression',params:{layer,path:path+'/selectors/expressionSelector/amount',expression:back+`var pop=${duration*.55}; var gap=textTotal>1?${duration*.45}/(textTotal-1):0; var s=back((time-${start}-(textIndex-1)*gap)/pop); [100*(1-s),100*(1-s),0]`}},
    {command:'prop.setExpression',params:{layer,path:'transform/scale',expression:back+`var s=100*back((time-${start})/${duration});[s,s,100]`}},
  ];
}
export function pagePushSteps(){
  const layer='Page push in';
  const progress='var p=Math.max(0,Math.min(1,time/thisComp.duration));';
  return [
    {command:'layer.newAdjustment',params:{name:layer}},
    {command:'effect.apply',params:{effect:'ec.distort.transform',layers:[layer]}},
    {command:'prop.set',params:{layer,path:'effects/#1/anchor',value:[960,540]}},
    {command:'prop.set',params:{layer,path:'effects/#1/position',value:[960,540]}},
    {command:'prop.setExpression',params:{layer,path:'effects/#1/scaleHeight',expression:progress+'100+8*p'}},
    {command:'prop.setExpression',params:{layer,path:'effects/#1/rotation',expression:progress+'-1.2*p'}},
    {command:'layer.arrange',params:{layers:[layer],to:'front'}},
  ];
}
export function iCanDoSteps() {
  const steps = [];
  // The reference has a clean warm-white centre and faint blue/peach dot fields at the edges.
  const dots=new Map();
  for(let y=0;y<=1080;y+=24) for(let x=0;x<=1920;x+=24){
    const fields=[[0,0,420,350,'#BBD9E9'],[150,1080,500,350,'#E9CFC8'],[1920,0,470,340,'#E9CFC8'],[1920,1080,420,300,'#BBD9E9']];
    for(const [cx,cy,sx,sy,fill] of fields){
      const a=.24*Math.exp(-((x-cx)**2/(2*sx*sx)+(y-cy)**2/(2*sy*sy)));
      if(a>.012){
        const key=fill+':'+(Math.round(a*50)/50).toFixed(2);
        dots.set(key,(dots.get(key)||'')+`M${x-3.5},${y}a3.5,3.5 0 1,0 7,0a3.5,3.5 0 1,0 -7,0z`);
      }
    }
  }
  const paths=[...dots].map(([key,d])=>{const [fill,opacity]=key.split(':');return `<path fill="${fill}" opacity="${opacity}" d="${d}"/>`;}).join('');
  writeFileSync(new URL('./assets/strawberry-background.svg',import.meta.url),`<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><rect width="1920" height="1080" fill="#FFFEFC"/>${paths}</svg>\n`);
  steps.push({command:'file.import',params:{paths:[new URL('./assets/strawberry-background.svg',import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1')]}});
  steps.push({command:'layer.addItem',params:{item:'strawberry-background.svg',position:[960,540]}});
  steps.push({command:'layer.rename',params:{layer:'strawberry-background.svg',name:'Strawberry dotted background'}});
  const set = (layer, path, value) => steps.push({command:'prop.set',params:{layer,path,value}});
  const expr = (layer, path, expression) => steps.push({command:'prop.setExpression',params:{layer,path,expression}});
  const addText = (name,text,size,fill,font='Satoshi') => {
    steps.push({command:'layer.newText',params:{name,text,font,style:font==='Satoshi'?'Black':'Regular',size,fill,position:[0,0],justify:'left'}});
    expr(name,'transform/anchor','var r=sourceRectAtTime(thisComp.duration-thisComp.frameDuration,false); [r.left,r.top+r.height/2,0]');
  };
  // Local zero is source 26.5 s. Each target is a measured resting frame.
  const cues = platformCues;
  const clock = `function smooth(a,b,t){var p=Math.max(0,Math.min(1,(t-a)/(b-a)));return p*p*(3-2*p);} var row=0; var cues=${JSON.stringify(cues)}; for(var k=1;k<cues.length;k++) row+=smooth(cues[k]-0.125,cues[k],time); var enter=1-smooth(0,0.17,time); var exit=smooth(2.21,2.38,time);`;
  addText('heading','Hermes now\nworks on',90,[13/255,42/255,76/255]);
  // Word-based position animator: top entrance, then a downward exit with anticipation.
  steps.push({command:'layer.addTextAnimator',params:{layer:'heading',properties:['position'],name:'Staggered word slide'}});
  steps.push({command:'layer.addTextSelector',params:{layer:'heading',animator:1,kind:'expression'}});
  set('heading','text/animators/animator/properties/position',[0,-800,0]);
  set('heading','text/animators/animator/selectors/expressionSelector/basedOn',2);
  expr('heading','text/animators/animator/selectors/expressionSelector/amount',
    'function clamp(p){return Math.max(0,Math.min(1,p));} function backOut(p){var u=clamp(p)-1;return 1+2.8*u*u*u+1.8*u*u;} function backIn(p){p=clamp(p);return 2.8*p*p*p-1.8*p*p;} var delay=(textIndex-1)*0.1; var enter=backOut((time-delay)/0.38); var exit=backIn((time-2.2-delay)/0.32); var amount=100*(1-enter-exit); [amount,amount,amount]');
  expr('heading','transform/anchor','var r=sourceRectAtTime(1,false);[r.left,r.top+r.height/2,0]');
  set('heading','transform/position',[250,540,0]);
  steps.push({command:'essential.addProperty',params:{comp:'type04',layer:'heading',path:'text/sourceText',name:'Heading'}});
  platforms.forEach(({id,label:word},i)=>{
    // Two frames between container, logo and label at the project's 30 fps.
    const cardStart=Math.max(0,cues[i]-0.35);
    const logoStart=cardStart+2/30;
    const textStart=cardStart+4/30;
    const scaleIn=(start,duration)=>`var p=Math.max(0,Math.min(1,(time-${start})/${duration}));var u=p-1;var s=100*(1+2.8*u*u*u+1.8*u*u);[s,s,100]`;
    const colour=[42/255,140/255,1];
    const label=`${word} label`, pill=`${word} pill`, glyph=`${word} icon`;
    const y=clock+`var y=540+(${i}-row)*230+enter*230-exit*700;`;
    const opacity=y+'var d=Math.abs(y-540)/230; 100*Math.max(0,1-d/2.35)*(1-exit)';
    const pale=[201/255,227/255,1];
    steps.push({command:'layer.newShape',params:{kind:'rounded',name:pill,size:[600,204],fill:pale,position:[0,0]}});
    set(pill,'contents/group/contents/rect/roundness',24);
    // Measure the settled label, then include its animated scale and glyph bounds.
    // Never measure at t=0: the typewriter has hidden the text at that instant.
    const bounds=`var l=thisComp.layer("${label}"); var r=l.sourceRectAtTime(thisComp.duration-thisComp.frameDuration,false); var a=l.sourceRectAtTime(time,false); var s=l.transform.scale[0]/100; var w=194+Math.max(r.width,a.width*s+12); var h=Math.max(204,a.height*s+48);`;
    expr(pill,'contents/group/contents/rect/size',bounds+'[w,h]');
    expr(pill,'transform/position',y+bounds+'[870+w/2,y,0]');
    expr(pill,'transform/opacity',opacity);
    expr(pill,'transform/scale',scaleIn(cardStart,0.24));
    addText(label,word,148,colour);
    steps.push(...textEntranceSteps(label,textStart,0.25));
    expr(label,'transform/position',y+'[1024,y,0]');
    expr(label,'transform/opacity',opacity);
    const file=`${id}.svg`;
    steps.push({command:'file.import',params:{paths:[new URL(`./assets/platforms/${file}`,import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1')]}});
    steps.push({command:'layer.addItem',params:{item:file,position:[956,540]}});
    steps.push({command:'layer.rename',params:{layer:file,name:glyph}});
    steps.push({command:'layer.setSwitch',params:{layers:[glyph],switch:'collapse',value:true}});
    expr(glyph,'transform/position',y+'[946,y,0]');
    expr(glyph,'transform/opacity',opacity);
    expr(glyph,'transform/scale',scaleIn(logoStart,0.25));
    steps.push({command:'essential.addProperty',params:{comp:'type04',layer:label,path:'text/sourceText',name:word}});
  });
  steps.push(...pagePushSteps());
  return steps;
}
