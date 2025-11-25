#!/usr/bin/env powershell
# Remove duplicate HTML content from index.html

$htmlPath = "C:\Users\yurij.prodan\SEO_Machine_2\frontend\index.html"
$lines = Get-Content $htmlPath

# Keep only lines 1-480 and 681-end (remove duplicate between 481-680)
$cleanedLines = @()
$cleanedLines += $lines[0..479]  # Lines 1-480
$cleanedLines += $lines[680..($lines.Length - 1)]  # Lines 681-end

Set-Content $htmlPath -Value $cleanedLines
Write-Host "Removed duplicate content from index.html"
Write-Host "New line count: $($cleanedLines.Length)"
