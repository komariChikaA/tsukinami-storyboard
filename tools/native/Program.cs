using System.Reflection;
using System.Text;
using System.Text.Json;
using StorybrewCommon.Scripting;
using StorybrewCommon.Storyboarding;
using StorybrewScripts;

var root=Path.GetFullPath(args.Length>0 ? args[0] : ".");
var context=new HostContext(root,Path.Combine(root,"assets"));
var effect=new Tsukinami();
typeof(StoryboardObjectGenerator).GetField("context",BindingFlags.Instance|BindingFlags.NonPublic).SetValue(effect,context);
effect.Generate();
Directory.CreateDirectory(Path.Combine(root,"output"));
var path=Path.Combine(root,"output","tsukinami.osb");
using(var writer=new StreamWriter(path,false,new UTF8Encoding(false)))
{
    writer.WriteLine("[Events]");
    var method=typeof(OsbSprite).GetMethods().First(m=>m.Name=="WriteOsb");
    foreach(HostLayer layer in context.Layers)
    foreach(var sprite in layer.Sprites)
    {
        var values=method.GetParameters().Select(p=> p.ParameterType==typeof(TextWriter) ? (object)writer :
            p.ParameterType==typeof(OsbLayer) ? OsbLayer.Foreground :
            p.ParameterType==typeof(CancellationToken) ? CancellationToken.None :
            p.ParameterType==typeof(ExportSettings) ? new ExportSettings() :
            p.ParameterType.IsValueType ? Activator.CreateInstance(p.ParameterType) : null).ToArray();
        method.Invoke(sprite,values);
    }
}
// Native engine samples independently verify the renderer's interpretation of the OSB.
var sampleTimes=new[]{0,1000,8500,32000,90000,130000,173000,218000,258000,278900};
var samples=new List<object>();
foreach(HostLayer layer in context.Layers)
foreach(var s in layer.Sprites)
foreach(int t in sampleTimes)
    if(s.StartTime<=t && t<s.EndTime)
    {
        var p=s.PositionAt(t);var z=s.ScaleAt(t);
        samples.Add(new{path=s.TexturePath,time=t,x=(double)p.X,y=(double)p.Y,sx=(double)z.X,sy=(double)z.Y,
            rotation=(double)s.RotationAt(t),opacity=(double)s.OpacityAt(t)});
    }
File.WriteAllText(Path.Combine(root,"output/native-samples.json"),JsonSerializer.Serialize(samples));
Console.WriteLine($"Storybrew generated {context.Layers.Sum(l=>((HostLayer)l).Sprites.Count)} sprites: {path}");
