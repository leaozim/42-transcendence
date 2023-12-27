coverage run --source='.' manage.py test
coverage_report=$(coverage report -m --omit=*/__init__.py,*urls.py,*factories.py,*/tests/*,*/migrations/*,*/models.py,*apps.py,*admin.py,srcs_core/*,*/forms.py)
coverage=$(echo "$coverage_report" | awk '/T/ {sub(/%/, "", $(NF)); printf "%.0f", $(NF)}')

echo "Relatório de Cobertura:"
echo "$coverage_report"

if [[ -n "$coverage" && "$coverage" -lt 80 ]]; then
    echo "Cobertura menor que 80%: $coverage%"
    exit 1
else
    echo "Cobertura igual ou maior que 80%: $coverage%"
    exit 0
fi
