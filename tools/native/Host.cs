using OpenTK;
using StorybrewCommon.Mapset;
using StorybrewCommon.Scripting;
using StorybrewCommon.Storyboarding;
using System.Reflection;
sealed class HostContext : GeneratorContext
{
    readonly string projectDir;
    readonly string mapsetDir;
    readonly Dictionary<string, StoryboardLayer> layers = new(StringComparer.Ordinal);
    public List<StoryboardLayer> Layers { get; } = new();

    public HostContext(string projectDir, string mapsetDir)
    {
        this.projectDir = projectDir;
        this.mapsetDir = mapsetDir;
    }

    public override string ProjectPath => projectDir;
    public override string ProjectAssetPath => projectDir;
    public override string MapsetPath => mapsetDir;
    public override Beatmap Beatmap => null;
    public override IEnumerable<Beatmap> Beatmaps => Array.Empty<Beatmap>();
    public override double AudioDuration => 279000;
    public override bool Multithreaded { get; set; }
    public override CancellationToken CancellationToken => CancellationToken.None;

    public override StoryboardLayer GetLayer(string identifier)
    {
        if (!layers.TryGetValue(identifier, out var layer))
        {
            layer = new HostLayer(identifier);
            layers[identifier] = layer;
            Layers.Add(layer);
        }
        return layer;
    }

    public override void AddDependency(string path) { }
    public override void AppendLog(string message) => Console.WriteLine(message);
    public override float[] GetFft(double time, string path, bool splitChannels) => Array.Empty<float>();
    public override float GetFftFrequency(string path) => 0;
}

sealed class HostLayer : StoryboardLayer
{
    readonly string identifier;
    public List<OsbSprite> Sprites { get; } = new();
    Vector2 origin;
    Vector2 position;
    double rotation;
    double scale = 1;
    bool reverseDepth;

    public HostLayer(string identifier) : base(identifier)
    {
        this.identifier = identifier;
    }

    public override string Identifier => identifier;
    public override Vector2 Origin { get => origin; set => origin = value; }
    public override Vector2 Position { get => position; set => position = value; }
    public override double Rotation { get => rotation; set => rotation = value; }
    public override double Scale { get => scale; set => scale = value; }
    public override bool ReverseDepth { get => reverseDepth; set => reverseDepth = value; }
    public override IEnumerable<StoryboardSegment> NamedSegments => Array.Empty<StoryboardSegment>();
    public override double StartTime => Sprites.Count == 0 ? 0 : Sprites.Min(s => s.StartTime);
    public override double EndTime => Sprites.Count == 0 ? 0 : Sprites.Max(s => s.EndTime);

    public override StoryboardSegment CreateSegment(string id) => throw new NotSupportedException();
    public override StoryboardSegment GetSegment(string id) => null;
    public override void Discard(StoryboardObject storyboardObject)
    {
        if (storyboardObject is OsbSprite sprite)
            Sprites.Remove(sprite);
    }

    public override OsbSprite CreateSprite(string path, OsbOrigin origin) =>
        CreateSprite(path, origin, DefaultPosition());

    public override OsbSprite CreateSprite(string path, OsbOrigin origin, Vector2 position)
    {
        var sprite = (OsbSprite)Activator.CreateInstance(typeof(OsbSprite), true);
        SetField(sprite, "texturePath", path);
        SetField(sprite, "Origin", origin);
        SetField(sprite, "initialPosition", position);
        Sprites.Add(sprite);
        return sprite;
    }

    public override OsbAnimation CreateAnimation(string path, int frameCount, double frameDelay, OsbLoopType loopType, OsbOrigin origin) =>
        CreateAnimation(path, frameCount, frameDelay, loopType, origin, DefaultPosition());

    public override OsbAnimation CreateAnimation(string path, int frameCount, double frameDelay, OsbLoopType loopType, OsbOrigin origin, Vector2 position)
    {
        var sprite = (OsbAnimation)Activator.CreateInstance(typeof(OsbAnimation), true);
        SetField(sprite, "texturePath", path);
        SetField(sprite, "Origin", origin);
        SetField(sprite, "initialPosition", position);
        SetField(sprite, "FrameCount", frameCount);
        SetField(sprite, "FrameDelay", frameDelay);
        SetField(sprite, "LoopType", loopType);
        Sprites.Add(sprite);
        return sprite;
    }

    public override OsbSample CreateSample(string path, double time, double volume)
    {
        var sample = (OsbSample)Activator.CreateInstance(typeof(OsbSample), true);
        SetField(sample, "audioPath", path);
        SetField(sample, "Time", time);
        SetField(sample, "Volume", volume);
        return sample;
    }

    public override void WriteOsb(TextWriter writer, ExportSettings settings, OsbLayer layer, StoryboardTransform transform, CancellationToken token) { }

    static Vector2 DefaultPosition()
    {
        var field = typeof(OsbSprite).GetField("DefaultPosition", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
        return field?.GetValue(null) is Vector2 value ? value : new Vector2(320, 240);
    }

    static void SetField(object target, string name, object value)
    {
        for (var type = target.GetType(); type != null; type = type.BaseType)
        {
            var field = type.GetField(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            if (field == null)
                continue;
            field.SetValue(target, value);
            return;
        }
        throw new MissingFieldException(target.GetType().Name, name);
    }
}
