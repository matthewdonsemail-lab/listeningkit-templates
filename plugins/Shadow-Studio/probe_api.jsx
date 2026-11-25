for (var k of ["executeCommand","command","runCommand","savePreset","execCommand"]) writeLn("app."+k+" = "+typeof app[k]);
writeLn("proj.savePreset = "+typeof app.project.savePreset);
writeLn("CompProto.savePreset = "+typeof CompItem.prototype.savePreset);
writeLn("LayerProto.savePreset = "+typeof Layer.prototype.savePreset);
