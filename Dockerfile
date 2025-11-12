# Base Python image
FROM python:3.11

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install pipenv
RUN pip install pipenv

# Set container working directory
WORKDIR /app

# Copy Pipfile first to leverage Docker cache
COPY Pipfile Pipfile.lock /app/

# Install dependencies using system packages (no virtualenv inside container)
RUN pipenv install --system --deploy

# Copy project files
COPY . /app/

# Expose Django default port
EXPOSE 8001

# Start Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]