FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p static && bandit -r . -f html -o static/bandit_report.html || true
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
