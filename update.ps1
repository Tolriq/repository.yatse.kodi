Add-Type -AssemblyName System.IO.Compression.FileSystem
function Unzip
{
    param([string]$zipfile, [string]$outpath)

    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipfile, $outpath)
}

Remove-Item .temp\* -Recurse -Force
	
Invoke-WebRequest -Uri "https://github.com/ytdl-org/youtube-dl/archive/master.zip" -OutFile ".temp\ydl.zip"

unzip "$PSScriptRoot\.temp\ydl.zip" "$PSScriptRoot\.temp"

Copy-Item -Force -recurse "$PSScriptRoot\.temp\youtube-dl-master\youtube_dl" -Destination "$PSScriptRoot\script.yatse.kodi\lib"

$file = "version.txt"
$fileVersion = (Get-Content $file | Select -First 1).Split(".")
$fileVersion[2] = [int]$fileVersion[2] + 1
$fileVersion -join "." | Set-Content $file
$fileVersion = (Get-Content $file | Select -First 1)

((Get-Content -path "script.yatse.kodi\addon.xml.template" -Raw) -replace '{Version}',$fileVersion) | Set-Content -Path "script.yatse.kodi\addon.xml"

py repo_generator.py
py repo_generator_matrix.py

git add -A
git commit -m "Sync youtubeDL"