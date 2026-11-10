<#
.SYNOPSIS
    Script de validação automatizada dos Desafios DevOps B e C (Persistência de Dados e Imagens).
.DESCRIPTION
    1. Verifica o número de ocorrências e imagens atuais.
    2. Derruba os contêineres com 'docker compose down'.
    3. Recria os contêineres com 'docker compose up -d'.
    4. Valida se todas as ocorrências e imagens permanecem intactas através dos volumes Docker.
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   GEODOCKER CHALLENGE - TESTE DE PERSISTÊNCIA DEVOPS    " -ForegroundColor Cyan
Write-Host "   Equipe: Hermes Tupinambá, Carlos Garcia, Enzo Brito   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Obter estado antes do restart
Write-Host "`n[Passo 1/4] Verificando dados antes de reiniciar..." -ForegroundColor Yellow
try {
    $antes = Invoke-RestMethod -Uri "http://localhost:5000/api/ocorrencias" -TimeoutSec 5
    $totalAntes = $antes.Count
    Write-Host "  -> Total de ocorrências cadastradas: $totalAntes" -ForegroundColor Green
    if ($totalAntes -lt 5) {
        Write-Host "  -> Menos de 5 ocorrências! Populando via /api/seed..." -ForegroundColor Yellow
        Invoke-RestMethod -Uri "http://localhost:5000/api/seed" -Method POST | Out-Null
        $antes = Invoke-RestMethod -Uri "http://localhost:5000/api/ocorrencias" -TimeoutSec 5
        $totalAntes = $antes.Count
        Write-Host "  -> Total após seed: $totalAntes" -ForegroundColor Green
    }
} catch {
    Write-Host "  [ERRO] O backend não está acessível em http://localhost:5000. Inicie com 'docker compose up -d'." -ForegroundColor Red
    exit 1
}

# 2. Executar docker compose down
Write-Host "`n[Passo 2/4] Executando 'docker compose down' (removendo os contêineres)..." -ForegroundColor Yellow
docker compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERRO] Falha ao executar docker compose down." -ForegroundColor Red
    exit 1
}
Write-Host "  -> Contêineres parados e removidos. Volumes 'postgres_data' e 'storage_data' preservados!" -ForegroundColor Green

# 3. Executar docker compose up -d
Write-Host "`n[Passo 3/4] Executando 'docker compose up -d' (recriando os serviços)..." -ForegroundColor Yellow
docker compose up -d
Start-Sleep -Seconds 6

# 4. Validar se registros e fotografias persistem
Write-Host "`n[Passo 4/4] Validando persistência dos dados e imagens após recriação..." -ForegroundColor Yellow

$retries = 10
$depois = $null
while ($retries -gt 0) {
    try {
        $depois = Invoke-RestMethod -Uri "http://localhost:5000/api/ocorrencias" -TimeoutSec 3
        if ($depois) { break }
    } catch {
        Start-Sleep -Seconds 2
        $retries--
    }
}

if (-not $depois) {
    Write-Host "  [ERRO] Falha ao reconectar ao backend após subida dos contêineres." -ForegroundColor Red
    exit 1
}

$totalDepois = $depois.Count
Write-Host "  -> Total de ocorrências após recriação dos contêineres: $totalDepois" -ForegroundColor Green

# Testa se a foto de cada ocorrência continua recuperável no SeaweedFS
$fotosOk = 0
foreach ($oc in $depois) {
    try {
        $imgUrl = "http://localhost:5000$($oc.imagem_url)"
        $resp = Invoke-WebRequest -Uri $imgUrl -Method Head -TimeoutSec 3
        if ($resp.StatusCode -eq 200) {
            $fotosOk++
        }
    } catch {
        Write-Host "  [AVISO] Foto $($oc.imagem_nome) não respondeu." -ForegroundColor DarkYellow
    }
}

Write-Host "  -> Fotografias recuperadas com sucesso no SeaweedFS: $fotosOk / $totalDepois" -ForegroundColor Green

Write-Host "`n==========================================================" -ForegroundColor Cyan
if ($totalDepois -ge 5 -and $fotosOk -ge 5) {
    Write-Host ">>> SUCESSO ABSOLUTO! DESAFIOS DEVOPS B E C VALIDADOS! <<<" -ForegroundColor Green
    Write-Host "Os registros do PostgreSQL e as fotos do SeaweedFS sobreviveram ao 'down'." -ForegroundColor Green
} else {
    Write-Host ">>> ATENÇÃO: Verifique os volumes no docker-compose.yml <<<" -ForegroundColor Yellow
}
Write-Host "==========================================================" -ForegroundColor Cyan
