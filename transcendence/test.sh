# coverage run --source='.' /transcendence/covmanage.py test
# coverage_report=$(coverage report -m --omit=*/__init__.py,*urls.py,*factories.py,*/tests/*,*/migrations/*,*/models.py,*apps.py,*admin.py,srcs_core/*,*/forms.py,*/views.py)
# coverage=$(echo "$coverage_report" | awk '/T/ {sub(/%/, "", $(NF)); printf "%.0f", $(NF)}')

# echo "Relatório de Cobertura:"
# echo "$coverage_report"

# if [[ -n "$coverage" && "$coverage" -lt 80 ]]; then
#     echo "Cobertura menor que 80%: $coverage%"
#     exit 1
# else
#     echo "Cobertura igual ou maior que 80%: $coverage%"
#     exit 0
# fi

#!/bin/bash

COVERAGE_DIR=/transcendence/coverage/

# Ajuste o caminho do arquivo .coverage
coverage run --source='.' /transcendence/manage.py test
coverage xml -o "$COVERAGE_DIR/coverage.xml"

coverage_report=$(coverage report -m --omit=*/__init__.py,*urls.py,*factories.py,*/tests/*,*/migrations/*,*/models.py,*apps.py,*admin.py,srcs_core/*,*/forms.py,*/views.py)
coverage=$(echo "$coverage_report" | awk '/T/ {sub(/%/, "", $(NF)); printf "%.0f", $(NF)}')

echo "Relatório de Cobertura:"
echo "$coverage_report"

# Adicione o caminho para o diretório de cobertura

if [[ -n "$coverage" && "$coverage" -lt 80 ]]; then
    echo "Cobertura menor que 80%: $coverage%"
    exit 1
else
    echo "Cobertura igual ou maior que 80%: $coverage%"
    exit 0
fi

