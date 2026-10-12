using System;

namespace StorybrewScripts;

// Camera targets are positions in the original 1672 x 941 BG.
public static class CameraRig
{
    public const double Duration = 278960;
    public const double ShakeStrength = 1.0;
    public const double BlurStrength = 1.0;
    // time (seconds), target X/Y, zoom relative to full height, roll (degrees)
    static readonly double[][] Shots =
    {
        new[]{0.0,836,470,1.15,-1.5}, new[]{7.0,725,430,1.28,2.5},
        new[]{16.0,980,400,1.32,-2.0}, new[]{22.8,836,470,1.15,0.0},
        new[]{26.4,720,415,1.46,2.5}, new[]{31.5,745,490,1.62,-3.5},
        new[]{37.0,1090,300,1.68,4.0}, new[]{43.6,735,430,1.43,-2.0},
        new[]{47.0,836,470,1.16,0.0}, new[]{53.0,1200,620,1.82,-4.0},
        new[]{61.0,760,360,1.30,2.0}, new[]{65.8,836,470,1.16,0.0},
        new[]{71.0,630,440,1.45,-3.0}, new[]{77.0,810,500,1.57,3.5},
        new[]{84.4,720,395,1.73,-3.0}, new[]{86.7,836,470,1.23,1.0},
        new[]{91.5,710,405,1.58,4.5}, new[]{96.2,900,480,1.29,-4.0},
        new[]{102.0,1110,330,1.77,4.0}, new[]{108.5,760,445,1.31,-2.5},
        new[]{113.5,736,450,1.72,3.0}, new[]{118.0,1010,580,1.44,-4.0},
        new[]{124.5,720,400,1.64,3.5}, new[]{131.0,836,470,1.16,0.0},
        new[]{138.0,1210,600,1.86,-4.0}, new[]{145.0,950,330,1.54,3.5},
        new[]{150.4,836,470,1.18,0.0}, new[]{157.0,720,430,1.46,-3.5},
        new[]{163.0,745,500,1.64,3.0}, new[]{169.0,1050,340,1.56,-4.0},
        new[]{171.5,836,470,1.24,0.0}, new[]{177.5,710,410,1.69,4.5},
        new[]{182.3,1120,340,1.78,-4.5}, new[]{188.0,800,450,1.33,3.0},
        new[]{194.0,1210,620,1.86,-4.0}, new[]{198.0,900,420,1.42,4.5},
        new[]{202.0,720,400,1.72,-3.0}, new[]{209.0,810,490,1.49,3.5},
        new[]{213.8,836,470,1.24,0.0}, new[]{219.0,720,420,1.74,4.5},
        new[]{224.0,1100,330,1.80,-4.5}, new[]{230.0,760,480,1.48,3.5},
        new[]{234.7,720,395,1.78,-3.5}, new[]{241.0,925,520,1.40,4.0},
        new[]{247.0,735,440,1.75,-3.5}, new[]{254.0,720,405,1.50,2.5},
        new[]{263.2,836,470,1.18,0.0}, new[]{270.0,950,420,1.34,-2.0},
        new[]{275.9,836,470,1.15,0.0}, new[]{278.96,836,470,1.15,0.0}
    };

    public static double[] Sample(double milliseconds, double kick, double energy)
    {
        double t=milliseconds/1000;
        int index=0;
        while(index<Shots.Length-2 && Shots[index+1][0]<t) index++;
        var a=Shots[index];var b=Shots[index+1];
        double q=Math.Clamp((t-a[0])/(b[0]-a[0]),0,1);
        double smooth=q*q*(3-2*q);
        double focusX=a[1]+(b[1]-a[1])*smooth;
        double focusY=a[2]+(b[2]-a[2])*smooth;
        bool chorus=(t>=86.66 && t<130.2)||(t>=171.46 && t<263.1);
        double strength=chorus?1.0:.68;
        double zoom=a[3]+(b[3]-a[3])*smooth+.028*kick+.008*Math.Sin(t*.8);
        double rotation=(a[4]+(b[4]-a[4])*smooth)*Math.PI/180
                       +.013*kick*strength*Math.Sin(t*53)+.004*Math.Sin(t*.9);
        double scale=480.0/941*zoom;
        double c=Math.Cos(rotation),s=Math.Sin(rotation);
        // Cover all four corners even under the strongest shake and roll.
        double halfX=(Math.Abs(c)*427+Math.Abs(s)*240+19)/scale;
        double halfY=(Math.Abs(s)*427+Math.Abs(c)*240+19)/scale;
        focusX=Math.Clamp(focusX,halfX,1672-halfX);
        focusY=Math.Clamp(focusY,halfY,941-halfY);
        double offsetX=(836-focusX)*scale,offsetY=(470.5-focusY)*scale;
        double shakeX=ShakeStrength*kick*strength*(7.5*Math.Sin(t*59)+2.3*Math.Sin(t*31));
        double shakeY=ShakeStrength*kick*strength*(5.5*Math.Cos(t*47)+1.8*Math.Sin(t*73));
        double x=320+c*offsetX-s*offsetY+shakeX;
        double y=240+s*offsetX+c*offsetY+shakeY;
        double transition=6*q*(1-q)*Math.Abs(b[3]-a[3])/(b[0]-a[0]);
        double blur=BlurStrength*Math.Clamp(.035+.38*kick*strength+transition*.55,.025,.74);
        double fade=Math.Min(Math.Clamp(t/1.8,0,1),Math.Clamp((278.96-t)/3,0,1));
        double sunX=(925-836)*scale,sunY=(610-470.5)*scale;
        return new[]{milliseconds,x,y,scale,rotation,blur,.085+.07*energy+.035*kick,
                     .027*kick,.06,fade,x+c*sunX-s*sunY,y+s*sunX+c*sunY};
    }
}
