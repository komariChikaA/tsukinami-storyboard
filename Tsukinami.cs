using System;
using System.IO;
using System.Text.Json;
using StorybrewCommon.Scripting;
using StorybrewCommon.Storyboarding;
using OpenTK;

namespace StorybrewScripts;
public class Tsukinami : StoryboardObjectGenerator
{
    // These controls can be edited in BrewCut without changing the source assets.
    public const double ShakeStrength = 1.0;
    public const double BlurStrength = 1.0;
    public const double LightStrength = 1.0;
    public override void Generate()
    {
        using var data = JsonDocument.Parse(File.ReadAllText(Path.Combine(ProjectPath,"data/animation.json")));
        var tracks = data.RootElement.GetProperty("tracks");
        var end = data.RootElement.GetProperty("duration_ms").GetDouble();
        var bg = GetLayer("01 Background").CreateSprite("bg.png",OsbOrigin.Centre);
        var blur = GetLayer("02 Blur").CreateSprite("sb/bg-blur.jpg",OsbOrigin.Centre);
        // @group 背景 / 音频驱动镜头与模糊
        for(int i=0;i<tracks.GetArrayLength()-1;i++)
        {
            var a=tracks[i]; var b=tracks[i+1];
            double t=a[0].GetDouble(), u=b[0].GetDouble();
            foreach(var sprite in new[]{bg,blur})
            {
                sprite.Move(t,u,320+(a[1].GetDouble()-320)*ShakeStrength,240+(a[2].GetDouble()-240)*ShakeStrength,
                               320+(b[1].GetDouble()-320)*ShakeStrength,240+(b[2].GetDouble()-240)*ShakeStrength);
                sprite.Scale(t,u,a[3].GetDouble(),b[3].GetDouble());
                sprite.Rotate(t,u,a[4].GetDouble(),b[4].GetDouble());
            }
            bg.Fade(t,u,a[9].GetDouble(),b[9].GetDouble());
            blur.Fade(t,u,a[5].GetDouble()*a[9].GetDouble()*BlurStrength,b[5].GetDouble()*b[9].GetDouble()*BlurStrength);
        }
        // @endgroup
        // @group 光影 / 呼吸暖光
        var glow=GetLayer("03 Light").CreateSprite("sb/glow.png",OsbOrigin.Centre,new Vector2(415,290));
        glow.ScaleVec(0,1.5,.9); glow.Additive(0,end);
        var light=GetLayer("03 Light").CreateSprite("sb/pixel.png",OsbOrigin.Centre);
        light.Move(0,320,240);light.ScaleVec(0,854,480); light.Color(0,1,.86,.65); light.Additive(0,end);
        for(int i=0;i<tracks.GetArrayLength()-1;i++)
        {
            var a=tracks[i];var b=tracks[i+1];double t=a[0].GetDouble(),u=b[0].GetDouble();
            glow.Fade(t,u,a[6].GetDouble()*a[9].GetDouble()*LightStrength,b[6].GetDouble()*b[9].GetDouble()*LightStrength);
            glow.Move(t,u,415+18*Math.Sin(t/17000),290,415+18*Math.Sin(u/17000),290);
            light.Fade(t,u,a[7].GetDouble()*a[9].GetDouble()*LightStrength,b[7].GetDouble()*b[9].GetDouble()*LightStrength);
        }
        // @endgroup
        // @group 光影 / 暗角和字幕安全区
        var shade=GetLayer("04 Shade").CreateSprite("sb/vignette.png",OsbOrigin.Centre);
        shade.Move(0,320,240);shade.Fade(0,1800,0,1);shade.Fade(end-3000,end,1,0);
        // @endgroup
        // @group 字幕 / 开场标题与歌词
        var title=GetLayer("05 Lyrics").CreateSprite("sb/title.png",OsbOrigin.Centre,new Vector2(320,201));
        title.Move(0,320,201);title.Scale(0,.45);title.Fade(500,1800,0,1);title.Fade(6600,7300,1,0);
        var tag=GetLayer("05 Lyrics").CreateSprite("sb/tagline.png",OsbOrigin.Centre,new Vector2(320,254));
        tag.Move(0,320,254);tag.Scale(0,.45);tag.Fade(1100,2400,0,1);tag.Fade(6600,7300,1,0);
        using var lyrics=JsonDocument.Parse(File.ReadAllText(Path.Combine(ProjectPath,"data/lyrics.json")));
        foreach(var cue in lyrics.RootElement.EnumerateArray())
        {
            double start=cue.GetProperty("start").GetDouble()*1000,stop=cue.GetProperty("end").GetDouble()*1000;
            double x=cue.GetProperty("x").GetDouble(),y=cue.GetProperty("y").GetDouble();
            double dx=cue.GetProperty("drift_x").GetDouble(),dy=cue.GetProperty("drift_y").GetDouble();
            var s=GetLayer("05 Lyrics").CreateSprite(cue.GetProperty("path").GetString(),OsbOrigin.Centre);
            s.Scale(start,cue.GetProperty("scale").GetDouble());
            s.Move(start,start+220,x-1.8*dx,y+dy,x,y);
            s.Move(start+220,stop-180,x,y,x+dx,y+dy);
            s.Move(stop-180,stop,x+dx,y+dy,x+2*dx,y+dy);
            s.Fade(start,start+180,0,1);s.Fade(stop-180,stop,1,0);
        }
        // @endgroup
    }
}
