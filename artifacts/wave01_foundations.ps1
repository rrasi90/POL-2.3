$ErrorActionPreference = "Stop"
. "C:\Star\pol\2.4\artifacts\mcp_common.ps1"
$D = @{ document_id = "tab-2" }

# ---- 1. token collections (Light + Night as parallel collections; no multi-mode tool) ----
$collections = (Mcp 41 "list_collections" $D | ConvertFrom-Json)
$existingLight = ($collections.collections | Where-Object name -eq "pol.light").id
$existingNight = ($collections.collections | Where-Object name -eq "pol.night").id

$tokens = @(
  @("bg.canvas","#F7F9FC","#0F141C"), @("surface.default","#FFFFFF","#151C27"),
  @("surface.subtle","#F1F5F9","#1B2431"), @("surface.elevated","#FFFFFF","#202A38"),
  @("border.subtle","#E2E8F0","#2A3646"), @("border.strong","#CBD5E1","#3A4A5F"),
  @("text.primary","#0F172A","#F8FAFC"), @("text.secondary","#475569","#CBD5E1"),
  @("text.muted","#64748B","#94A3B8"), @("text.disabled","#94A3B8","#64748B"),
  @("brand.primary","#2563EB","#60A5FA"), @("brand.hover","#1D4ED8","#93C5FD"),
  @("brand.active","#1E40AF","#3B82F6"), @("brand.accent","#4F46E5","#818CF8"),
  @("semantic.success","#15803D","#4ADE80"), @("semantic.warning","#B45309","#FBBF24"),
  @("semantic.danger","#B91C1C","#F87171"), @("semantic.info","#1D4ED8","#60A5FA"),
  @("focus.ring","#2563EB","#93C5FD")
)
if ($existingLight -and $existingNight) {
  $colLight = $existingLight; $colNight = $existingNight
  Write-Output "COLL reuse light=$colLight night=$colNight"
  $varMap = @{}
  $lv = (Mcp 46 "list_variables" (@{ type = "COLOR" } + $D) | ConvertFrom-Json)
  foreach ($v in $lv.variables) {
    $side = if ($v.collectionId -eq $colLight -or $v.collection_id -eq $colLight) { "light" } else { "night" }
    if (-not $varMap.ContainsKey($v.name)) { $varMap[$v.name] = @{} }
    $varMap[$v.name][$side] = $v.id
  }
  # fallback: query each collection
  if ($varMap.Count -eq 0 -or -not $varMap["bg.canvas"]) {
    foreach ($pair in @(@("light",$colLight),@("night",$colNight))) {
      $varsInCol = (Mcp 47 "list_variables" $D | ConvertFrom-Json)
    }
  }
} else {
$colLight = ((Mcp 44 "create_collection" (@{ name = "pol.light" } + $D) | ConvertFrom-Json)).id
$colNight = ((Mcp 45 "create_collection" (@{ name = "pol.night" } + $D) | ConvertFrom-Json)).id
Write-Output "COLL light=$colLight night=$colNight"
$varMap = @{}
$i = 50
foreach ($t in $tokens) {
  $n = $t[0]
  $lv = ((Mcp $i "create_variable" (@{ name = $n; type = "COLOR"; collection_id = $colLight; value = $t[1] } + $D) | ConvertFrom-Json)).id
  $nv = ((Mcp ($i+1) "create_variable" (@{ name = $n; type = "COLOR"; collection_id = $colNight; value = $t[2] } + $D) | ConvertFrom-Json)).id
  $varMap[$n] = @{ light = $lv; night = $nv }
  $i += 2
}
Write-Output "VARS: $($varMap.Count) pairs"
# FLOAT scale tokens
foreach ($f in @(@("radius.xs",4),@("radius.sm",8),@("radius.md",12),@("radius.lg",16),@("radius.xl",20),@("space.1",4),@("space.2",8),@("space.3",12),@("space.4",16),@("space.5",20),@("space.6",24),@("space.7",32),@("space.8",40),@("space.9",48),@("space.10",64))) {
  $null = Mcp $i "create_variable" (@{ name = $f[0]; type = "FLOAT"; collection_id = $colLight; value = "$($f[1])" } + $D); $i++
}
Write-Output "FLOAT scale tokens created"
}

# ---- 2. Foundations board ----
function SwatchRow($token, $light, $night, $y) {
  "<frame name=""row $token"" width={920} height={44} fill=""#FFFFFF00"" x={24} y={$y}>" +
  "<frame name=""swl $token"" width={36} height={36} fill=""$light"" cornerRadius={6} x={0} y={4}></frame>" +
  "<text fontSize={13} fill=""#475569"" x={52} y={13}>$token</text>" +
  "<text fontSize={12} fill=""#64748B"" x={300} y={14}>$light</text>" +
  "<frame name=""swn $token"" width={36} height={36} fill=""$night"" cornerRadius={6} x={560} y={4}></frame>" +
  "<text fontSize={12} fill=""#64748B"" x={612} y={14}>$night</text>" +
  "</frame>"
}
$rows = ""
$y = 76
foreach ($t in $tokens) { $rows += SwatchRow $t[0] $t[1] $t[2] $y; $y += 48 }

$typeRows = ""
$types = @(@("Display XL",32,40),@("Display L",28,36),@("Heading 1",24,32),@("Heading 2",20,28),@("Heading 3",18,26),@("Title",16,24),@("Body",14,22),@("Body Small",13,20),@("Label",12,18),@("Caption",11,16))
$ty = 76
foreach ($tp in $types) {
  $typeRows += "<frame name=""type $($tp[0])"" width={520} height={54} fill=""#FFFFFF"" cornerRadius={8} x={24} y={$ty}>" +
  "<text fontSize={$($tp[1])} fill=""#0F172A"" x={16} y={8}>$($tp[0])</text>" +
  "<text fontSize={11} fill=""#64748B"" x={340} y={20}>$($tp[1]) / $($tp[2])</text></frame>"
  $ty += 60
}

$spacingRows = ""
$sy = 0
foreach ($s in @(@("space.1",4),@("space.2",8),@("space.3",12),@("space.4",16),@("space.5",20),@("space.6",24),@("space.7",32),@("space.8",40),@("space.9",48),@("space.10",64))) {
  $spacingRows += "<frame name=""sp $($s[0])"" width={520} height={26} fill=""#FFFFFF00"" x={0} y={$sy}>" +
  "<frame name=""spbar $($s[0])"" width={$($s[1])} height={14} fill=""#2563EB"" cornerRadius={3} x={120} y={6}></frame>" +
  "<text fontSize={11} fill=""#475569"" x={0} y={6}>$($s[0])</text>" +
  "<text fontSize={11} fill=""#64748B"" x={260} y={6}>$($s[1])px</text></frame>"
  $sy += 28
}

$radiusRows = ""
$ry = 0
foreach ($r in @(@("radius.xs",4),@("radius.sm",8),@("radius.md",12),@("radius.lg",16),@("radius.xl",20))) {
  $radiusRows += "<frame name=""rad $($r[0])"" width={520} height={56} fill=""#FFFFFF00"" x={0} y={$ry}>" +
  "<frame name=""radbox $($r[0])"" width={44} height={44} fill=""#F1F5F9"" stroke=""#CBD5E1"" strokeWidth={1} cornerRadius={$($r[1])} x={120} y={4}></frame>" +
  "<text fontSize={11} fill=""#475569"" x={0} y={22}>$($r[0])</text>" +
  "<text fontSize={11} fill=""#64748B"" x={260} y={22}>$($r[1])px</text></frame>"
  $ry += 60
}

$boardJsx = "<frame name=""WAVE-01 Foundations"" width={2000} height={1780} fill=""#F7F9FC"" cornerRadius={16}>" +
"<text fontSize={26} fontWeight={700} fill=""#0F172A"" x={32} y={28}>POL Precision Commerce - Design Foundations</text>" +
"<text fontSize={13} fill=""#64748B"" x={32} y={66}>Source: 56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md | Master Tree v4.3.0 | tokens: pol.light / pol.night collections</text>" +
"<text fontSize={15} fontWeight={600} fill=""#0F172A"" x={24} y={104}>Color tokens (Light | Night)</text>" +
$rows +
"<frame name=""col-type"" width={560} height={700} fill=""#FFFFFF00"" x={1000} y={100}>" +
"<text fontSize={15} fontWeight={600} fill=""#0F172A"" x={24} y={0}>Type scale (Vazirmatn)</text>" +
$typeRows + "</frame>" +
"<frame name=""col-spacing"" width={560} height={300} fill=""#FFFFFF00"" x={1000} y={880}>" +
"<text fontSize={15} fontWeight={600} fill=""#0F172A"" x={24} y={0}>Spacing (4px base)</text>" +
$spacingRows + "</frame>" +
"<frame name=""col-radius"" width={560} height={320} fill=""#FFFFFF00"" x={1000} y={1240}>" +
"<text fontSize={15} fontWeight={600} fill=""#0F172A"" x={24} y={0}>Radius</text>" +
$radiusRows + "</frame>" +
"</frame>"

[IO.File]::WriteAllText("C:\Star\pol\2.4\artifacts\board.jsx", $boardJsx, [Text.Encoding]::UTF8)
$board = (Mcp 90 "render" (@{ document_id = "tab-2"; x = 2200; y = 0; jsx = $boardJsx }))
$boardId = ($board | ConvertFrom-Json).id
Write-Output "BOARD: $boardId"

# ---- 3. bind swatches to variables ----
if ($varMap.Count -eq 0 -or -not $varMap["bg.canvas"]) {
  $lvx = (Mcp 46 "list_variables" (@{ type = "COLOR" } + $D) | ConvertFrom-Json)
  $varMap = @{}
  foreach ($v in $lvx.variables) {
    $side = if ($v.collectionId -eq $colLight) { "light" } else { "night" }
    if (-not $varMap.ContainsKey($v.name)) { $varMap[$v.name] = @{} }
    $varMap[$v.name][$side] = $v.id
  }
}
$bound = 0
foreach ($t in $tokens) {
  $n = $t[0]
  $ln = (Mcp 100 "find_nodes" (@{ name = "swl $n" } + $D) | ConvertFrom-Json)
  $nn = (Mcp 101 "find_nodes" (@{ name = "swn $n" } + $D) | ConvertFrom-Json)
  $lnid = $ln.nodes[0].id
  $nnid = $nn.nodes[0].id
  if ($lnid -and $varMap[$n] -and $varMap[$n]["light"]) { $null = Mcp 102 "bind_variable" (@{ node_id = $lnid; field = "fills/0/color"; variable_id = $varMap[$n]["light"] } + $D); $bound++ }
  if ($nnid -and $varMap[$n] -and $varMap[$n]["night"]) { $null = Mcp 103 "bind_variable" (@{ node_id = $nnid; field = "fills/0/color"; variable_id = $varMap[$n]["night"] } + $D); $bound++ }
}
Write-Output "BOUND: $bound"

# ---- 4. save + export evidence ----
Write-Output (Mcp 104 "save_file" $D)
$imgRaw = (Mcp 105 "export_image" (@{ ids = @($boardId); format = "PNG"; maxEdge = 2000 } + $D))
if ([string]::IsNullOrWhiteSpace($imgRaw)) { Write-Output "EXPORT EMPTY, retry..."; Start-Sleep -Seconds 2; $imgRaw = (Mcp 106 "export_image" (@{ ids = @($boardId); format = "PNG"; maxEdge = 1600 } + $D)) }
$imgObj = $imgRaw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path "C:\Star\pol\2.4\artifacts\evidence" | Out-Null
$png = $imgObj.data; if (-not $png) { $png = $imgObj.base64 }; if (-not $png) { $png = $imgObj.png }
if ($png) {
  [IO.File]::WriteAllBytes("C:\Star\pol\2.4\artifacts\evidence\wave01_foundations.png", [Convert]::FromBase64String($png))
  Write-Output "EVIDENCE PNG saved: $((Get-Item 'C:\Star\pol\2.4\artifacts\evidence\wave01_foundations.png').Length) bytes"
} else {
  Write-Output ("EXPORT KEYS: " + (($imgObj | Get-Member -MemberType NoteProperty | ForEach-Object Name) -join ","))
  Write-Output ("EXPORT RESP: " + $imgRaw.Substring(0, [Math]::Min(300, $imgRaw.Length)))
}

# structural inspection evidence
Write-Output (Mcp 106 "get_node" (@{ id = $boardId; depth = 1 } + $D))
Write-Output "DONE"




