# Dockerfile simples (opcional). Usado quando for necessário construir imagem personalizada.
FROM quay.io/astronomer/astro-runtime:8.8.0

COPY requirements.txt /requirements.txt

USER astro
RUN pip install --no-cache-dir -r /requirements.txt
