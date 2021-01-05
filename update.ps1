Add-Type -AssemblyName System.IO.Compression.FileSystem
function Unzip
{
    param([string]$zipfile, [string]$outpath)

    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipfile, $outpath)
}

Remove-Item temp\* -Recurse -Force
	
Invoke-WebRequest -Uri "https://github.com/ytdl-org/youtube-dl/archive/master.zip" -OutFile "temp\ydl.zip"

unzip "$PSScriptRoot\temp\ydl.zip" "$PSScriptRoot\temp"

Copy-Item -Force -recurse "$PSScriptRoot\temp\youtube-dl-master\youtube_dl" -Destination "$PSScriptRoot\script.yatse.kodi\lib"
