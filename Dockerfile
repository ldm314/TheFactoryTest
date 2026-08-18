# The application The Factory built. Generated; not edited by hand.
FROM python:3.12-slim

RUN pip install --no-cache-dir "psycopg[binary]==3.3.4" \
 && useradd --create-home --uid 10001 app

WORKDIR /srv
COPY . /srv
USER app

# The database is the application's, not this image's: DATABASE_URL points at it.
ENV PORT=8080
EXPOSE 8080
CMD ["python", "app.py"]
