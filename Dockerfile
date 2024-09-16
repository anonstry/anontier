FROM python:latest
 
COPY requirements.txt .
RUN pip install -r requirements.txt --break-system-packages
 
ENV ENV_FOR_DYNACONF="production"

#COPY app .
#COPY assets .
#COPY .secrets.toml .
COPY . .

CMD ["python", "-m", "app"]
