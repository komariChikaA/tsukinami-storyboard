using System;
using System.Globalization;
using System.IO;
using System.Linq;
using StorybrewCommon.Scripting;
using StorybrewCommon.Storyboarding;

namespace StorybrewScripts;

public class Tsukinami : StoryboardObjectGenerator
{
    public override void Generate()
    {
        var samples=File.ReadAllLines(Path.Combine(ProjectPath,"assets/sb/music.csv"))
            .Skip(1).Select(line=>line.Split(',').Select(v=>double.Parse(v,CultureInfo.InvariantCulture)).ToArray())
            .Select(row=>CameraRig.Sample(row[0],row[1],row[2])).ToArray();
        var end=CameraRig.Duration;
        var bg=GetLayer("01 Background").CreateSprite("bg.png",OsbOrigin.Centre);
        var blur=GetLayer("02 Blur").CreateSprite("sb/bg-blur.jpg",OsbOrigin.Centre);
        for(int i=0;i<samples.Length-1;i++)
        {
            var a=samples[i];var b=samples[i+1];double t=a[0],u=b[0];
            foreach(var sprite in new[]{bg,blur})
            {
                sprite.Move(t,u,a[1],a[2],b[1],b[2]);
                sprite.Scale(t,u,a[3],b[3]);sprite.Rotate(t,u,a[4],b[4]);
            }
            bg.Fade(t,u,a[9],b[9]);blur.Fade(t,u,a[5]*a[9],b[5]*b[9]);
        }

        var glow=GetLayer("03 Light").CreateSprite("sb/glow.png",OsbOrigin.Centre);
        glow.ScaleVec(0,1.5,.9);glow.Additive(0,end);
        var light=GetLayer("03 Light").CreateSprite("sb/pixel.png",OsbOrigin.Centre);
        light.Move(0,320,240);light.ScaleVec(0,854,480);light.Color(0,1,.86,.65);light.Additive(0,end);
        for(int i=0;i<samples.Length-1;i++)
        {
            var a=samples[i];var b=samples[i+1];double t=a[0],u=b[0];
            glow.Move(t,u,a[10],a[11],b[10],b[11]);
            glow.Fade(t,u,a[6]*a[9],b[6]*b[9]);light.Fade(t,u,a[7]*a[9],b[7]*b[9]);
        }
        var shade=GetLayer("04 Shade").CreateSprite("sb/vignette.png",OsbOrigin.Centre);
        shade.Move(0,320,240);shade.Fade(0,1800,0,1);shade.Fade(end-3000,end,1,0);

        var title=GetLayer("05 Lyrics").CreateSprite("sb/title.png",OsbOrigin.Centre);
        title.Move(0,320,100);title.Scale(0,.48);title.Fade(500,1800,0,1);title.Fade(6600,7300,1,0);
        var artist=GetLayer("05 Lyrics").CreateSprite("sb/artist.png",OsbOrigin.Centre);
        artist.Move(0,320,145);artist.Scale(0,.45);artist.Fade(1100,2400,0,1);artist.Fade(6600,7300,1,0);

        // Each TSV row maps one sung line to its texture and animation.
        foreach(var line in File.ReadAllLines(Path.Combine(ProjectPath,"assets/sb/lyrics.tsv")).Skip(1))
        {
            var v=line.Split('\t');
            double Number(int index)=>double.Parse(v[index],CultureInfo.InvariantCulture);
            double start=Number(0),stop=Number(1),x=Number(3),y=Number(4),dx=Number(5),dy=Number(6);
            var lyric=GetLayer("05 Lyrics").CreateSprite(v[2],OsbOrigin.Centre);
            lyric.Scale(start,Number(7));
            lyric.Move(start,start+220,x-1.8*dx,y+dy,x,y);
            lyric.Move(start+220,stop-180,x,y,x+dx,y+dy);
            lyric.Move(stop-180,stop,x+dx,y+dy,x+2*dx,y+dy);
            lyric.Fade(start,start+180,0,1);lyric.Fade(stop-180,stop,1,0);
        }
    }
}
