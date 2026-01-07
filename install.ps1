# MediaDownloader Installer
# Installs the latest release of MediaDownloader

$ErrorActionPreference = "Stop"
$repo = "alpineplacebo/MediaDownloader"
$installDir = "$env:LOCALAPPDATA\MediaDownloader"
$exeName = "MediaDownloader.exe"

Write-Host "Installing MediaDownloader..." -ForegroundColor Cyan

# check if running as admin (optional, but good for removing old versions if needed)
# For local app data, admin is not strictly required.

# Create installation directory
if (!(Test-Path -Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir | Out-Null
    Write-Host "Created directory: $installDir" -ForegroundColor Gray
}

# Fetch latest release info
$ghAvailable = (Get-Command gh -ErrorAction SilentlyContinue)

if ($ghAvailable) {
    Write-Host "Detected gh CLI. Using authenticated download..." -ForegroundColor Cyan
    try {
        # Create dir if not exists (already done above)
        
        # Download using gh
        # We use 'latest' to fetch the latest release
        Set-Location -Path $installDir
        gh release download --repo $repo --pattern $exeName --clobber
        
        if (!(Test-Path $exeName)) {
            throw "Download failed or file not found."
        }
        
        Write-Host "Download complete." -ForegroundColor Green
    } catch {
        Write-Error "Failed to install using gh CLI: $_"
        exit 1
    }
} else {
    # Fallback to public API (Will fail for private repos)
    Write-Host "gh CLI not found. Attempting public download..." -ForegroundColor Yellow
    
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
    } catch {
        Write-Error "Failed to install via public method: $_"
        Write-Host "NOTE: For private repositories, please install the GitHub CLI (gh) and authenticate." -ForegroundColor Red
        exit 1
    }
}

# Create Shortcut on Desktop
$wshShell = New-Object -ComObject WScript.Shell
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path -Path $desktopPath -ChildPath "MediaDownloader.lnk"
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path -Path $installDir -ChildPath $exeName
$shortcut.WorkingDirectory = $installDir
$shortcut.Description = "Launch MediaDownloader"
$shortcut.Save()

Write-Host "Shortcut created on Desktop." -ForegroundColor Green
Write-Host "Installation successful!" -ForegroundColor Cyan
