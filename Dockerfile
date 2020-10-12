FROM python:3.8
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN apt-get update && apt-get -y upgrade && \
    apt-get clean && \
    addgroup --system app && adduser --disabled-password app --ingroup app
ENV APP_HOME=/code
RUN mkdir $APP_HOME && mkdir $APP_HOME/static
WORKDIR $APP_HOME
COPY . $APP_HOME
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir && \
    chmod +x entrypoint.sh && \
    chown -R app:app /code
USER app
ENTRYPOINT ["/code/entrypoint.sh"]
