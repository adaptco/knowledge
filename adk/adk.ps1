<#
.SYNOPSIS
    Host wrapper for the ADK (Artifact Development Kit) Docker CLI.
.DESCRIPTION
    Builds the adk-cli Docker image and runs commands inside it.
    Mounts the current directory to /workspace.
.EXAMPLE
    .\adk.ps1 validate contracts
#>

$ErrorActionPreference = "Stop"

# Check for Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH. Please install Docker Desktop."
    exit 1
}

# Build the image if strictly necessary, but for dev speed, we can check existence.
# For now, we'll force build to ensure latest code is used, or check if image exists.
# A fast check:
$ImageExists = docker images -q adk-cli

if (-not $ImageExists) {
    Write-Host "Building ADK CLI Docker image..." -ForegroundColor Cyan
    # Must run build from the script's root (assuming script is in root of repo)
    $ScriptPath = $PSScriptRoot
    docker build -t adk-cli -f "$ScriptPath/cli/Dockerfile" "$ScriptPath"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker build failed."
        exit 1
    }
}

# Run the container
# Mount PWD to /workspace
# Set WorkDir to /workspace
Write-Host "Running ADK CLI..." -ForegroundColor Green
docker run --rm -it `
    -v "${PWD}:/workspace" `
    -w "/workspace" `
    adk-cli $args
