FROM python:3.12.0-slim-bookworm

ENV PYTHONBUFFERED=1 \
    PYTHONWRITEBYTECODE=1 \
    APP=/app

WORKDIR $APP

COPY requirements.txt $APP
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . $APP

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangoproj.wsgi"]
