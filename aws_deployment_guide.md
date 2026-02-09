# AWS Deployment Guide for Sahana Eden

This guide provides instructions for deploying Sahana Eden to Amazon Web Services (AWS) using the provided configuration files.

## Prerequisites
- An AWS Account
- AWS CLI installed and configured
- Docker installed (for building the image locally if needed)

## Option 1: AWS Elastic Beanstalk (Recommended)
Elastic Beanstalk is the easiest way to deploy containerized applications on AWS. It handles provisioning, load balancing, and auto-scaling.

### 1. Prepare the Docker Image
You can use the pre-built image `devinbalkind/sahana-eden:latest` or build your own.

**To build your own:**
```bash
# Build for AMD64 (Required for AWS Elastic Beanstalk default instances)
docker build --platform linux/amd64 -t your-username/sahana-eden:latest .

# Push to Docker Hub
docker push your-username/sahana-eden:latest
```

### 2. Configure `Dockerrun.aws.json`
Ensure `Dockerrun.aws.json` points to the correct image:
```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "devinbalkind/sahana-eden:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8000"
    }
  ]
}
```

### 3. Create Application on AWS
1.  Go to the [AWS Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk).
2.  Click **Create Application**.
3.  **Application Name**: Sahana Eden
4.  **Platform**: Docker
5.  **Platform Branch**: Docker running on 64bit Amazon Linux 2023
6.  **Application Code**: Select **Upload your code** and upload the `Dockerrun.aws.json` file.
7.  **Presets**: Select **Single instance (free tier eligible)** for testing.
8.  Click **Next** and configure:
    -   **Service Access**: Create and use a new service role if needed.
    -   **Instance key pair**: Select a key pair if you want SSH access.
9.  **Environment Properties**:
    -   Add `WEB2PY_PASSWORD` = `your_secure_password` (Default is `password`).
10. Review and **Submit**.

### 4. Access & Verification
Once the environment is **Green (Ready)**, click the URL provided.
-   **Home Page**: `http://<your-env-url>/` (Should redirect to `/eden`)
-   **Health Check**: `http://<your-env-url>/eden/default/health_check`
    -   Use this URL to verify database state and view recent error logs.

## Troubleshooting & Debugging

### 500 Internal Server Errors
If you encounter a "Internal Server Error" or a crash ticket:
1.  Visit the **Health Check** URL: `/eden/default/health_check`
2.  Scroll to the bottom to see **Recent Error Tickets**.
3.  The traceback will pinpoint the exact file and line number of the error.

### Common Issues
-   **Database Missing Records**: The `health_check` will show counts for `SITE_DEFAULT` records in `gis_config` and `gis_hierarchy`. If these are 0, the `setup_map.py` script did not run correctly.
-   **Architecture Mismatch**: Ensure you built the Docker image with `--platform linux/amd64`. AWS EC2 instances (t2/t3) are typically AMD64, while local Macs are ARM64.

## Option 2: AWS EC2 with Docker Compose
This option gives you full control over a single server instance.

1.  **Launch EC2 Instance**:
    - Launch an EC2 instance (e.g., Ubuntu 20.04 or Amazon Linux 2).
    - Ensure the Security Group allows inbound traffic on port **8000** (and 22 for SSH).

2.  **Install Docker and Docker Compose**:
    SSH into your instance and run:
    ```bash
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
    sudo usermod -aG docker $USER
    # Log out and back in for group changes to take effect
    ```

3.  **Deploy**:
    - Copy `docker-compose.aws.yml` to the server as `docker-compose.yml`.
    - Run:
      ```bash
      docker-compose up -d
      ```

4.  **Access**:
    Visit `http://<your-ec2-public-ip>:8000/eden`.

## Production Considerations (Scaling)
- **Database**: For production, it is highly recommended to use an external database like AWS RDS (PostgreSQL) instead of the internal SQLite database. You would need to update `models/000_config.py` with the database connection string.
- **Security**: Change the default password in the `Dockerfile` or pass it as an environment variable.

### Scaling & Environment Types
You can start with a **Single Instance** environment to save costs (~$17/mo) and switch to **Load Balanced** later.

**To switch:**
1.  Go to your Environment in the AWS Console.
2.  Click **Configuration** -> **Capacity** -> **Edit**.
3.  Change **Environment Type** from "Single Instance" to "Load Balanced".
4.  Apply changes.

**Important Warning**:
Before you scale beyond 1 instance, you **MUST** externalize your state:
*   **Database**: You cannot use SQLite. You must use **AWS RDS** (PostgreSQL).
*   **File Uploads**: You cannot store uploads locally. You must configure Eden to use **AWS S3**.
*   **Sessions**: Ensure sessions are stored in the database (default) or a shared cache (Redis), not local files.
