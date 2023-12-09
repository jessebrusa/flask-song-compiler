# Use Python 3.11.2 as the base image
FROM python:3.11.2

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev

# Create a virtual environment and activate it
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"
ENV DB_HOST=postgres

# Upgrade pip
RUN pip install --upgrade pip

# Install vim
RUN apt-get update && apt-get install -y vim

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright and its dependencies
RUN playwright install --with-deps chromium

# Expose port 5001
EXPOSE 5001

# Run the application
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5001", "app:app"]