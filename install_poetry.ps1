# PowerShell script to install Poetry on Windows
# Run this script as: .\install_poetry.ps1

Write-Host "=== Installing Poetry on Windows ===" -ForegroundColor Green

# Check if Python is installed
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Download and install Poetry
Write-Host "`nDownloading Poetry installer..." -ForegroundColor Yellow
try {
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    Write-Host "✓ Poetry installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install Poetry. Error: $_" -ForegroundColor Red
    exit 1
}

# Add Poetry to PATH for current session
Write-Host "`nAdding Poetry to PATH..." -ForegroundColor Yellow
$poetryPath = "$env:APPDATA\Python\Scripts"

# Check if path exists
if (Test-Path $poetryPath) {
    # Add to current session
    $env:Path += ";$poetryPath"

    # Add to user PATH permanently
    $userPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    if ($userPath -notlike "*$poetryPath*") {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$userPath;$poetryPath",
            [EnvironmentVariableTarget]::User
        )
        Write-Host "✓ Poetry added to PATH permanently" -ForegroundColor Green
    } else {
        Write-Host "✓ Poetry already in PATH" -ForegroundColor Green
    }
} else {
    Write-Host "⚠ Poetry installation path not found at: $poetryPath" -ForegroundColor Yellow
    Write-Host "  You may need to add it manually or restart PowerShell" -ForegroundColor Yellow
}

# Verify installation
Write-Host "`nVerifying Poetry installation..." -ForegroundColor Yellow
try {
    $poetryVersion = poetry --version
    Write-Host "✓ $poetryVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Poetry installed but not in PATH yet." -ForegroundColor Yellow
    Write-Host "  Please restart PowerShell and try again." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n=== Poetry Installation Complete! ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Close and reopen PowerShell (if poetry --version doesn't work)"
Write-Host "2. Run: poetry install"
Write-Host "3. Run: poetry run pre-commit install"
Write-Host "4. Run: poetry run pre-commit run --all-files"

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
