# Use Python 3.10.9 as the base image
FROM --platform=linux/amd64 python:3.10.9

# Set the working directory to /app
WORKDIR /app

# Upgrade pip and setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

RUN playwright install --with-deps chromium

CMD [ "flask", "run","--host","0.0.0.0","--port","5001"]