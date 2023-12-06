FROM --platform=linux/amd64 postgres:16.0

ENV POSTGRES_USER="postgres"
ENV POSTGRES_PASSWORD="p48dT7k78n$G756JrcS%"
ENV POSTGRES_DB="song-compiler"

# Stop the PostgreSQL service
RUN service postgresql stop

# Remove the existing data directory if it exists
RUN rm -rf /var/lib/postgresql/data

# Copy the custom SQL script
COPY init.sql /docker-entrypoint-initdb.d/

# Create the directory and update pg_hba.conf
RUN mkdir -p /etc/postgresql/16/main/ && \
    echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/16/main/pg_hba.conf
