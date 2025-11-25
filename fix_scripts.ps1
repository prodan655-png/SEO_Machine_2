#!/usr/bin/env powershell
# Revert index.html to fix script order

$htmlPath = "C:\Users\yurij.prodan\SEO_Machine_2\frontend\index.html"
$content = Get-Content $htmlPath -Raw

# Find and replace script order
$content = $content -replace '<script src="diff-tracking.js"></script>\r?\n\s*<script src="keyword-highlighting.js"></script>\r?\n\s*<script src="surfer-integration.js"></script>\r?\n\s*<script src="app.js"></script>', '<script src="app.js"></script>
    <script src="diff-tracking.js"></script>
    <script src="keyword-highlighting.js"></script>
    <script src="surfer-integration.js"></script>'

Set-Content $htmlPath -Value $content -NoNewline
Write-Host "Fixed script order in index.html"
