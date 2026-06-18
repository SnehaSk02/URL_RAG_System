# Change the base image to match your local version
FROM python:3.11.9-slim

WORKDIR /code

# Copy and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of your backend code
COPY . .

# Run your API
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "7860"]