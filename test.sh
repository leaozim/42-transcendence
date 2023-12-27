coverage=$(awk '/T/ {sub(/%/, "", $(NF)); printf "%.0f", $(NF)}' teste.txt)

if [[ -n "$coverage" && "$coverage" -lt 80 ]]; then
    exit 1
else
    exit 0
fi
