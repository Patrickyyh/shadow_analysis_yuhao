FROM python:3.11.4
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN mkdir /app

WORKDIR /app

COPY . /app/


RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -rf /root/.cache/pip
CMD ["python" ,"/app/manage.py", "runserver", "0.0.0.0:8000"]


