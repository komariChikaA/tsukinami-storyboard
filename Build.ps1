param(
    [string]$Storybrew = 'D:\software\storybrew.1.96',
    [string]$Encoder = 'libx264',
    [switch]$NoVideo
)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$mapsetPath=(Join-Path $PSScriptRoot 'assets').Replace('\','/')
$userConfig="FormatVersion: 7`nEditor: `"storybrew editor 1.96`"`nMapsetPath: `"$mapsetPath`"`nExportTimeAsFloatingPoint: No`nOwnsOsb: No`n"
[IO.File]::WriteAllText((Join-Path $PSScriptRoot '.sbrew/user.yaml'),$userConfig,[Text.UTF8Encoding]::new($false))
$env:PYTHONUTF8='1'
python tools/prepare.py
if ($LASTEXITCODE -ne 0) { throw '素材与动画轨迹生成失败。' }
dotnet build tools/native --nologo "-p:StorybrewDir=$Storybrew"
if ($LASTEXITCODE -ne 0) { throw '原生 Storybrew 构建失败。' }
dotnet tools/native/bin/Debug/net8.0-windows/Native.dll $PSScriptRoot
if ($LASTEXITCODE -ne 0) { throw '原生 OSB 导出失败。' }
python tools/render.py --verify-only
if ($LASTEXITCODE -ne 0) { throw 'OSB 和原生引擎求值验证失败。' }
python tools/validate.py
if ($LASTEXITCODE -ne 0) { throw '歌词完整性、移动范围与镜头边缘检查失败。' }
if (-not $NoVideo) {
    python -u tools/render.py --encoder $Encoder
    if ($LASTEXITCODE -ne 0) { throw '压制失败。' }
    python tools/verify_video.py
    if ($LASTEXITCODE -ne 0) { throw '完整视频解码检查失败。' }
}
python tools/package.py
if ($LASTEXITCODE -ne 0) { throw '打包失败。' }
