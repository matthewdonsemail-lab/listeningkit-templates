// Native EffectCraft UI primitives. Coordinates are composition pixels; no HTML screenshots.
export const C={navy:[.051,.165,.298],blue:[.165,.549,1],pale:[.937,.965,1],line:[.79,.88,.98],muted:[.37,.47,.59],white:[1,1,1],green:[.13,.56,.42]};
const path=name=>new URL('./assets/'+name,import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1');
export function sceneKit(comp,duration,caption){
  const steps=[],groups=[];
  const cmd=(command,params)=>steps.push({command,params});
  const set=(layer,path,value)=>cmd('prop.set',{layer,path,value});
  const expr=(layer,path,expression)=>cmd('prop.setExpression',{layer,path,expression});
  const parent=name=>{if(groups.length)cmd('layer.setParent',{layers:[name],parent:groups.at(-1),compensate:false});};
  const smooth='function sm(a,b){var p=Math.max(0,Math.min(1,(time-a)/(b-a)));return p*p*(3-2*p);}';
  const show=(name,start=0,end=duration)=>expr(name,'transform/opacity',`time>=${start}&&time<${end}?100:0`);
  function group(name,start=0,x=960,y=540,slide=30){
    cmd('layer.newNull',{name});set(name,'transform/anchor',[x,y,0]);set(name,'transform/position',[x,y,0]);parent(name);groups.push(name);
    expr(name,'transform/scale',`var p=Math.max(0,Math.min(1,(time-${start})/.5));var u=p-1;var s=100*(1+2.6*u*u*u+1.6*u*u);[s,s,100]`);
    expr(name,'transform/position',smooth+`[${x},${y}+${slide}*(1-sm(${start},${start+.5})),0]`);
    show(name,start);return name;
  }
  const end=()=>groups.pop();
  function rect(name,x,y,w,h,fill=C.white,r=20,stroke=null){
    cmd('layer.newShape',{kind:'rounded',name,size:[w,h],fill,position:[x,y],...(stroke?{stroke,strokeWidth:2}:{})});set(name,'contents/group/contents/rect/roundness',r);parent(name);return name;
  }
  function text(name,copy,x,y,size=28,fill=C.navy,font='Satoshi',style='Medium'){
    cmd('layer.newText',{name,text:copy,font,style:font==='Schoolbell'?'Regular':style,size,fill,position:[x,y],justify:'left'});
    expr(name,'transform/anchor','var r=sourceRectAtTime(0,false);[r.left,r.top+r.height/2,0]');parent(name);return name;
  }
  function typed(name,copy,x,y,size,start,span,fill=C.navy){text(name,copy,x,y,size,fill);expr(name,'text/sourceText',`var s=value;if(s.text!==undefined)s=s.text;s=String(s);s.slice(0,Math.floor(s.length*Math.max(0,Math.min(1,(time-${start})/${span}))))`);cmd('essential.addProperty',{comp,layer:name,path:'text/sourceText',name});return name;}
  function badge(name,copy,x,y,w,fill=C.pale,ink=C.blue,start=0){group(name+' group',start,x+w/2,y,12);rect(name+' background',x+w/2,y,w,40,fill,12);text(name,copy,x+13,y,21,ink,'Satoshi','Bold');end();}
  function icon(name,file,x,y,size=32){cmd('file.import',{paths:[path('platforms/'+file+'.svg')]});cmd('layer.addItem',{item:file+'.svg',position:[x,y]});cmd('layer.rename',{layer:file+'.svg',name});set(name,'transform/scale',[size/104*100,size/104*100,100]);parent(name);return name;}
  function cursor(start,from,to,click){
    cmd('layer.newShape',{kind:'none',name:'Cursor',position:from});
    cmd('shape.newPath',{layer:'Cursor',vertices:[[0,0],[0,38],[10,29],[18,46],[27,42],[19,26],[33,26]],closed:true,fill:C.white,stroke:C.navy,strokeWidth:3});
    expr('Cursor','transform/position',smooth+`var p=sm(${start},${click});[${from[0]}+${to[0]-from[0]}*p,${from[1]}+${to[1]-from[1]}*p,0]`);
    expr('Cursor','transform/scale',smooth+`var s=100-20*(sm(${click},${click+.09})-sm(${click+.09},${click+.24}));[s,s,100]`);show('Cursor',start,click+.8);parent('Cursor');
    rect('Click ring',to[0],to[1],58,58,C.pale,29,C.blue);expr('Click ring','transform/scale',smooth+`var s=40+130*sm(${click},${click+.45});[s,s,100]`);expr('Click ring','transform/opacity',smooth+`100*(sm(${click},${click+.04})-sm(${click+.04},${click+.45}))`);
  }
  cmd('comp.new',{name:comp,width:1920,height:1080,frameRate:30,duration,background:'#FFFEFC',open:true});
  cmd('file.import',{paths:[path('strawberry-background.svg')]});cmd('layer.addItem',{item:'strawberry-background.svg',position:[960,540]});
  group('Demo page',0,960,540,60);
  if(comp!=='logAgentDemo'){
    expr('Demo page','transform/scale','[100,100,100]');
    expr('Demo page','transform/position',comp==='logListeningDemo'?smooth+'[960,540+900*sm(8.05,8.4),0]':'[960,540,0]');
  }
  text('Scene caption',caption,156,125,54,C.blue,'Schoolbell');
  rect('Window shadow',972,570,1640,750,C.navy,30);
  rect('Window',960,554,1640,750,C.white,30,C.line);
  rect('Chrome',960,218,1636,74,C.pale,26);
  [0,1,2].forEach(i=>rect('Chrome dot '+i,177+i*23,218,11,11,i===0?C.blue:C.line,6));
  text('Window title','Hermes / Log',273,218,25,C.navy,'Satoshi','Bold');
  text('Connected','CONNECTED',1518,218,18,C.green,'Satoshi','Bold');
  return {steps,cmd,set,expr,show,smooth,group,end,rect,text,typed,badge,icon,cursor,path,finish(){
    while(groups.length)end();
    cmd('layer.newAdjustment',{name:'UI camera'});cmd('effect.apply',{effect:'ec.distort.transform',layers:['UI camera']});
    set('UI camera','effects/#1/anchor',[960,540]);set('UI camera','effects/#1/position',[960,540]);
    const offset={logAgentDemo:0,logInboxDemo:7.2,logReplyDemo:15.2,logListeningDemo:24.2}[comp];
    expr('UI camera','effects/#1/scaleHeight',`100+4*Math.max(0,Math.min(1,(${offset}+time)/32.6))`);
    expr('UI camera','effects/#1/rotation',`-.35*Math.max(0,Math.min(1,(${offset}+time)/32.6))`);
    cmd('essential.addProperty',{comp,layer:'Scene caption',path:'text/sourceText',name:'Caption'});
    cmd('essential.setName',{comp,name:comp});cmd('comp.close',{comp});return steps;
  }};
}
