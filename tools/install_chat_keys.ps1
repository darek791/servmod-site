# ONE-TIME: gives the server the chat address and the key from tools\chat_key.txt (added to /etc/servmod/pay.env). Switches the chat widget on.
# Run chat_pc_setup first. To switch the chat off again: run with the word OFF as the first argument.
param([string]$mode = "on")
$ErrorActionPreference = "Stop"
$srv = "root@167.233.108.235"; $key = "$env:USERPROFILE\.ssh\id_ed25519"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($mode -ieq "off") { $body = ""; $cmd = "sed -i '/^CHAT_/d' /etc/servmod/pay.env; systemctl restart servmod-api; sleep 2; curl -fsS http://127.0.0.1:8100/api/chat/status; echo" }
else {
  $k = (Get-Content (Join-Path $dir "chat_key.txt") -Raw).Trim()
  if ($k -notmatch '^[0-9a-f]{64}$') { throw "chat_key.txt missing or wrong" }
  $body = "CHAT_URL=https://llm.servmod.com`nCHAT_KEY=$k`nCHAT_MODEL=qwen2.5:14b`n"
  $cmd = "umask 077; touch /etc/servmod/pay.env; sed -i '/^CHAT_/d' /etc/servmod/pay.env; cat >> /etc/servmod/pay.env; chown root:servmod /etc/servmod/pay.env; chmod 640 /etc/servmod/pay.env; systemctl restart servmod-api; sleep 2; systemctl is-active servmod-api; curl -fsS http://127.0.0.1:8100/api/chat/status; echo"
}
($body -replace "`r","") | ssh -i $key $srv $cmd
Write-Host "`nDone. With the chat on, the 'Ask ServMod' button appears on servmod.com." -ForegroundColor Green
