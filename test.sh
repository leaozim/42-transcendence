coverage=$(coverage report -m --omit=*/__init__.py,*urls.py,*factories.py,*/tests/*,*/migrations/*,*/models.py,*apps.py,*admin.py,srcs_core/*,*/forms.py | awk '/T/ {sub(/%/, "", $(NF)); printf "%.0f", $(NF)}')

if [[ -n "$coverage" && "$coverage" -lt 80 ]]; then
    echo "Cobertura menor que 80%: $coverage%"
    exit 1
else
    echo "Sucesso! Cobertura em: $coverage%"
    exit 0
fi
