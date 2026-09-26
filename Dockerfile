# The application The Factory built. Generated; not edited by hand.
FROM python:3.12-slim

WORKDIR /srv
COPY requirements.txt /srv/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
 && useradd --create-home --uid 10001 app

COPY . /srv
USER app

ENV PORT=8080
EXPOSE 8080
CMD ["python", "app.py"]
