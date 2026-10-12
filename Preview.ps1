param(
    [string]$BrewCut = 'E:\系统默认\桌面\mad\brewcut',
    [string]$Storybrew = 'D:\software\storybrew.1.96',
    [int]$Port = 18744,
    [switch]$NoBrowser
)
$ErrorActionPreference='Stop'
$previewArguments=@{Project=$PSScriptRoot;Mapset=(Join-Path $PSScriptRoot 'assets');Storybrew=$Storybrew;Port=$Port;NoBrowser=$NoBrowser}
& (Join-Path $BrewCut 'Start.ps1') @previewArguments
