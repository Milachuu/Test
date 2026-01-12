import subprocess
import sys

# List of required packages (stdlib items removed)
required_packages = [
    "flask",
    "werkzeug",
    "pyotp",
    "qrcode",
    "pillow",                  # required by qrcode for image generation
    "wtforms",                 # NOT stdlib (WTForms is a package you pip install)
    "email-validator",
    "mysql-connector-python",
    "python-dotenv",           # correct PyPI name is python-dotenv, not dotenv
    "stripe",
    "geopy",
    "cryptography"
]

# Try to install any missing packages
for package in required_packages:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
    else:
        print(f"✅ {package} installed successfully")
