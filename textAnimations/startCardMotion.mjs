import {fileURLToPath} from 'node:url';

const blue=[42/255,140/255,1],navy=[13/255,42/255,76/255],white=[1,1,1],dark=[16/255,24/255,32/255],chrome=[23/255,35/255,46/255];
export const startMotionNames=['logAgentDemo','logInboxDemo','logReplyDemo','logListeningDemo'];
export const startPartNames=['startCardParts','startClient','startPrompt','startTools','startPromptDiscord','startToolsDiscord','startPromptSlack','startToolsSlack','startTongueX','startTongueDiscord','startTongueSlack','startReply','startVoice','startHermes',...['x','facebook','discord','slack','instagram','reddit','linkedin'].map(p=>'startTile'+p),...['X','Discord','Slack','Reply'].flatMap(p=>['startClientContent'+p,'startClientReveal'+p,'startPlay'+p])];
const asset=p=>fileURLToPath(new URL('./assets/'+p,import.meta.url)).replaceAll('\\','/');
const math='function sm(a,b){var p=Math.max(0,Math.min(1,(time-a)/(b-a)));return p*p*(3-2*p);}function bk(a,b){var p=Math.max(0,Math.min(1,(time-a)/(b-a))),u=p-1;return 1+2.8*u*u*u+1.8*u*u;}';

export function kit(comp,w=1920,h=1080,duration=12){
  const steps=[],cmd=(command,params)=>steps.push({command,params});
  const set=(layer,path,value)=>cmd('prop.set',{layer,path,value});
  const ex=(layer,path,expression)=>cmd('prop.setExpression',{layer,path,expression:math+expression});
  const rect=(name,x,y,rw,rh,fill=white,r=20,stroke=null)=>{cmd('layer.newShape',{kind:'rounded',name,size:[rw,rh],fill,position:[x,y],...(stroke?{stroke,strokeWidth:1.5}:{})});set(name,'contents/group/contents/rect/roundness',r);return name;};
  const text=(name,copy,x,y,size=28,fill=white,font='Satoshi',style='Medium')=>{cmd('layer.newText',{name,text:copy,font,style:font==='Schoolbell'?'Regular':style,size,fill,position:[x,y],justify:'left'});ex(name,'transform/anchor','var r=sourceRectAtTime(thisComp.duration,false);[r.left,r.top+r.height/2,0]');return name;};
  const control=(name,label=name)=>cmd('essential.addProperty',{comp,layer:name,path:'text/sourceText',name:label});
  const soft=(name,amount=14,size=32)=>{cmd('layer.style.dropShadow',{layers:[name]});set(name,'layerStyles/dropShadow/color',[...navy,1]);set(name,'layerStyles/dropShadow/opacity',amount);set(name,'layerStyles/dropShadow/distance',8);set(name,'layerStyles/dropShadow/size',size);};
  const image=(name,item,x,y,scale=100)=>{cmd('layer.addItem',{item,position:[x,y]});cmd('layer.rename',{layer:item,name});set(name,'transform/scale',[scale,scale,100]);return name;};
  const logo=(p,x,y,size=60,light=false)=>{const n='Logo '+p;image(n,p+'.svg',x,y,size/104*100);if(light){cmd('effect.apply',{effect:'Tint',layers:[n]});set(n,'effects/#1/black',[1,1,1,1]);set(n,'effects/#1/white',[1,1,1,1]);}return n;};
  const finish=()=>{cmd('essential.setName',{comp,name:comp});cmd('comp.close',{comp});return steps;};
  cmd('comp.new',{name:comp,width:w,height:h,frameRate:30,duration,open:true});
  return {steps,cmd,set,ex,rect,text,control,soft,image,logo,finish};
}

export function startPartsSteps(){
  const all=[{command:'file.import',params:{paths:[asset('startCards/hermesAgent.png'),asset('startCards/hermes.svg'),...['x','facebook','discord','slack','instagram','reddit','linkedin'].map(p=>asset('platforms/'+p+'.svg'))]}}];
  let k=kit('startClient',1040,640),{rect,text,image}=k;
  rect('Client frame',520,320,1000,592,dark,18,[.31,.38,.46]);
  rect('Client chrome',520,58,996,64,chrome,17);rect('Chrome seam',520,90,996,2,[.22,.29,.36],0);
  image('Hermes logo','hermesAgent.png',68,58,65);text('Client name','Hermes Agent',104,58,25,white,'Satoshi','Bold');text('Client demo label','log workspace',808,58,20,[.61,.7,.78]);
  rect('Composer',520,555,920,62,[.09,.13,.17],16,[.22,.28,.34]);text('Composer text','›  Ask anything…',83,555,24,[.53,.62,.7]);rect('Composer send',937,555,38,38,[.28,.36,.45],19);text('Composer arrow','↑',926,554,28);
  k.control('Client name');all.push(...k.finish());

  const sessions=[['','Who is waiting for a reply?','X inbox / conversation context','twitterDms','waiting: true','6 conversations waiting on you'],['Discord','Catch up on my Discord mentions.','Discord / channel context','search','mentions: you','3 conversations need a reply'],['Slack','Which Slack conversations need me?','Slack / conversation context','slackChats','workspace: growth-co','14 DMs · 3 group conversations']];
  for(const [suffix,prompt,guide,call,args,result]of sessions){
  k=kit('startPrompt'+suffix,940,130);k.rect('Prompt',470,65,920,110,[.12,.2,.28],17,[.21,.32,.43]);k.text('Prompt text','›  '+prompt,37,65,33,[.72,.88,1]);k.control('Prompt text');all.push(...k.finish());
  k=kit('startTools'+suffix,940,290);
  [['getGuide',guide,'Instructions ready'],[call,args,result]].forEach(([tool,args,result],i)=>{
    const y=77+i*138;k.rect('Tool '+i,470,y,920,126,[.09,.14,.19],14,[.25,.31,.37]);k.text('Tool name '+i,'log · '+tool,31,y-29,25,[.89,.94,1],'Satoshi','Bold');k.text('Tool args '+i,args,415,y-29,22,[.53,.65,.75]);k.text('Tool result '+i,'✓  '+result,31,y+26,27,[.52,.89,.77]);
  });k.control('Tool result 1');all.push(...k.finish());
  }

  const tongues=[['X','x','Reply guy on X','Catch up on DMs and mentions.\nThoughtful replies, in your voice.'],['Discord','discord','Inbox catch-up on Discord','Find unanswered DMs and mentions.\nGet relevant replies ready.'],['Slack','slack','Answer the queue on Slack','See which conversations need you.\nClear replies, with the full context.']];
  for(const [label,p,title,copy]of tongues){
    k=kit('startTongue'+label,1080,270);
    k.rect('Blue card edge',540,142,1040,226,[.1,.375,.784],21);
    k.rect('Blue play card',540,134,1040,226,blue,21);k.cmd('effect.apply',{effect:'Gradient Ramp',layers:['Blue play card']});
    k.set('Blue play card','effects/#1/startColor',[.31,.65,1,1]);k.set('Blue play card','effects/#1/endColor',[.12,.47,.94,1]);k.set('Blue play card','effects/#1/start',[540,20]);k.set('Blue play card','effects/#1/end',[540,250]);
    k.logo(p,85,88,62,true);k.text('Play title',title,140,86,p==='slack'?41:46,white,'Schoolbell');
    k.text('Play description',copy,52,169,29,white);k.rect('Copy button',960,86,108,48,white,12);k.text('Copy label','Copy',932,86,24,navy,'Satoshi','Bold');
    k.control('Play title');k.control('Play description');all.push(...k.finish());
  }
  k=kit('startReply',900,220);k.rect('Reply bubble',450,110,860,178,white,25,[.76,.85,.95]);k.soft('Reply bubble',10,28);k.text('Reply author','HERMES DRAFT',47,58,20,blue,'Satoshi','Bold');k.text('Reply text','Building Log — Hermes can work\nacross my social accounts.',47,123,35,navy);k.control('Reply text');all.push(...k.finish());
  k=kit('startVoice',650,150);k.rect('Voice card',325,75,620,120,white,20,[.73,.86,1]);k.text('Voice title','Your voice',36,52,31,navy,'Schoolbell');k.rect('Voice rail',324,111,568,6,[.83,.91,1],3);k.rect('Voice fill',324,111,568,6,blue,3);k.text('Voice result','✓  Ready for review',298,52,25,blue,'Satoshi','Bold');k.control('Voice result');all.push(...k.finish());
  k=kit('startHermes',350,390);k.rect('Hermes tile edge',175,192,300,300,[.78,.88,.98],40);k.rect('Hermes tile',175,184,300,300,white,40);k.image('Hermes logo','hermes.svg',175,161,750);k.text('Hermes tile label','Hermes',105,287,35,navy,'Schoolbell');k.control('Hermes tile label');all.push(...k.finish());
  for(const p of ['x','facebook','discord','slack','instagram','reddit','linkedin']){
    k=kit('startTile'+p,250,290);k.rect('Tile edge',125,128,212,212,[.75,.86,.97],32);k.rect('Tile face',125,121,212,212,white,32);k.logo(p,125,117,112);k.text('Platform name',p==='x'?'Twitter/X':p[0].toUpperCase()+p.slice(1),35,254,24,navy,'Satoshi','Bold');k.control('Platform name');all.push(...k.finish());
  }
  for(const platform of ['X','Discord','Slack','Reply']){
    const suffix=platform==='X'||platform==='Reply'?'':platform;
    k=kit('startClientContent'+platform,1040,640);
    k.image('Client frame','startClient',520,320);
    k.image('Prompt','startPrompt'+suffix,520,169);
    k.image('Tools','startTools'+suffix,520,389);
    if(platform==='Reply'){
      k.image('Reply','startReply',520,380,94);k.ex('Reply','transform/opacity','100*sm(2.5,2.8)');
      k.image('Voice review','startVoice',520,495,90);k.ex('Voice review','transform/opacity','100*sm(3.7,4)');
    }
    all.push(...k.finish());
    k=kit('startClientReveal'+platform,1200,1080);
    k.image('Sliding client','startClientContent'+platform,600,440);
    k.ex('Sliding client','transform/position','var p=Math.max(0,Math.min(1,(time-.5))),u=p-1;var s=1+1.65*u*u*u+.65*u*u;[600,440+650*(1-s),0]');
    all.push(...k.finish());
    k=kit('startPlay'+platform,1200,1080);
    k.image('Hero Client','startClientReveal'+platform,600,540);
    k.cmd('layer.addMask',{layer:'Hero Client',shape:'rect',rect:[40,0,1120,744],mode:'Add'});
    k.image('Tongue','startTongue'+(platform==='Reply'?'X':platform),600,827);
    k.ex('Tongue','transform/scale','var s=100*bk(0,.42);[s,s,100]');
    k.ex('Tongue','transform/opacity','time<=0?0:100');
    k.cmd('essential.addProperty',{comp:'startPlay'+platform,layer:'Tongue',path:'transform/scale',name:'Tongue scale'});
    all.push(...k.finish());
  }
  k=kit('startCardParts',1200,1080);k.image('Complete 2D card','startPlayX',600,540);k.text('Parts label','/start · editable 2D component',120,1020,35,navy,'Schoolbell');k.control('Parts label');all.push(...k.finish());
  return all;
}

export function stage(name,duration){
  const k=kit(name,1920,1080,duration),{cmd,set,ex,rect,text}=k;
  cmd('comp.settings',{comp:name,renderer:'classic3D',shutterAngle:150,motionBlurSamples:8});
  cmd('layer.newSolid',{name:'Studio gradient',color:'#EFF6FF',width:1920,height:1080});cmd('effect.apply',{effect:'Gradient Ramp',layers:['Studio gradient']});
  set('Studio gradient','effects/#1/startColor',[.985,.99,1,1]);set('Studio gradient','effects/#1/endColor',[.7,.84,1,1]);set('Studio gradient','effects/#1/start',[960,150]);set('Studio gradient','effects/#1/end',[960,1400]);
  cmd('layer.newCamera',{name:'3D Camera',type:'twoNode',angleOfView:50,position:[960,470,-2200],poi:[960,520,0]});
  const three=n=>{cmd('layer.setSwitch',{layers:[n],switch:'threeD',value:true});cmd('layer.setSwitch',{layers:[n],switch:'motionBlur',value:true});};
  function rig(n,pos,rotation=[0,0,0],scale=100){cmd('layer.newNull',{name:n});three(n);set(n,'transform/anchor',[0,0,0]);set(n,'transform/position',pos);set(n,'transform/orientation',rotation);set(n,'transform/scale',[scale,scale,scale]);return n;}
  function plane(n,source,pos,parent=null,scale=100){cmd('layer.addItem',{item:source,position:[pos[0],pos[1]]});cmd('layer.rename',{layer:source,name:n});three(n);set(n,'transform/position',pos);set(n,'transform/scale',[scale,scale,scale]);if(parent)cmd('layer.setParent',{layers:[n],parent,compensate:false});return n;}
  function rise(n,start,span=.45,depth=320){ex(n,'transform/position',`var p=bk(${start},${start+span});var v=value;[v[0],v[1]+80*(1-p),v[2]+${depth}*(1-p)]`);ex(n,'transform/opacity',`time<${start}?0:100`);}
  function stack(n,p,platform='X',scale=100,rot=[0,0,0],delay=0){
    plane(n,'startPlay'+platform,p,null,scale);
    set(n,'transform/orientation',rot);
    if(delay)cmd('layer.timing',{layers:[n],start:delay,in:delay,out:duration});
    return n;
  }
  function cam(position,poi,roll='0'){ex('3D Camera','transform/position',position);ex('3D Camera','transform/poi',poi);ex('3D Camera','transform/rotation',roll);}
  const caption=(copy)=>{text('Motion caption',copy,96,95,39,navy,'Schoolbell');k.control('Motion caption');};
  return {...k,three,rig,plane,rise,stack,cam,caption};
}

export function startSceneSteps(name){
  const duration={logAgentDemo:7.2,logInboxDemo:8,logReplyDemo:9,logListeningDemo:8.4}[name];
  const k=stage(name,duration),{ex,set,plane,rig,stack,cam,caption,rise}=k;
  if(name==='logAgentDemo'){
    caption('Your agent. Connected to your world.');
    stack('Hero',[960,510,0],'X',93,[0,-8,-2]);
    ex('Hero','transform/rotationY','-6+10*sm(1,5.8)');
    ex('Hero','transform/position','[960-1250*sm(6.65,7.2),510,100*sm(6.65,7.2)]');
    cam('var p=sm(0,6.6);[1410-710*p,300+220*p,-2300+260*p]','[960,525,20]','-2+3*sm(0,6.6)');
  }
  if(name==='logInboxDemo'){
    caption('The same Hermes. Every platform.');
    stack('X stack',[130,550,330],'X',73,[2,20,-7],0);
    stack('Discord stack',[960,520,-60],'Discord',84,[-2,-4,0],.12);
    stack('Slack stack',[1790,550,300],'Slack',73,[2,-20,7],.24);
    ex('X stack','transform/position','var p=sm(1.2,6.4);[130+60*p,550-20*p,330+90*p]');
    ex('Discord stack','transform/position','var p=sm(2,5);[960,520-30*p,-60-80*p]');
    ex('Slack stack','transform/position','var p=sm(1.2,6.4);[1790-60*p,550-20*p,300+90*p]');
    ex('Discord stack','transform/rotationY','-12+24*sm(.8,6.5)');
    cam('var p=sm(0,6.8),q=sm(6.8,8);[500+800*p-280*q,360+190*p,-2630+80*p+740*q]','var p=sm(0,6.8);[720+480*p-240*sm(6.8,8),520,70]','1.5-3*sm(0,6.8)');
  }
  if(name==='logReplyDemo'){
    caption('Context becomes a reply. In your voice.');
    stack('Hero reply',[960,500,30],'Reply',93,[0,-7,-2],0);
    cam('var p=sm(0,5.8),q=sm(5.8,9);[1360-670*p+280*q,300+310*p-100*q,-2290+380*p-390*q]','[960,520,10]','-2+3*sm(0,6)-1*sm(6,9)');
  }
  if(name==='logListeningDemo'){
    caption('One agent. Your favourite platforms.');
    ['X','Discord','Slack'].forEach((platform,i)=>{
      const n='Play '+platform,start=i*2.5;
      stack(n,[960,520,0],platform,92,[0,-8,0],start);
      ex(n,'transform/position',`var p=bk(${start},${start+.65}),q=sm(${start+2.4},${start+3.1});[960+1500*(1-p)-1500*q,520,100*(1-p)]`);
    });
    cam('var p=sm(0,7.6);[1180-410*p,400+140*p,-2280+150*p]','[960,530,20]','-1+2*sm(0,7.6)');
  }
  return k.finish();
}
