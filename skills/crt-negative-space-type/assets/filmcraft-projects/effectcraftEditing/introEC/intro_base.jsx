// The EffectCraft walkthrough's cold open in EffectCraft (matt, 2026-11-16): the FilmCraft intro (intro_plate.mp4,
// 20min-v10's first 17.5 s) under a black-to-transparent gradient on the left, and the hook lines as text cards on the
// left (Satoshi, the launch film's font). Rebuilds comp "intro" from scratch; intro_fx.jsx adds the lines, the
// thermograms, the transitions and the CRT on top.
var D="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/";
var F=30, W=1920, H=1080, DUR=525/F;
// [start frame, text]: the hook lines' timeline starts (hook_times.txt), at 30 fps
var CARDS=[
  [0,   "I DID NOT\rTOUCH THE\rTIMELINE"],
  [68,  "ONE\rPROMPT."],
  [83,  "YOU SIMPLY NEED\rFREE LIBRARIES\rAND A CLAUDE CODE\rSUBSCRIPTION."],
  [176, "YOU COULDN'T TELL\rTHIS WAS MADE\rWITH AI."],
  [221, "THAT SHIT IS\rOVER AND\rFUCKING DONE\rWITH."],
  [290, "YOU NEVER PAY\rFOR PLUGINS."],
  [344, "NEVER."],
  [351, "IT LITERALLY\rWOULD HAVE\rTAKEN A WEEK."],
  [437, "IT'S DONE\rIN 2 DAYS."],
  [481, "THE GREATEST\rUPGRADE\rWE'LL EVER\rHAVE."]];
var SIZE=[118,150,92,104,104,112,220,112,140,112];
// first-baseline y per card, so each block sits centred on the frame (from the rects of a first build)
var Y=[471,522,442,478,430,527,618,473,523,421];
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
var old=findComp("intro"); if(old) old.remove();
var C=app.project.items.addComp("intro", W, H, 1, DUR, F);
function imp(p){ return app.project.importFile(new ImportOptions(new File(p))); }
var plate=C.layers.add(imp(D+"intro_plate.mp4")); plate.name="plate";
var grad=C.layers.add(imp(D+"left_gradient.png")); grad.name="left gradient"; grad.outPoint=DUR;
for (var i=0;i<CARDS.length;i++){
  var a=CARDS[i][0], b=(i+1<CARDS.length?CARDS[i+1][0]:525);
  var L=C.layers.addText(CARDS[i][1]); L.name="card "+(i+1);
  var td=L.property("Source Text").value;
  td.font="Satoshi"; td.fauxBold=true; td.fontSize=SIZE[i]; td.fillColor=[1,1,1]; td.tracking=0; td.leading=SIZE[i]*0.95;
  td.justification=ParagraphJustification.LEFT_JUSTIFY;
  L.property("Source Text").setValue(td);
  L.startTime=0; L.inPoint=a/F; L.outPoint=b/F;
  L.property("Transform").property("Position").setValue([110, Y[i]]);
  // a slow push over the card, from the left edge
  L.property("Transform").property("Scale").expression="var u=(time-inPoint)/(outPoint-inPoint); var k=100+4*u; [k,k]";
}
writeLn("intro: plate, gradient, "+CARDS.length+" cards, "+DUR.toFixed(2)+" s");
