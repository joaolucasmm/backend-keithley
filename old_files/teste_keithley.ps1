# teste_keithley.ps1
# Script para testar a API da Keithley 2611B
# Para Rodar: powershell -ExecutionPolicy Bypass -File teste_keithley.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Teste da API Keithley 2611B" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Teste 1: Health Check
Write-Host "1. Testando Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -ErrorAction Stop
    Write-Host "   Status: $($health.status)" -ForegroundColor Green
    Write-Host "   Servico: $($health.servico)" -ForegroundColor Green
} catch {
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Teste 2: Conexão com Keithley
Write-Host "2. Verificando conexao com Keithley..." -ForegroundColor Yellow
try {
    $conexao = Invoke-RestMethod -Uri "http://localhost:8000/api/testar_conexao" -Method Get -ErrorAction Stop
    
    if ($conexao.status -eq "conectado") {
        Write-Host "   Status: CONECTADO" -ForegroundColor Green
        Write-Host "   Instrumento: $($conexao.instrumento)" -ForegroundColor Green
        Write-Host "   Endereco USB: USB0::0x05E6::0x2611::4629001::INSTR" -ForegroundColor Gray
    } else {
        Write-Host "   Status: $($conexao.status)" -ForegroundColor Red
        Write-Host "   Mensagem: $($conexao.mensagem)" -ForegroundColor Red
    }
} catch {
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Verifique se o servidor backend esta rodando (python main.py)" -ForegroundColor Yellow
}
Write-Host ""

# Teste 3: Medição de Tensão
Write-Host "3. Testando medicao de tensao (3 leituras)..." -ForegroundColor Yellow
$bodyTensao = @{
    num_leituras = 3
    delay_entre_leituras = 0.5
    modo_medicao = "tensao"
    nivel_tensao_aplicada = 0.0
}

try {
    $bodyJson = $bodyTensao | ConvertTo-Json
    $medicao = Invoke-RestMethod -Uri "http://localhost:8000/api/medir" -Method Post -Body $bodyJson -ContentType "application/json" -ErrorAction Stop
    
    if ($medicao.status -eq "sucesso") {
        Write-Host "   Status: $($medicao.status)" -ForegroundColor Green
        Write-Host "   Valores: $($medicao.medicoes -join ', ') V" -ForegroundColor Cyan
    } else {
        Write-Host "   Erro: $($medicao.mensagem)" -ForegroundColor Red
    }
} catch {
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Resumo final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO DA CONEXAO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    $resumo = Invoke-RestMethod -Uri "http://localhost:8000/api/testar_conexao" -Method Get -ErrorAction Stop
    
    if ($resumo.status -eq "conectado") {
        Write-Host ""
        Write-Host "KEITHLEY 2611B - CONECTADA" -ForegroundColor Green
        Write-Host "   Identificacao: $($resumo.instrumento)" -ForegroundColor White
        Write-Host "   Endereco USB: USB0::0x05E6::0x2611::4629001::INSTR" -ForegroundColor White
        Write-Host "   Status: Pronto para medicoes" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "KEITHLEY 2611B - DESCONECTADA" -ForegroundColor Red
        Write-Host "   $($resumo.mensagem)" -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "ERRO: Nao foi possivel conectar ao servidor" -ForegroundColor Red
    Write-Host "Verifique se o backend esta rodando: python main.py" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testes concluidos!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Read-Host "`nPressione Enter para sair"