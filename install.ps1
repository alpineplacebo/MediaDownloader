# MediaDownloader Installer
# Installs the latest release of MediaDownloader

$ErrorActionPreference = "Stop"
$repo = "alpineplacebo/MediaDownloader"
$installDir = "$env:LOCALAPPDATA\MediaDownloader"
$exeName = "MediaDownloader.exe"

Write-Host "Installing MediaDownloader..." -ForegroundColor Cyan

# Create installation directory
if (!(Test-Path -Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir | Out-Null
    Write-Host "Created directory: $installDir" -ForegroundColor Gray
}

# Fetch latest release info
$latestUrl = "https://api.github.com/repos/$repo/releases/latest"
try {
    $latest = Invoke-RestMethod -Uri $latestUrl
    $asset = $latest.assets | Where-Object { $_.name -eq $exeName } | Select-Object -First 1

    if (!$asset) {
        Write-Error "Could not find $exeName in the latest release."
        exit 1
    }
    
    $downloadUrl = $asset.browser_download_url
    $outputPath = Join-Path -Path $installDir -ChildPath $exeName

    Write-Host "Downloading latest version ($($latest.tag_name))..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath
    
    Write-Host "Download complete." -ForegroundColor Green
    
    # Create Shortcut on Desktop
    $wshShell = New-Object -ComObject WScript.Shell
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path -Path $desktopPath -ChildPath "MediaDownloader.lnk"
    $shortcut = $wshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $outputPath
    $shortcut.WorkingDirectory = $installDir
    $shortcut.Description = "Launch MediaDownloader"
    $shortcut.Save()
    
    Write-Host "Shortcut created on Desktop." -ForegroundColor Green
    Write-Host "Installation successful!" -ForegroundColor Cyan

} catch {
    Write-Error "Failed to install: $_"
}
