# Sandbox Instructions: Sahana Eden (Docker Demo)

> [!WARNING]
> **FOR EVALUATION ONLY**. This configuration is not secure or performant enough for real-world deployment.


I have successfully installed the code, fixed several compatibility issues with the latest Web2py version, and verified the application locally.

## Changes Made
1.  **Fixed `modules/updatechk.py`**: Resolved an `IndexError` caused by empty lines in requirements files.
2.  **Fixed `modules/core/resource/importer.py`**: Resolved a `TypeError` by updating the `_filter_fields` call to be compatible with the latest PyDAL version (`id=True` -> `allow_id=True`).
3.  **Fixed `setup_map.py`**: Resolved an `IntegrityError` by checking for existing projections by name to prevent duplicate insertions.

## Deployment Steps

### 1. Build the Docker Image
You need to build the Docker image for the `linux/amd64` platform (required for AWS Elastic Beanstalk).

```bash
# Replace 'your-username' with your Docker Hub username
docker build --platform linux/amd64 -t your-username/sahana-eden:latest .
```

### 2. Push to Docker Hub
Push the built image to your Docker Hub repository.

```bash
docker push your-username/sahana-eden:latest
```

### 3. Update Configuration
Edit `Dockerrun.aws.json` to point to your Docker image.

**File:** `Dockerrun.aws.json`
```json
{
    "AWSEBDockerrunVersion": "1",
    "Image": {
        "Name": "your-username/sahana-eden:latest",  <-- UPDATE THIS LINE
        "Update": "true"
    },
    "Ports": [
        {
            "ContainerPort": "8000"
        }
    ],
    "Logging": "/var/log/web2py"
}
```

### 4. Deploy to AWS Elastic Beanstalk (Detailed Instructions)

1.  **Go to the Console**: Visit the [AWS Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk).
2.  **Create Application**: Click the orange **Create Application** button.
3.  **Configure Application Information**:
    *   **Application Name**: Enter `Sahana Eden` (or your preferred name).
    *   **Application Tags**: (Optional) Leave blank.
4.  **Platform**:
    *   **Platform**: Select **Docker**.
    *   **Platform Branch**: Select **Docker running on 64bit Amazon Linux 2023** (Recommended).
    *   **Platform Version**: Select the latest available version (e.g., 4.0.0).
5.  **Application Code**:
    *   Select **Upload your code**.
    *   **Version Label**: Enter a version label (e.g., `v1-initial-deploy`).
    *   **Source Code Origin**: Select **Local file**.
    *   **Choose File**: Click the button and upload the `Dockerrun.aws.json` file from your project directory.
6.  **Presets**:
    *   Select **Single instance (free tier eligible)**. This is best for testing and low cost.
7.  **Next Steps (Wizard)**: Click **Next** to proceed through the configuration wizard.
    *   **Service Access**:
        *   **Service Role**: Select **Create and use new service role** (if this is your first time) or select an existing one like `aws-elasticbeanstalk-service-role`.
        *   **EC2 Key Pair**: (Optional) Select an SSH key pair if you want to be able to SSH into the instance later.
        *   **EC2 Instance Profile**: Select **Create and use new instance profile** or use an existing one like `aws-elasticbeanstalk-ec2-role`.
    *   **Virtual Private Cloud (VPC)**: You can usually leave this as default (default VPC).
    *   **Instance Traffic and Scaling**: Leave defaults for Single Instance.
8.  **Environment Properties (Important)**:
    *   Scroll down to the **Environment properties** section (usually in the "Configure updates, monitoring, and logging" step or "Modify" software settings).
    *   Add a new property:
        *   **Name**: `WEB2PY_PASSWORD`
        *   **Value**: `your_secure_password` (Choose a strong password).
9.  **Review and Submit**: Review your settings and click **Submit**.

## Verification
Once the environment status turns **Green (Ready)** (this takes about 5-10 minutes):
1.  Click the URL provided near the top of the dashboard (e.g., `http://sahana-eden-env.eba-xyz.us-east-1.elasticbeanstalk.com`).
2.  It should redirect you to the Sahana Eden home page.
3.  Check the health check URL:
    `http://<your-env-url>/eden/default/health_check`

It should return **200 OK** and show non-zero counts for `GIS Config` and `GIS Hierarchy`.
