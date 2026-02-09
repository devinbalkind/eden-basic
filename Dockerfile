FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    unzip \
    libpcre2-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt

# Install Web2py
RUN git clone --recursive https://github.com/web2py/web2py.git
# Copy routes.py for default application
COPY routes.py /opt/web2py/routes.py

# Create web2py user
RUN useradd -m web2py

# Set permissions
RUN chown -R web2py:web2py /opt/web2py
WORKDIR /opt/web2py

# Copy Eden application
COPY . applications/eden

# Install Python dependencies
RUN pip install --no-cache-dir -r applications/eden/requirements.txt
# Install key optional dependencies (skip GDAL, selenium, pyserial which need system libs)
RUN pip install --no-cache-dir shapely geopy openpyxl Pillow reportlab xlwt xlrd pyparsing || true

# Configure Eden
RUN cp applications/eden/modules/templates/000_config.py applications/eden/models/000_config.py && \
    sed -i 's/FINISHED_EDITING_CONFIG_FILE = False/FINISHED_EDITING_CONFIG_FILE = True/' applications/eden/models/000_config.py

# Create VERSION file to satisfy Eden's check (if missing in git clone)
RUN echo "Version 2.21.2-stable+timestamp.2021.10.15.07.44.23" > VERSION

# Expose port
EXPOSE 8000

# Start Web2py
# Copy entrypoint script
COPY docker-entrypoint.sh /opt/web2py/docker-entrypoint.sh
RUN chmod +x /opt/web2py/docker-entrypoint.sh

# Set default password (can be overridden)
ENV WEB2PY_PASSWORD=password

# Start Web2py via entrypoint
CMD ["/opt/web2py/docker-entrypoint.sh"]
