# Dockerfile

# Use a imagem oficial do Python como base
FROM python:3.11.4

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY transcendence/requirements/local.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r local.txt

# Copia o restante do código para o diretório de trabalho
COPY . .

# Expõe a porta 8000, que é a porta padrão para projetos Django
EXPOSE 8000

# Comando padrão para executar o aplicativo quando o contêiner for iniciado
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
