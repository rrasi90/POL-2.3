function Mcp($id, $tool, $toolArgs) {
  $h = @{ Authorization = "Bearer ece8509c5f45bc233a7b3452d7dd0dad816f4d702380197cf41bfc1910d93856"; Accept = "application/json, text/event-stream"; "Mcp-Session-Id" = "fe4d5663-8629-41d1-9863-af0ae5df653d" }
  $payload = @{ jsonrpc = "2.0"; id = $id; method = "tools/call"; params = @{ name = $tool; arguments = $toolArgs } } | ConvertTo-Json -Depth 8 -Compress
  $raw = (Invoke-WebRequest -Uri "http://127.0.0.1:7600/mcp" -Method Post -Headers $h -ContentType "application/json" -Body ([System.Text.Encoding]::UTF8.GetBytes($payload)) -UseBasicParsing).Content
  $r = $raw | ConvertFrom-Json
  if ($null -eq $r.result -or $r.result.isError) { Write-Host ("RAW: " + $raw); throw "MCP $tool failed" }
  return $r.result.content[0].text
}
