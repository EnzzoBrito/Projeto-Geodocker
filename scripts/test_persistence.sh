#!/usr/bin/env bash
# =============================================================================
# Script de validação dos Desafios DevOps B e C para Linux / Git Bash / macOS
# =============================================================================

set -e

echo -e "\033[1;36m==========================================================\033[0m"
echo -e "\033[1;36m   GEODOCKER CHALLENGE - TESTE DE PERSISTÊNCIA DEVOPS    \033[0m"
echo -e "\033[1;36m   Equipe: Hermes Tupinambá, Carlos Garcia, Enzo Brito   \033[0m"
echo -e "\033[1;36m==========================================================\033[0m"

echo -e "\n\033[1;33m[Passo 1/4] Verificando dados antes do restart...\033[0m"
curl -s http://localhost:5000/api/seed -X POST > /dev/null
TOTAL_ANTES=$(curl -s http://localhost:5000/api/ocorrencias | grep -o '"id":' | wc -l)
echo -e "  -> Total de ocorrências cadastradas: $TOTAL_ANTES"

echo -e "\n\033[1;33m[Passo 2/4] Executando 'docker compose down'...\033[0m"
docker compose down
echo -e "  -> Contêineres removidos. Volumes preservados."

echo -e "\n\033[1;33m[Passo 3/4] Executando 'docker compose up -d'...\033[0m"
docker compose up -d
sleep 6

echo -e "\n\033[1;33m[Passo 4/4] Validando persistência dos dados e imagens...\033[0m"
TOTAL_DEPOIS=$(curl -s http://localhost:5000/api/ocorrencias | grep -o '"id":' | wc -l)
echo -e "  -> Total de ocorrências após recriação: $TOTAL_DEPOIS"

if [ "$TOTAL_DEPOIS" -ge 5 ]; then
    echo -e "\n\033[1;32m==========================================================\033[0m"
    echo -e "\033[1;32m>>> SUCESSO! DESAFIOS B E C VALIDADOS COM ÊXITO! <<<       \033[0m"
    echo -e "\033[1;32m==========================================================\033[0m"
else
    echo -e "\n\033[1;31m>>> ERRO: Dados não persistiram. Verifique os volumes. <<<\033[0m"
    exit 1
fi
