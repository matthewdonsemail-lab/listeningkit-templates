// hermesharness (matt, 2026-11-15): the Hermes Agent desktop app as native layers, from matt's screenshot of it.
// Project panel folder "hermes":
//   hermesharness       the empty app: a light window with the traffic lights, the sidebar (New session, Skills &
//                       Tools, Messaging, Artifacts), the "New session" top bar, the blue HERMES AGENT wordmark and its
//                       line in the middle, the "Send follow-up" input with the black send button, the status bar
//   hermesharness 1-4   the same app running one of the launch film's four ending lines (plugins/endingTerminal.jsx):
//                       the prompt types into the input and sends; the wordmark fades, the message lands as a bubble,
//                       then the tool call card (tool, arguments, result), the next tool and Hermes' reply come in
// Inside the window every box uses rounded-sm (RS). Every part is its own named layer. Rebuilt in place. Sizes, colours and fonts are the constants below; the wordmark
// is set in Bodoni MT Black, the closest installed face to the app's.
// Run in EffectCraft: File > Scripts > Run Script File... > plugins/hermesHarness.jsx
// or headless:        effectcraft-cli --project textAnimations.ecproj script plugins/hermesHarness.jsx --save
var W=1920, H=1080, FPS=30, DUR=8;
var BG=[1,1,1];                                        // behind the window
var WIN=[0.973,0.98,0.996], SIDE=[0.988,0.992,1], LINE=[0.88,0.9,0.94];
var INK=[0.16,0.18,0.23], GREY=[0.45,0.48,0.55], LIGHT=[0.62,0.65,0.7];
var BLUE=[0.11,0.33,0.93], CHIP=[0.91,0.94,1], CARD=[0.957,0.965,0.98], GREEN=[0.10,0.55,0.36], BLACK=[0.08,0.08,0.09];
var UI="Segoe UI", MONO="JetBrains Mono", MARK="Bodoni MT Black";
// the window
var X0=140, Y0=40, X1=1780, Y1=1040, R=18, SIDEW=330, TOPH=58, STATUSH=40;
var RS=3;   // inside the window the app uses Tailwind rounded-sm (2px), at this comp's ~1.3x scale
var MX0=X0+SIDEW, MCX=(MX0+X1)/2;                      // the main pane
var CARDS=[
  {prompt:"Reply to my DMs. Make it sound like me, not like AI.", tool:"● log · clone_voice",
   args:"your messages · your phrasing · your timing", result:"✓ Writing as you",
   next:"log · twitterDms · draft 6 replies", reply:"6 replies ready. They sound like you. Nobody can tell."},
  {prompt:"Who in my conversations is worth following up with?", tool:"● log · index_conversations",
   args:"X · Discord · Slack · Instagram · LinkedIn", result:"✓ Every conversation you've ever had",
   next:"SubQ · rank by who's ready", reply:"38 opportunities are waiting on you. Here's who to start with."},
  {prompt:"Find customers. Hire a designer. Book me on podcasts.", tool:"● log · run_play",
   args:"customers · hires · investors · podcasts", result:"✓ Running on every platform",
   next:"log · reply in your voice", reply:"Whatever you want, done your way."},
  {prompt:"Where does my data go?", tool:"● log · local",
   args:"your laptop · no cloud · no upload", result:"✓ Everything stays on this machine",
   next:"Hermes Agent · running locally", reply:"Nowhere. It's all local. That's what counts."}
];

function find(type,name){ for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof type && it.name===name) return it; } return null; }
var folder=find(FolderItem,"hermes")||app.project.items.addFolder("hermes");

function build(name,card){
  var C=find(CompItem,name);
  if(C){ for (var k=C.numLayers;k>=1;k--) C.layer(k).remove(); C.duration=DUR; }
  else C=app.project.items.addComp(name,W,H,1,DUR,FPS);
  C.parentFolder=folder;
  function span(L){ L.startTime=0; L.inPoint=0; L.outPoint=DUR; return L; }
  function shape(n,kind,cx,cy,w,h,fill,r,stroke,sw){
    var L=span(C.layers.addShape()); L.name=n;
    var g=L.property("Contents").addProperty("ADBE Vector Group"), c=g.property("Contents");
    var sh=c.addProperty(kind==="ellipse"?"ADBE Vector Shape - Ellipse":"ADBE Vector Shape - Rect");
    sh.property("Size").setValue([w,h]); if(kind!=="ellipse" && r) sh.property("Roundness").setValue(r);
    if(stroke){ var s=c.addProperty("ADBE Vector Graphic - Stroke"); s.property("Color").setValue(stroke); s.property("Stroke Width").setValue(sw||2); }
    if(fill){ var f=c.addProperty("ADBE Vector Graphic - Fill"); f.property("Color").setValue(fill); }
    L.property("Transform").property("Position").setValue([cx,cy]); return L; }
  function rect(n,x,y,w,h,fill,r,stroke,sw){ return shape(n,"rect",x+w/2,y+h/2,w,h,fill,r||0,stroke,sw); }
  function dot(n,cx,cy,d,fill,stroke){ return shape(n,"ellipse",cx,cy,d,d,fill,0,stroke,2); }
  function text(n,copy,x,y,size,color,font,just){ var t=span(C.layers.addText(copy)); t.name=n;
    try{ var td=t.property("Source Text").value; td.font=font; td.fontSize=size; td.fillColor=color; td.applyFill=true; td.applyStroke=false;
      td.justification=just==="c"?ParagraphJustification.CENTER_JUSTIFY:just==="r"?ParagraphJustification.RIGHT_JUSTIFY:ParagraphJustification.LEFT_JUSTIFY;
      t.property("Source Text").setValue(td); }catch(x){}
    t.property("Transform").property("Position").setValue([x,y]); return t; }
  function at(L,t0,slide){ var tr=L.property("Transform"), p=tr.property("Position").value;
    tr.property("Opacity").expression="time<"+t0.toFixed(2)+"?0:100*Math.min(1,(time-"+t0.toFixed(2)+")/0.12)";
    tr.property("Position").expression="var p=Math.max(0,Math.min(1,(time-"+t0.toFixed(2)+")/0.35)),u=p-1,k=1+2.8*u*u*u+1.8*u*u;["+p[0]+","+p[1]+"+"+(slide||16)+"*(1-k)]"; }
  function until(L,t1){ L.property("Transform").property("Opacity").expression="time<"+t1.toFixed(2)+"?100:Math.max(0,100-(time-"+t1.toFixed(2)+")/0.2*100)"; }

  // the window: background, a soft shadow, the frame, the sidebar, the dividers
  var bg=span(C.layers.addSolid([0,0,0],"background",W,H,1)); bg.property("Effects").addProperty("ADBE Fill").property("Color").setValue(BG);
  var sh=rect("window shadow",X0+6,Y0+14,X1-X0,Y1-Y0,[0,0,0],R); sh.property("Transform").property("Opacity").setValue(10);
  try{ sh.property("Effects").addProperty("ADBE Gaussian Blur 2").property("Blurriness").setValue(30); }catch(x){}
  rect("window",X0,Y0,X1-X0,Y1-Y0,WIN,R,LINE,2);
  rect("sidebar",X0+2,Y0+2,SIDEW-2,Y1-Y0-STATUSH-4,SIDE,0);
  rect("sidebar edge",MX0,Y0,1,Y1-Y0-STATUSH,LINE,0);
  rect("top bar edge",MX0,Y0+TOPH,X1-MX0,1,LINE,0);
  rect("status bar edge",X0,Y1-STATUSH,X1-X0,1,LINE,0);
  // traffic lights, the panel and search icons
  dot("close",X0+30,Y0+29,17,[1,0.37,0.34]); dot("minimise",X0+56,Y0+29,17,[1,0.74,0.18]); dot("zoom",X0+82,Y0+29,17,[0.16,0.78,0.25]);
  rect("panel icon",X0+108,Y0+20,20,18,null,RS,GREY,2); dot("search icon",X0+150,Y0+28,15,null,GREY);
  // the sidebar
  var items=["New session","Skills & Tools","Messaging","Artifacts"];
  for (var i=0;i<items.length;i++){ var y=Y0+98+i*46;
    rect("sidebar icon "+(i+1),X0+26,y-10,18,18,null,RS,GREY,2); text("sidebar "+items[i],items[i],X0+58,y+6,22,INK,UI); }
  // the top bar
  text("session title","New session ▾",MX0+28,Y0+TOPH/2+8,21,INK,UI);
  for (var i=0;i<4;i++) dot("top icon "+(i+1),X1-150+i*34,Y0+TOPH/2,17,null,GREY);
  // the empty state: the wordmark and its line
  var mark=text("wordmark","HERMES AGENT",MCX,Y0+420,112,BLUE,MARK,"c");
  var sub=text("tagline","Describe the task in your own words. I'll pick the right tools, explain my plan, and check\rin before risky steps.",MCX,Y0+488,24,GREY,UI,"c");
  // the input
  var IY=Y1-STATUSH-118;
  rect("input",MX0+30,IY,X1-MX0-60,72,[1,1,1],RS,LINE,2);
  var plus=text("input plus","+",MX0+58,IY+46,30,GREY,UI);
  var ph=text("input placeholder","Send follow-up",MX0+92,IY+44,22,LIGHT,UI);
  dot("mic icon",X1-108,IY+36,18,null,GREY);
  dot("send button",X1-66,IY+36,46,BLACK); text("send arrow","↑",X1-66,IY+46,26,[1,1,1],UI,"c");
  // the status bar
  text("status left","⌘     Gateway ready     Agents     Cron",X0+24,Y1-14,17,GREY,UI);
  text("status right","glm-5.1  ollama-cloud        v0.15.1 (+2)  75b6d4a",X1-24,Y1-14,17,GREY,UI,"r");
  if(!card) return C;

  // the conversation: the prompt types into the input, sends; the bubble, the tool card, the next tool, the reply
  var type=Math.max(0.8,card.prompt.length/42), send=0.4+type+0.15;
  ph.property("Transform").property("Opacity").expression="time<0.4||time>="+send.toFixed(2)+"?100:0";  // back once it sends
  var typed=text("input text","",MX0+92,IY+44,22,INK,UI), st=typed.property("Source Text"), n=Math.ceil(type*FPS/2);
  for (var s=0;s<=n;s++){ var d=st.value; d.text=card.prompt.substring(0,Math.round(card.prompt.length*s/n)); st.setValueAtTime(0.4+s*2/FPS,d); }
  var dd=st.value; dd.text=""; st.setValueAtTime(send,dd);
  until(mark,send); until(sub,send);
  var bw=Math.min(980,card.prompt.length*12.6+56), by=Y0+TOPH+46;
  at(rect("message bubble",X1-48-bw,by,bw,64,CHIP,RS),send,12);
  at(text("message",card.prompt,X1-48-bw+28,by+40,23,INK,UI),send,12);
  var cy=by+108, cw=860, t1=send+0.45;
  at(rect("tool card",MX0+48,cy,cw,150,CARD,RS,LINE,2),t1,16);
  at(text("tool",card.tool,MX0+76,cy+46,24,BLUE,MONO),t1,16);
  at(text("tool arguments",card.args,MX0+76,cy+86,20,GREY,MONO),t1+0.15,16);
  at(text("tool result",card.result,MX0+76,cy+126,24,GREEN,MONO),t1+0.45,16);
  at(text("next tool",card.next,MX0+52,cy+196,20,LIGHT,MONO),t1+0.75,12);
  at(text("reply",card.reply,MX0+52,cy+258,28,INK,UI),t1+1.05,12);
  return C;
}
build("hermesharness",null);
for (var i=0;i<CARDS.length;i++) build("hermesharness "+(i+1),CARDS[i]);
writeLn("hermes: hermesharness + hermesharness 1-"+CARDS.length+" (the Hermes Agent app, "+(X1-X0)+"x"+(Y1-Y0)+" window)");
