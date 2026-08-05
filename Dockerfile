FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd -r -u 10001 appuser
COPY --from=build /install /usr/local
COPY app ./app
ENV PORT=8080 PYTHONUNBUFFERED=1
EXPOSE 8080
USER appuser
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "app.main:app"]