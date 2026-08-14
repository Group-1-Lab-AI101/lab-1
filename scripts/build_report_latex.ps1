param(
    [string]$OutputPdf = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot "docs\TECHNICAL_REPORT.tex"
$buildDir = Join-Path $projectRoot "tmp\report-latex"
if ([string]::IsNullOrWhiteSpace($OutputPdf)) {
    $OutputPdf = Join-Path $projectRoot "output\pdf\1 - Report.pdf"
}

New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPdf) | Out-Null

Push-Location $projectRoot
try {
    & latexmk -xelatex -interaction=nonstopmode -halt-on-error `
        -output-directory="$buildDir" "$source"
    if ($LASTEXITCODE -ne 0) {
        throw "XeLaTeX report build failed."
    }
}
finally {
    Pop-Location
}

$builtPdf = Join-Path $buildDir "TECHNICAL_REPORT.pdf"
if (-not (Test-Path -LiteralPath $builtPdf)) {
    throw "Expected report PDF was not produced."
}
Copy-Item -LiteralPath $builtPdf -Destination $OutputPdf -Force
Write-Output (Resolve-Path -LiteralPath $OutputPdf).Path
