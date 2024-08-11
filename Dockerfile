FROM public.ecr.aws/docker/library/python:3.12-slim

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

ENV PORT=8000

WORKDIR /var/task

COPY requirements.lock ./
COPY pyproject.toml ./
COPY README.md ./

RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

COPY src ./src
CMD python src/mess_with_fasthtml/web/main.py 