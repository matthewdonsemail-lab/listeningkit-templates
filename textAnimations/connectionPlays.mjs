import {fileURLToPath} from 'node:url';
import {kit,stage} from './startCardMotion.mjs';

const blue=[.165,.549,1],navy=[.051,.165,.298],white=[1,1,1],ink=[.08,.09,.11],muted=[.38,.41,.45];
export const connectionPlatforms=['X','Slack','Discord','Instagram','Reddit','Facebook','LinkedIn'];
const icons={X:'x',Slack:'slack',Discord:'discord',Instagram:'instagram',Reddit:'reddit',Facebook:'facebook',LinkedIn:'linkedin'};
export const connectionPartNames=['connectionCardParts',...connectionPlatforms.flatMap(p=>['connectionPanel'+p,'connectionReveal'+p,'connectionTongue'+p,'connectionPlay'+p])];
const summaries={X:'Read DMs, post, reply and follow\nfrom your own account.',Slack:'Read channels and DMs, reply and react\nin your workspaces.',Discord:'Read servers and DMs. Reply, react\nand send in your own session.',Instagram:'Read DM threads, reply with text\nor a photo, and watch them live.',Reddit:'Read subreddits and posts.\nReply, vote and post from your account.',Facebook:'Groups, Marketplace and the seller inbox,\nin your own browser.',LinkedIn:'Read your LinkedIn session.\nKeep the context of your conversations.'};

export function connectionPartsSteps(){
  const all=[{command:'file.import',params:{paths:[...Object.values(icons).map(p=>fileURLToPath(new URL('./assets/platforms/'+p+'.svg',import.meta.url)).replaceAll('\\','/')),fileURLToPath(new URL('./assets/startCards/listingClearOut.webp',import.meta.url)).replaceAll('\\','/')]}}];
  for(const platform of connectionPlatforms){
    let k=kit('connectionPanel'+platform,1040,640),{rect,text,ex,set}=k;
    const ui=(n,s,x,y,size=26,color=ink,bold=false)=>text(n,s,x,y,size,color,'Segoe UI',bold?'Bold':'Regular');
    const avatar=(n,s,x,y,color=blue)=>{rect(n+' avatar',x,y,46,46,color,23);ui(n+' initial',s[0],x-12,y,23,white,true);};
    const tag=(n,s,x,y,w=178)=>{rect(n+' badge',x+w/2,y,w,32,blue,12);ui(n+' tag',s,x+10,y,17,white,true);};
    const visible=(n,t)=>ex(n,'transform/opacity',`100*sm(${t},${t+.25})`);
    rect('Platform shell',520,320,1000,592,white,18,[.84,.86,.88]);
    if(platform==='X'){
      ui('Messages','Messages',51,68,33,ink,true);k.logo('x',962,68,35);rect('Search',520,127,936,54,[.95,.96,.97],25);ui('Search text','Search Direct Messages',76,127,22,muted);
      [['Sarah Builds','@sarah_builds · 2m','how much for a full site?','Waiting on you'],['Tom','@tomgrowth · 1h','You: saw your post about cold email','Seen, no reply'],['Jay','@jaylocal · 3h','yeah let’s do thursday','Waiting on you']].forEach((r,i)=>{const y=225+i*108;avatar('Person '+i,r[0],76,y);ui('Name '+i,r[0],114,y-17,24,ink,true);ui('Handle '+i,r[1],350,y-17,20,muted);ui('Message '+i,r[2],114,y+21,24);tag('Status '+i,r[3],794,y,191);});
      rect('Composer',520,556,936,66,[.94,.95,.96],18);ui('Draft',"depends what you need, what's the site for?",73,556,26);tag('Dry','dry run',838,556,115);
    }else if(platform==='Slack'){
      rect('Slack sidebar',152,320,264,592,[.29,.082,.294],18);k.logo('slack',64,66,33,true);ui('Workspace','growth-co',94,66,27,white,true);ui('DM label','Direct messages',44,132,19,[.8,.75,.81],true);
      ['Priya','Tom, Jay','Sam'].forEach((s,i)=>{if(!i)rect('Selected DM',152,186,242,48,[.067,.392,.639],7);ui('DM '+i,'●  '+s,49,186+i*58,25,white);});
      avatar('Header person','Priya',332,66,[.878,.118,.353]);ui('Chat name','Priya',369,66,29,ink,true);tag('Live','watching live',821,66,175);rect('Header divider',650,111,720,2,[.85,.85,.85],0);
      ['did the outreach sheet work for you?','we got 9 calls booked off it this week'].forEach((s,i)=>{const y=208+i*137;avatar('Priya '+i,'Priya',333,y,[.878,.118,.353]);ui('Author '+i,'Priya',371,y-21,25,ink,true);ui('Time '+i,'4:12 PM',474,y-21,18,muted);ui('Text '+i,s,371,y+25,26);});
      rect('Slack draft',650,542,675,88,white,14,[.73,.73,.73]);ui('Slack draft text',"that's brilliant, what changed?",333,542,26);tag('Slack dry','dry run',852,542,114);
    }else if(platform==='Discord'){
      rect('Discord background',520,320,1000,592,[.192,.2,.22],18);rect('Server rail',72,320,104,592,[.118,.122,.133],18);k.logo('discord',72,74,48,true);rect('Growth server',72,162,62,62,blue,20);ui('Growth server initials','GM',49,162,24,white,true);
      ui('Channel','# marketing',156,68,30,white,true);tag('Watching','watching live',803,68,183);rect('Discord divider',570,111,900,2,[.12,.13,.14],0);
      [['mila','anyone tried the new ads manager?',[.96,.5,1]],['deano','yeah, cut our cost per lead in half',[.26,.71,.51]],['mila','send me the setup?',[.96,.5,1]]].forEach(([n,s,c],i)=>{const y=190+i*113;avatar('Discord user '+i,n,167,y,c);ui('Discord author '+i,n,204,y-18,24,c,true);ui('Discord time '+i,'Today at 4:13 PM',327,y-18,18,[.58,.61,.64]);ui('Discord text '+i,s,204,y+24,26,[.86,.87,.88]);});
      rect('Discord composer',570,549,840,65,[.22,.23,.25],14);ui('Discord draft',"+   here you go, it's three steps",174,549,26,[.86,.87,.88]);tag('Discord dry','dry run',836,549,120);
    }else if(platform==='Instagram'){
      avatar('Maya','maya',78,72,[.59,.18,.75]);ui('Maya name','maya.makes',119,58,27,ink,true);ui('Active','Active now',119,90,19,muted);k.logo('instagram',773,73,38);tag('Instagram live','watching live',821,73,175);rect('Instagram divider',520,120,998,2,[.86,.86,.86],0);
      rect('Incoming bubble',286,213,435,80,[.94,.94,.94],30);ui('Incoming copy','finally launched the shop',93,213,28);
      rect('Meme card',771,354,374,178,[.115,.11,.115],28);ui('Meme icon','▧',739,307,42,[.85,.85,.85]);ui('Meme text','A MEME THAT FITS\nTHE MOMENT',649,365,25,white,true);tag('Photo state','sent with photo',767,468,203);
      rect('Instagram composer',520,557,936,65,white,29,[.86,.86,.86]);ui('Instagram draft','massive, what are you selling first?',78,557,26);tag('Instagram dry','dry run',835,557,120);
    }else if(platform==='Reddit'){
      k.logo('reddit',70,67,42);ui('Reddit wordmark','reddit',106,67,32,ink,true);rect('Reddit search',611,67,495,48,[.92,.93,.94],24);ui('Reddit search text','Search Reddit',394,67,22,muted);
      [['r/marketing','What actually worked to get your\nfirst 100 customers?','↑  1.2k  ↓     348 comments'],['r/smallbusiness','Is anyone still getting leads\nfrom Facebook groups?','↑  412  ↓       97 comments']].forEach(([sub,body,stats],i)=>{const y=235+i*225;rect('Post '+i,520,y,932,203,[.98,.985,.99],17);ui('Subreddit '+i,sub+'  ·  5 hr. ago',74,y-67,22,muted,true);ui('Post title '+i,body,74,y-8,31,ink,true);ui('Post stats '+i,stats+'     Share',74,y+67,22,muted);});
    }else if(platform==='Facebook'){
      rect('Facebook surface',520,320,1000,592,[.94,.95,.96],18);k.logo('facebook',69,67,42);rect('Marketplace search',568,67,830,49,white,24);ui('Marketplace search text','Search Marketplace',178,67,24,muted);
      rect('Listing',520,232,936,202,white,15);k.image('Listing photograph','listingClearOut.webp',165,232,34);ui('Price','$80',279,175,34,ink,true);ui('Listing title','Same-day rubbish removal',279,224,29);ui('Location','Bethlehem, PA  ·  Active  ·  14 clicks',279,272,22,muted);
      rect('Facebook post',520,458,936,219,white,15);avatar('Dana','Dana',93,393,[.89,.25,.37]);ui('Dana name','Dana Miller  ›  Lehigh Valley Locals',133,382,25,ink,true);ui('Dana time','12m · Public',133,416,18,muted);ui('Facebook request','anyone know someone who can clear\na garage this week?',75,478,29);ui('Facebook actions','Like                     Comment                     Share',94,551,22,muted,true);
    }else{
      rect('LinkedIn surface',520,320,1000,592,[.957,.949,.933],18);k.logo('linkedin',69,66,42);rect('LinkedIn search',500,67,730,49,[.929,.953,.973],8);ui('LinkedIn search text','Search',155,67,24,muted);tag('Session','session saved',818,67,179);
      rect('LinkedIn profile',520,225,936,188,white,12,[.88,.875,.86]);rect('Profile cover',520,155,932,48,[.66,.74,.75],10);avatar('You','Your Name',93,224,[.04,.4,.76]);ui('Profile name','Your Name',136,217,28,ink,true);ui('Profile role','Growth marketer helping local businesses get found',136,262,24,muted);
      rect('LinkedIn post',520,462,936,239,white,12,[.88,.875,.86]);avatar('Priya Shah','Priya',92,390,[.56,.345,.286]);ui('Priya name','Priya Shah',132,379,25,ink,true);ui('Priya role','Head of Growth · 1h',132,411,20,muted);ui('LinkedIn post copy','We tested 4 outreach channels this quarter.\nHere is what booked meetings…',75,473,29);ui('LinkedIn actions','Like             Comment             Repost             Send',86,552,22,muted,true);
    }
    const draftLayer={Slack:'Slack draft text',Discord:'Discord draft',Instagram:'Instagram draft',X:'Draft'}[platform];
    if(draftLayer)ex(draftLayer,'text/sourceText','var s=value;if(s.text!==undefined)s=s.text;s=String(s);s.slice(0,Math.floor(s.length*sm(1.55,2.65)))');
    if(platform==='Instagram')for(const n of ['Meme card','Meme icon','Meme text','Photo state badge','Photo state tag'])visible(n,1.65);
    k.cmd('essential.addProperty',{comp:'connectionPanel'+platform,layer:'Platform shell',path:'contents/group/contents/fill/color',name:'Panel surface'});all.push(...k.finish());
    k=kit('connectionReveal'+platform,1200,1080);k.image('Sliding platform preview','connectionPanel'+platform,600,440);k.ex('Sliding platform preview','transform/position','var p=Math.max(0,Math.min(1,time-.5)),u=p-1,s=1+1.65*u*u*u+.65*u*u;[600,440+650*(1-s),0]');all.push(...k.finish());
    k=kit('connectionTongue'+platform,1080,270);k.rect('Blue card edge',540,142,1040,226,[.1,.375,.784],21);k.rect('Blue card',540,134,1040,226,blue,21);k.cmd('effect.apply',{effect:'Gradient Ramp',layers:['Blue card']});k.set('Blue card','effects/#1/startColor',[.31,.65,1,1]);k.set('Blue card','effects/#1/endColor',[.12,.47,.94,1]);k.set('Blue card','effects/#1/start',[540,20]);k.set('Blue card','effects/#1/end',[540,250]);k.logo(icons[platform],85,84,60,true);k.text('Platform label',platform,140,83,49,white,'Schoolbell');k.text('Platform summary',summaries[platform],52,171,29,white);k.rect('Sign in button',958,83,129,47,white,11);k.text('Sign in label','Sign in',918,83,23,navy,'Satoshi','Bold');k.control('Platform summary');all.push(...k.finish());
    k=kit('connectionPlay'+platform,1200,1080);k.image('Hero Client','connectionReveal'+platform,600,540);k.cmd('layer.addMask',{layer:'Hero Client',shape:'rect',rect:[40,0,1120,744],mode:'Add'});k.image('Tongue','connectionTongue'+platform,600,827);k.ex('Tongue','transform/scale','var s=100*bk(0,.42);[s,s,100]');k.cmd('essential.addProperty',{comp:'connectionPlay'+platform,layer:'Tongue',path:'transform/scale',name:'Tongue scale'});all.push(...k.finish());
  }
  const p=kit('connectionCardParts',1200,1080);p.image('Slack play component','connectionPlaySlack',600,540);p.text('Components label','/connections · editable 2D plays',100,1020,32,navy,'Schoolbell');p.control('Components label');all.push(...p.finish());return all;
}

export const journeyTempo=120;
export const journeyDuration=8;
export const journeyStops=[
  {platform:'X',source:'startPlayX',center:[960,520,0],arrival:.5,depart:1,entry:0},
  {platform:'Slack',source:'connectionPlaySlack',center:[2720,310,680],arrival:1.5,depart:2,entry:1.1},
  {platform:'Discord',source:'connectionPlayDiscord',center:[4470,750,-240],arrival:2.5,depart:3,entry:2.1},
  {platform:'Instagram',source:'connectionPlayInstagram',center:[6200,330,930],arrival:3.5,depart:4,entry:3.1},
  {platform:'Reddit',source:'connectionPlayReddit',center:[7930,690,160],arrival:4.5,depart:5,entry:4.1},
  {platform:'Facebook',source:'connectionPlayFacebook',center:[9660,290,1190],arrival:5.5,depart:6,entry:5.1},
  {platform:'LinkedIn',source:'connectionPlayLinkedIn',center:[11400,550,440],arrival:6.5,depart:7.5,entry:6.1},
];

export function journeySteps(){
  const k=stage('logPlayJourney',journeyDuration),{cmd,set,ex,plane,cam}=k;
  k.steps.unshift({command:'effect.plugins.load',params:{folder:'C:/Users/0/AppData/Roaming/EffectCraft/Plug-ins'}});
  cmd('layer.setSwitch',{layers:['Studio gradient'],switch:'video',value:false});
  cmd('layer.addItem',{item:'ditherGradientBackground',position:[960,540]});
  cmd('layer.rename',{layer:'ditherGradientBackground',name:'Built dither background'});
  cmd('essential.set',{layer:'Built dither background',control:'Wipe',value:61});
  // eg149 is the existing source's Wipe control; animate only this instance.
  ex('Built dither background','essential/eg149','61+5*Math.sin(time*.48)');
  ex('Built dither background','transform/scale','[106,106,100]');
  ex('Built dither background','transform/position','[960+20*Math.sin(time*.3),540+12*Math.sin(time*.4),0]');
  cmd('layer.enableTimeRemap',{layers:['Built dither background'],value:true});
  ex('Built dither background','timeRemap','Math.min(time*.45,4.9)');
  cmd('layer.timing',{layers:['Built dither background'],in:0,out:journeyDuration});
  cmd('layer.arrange',{layers:['Built dither background'],to:'back'});
  cmd('essential.addProperty',{comp:'logPlayJourney',layer:'3D Camera',path:'cameraOptions/zoom',name:'Camera framing'});
  // World-space routes share the cards' depth changes. Short trimmed strokes travel
  // over faint continuous rails; the camera supplies their perspective and parallax.
  journeyStops.slice(0,-1).forEach((a,i)=>{
    const b=journeyStops[i+1];
    [-1,1].forEach((side,r)=>{
      const pos=[a.center[0]-750,a.center[1]+side*520,a.center[2]+300+r*180];
      const dx=b.center[0]+750-pos[0],dz=b.center[2]+300+r*180-pos[2];
      const length=Math.hypot(dx,dz),dy=b.center[1]-a.center[1];
      const vertices=[[0,0],[length*.22,-side*35],[length*.5,dy+side*75],[length*.78,dy],[length,dy]];
      const inTangents=vertices.map((_,j)=>j?[-length*.09,0]:[0,0]);
      const outTangents=vertices.map((_,j)=>j<4?[length*.09,0]:[0,0]);
      for(const pulse of [false,true]){
        const n=`Route ${i+1} ${r+1} ${pulse?'travel':'rail'}`;
        cmd('layer.newShape',{kind:'none',name:n});
        cmd('shape.newPath',{layer:n,vertices,inTangents,outTangents,space:'layer',closed:false,fill:false,stroke:blue,strokeWidth:pulse?6:3});
        k.three(n);set(n,'transform/anchor',[0,0,0]);set(n,'transform/position',pos);
        set(n,'transform/rotationY',-Math.atan2(dz,dx)*180/Math.PI);
        set(n,'transform/opacity',pulse?68:25);
        set(n,'contents/group/contents/stroke/cap',1);
        cmd('layer.addShapeItem',{layer:n,kind:'trim'});
        if(pulse){
          set(n,'contents/trim/end',11);
          ex(n,'contents/trim/offset',`time*160+${i*67+r*150}`);
        }else ex(n,'contents/trim/end','100*sm(0,.4)');
      }
    });
  });
  journeyStops.forEach((stop,i)=>{
    const n=stop.platform+' play';plane(n,stop.source,stop.center,null,100);set(n,'transform/orientation',[0,i%2?-5:5,i%2?1:-1]);
    cmd('layer.enableTimeRemap',{layers:[n],value:true});
    ex(n,'timeRemap',`Math.max(0,(time-${stop.entry})*3.8)`);
    cmd('layer.timing',{layers:[n],start:stop.entry,in:stop.entry,out:journeyDuration});
    const popStart=i?stop.arrival-.18:0,popEnd=i?stop.arrival+.22:.48;
    const pop=`var p=Math.max(0,Math.min(1,(time-${popStart})/${popEnd-popStart})),u=p-1,pop=1+3.4*u*u*u+2.4*u*u;`;
    ex(n,'transform/scale',pop+`var a=time-${stop.arrival},j=a<0?0:Math.exp(-a*13)*Math.sin(a*29),s=92*pop;[s*(1-.1*(1-p)+.035*j),s*(1+.09*(1-p)-.03*j),100]`);
    ex(n,'transform/position',pop+`var v=value,a=time-${stop.arrival};[v[0],v[1]+80*(1-pop)+4*Math.sin(time*3+${i}),v[2]+240*(1-pop)-16*Math.max(0,a)]`);
  });
  const clock=`var stops=${JSON.stringify(journeyStops)};function ease(p){p=Math.max(0,Math.min(1,p));return p*p*p*(10+p*(-15+6*p));}var target=stops[0].center.slice(),d=2800-800*bk(0,.5),turn=0;for(var i=1;i<stops.length;i++){var a=stops[i-1].depart,b=stops[i].arrival;if(time>=a){var p=ease((time-a)/(b-a)),s=stops[i-1].center,e=stops[i].center;target=[s[0]+(e[0]-s[0])*p,s[1]+(e[1]-s[1])*p,s[2]+(e[2]-s[2])*p];d=2000+300*Math.sin(Math.PI*p);turn=Math.sin(Math.PI*p)*(i%2?1:-1);}}var index=0;for(var j=0;j<stops.length;j++)if(time>=stops[j].arrival)index=j;var stop=stops[index],next=stops[index+1],age=time-stop.arrival,ring=age<0?0:Math.exp(-age*13)*Math.sin(age*27);var travel=index?stops[index-1].center:stop.center;target[0]+=(stop.center[0]-travel[0])*.035*ring;target[1]+=(stop.center[1]-travel[1])*.035*ring;target[2]+=(stop.center[2]-travel[2])*.035*ring;d-=170*ring;d-=65*sm(stop.arrival,stop.depart)*(next?1-sm(stop.depart,next.arrival):1);d+=450*sm(7.5,8);`;
  cam(clock+'[target[0]+140+95*turn,target[1]-90-65*turn,target[2]-d]',clock+'[target[0]-25*ring,target[1]+15*ring,target[2]]',clock+'-.55+2.1*turn+1.4*ring');
  return k.finish();
}
