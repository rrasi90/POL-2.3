function Mcp($id, $tool, $toolArgs) {
  $cfg = Get-Content "C:\Users\rrasi_oorj8fq\AppData\Local\OpenPencil\mcp.json" -Raw | ConvertFrom-Json
  $h = @{ Authorization = "Bearer $($cfg.authToken)"; Accept = "application/json, text/event-stream"; "Mcp-Session-Id" = $script:McpSessionId }
  $payload = @{ jsonrpc = "2.0"; id = $id; method = "tools/call"; params = @{ name = $tool; arguments = $toolArgs } } | ConvertTo-Json -Depth 8 -Compress
  $raw = (Invoke-WebRequest -Uri "http://127.0.0.1:7600/mcp" -Method Post -Headers $h -ContentType "application/json" -Body ([System.Text.Encoding]::UTF8.GetBytes($payload)) -UseBasicParsing -TimeoutSec 60).Content
  if ($raw.StartsWith("event:")) {
    $line = ($raw -split "`n" | Where-Object { $_ -like "data:*" } | Select-Object -Last 1)
    $raw = $line.Substring(5)
  }
  $r = $raw | ConvertFrom-Json
  if ($null -eq $r.result -or $r.result.isError) { Write-Host ("RAW: " + $raw); throw "MCP $tool failed" }
  return $r.result.content[0].text
}

function McpInit {
  $cfg = Get-Content "C:\Users\rrasi_oorj8fq\AppData\Local\OpenPencil\mcp.json" -Raw | ConvertFrom-Json
  $h = @{ Authorization = "Bearer $($cfg.authToken)"; Accept = "application/json, text/event-stream"; "Content-Type" = "application/json" }
  $init = @{ jsonrpc="2.0"; id=1; method="initialize"; params=@{ protocolVersion="2024-11-05"; capabilities=@{}; clientInfo=@{ name="opencode"; version="1.0" } } } | ConvertTo-Json -Depth 6 -Compress
  $r = Invoke-WebRequest -Uri "http://127.0.0.1:7600/mcp" -Method Post -Headers $h -ContentType "application/json" -Body ([System.Text.Encoding]::UTF8.GetBytes($init)) -UseBasicParsing -TimeoutSec 15
  $script:McpSessionId = $r.Headers['Mcp-Session-Id']
  $h2 = $h.Clone(); $h2["Mcp-Session-Id"] = $script:McpSessionId
  $notif = @{ jsonrpc="2.0"; method="notifications/initialized" } | ConvertTo-Json -Compress
  $null = Invoke-WebRequest -Uri "http://127.0.0.1:7600/mcp" -Method Post -Headers $h2 -ContentType "application/json" -Body ([System.Text.Encoding]::UTF8.GetBytes($notif)) -UseBasicParsing
  Write-Output "SESSION: $script:McpSessionId"
}
