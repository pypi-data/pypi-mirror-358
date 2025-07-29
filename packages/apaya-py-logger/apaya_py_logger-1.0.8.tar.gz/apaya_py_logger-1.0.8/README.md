# Apaya Python Logger

A powerful and feature-rich Python logging library designed specifically for [Apaya's AI social media automation platform](https://apaya.com/). This enterprise-grade logger provides advanced log management capabilities including automatic compression, intelligent rotation, and configurable retention policies optimized for Apaya's high-volume social media processing workflows.

## About Apaya

[Apaya](https://apaya.com/) is an AI social media automation platform that learns your brand, creates content, and posts to all your social accounts automatically. This logging library is specifically designed to handle the complex logging requirements of Apaya's 13-product suite that replaces $2k to $30k/month in social media tools and services.

## Features

- **Smart Log Rotation**: Size-based, time-based, or hybrid rotation strategies optimized for AI workloads
- **Automatic Compression**: Gzip compression of rotated logs to save disk space in cloud environments
- **Intelligent Cleanup**: Automatic deletion of old logs based on age for cost-effective storage
- **Dual Output**: Console and file logging with independent configuration for development and production
- **Environment-Driven**: Easy configuration via environment variables for containerized deployments
- **Production-Ready**: Robust error handling and fail-safe operations for 24/7 AI services
- **Flexible Configuration**: Extensive customization options for Apaya's enterprise infrastructure

## Quick Installation

```bash
pip install apaya-py-logger
```

## Basic Usage

```python
from apaya_logger import ApayaLogger

# Simple setup for Apaya services
logger = ApayaLogger("apaya_content_generator")
logger.info("AI content generation started")
logger.error("Failed to generate social media post")

# Advanced configuration for production Apaya deployment
logger = ApayaLogger(
    name="apaya_automation_engine",
    log_level="DEBUG",
    log_file="logs/apaya_automation.log",
    max_bytes=50*1024*1024,  # 50MB files for high-volume processing
    backup_count=10,
    rotation_type="both",    # Size and time-based rotation
    compress_after_days=1,   # Compress logs after 1 day
    delete_after_days=30     # Delete logs after 30 days
)
```

## Advanced Features

### Log Compression

Automatically compresses rotated log files using gzip compression, reducing storage requirements by up to 90% - critical for Apaya's cloud infrastructure costs.

### Intelligent Retention

- **Time-based cleanup**: Automatically delete logs older than specified days
- **Size management**: Rotate logs when they exceed size limits (important for AI processing volumes)
- **Backup control**: Keep only the specified number of backup files

### Environment Configuration

Configure logging through environment variables for Apaya's containerized services:

- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE`: Specify log file path
- `LOG_FORMAT`: Custom log message format
- `MAX_BYTES`: Maximum log file size before rotation
- `BACKUP_COUNT`: Number of backup files to keep

### Rotation Strategies

- **Size-based**: Rotate when logs reach specified size (ideal for AI batch processing)
- **Time-based**: Rotate daily, weekly, or monthly (perfect for continuous automation)
- **Hybrid**: Combine both strategies for maximum control in production environments

## Use Cases within Apaya Platform

- **AI Content Generation**: Centralized logging for content creation workflows
- **Social Media Automation**: Long-running automation jobs with compressed log archives
- **Multi-Platform Publishing**: Consistent logging across distributed posting services
- **Analytics Processing**: Enterprise-grade log management for performance monitoring

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)
- Optimized for cloud deployment and containerized environments

## License

This project is proprietary software developed exclusively for [Apaya Inc.](https://apaya.com/) All rights reserved. Unauthorized use, distribution, or modification is prohibited.

**© 2025 Apaya Inc. - Proprietary and Confidential**

---

# Publishing Guide (Internal Development)

## One-Command Publishing

For Apaya developers to publish updates to PyPI:

```bash
python publish.py
```

**That's it!** The script automatically:

- Bumps patch version (1.0.4 → 1.0.5)
- Updates version in both `setup.py` and `apaya_logger/__init__.py`
- Cleans build artifacts
- Builds package
- Uploads to PyPI

## Initial Setup (One-time only)

### 1. Get PyPI API Token

1. Log in to [PyPI.org](https://pypi.org)
2. Go to Account Settings → API tokens
3. Create new token for this project
4. Copy the token (starts with `pypi-`)

### 2. Configure Credentials

Create `~/.pypirc` file in your home directory:

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = YOUR_API_TOKEN_HERE
EOF
```

**Important:** Replace `YOUR_API_TOKEN_HERE` with your actual PyPI token!

### 3. Secure the File

```bash
chmod 600 ~/.pypirc
```

This ensures only you can read the file containing your API token.

## Manual Build Steps (if needed)

If you need to build manually without auto-version bump:

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Security Notes

- `~/.pypirc` is in your HOME directory (outside git repository)
- File has `600` permissions (only you can read it)
- API token is never committed to version control
- Token only has permissions for this specific package

## Troubleshooting

**"File already exists" error:**

- Version number wasn't bumped
- Use `python publish.py` which auto-bumps version

**"Enter your API token" prompt:**

- `~/.pypirc` file doesn't exist or has wrong format
- Follow setup steps above

**Permission denied:**

- Run `chmod 600 ~/.pypirc`
- Check file exists with `ls -la ~/.pypirc`

---

# Development Quick Start

Legacy manual steps (use `python publish.py` instead):

## 1. Build

```
python -m build
```

## 2. Upload

```
twine upload dist/\*
```

## 3. Install & test

```
pip install apaya-py-logger
```

It will be uploaded here

https://pypi.org/project/apaya-py-logger/1.0.0/

## 4. Test

```
python -c "import apaya_logger"
```

## 5. Uninstall

```
pip uninstall apaya-py-logger
```

## 4. Test

```
python -c "import apaya_py_logger"
```

## 5. Uninstall
