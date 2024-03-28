coverage() {
	python -m coverage $@
}

coverage erase
coverage run manage.py test
coverage_report=$(coverage report -m --omit=*/__init__.py,*urls.py,*factories.py,*/tests/*,*/migrations/*,*/models.py,*apps.py,*admin.py,srcs_core/*,*/forms.py,*/views.py)
coverage_result=$(echo "$coverage_report" | awk '/T/ {sub(/%/, "", $(NF)); printf "%.0f", $(NF)}')

echo "Relatório de Cobertura:"
echo "$coverage_report"

if [[ -n "$coverage_result" && "$coverage_result" -lt 80 ]]; then
    echo "Cobertura menor que 80%: $coverage_result%"
    exit 1
else
    echo "Cobertura igual ou maior que 80%: $coverage_result%"
    exit 0
fi
