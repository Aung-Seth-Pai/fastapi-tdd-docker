# pull official base image
FROM python:3.13.3-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project metadata
COPY pyproject.toml uv.lock ./

RUN uv pip install --no-cache --system .
 
# Copy the rest of the app
COPY . .

# Fix permissions so non-root user can read the app
RUN chown -R appuser:appuser /usr/src/app

# Switch to non-root user
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]