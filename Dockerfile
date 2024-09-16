FROM python:latest
 
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --break-system-packages
 
ENV ENV_FOR_DYNACONF="production"

COPY . .

CMD ["python", "-m", "src"]
