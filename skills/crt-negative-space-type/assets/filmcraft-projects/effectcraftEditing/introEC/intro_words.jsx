// matt, 2026-11-16: "the words animate in when I am talking": each card's text builds word by word, each word landing
// when he says it (beats.json: the transcript's word times on the edit's timeline). A Source Text expression keeps the
// card's own line breaks, so the layout never moves as words arrive. Card 10 now carries all of the line
// ("THIS IS THE GREATEST UPGRADE WE'LL EVER HAVE."). Rerun is safe.
var D="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/";
var TEXT={10:"THIS IS THE\rGREATEST\rUPGRADE WE'LL\rEVER HAVE."};
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var f=new File(D+"beats.json"); f.open("r"); var beats=JSON.parse(f.read()); f.close();
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
for (var i=0;i<beats.length;i++){
  var L=byName(C,"card "+(i+1)); if(!L) throw new Error("no card "+(i+1));
  var st=L.property("Source Text");
  st.expression="";
  if(TEXT[i+1]){ var td=st.value; td.text=TEXT[i+1]; st.setValue(td); }
  var full=st.value.text;
  var lines=full.split("\r"), toks=[], wi=0, words=beats[i].words;
  for (var l=0;l<lines.length;l++){
    var ws=lines[l].split(" ");
    for (var w=0;w<ws.length;w++){
      if(wi>=words.length) throw new Error("card "+(i+1)+": more words than spoken");
      toks.push([words[wi][0], (toks.length? (w===0?"\r":" ") : "")+ws[w]]); wi++;
    }
  }
  if(wi!==words.length) throw new Error("card "+(i+1)+": "+wi+" card words, "+words.length+" spoken");
  st.expression="var W="+JSON.stringify(toks)+",s='';for(var i=0;i<W.length;i++)if(time>=W[i][0]-0.04)s+=W[i][1];s";
  writeLn("card "+(i+1)+": "+toks.length+" words from "+toks[0][0]+" s");
}
