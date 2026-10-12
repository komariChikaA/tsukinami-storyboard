# ツキナミ Storyboard

以用户提供的 4 分 39 秒歌曲和 BG 制作的单图音乐 storyboard：音频驱动的模糊、抖动、光晕，以及四角交替、滑入、漂移、滑出的日文歌词。

本项目使用本机 Storybrew 1.96 生成原生 osu! storyboard，视频和 OSB 共用同一组动画轨迹。

工程素材位于 `assets/`，源码和构建工具独立存放；中间帧、模型、日志和压制视频均不进入 Git 历史。

歌曲与 BG 由用户提供，仓库不授予这些素材的再分发许可。

## 成品

[Release 下载](https://github.com/komariChikaA/tsukinami-storyboard/releases)提供完整 **1920×1080 / 30fps / H.264 + AAC** 视频、可移植 OSB 素材包、日文 SRT 和 SHA-256 校验文件。

## 构建

需要 Windows、Python 3.12、FFmpeg、.NET 8 SDK、本机 Storybrew 1.96 和 Windows 自带的日文字体 `Meiryo`。

```powershell
python -m pip install -r requirements.txt
./Build.ps1 -Storybrew 'D:/software/storybrew.1.96'
# NVIDIA 显卡可用时使用硬件编码，交付视频采用此方式
./Build.ps1 -Encoder h264_nvenc
# 仅重建 OSB、素材包和字幕
./Build.ps1 -NoVideo
```

所有结果写入 `output/`。渲染器直接读取原生 Storybrew 导出的 OSB，支持本工程实际使用的线性 M/S/V/R/F/C 和加算 P 命令；遇到其他命令或曲线会明确停止。

## 本机编辑

```powershell
./Preview.ps1
# 如本机 BrewCut 安装在其他位置
./Preview.ps1 -BrewCut 'D:/tools/brewcut' -Storybrew 'D:/software/storybrew.1.96'
```

BrewCut 工作台支持图层、源码映射和预览，默认使用 `127.0.0.1:18744`。也可将本工程载入 Storybrew，素材目录选择工程的 `assets/`。

## 调整

- `Tsukinami.cs`：效果分组，`ShakeStrength`、`BlurStrength`、`LightStrength`。
- `data/lyrics.json`：歌词时间、语义分行、四角布局和移动幅度。歌词以 `data/lyrics.txt` 为准。
- `tools/prepare.py`：音频 STFT 检测、纹理生成与布局计算。
- `tools/render.py`：OSB 压制；生成视频前与原生引擎采样进行数值比较。

修改后运行 `Build.ps1`。仅调整时间可以直接编辑 JSON；`set_cues.py` 会重置为初版编辑时间表，不在常规构建中运行。`transcribe.py` 和 `refine_timing.py` 是可选的本地时间辅助工具，需要额外安装 `faster-whisper`；模型和识别日志保存在忽略的 `work/`，无需识别即可复现成品。

公开参考见 [docs/references.md](docs/references.md)，技术验证见 [docs/validation.md](docs/validation.md)。视觉强度及演唱细节同步仍以用户验收为准，Issue 状态保持 Qualified。
