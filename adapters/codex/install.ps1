$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
$SourceDir = Join-Path $RepoRoot "skills\claimlint"
$TargetDir = Join-Path $RepoRoot ".agents\skills\claimlint"

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Copy-Item -Path (Join-Path $SourceDir "*") -Destination $TargetDir -Recurse -Force

Write-Output "Installed ClaimLint skill to $TargetDir"
