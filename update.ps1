Add-Type -AssemblyName System.IO.Compression.FileSystem
function Unzip
{
    param([string]$zipfile, [string]$outpath)

    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipfile, $outpath)
}

Remove-Item .temp\* -Recurse -Force
	
Invoke-WebRequest -Uri "https://github.com/yt-dlp/yt-dlp/archive/master.zip" -OutFile ".temp\ydl.zip"

unzip "$PSScriptRoot\.temp\ydl.zip" "$PSScriptRoot\.temp"

Remove-Item -Force  -recurse "$PSScriptRoot\script.yatse.kodi\lib\youtube_dl"
Copy-Item -Force -recurse "$PSScriptRoot\.temp\yt-dlp-master\yt_dlp\" -Destination "$PSScriptRoot\script.yatse.kodi\lib\"
Move-Item "$PSScriptRoot\script.yatse.kodi\lib\yt_dlp" "$PSScriptRoot\script.yatse.kodi\lib\youtube_dl"


$file = "version.txt"
$fileVersion = (Get-Content $file | Select -First 1).Split(".")
$fileVersion[2] = [int]$fileVersion[2] + 1
$fileVersion -join "." | Set-Content $file
$fileVersion = (Get-Content $file | Select -First 1)

((Get-Content -path "script.yatse.kodi\addon.xml.template" -Raw) -replace '{Version}',$fileVersion) | Set-Content -Path "script.yatse.kodi\addon.xml"

#python repo_generator.py
python repo_generator_matrix.py

git add -A
git commit -m "Sync yt-dlp"