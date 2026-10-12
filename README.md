# ツキナミ

副标题：分島花音。

Storybrew 1.96 工程：随音乐的震动、模糊、缩放与旋转，配合人物、天空音符和右侧沙发的局部取景；52 行日文歌词交替出现在四角并移动。

## 使用

打开 `project.sbrew.yaml`，将谱面/素材目录设为本工程的 `assets`，在 Storybrew 中生成和导出。需要 Windows、.NET 8 和 Storybrew 1.96。

`assets` 同时是完整素材目录；本作品实际使用的纹理均已包含，打开工程无需额外生成纹理。

在 osu! 中观看：下载 Release 的 `tsukinami-storyboard-v2.osz` 并导入，选择 `Storyboard Preview`，开启 Auto，启用 storyboard 并将背景暗化设为 0%。预览谱面只有首尾两个物件，中间为休息段.

## 工程内容

- `Tsukinami.cs`：背景、光影、标题、歌词的原生 Storybrew 动画。
- `scriptslibrary/CameraRig.cs`：取景点、镜头缩放/旋转与重拍震动。
- `.sbrew/`：Storybrew 图层和工程配置。
- `assets/`：歌曲、BG、storyboard 谱面，以及实际使用的纹理、音频采样表和歌词时间表。
- `scripts.csproj`：工程脚本的编译引用；可用 StorybrewDir 指定本机引擎目录。

调整镜头可修改 CameraRig 的 Shots、ShakeStrength、BlurStrength；歌词的时间和位置位于 `assets/sb/lyrics.tsv`。

[压制视频与 OSB 成品下载](https://github.com/komariChikaA/tsukinami-storyboard/releases/tag/v1.0.0-rc.2)。

工程结构参考 [Milkitic/storybrew.Benibotan](https://github.com/Milkitic/storybrew.Benibotan) 与 [munehime/osu-storyboards](https://github.com/munehime/osu-storyboards)；歌词空间变化参考前者的 WordPanel / WordPanel2。没有复制第三方场景代码或贴图。
