# ONE-TIME on the PC: makes the chat key, installs cloudflared, creates the tunnel llm.servmod.com -> gateway, autostarts the gateway.
# Run chat_pc_setup.cmd. Nothing secret is printed; the key stays in tools\chat_key.txt (never commit it).
$ErrorActionPreference = "Continue"   # cloudflared writes warnings to stderr
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$keyf = Join-Path $dir "chat_key.txt"
if (-not (Test-Path $keyf)) { $b = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); ([BitConverter]::ToString($b) -replace "-","").ToLower() | Set-Content -NoNewline $keyf; Write-Host "Chat key created: $keyf" }
$models = (ollama list 2>&1 | Out-String); Write-Host "`nOllama models:`n$models`n"
if ($models -notmatch "qwen2.5:14b") { $a = Read-Host "qwen2.5:14b is not installed. Download it now (about 9 GB)? [y/N]"; if ($a -eq "y") { ollama pull qwen2.5:14b } }
if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) { Write-Host "Installing cloudflared..."; winget install --id Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements; $env:Path += ";C:\Program Files (x86)\cloudflared;C:\Program Files\cloudflared" }
function CF($a) { cmd /c "cloudflared $a 2>&1" | Out-Host }   # cmd merges stderr, so warnings do not look like errors
if (-not (Test-Path "$env:USERPROFILE\.cloudflared\cert.pem")) { Write-Host "`nA browser opens: log in to Cloudflare and pick the servmod.com zone."; CF "tunnel login" } else { Write-Host "Cloudflare login already done." }
$name = "servmod-chat"
$have = (cmd /c "cloudflared tunnel list --output json 2>nul" | Out-String)
if ($have -notmatch $name) { CF "tunnel create $name" } else { Write-Host "Tunnel $name already exists." }
CF "tunnel route dns $name llm.servmod.com"
$id = (((cmd /c "cloudflared tunnel list --output json 2>nul" | Out-String) | ConvertFrom-Json) | Where-Object { $_.name -eq $name }).id
$cf = "$env:USERPROFILE\.cloudflared"
@"
tunnel: $id
credentials-file: $cf\$id.json
ingress:
  - hostname: llm.servmod.com
    service: http://127.0.0.1:11500
  - service: http_status:404
"@ | Set-Content "$cf\config-servmod-chat.yml"
# autostart: gateway + tunnel at logon
$py = (Get-Command python).Source
$act1 = New-ScheduledTaskAction -Execute $py -Argument "`"$dir\chat_gateway.py`"" -WorkingDirectory $dir
$act2 = New-ScheduledTaskAction -Execute (Get-Command cloudflared).Source -Argument "tunnel --config `"$cf\config-servmod-chat.yml`" run $name"
$trg = New-ScheduledTaskTrigger -AtLogOn; $set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "ServMod chat gateway" -Action $act1 -Trigger $trg -Settings $set -Force | Out-Null
Register-ScheduledTask -TaskName "ServMod chat tunnel" -Action $act2 -Trigger $trg -Settings $set -Force | Out-Null
Start-ScheduledTask "ServMod chat gateway"; Start-ScheduledTask "ServMod chat tunnel"
Start-Sleep 8
try { Write-Host ("Gateway: " + (Invoke-RestMethod http://127.0.0.1:11500/health | ConvertTo-Json -Compress)) } catch { Write-Host "Gateway not answering yet" -ForegroundColor Yellow }
try { Write-Host ("Tunnel:  " + (Invoke-RestMethod https://llm.servmod.com/health | ConvertTo-Json -Compress)) } catch { Write-Host "Tunnel not answering yet (DNS can take a minute)" -ForegroundColor Yellow }
Write-Host "`nNext: run install_chat_keys.cmd to give the server the address and key." -ForegroundColor Green
