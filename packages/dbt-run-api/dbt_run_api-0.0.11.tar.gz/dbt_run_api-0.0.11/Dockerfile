FROM docker.io/python:3.11 as build-venv
COPY requirements.txt .
RUN apt update && apt upgrade -y && apt install -y build-essential libpq-dev
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -r requirements.txt


FROM docker.io/python:3.11
RUN apt update && apt upgrade -y && apt install -y build-essential postgresql-client && apt clean
ENV APP_HOME /workdir
ENV PATH="/opt/venv/bin:$PATH:$PATH:$APP_HOME"
ENV PYTHONUNBUFFERED=1
RUN useradd -m -d /dbt-runner -s /bin/bash dbt-runner
USER dbt-runner
COPY --chown=dbt-runner:dbt-runner dbt_run_api $APP_HOME/dbt_run_api
COPY --chown=dbt-runner:dbt-runner logs $APP_HOME/
COPY --chown=dbt-runner:dbt-runner --from=build-venv /opt/venv /opt/venv

WORKDIR $APP_HOME
CMD ["uvicorn", "dbt_run_api:app", "--host", "0.0.0.0", "--port", "8000"]
