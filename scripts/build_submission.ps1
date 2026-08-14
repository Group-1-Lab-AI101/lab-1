param(
    [Parameter(Mandatory = $true)]
    [string]$GroupId,

    [Parameter(Mandatory = $true)]
    [string]$ReportPdf,

    [Parameter(Mandatory = $true)]
    [string]$VideoUrl,

    [string]$SlideDeck = ""
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

if ([string]::IsNullOrWhiteSpace($GroupId) -or
    $GroupId.Contains("..") -or
    $GroupId.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0) {
    throw "GroupId must be a safe filename component."
}

$uri = $null
if (-not [Uri]::TryCreate($VideoUrl, [UriKind]::Absolute, [ref]$uri) -or
    $uri.Scheme -notin @("http", "https")) {
    throw "VideoUrl must be an absolute http(s) URL."
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$reportPath = (Resolve-Path -LiteralPath $ReportPdf).Path
if ([IO.Path]::GetExtension($reportPath) -ne ".pdf") {
    throw "ReportPdf must point to a PDF file."
}

if ([string]::IsNullOrWhiteSpace($SlideDeck)) {
    $SlideDeck = Join-Path $projectRoot "output\presentation\1 - Slide.pptx"
}
$slidePath = (Resolve-Path -LiteralPath $SlideDeck).Path
if ([IO.Path]::GetExtension($slidePath) -notin @(".pptx", ".pdf")) {
    throw "SlideDeck must point to a PPTX or PDF file."
}

$outputRoot = Join-Path $projectRoot "output\submission"
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null
$staging = Join-Path $outputRoot ("staging-" + [Guid]::NewGuid().ToString("N"))
$outputRootFull = [IO.Path]::GetFullPath($outputRoot) + [IO.Path]::DirectorySeparatorChar
$stagingFull = [IO.Path]::GetFullPath($staging)
if (-not $stagingFull.StartsWith($outputRootFull, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to create staging outside the submission output directory."
}

$slideExtension = [IO.Path]::GetExtension($slidePath)
$zipPath = Join-Path $outputRoot "$GroupId.zip"

try {
    New-Item -ItemType Directory -Path $staging | Out-Null
    Copy-Item -LiteralPath $reportPath -Destination (Join-Path $staging "$GroupId - Report.pdf")
    Copy-Item -LiteralPath $slidePath -Destination (Join-Path $staging "$GroupId - Slide$slideExtension")

    @(
        "SOURCE CODE LINKS - $GroupId"
        ""
        "https://github.com/Group-1-Lab-AI101/lab-1"
        "https://github.com/Group-1-Lab-AI101/lab-1-backend"
        "https://github.com/Group-1-Lab-AI101/lab-1-frontend"
    ) | Set-Content -LiteralPath (Join-Path $staging "$GroupId - SC.txt") -Encoding UTF8

    @(
        "DEMO VIDEO - $GroupId"
        ""
        $VideoUrl
        ""
        "Verify this link in a signed-out browser before submission."
    ) | Set-Content -LiteralPath (Join-Path $staging "$GroupId - Video.txt") -Encoding UTF8

    Get-Content -LiteralPath (Join-Path $projectRoot "output\submission\1 - Data.txt") |
        Set-Content -LiteralPath (Join-Path $staging "$GroupId - Data.txt") -Encoding UTF8

    Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zipPath -Force

    $expectedEntries = @(
        "$GroupId - SC.txt"
        "$GroupId - Report.pdf"
        "$GroupId - Slide$slideExtension"
        "$GroupId - Video.txt"
        "$GroupId - Data.txt"
    ) | Sort-Object
    $archive = [IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        $actualEntries = $archive.Entries |
            ForEach-Object { $_.FullName } |
            Sort-Object
    }
    finally {
        $archive.Dispose()
    }
    if (Compare-Object -ReferenceObject $expectedEntries -DifferenceObject $actualEntries) {
        throw "Submission ZIP does not contain exactly the five required files."
    }
}
catch {
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }
    throw
}
finally {
    if (Test-Path -LiteralPath $stagingFull) {
        if (-not $stagingFull.StartsWith($outputRootFull, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove staging outside the submission output directory."
        }
        Remove-Item -LiteralPath $stagingFull -Recurse -Force
    }
}

Write-Output $zipPath
