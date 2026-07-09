# One-shot installer - Windows PowerShell. One-line run (no admin needed):
#   irm https://raw.githubusercontent.com/rainbowww/skills/main/portable-ai-setup/install.ps1 | iex
# Does: download latest version from GitHub -> install -> apply Claude Code
# semi-auto setting -> open the paste-ready prompt file.
# ASCII-only ON PURPOSE: Windows PowerShell 5.1 reads a saved .ps1 as ANSI/CP949
# without a BOM, so Korean here would break. Korean guidance lives in the
# downloaded prompt files (read as UTF-8 by the editor), not in this launcher.
$ErrorActionPreference = "Stop"

# color boxes: info=white bg, warn=yellow bg, danger=red bg
function Info($m)   { Write-Host " $m " -BackgroundColor White  -ForegroundColor Black }
function Warn($m)   { Write-Host " $m " -BackgroundColor Yellow -ForegroundColor Black }
function Danger($m) { Write-Host " $m " -BackgroundColor Red    -ForegroundColor White }

$repo = "rainbowww/skills"
$branches = @("main", "claude/claude-md-docs-8r1kk7")  # prefer main, fall back to work branch
$files = @(
  "VERSION", "SKILL.md", "README.md", "export.sh", "export.ps1",
  "install.sh", "install.ps1",
  "prompts/universal-system-prompt.md", "prompts/final-work-instruction.md",
  "prompts/claudeai-instructions.md", "prompts/PASTE-claude-ai.txt",
  "templates/CLAUDE.md.template",
  "locations/A-company.md", "locations/B-home.md", "locations/C-school.md"
)

# 1) find a live branch (retry for transient 429)
$base = $null
foreach ($b in $branches) {
  for ($try = 1; $try -le 4; $try++) {
    try {
      # [string] cast is required: a numeric-only VERSION is parsed as Int64 by
      # irm and Int64 has no .Trim(), which would crash here.
      $v = ([string](Invoke-RestMethod "https://raw.githubusercontent.com/$repo/$b/portable-ai-setup/VERSION")).Trim()
      $base = "https://raw.githubusercontent.com/$repo/$b/portable-ai-setup"
      break
    } catch { if ($try -lt 4) { Start-Sleep -Seconds ($try * 3) } }
  }
  if ($base) { break }
}
if (-not $base) { Danger "Package not found on GitHub. Check your internet connection."; exit 1 }

# 2) install into a version folder (per-version isolation avoids confusion)
$dest = Join-Path $HOME "portable-ai-setup_Ver$v"
New-Item -ItemType Directory -Force -Path $dest, "$dest/prompts", "$dest/templates", "$dest/locations" | Out-Null
foreach ($f in $files) {
  # retry up to 4 times for transient errors (e.g. 429)
  $ok = $false
  for ($try = 1; $try -le 4; $try++) {
    try {
      Invoke-WebRequest "$base/$f" -OutFile (Join-Path $dest $f) -UseBasicParsing
      $ok = $true; break
    } catch {
      if ($try -lt 4) { Start-Sleep -Seconds ($try * 3) }
    }
  }
  if (-not $ok) { Danger "Download failed: $f - try again in a moment."; exit 1 }
  # check-then-continue: verify the file exists and is non-empty
  $fp = Join-Path $dest $f
  if (-not (Test-Path $fp) -or ((Get-Item $fp).Length -lt 1)) { Danger "Incomplete download: $f"; exit 1 }
  Start-Sleep -Milliseconds 300  # spacing between requests (rate-limit guard)
}

# 3) Claude Code semi-auto setting (create only if missing - protect existing config)
$ccDir = Join-Path $HOME ".claude"
$ccSettings = Join-Path $ccDir "settings.json"
if (-not (Test-Path $ccSettings)) {
  New-Item -ItemType Directory -Force -Path $ccDir | Out-Null
  '{ "permissions": { "defaultMode": "acceptEdits" } }' | Set-Content $ccSettings -Encoding UTF8
  $running = Get-Process -Name "claude*" -ErrorAction SilentlyContinue
  if ($running) { Warn "Claude Code is running - restart it to apply the semi-auto setting." }
  else          { Info "Claude Code semi-auto setting applied - no restart needed, loads next run." }
} else {
  Info "Claude Code config already exists - left untouched. Toggle semi-auto with Shift+Tab."
}

# 4) done + open the paste-ready file (its whole content is what you paste)
Write-Host ""
Info "Install complete: version $v  ->  $dest"
Info "In the file that opens: Ctrl+A -> Ctrl+C -> paste into your AI tool's instructions box. That's all."
Warn "On a shared PC, delete after use: Remove-Item -Recurse '$dest'"
# notepad is Windows-only - on mac/Linux pwsh just print the path
if ($env:OS -eq "Windows_NT") {
  Start-Process notepad (Join-Path $dest "prompts/PASTE-claude-ai.txt")
} else {
  Info "Paste-ready file: $(Join-Path $dest 'prompts/PASTE-claude-ai.txt')"
}
