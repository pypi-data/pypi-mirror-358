# Tyler EFM Client - Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tyler Technologies](https://img.shields.io/badge/Tyler-Technologies-blue.svg)](https://tylertech.com)

A production-ready Python SDK for integrating with Tyler Technologies Electronic Filing Manager (EFM) services. This package simplifies authentication and SOAP service calls for Electronic Court Filing (ECF) systems.

## 🚀 Features

- **Simple Authentication**: One method to authenticate with Tyler EFM services
- **Flexible SOAP Operations**: Call any Tyler EFM SOAP operation with automatic security handling
- **WS-Security Support**: Automatic RSA-SHA1/SHA1 digital signatures (Tyler legacy compatibility)
- **Certificate Management**: Automatic PFX certificate handling and cleanup
- **Response Formats**: Choose between XML and JSON response formats
- **Production Ready**: Built from working Tyler ECF 5.0 integration code
- **Type Hints**: Full typing support for better development experience

## 📦 Installation

Install the package using pip:

```bash
pip install tyler-efm-client
```

### Requirements

- Python 3.8+
- Valid Tyler EFM PFX certificate
- Access to Tyler EFM services (staging or production)

## 🔧 Quick Start

### 1. Configuration Setup

Copy `config.example.json` to `config.json` and update with your credentials:

```json
{
  "service": {
    "endpoint": "https://georgia-stage.tylertech.cloud/EFM/EFMUserService.svc",
    "court_service_url": "https://georgia-stage.tylertech.cloud/efm/v5/CourtRecordService.svc"
  },
  "certificate": {
    "pfx_file": "YOUR_CERTIFICATE.pfx",
    "pfx_password": "YOUR_PFX_PASSWORD"
  },
  "credentials": {
    "email": "your-email@domain.com",
    "password": "your-password"
  }
}
```

**Note**: The `config.json` file is excluded from version control for security.

### 2. Basic Authentication

```python
from tyler_efm_client import TylerEFMClient

# Initialize client with config file
client = TylerEFMClient('config.json')

# Authenticate using config
auth_result = client.authenticate()

if auth_result.success:
    print(f"Password Hash: {auth_result.password_hash}")
    print(f"User: {auth_result.first_name} {auth_result.last_name}")
else:
    print(f"Error: {auth_result.error_message}")
```

### Service Operations

```python
# Call GetCaseList operation
soap_body = '''<wrappers:GetCaseListRequest xmlns:wrappers="https://docs.oasis-open.org/legalxml-courtfiling/ns/v5.0/wrappers">
    <!-- Your SOAP body content -->
</wrappers:GetCaseListRequest>'''

response = client.call_service(
    base_url="https://your-tyler-server.com/efm/v5/CourtRecordService.svc",
    password_hash=auth_result.password_hash,
    operation="GetCaseList",
    soap_body=soap_body,
    user_email="your-email@example.com",
    return_json=True  # Get JSON response instead of XML
)

if response.success:
    print("Service call successful!")
    if response.json_data:
        # Work with JSON data
        print(response.json_data)
    else:
        # Work with raw XML
        print(response.raw_xml)
```

## 📚 API Reference

### TylerEFMClient

The main client class for Tyler EFM operations.

#### authenticate(base_url, pfx_file, pfx_password, user_email, user_password)

Authenticate with Tyler EFM User Service.

**Parameters:**
- `base_url` (str): Base URL for the EFM User Service
- `pfx_file` (str): Path to the PFX certificate file
- `pfx_password` (str): Password for the PFX certificate  
- `user_email` (str): User's email address
- `user_password` (str): User's password

**Returns:** `AuthenticationResult` object with:
- `success` (bool): Whether authentication succeeded
- `password_hash` (str): Password hash for subsequent service calls
- `user_id` (str): User's unique identifier
- `first_name` (str): User's first name
- `last_name` (str): User's last name
- `email` (str): User's email
- `expiration_date` (str): Token expiration date
- `error_code` (str): Error code if authentication failed
- `error_message` (str): Error message if authentication failed

#### call_service(base_url, password_hash, operation, soap_body, **kwargs)

Call any Tyler EFM SOAP service operation.

**Parameters:**
- `base_url` (str): Base URL for the EFM service
- `password_hash` (str): Password hash from authentication
- `operation` (str): Name of the SOAP operation
- `soap_body` (str): SOAP body content as XML string
- `user_email` (str, optional): User's email (required for Court Record Service)
- `pfx_file` (str, optional): Path to PFX certificate if not from authentication
- `pfx_password` (str, optional): PFX password if not from authentication
- `return_json` (bool, optional): Return JSON instead of XML (default: False)
- `soap_action` (str, optional): Custom SOAP action header

**Returns:** `ServiceResponse` object with:
- `success` (bool): Whether the service call succeeded
- `status_code` (int): HTTP status code
- `raw_xml` (str): Raw XML response
- `json_data` (dict, optional): JSON representation of response if requested
- `error_message` (str, optional): Error message if call failed

## 🏗️ Architecture

This SDK implements Tyler's exact ECF 5.0 requirements:

### Authentication (User Service)
- **WS-Security**: Digital signatures using RSA-SHA1/SHA1 (Tyler legacy requirement)
- **Certificate Auth**: Mutual TLS using PFX certificates
- **SOAP Structure**: Exact Tyler-compatible XML namespace handling

### Court Record Service Operations
- **UserNameHeader**: Special header structure required by Court Record Service
- **No Namespace Prefix**: Critical requirement - UserNameHeader must not have namespace prefix
- **Header Order**: UserNameHeader must be first header element
- **Password Hash**: Uses hashed password from authentication, not plain password

## 🔒 Security Features

- **Automatic Certificate Handling**: PFX files are processed and cleaned up automatically
- **WS-Security Signatures**: RSA-SHA1 digital signatures for message integrity
- **Legacy Algorithm Support**: SHA1 and RSA-SHA1 for Tyler compatibility
- **Secure Cleanup**: Temporary certificate files are automatically removed
- **HTTPS Only**: All communications use HTTPS with certificate verification

## 📖 Examples

The `examples/` directory contains complete working examples:

- `authentication_example.py` - Basic authentication
- `getcaselist_example.py` - GetCaseList operation
- `complete_workflow_example.py` - Full workflow with multiple operations

## 🐛 Error Handling

The SDK provides specific exception types:

```python
from tyler_efm_client import TylerEFMError, TylerAuthenticationError

try:
    auth_result = client.authenticate(...)
except TylerAuthenticationError as e:
    print(f"Authentication failed: {e}")
except TylerEFMError as e:
    print(f"EFM service error: {e}")
```

## 🧪 Testing

The SDK is built from working Tyler ECF integration code and tested against:

- Tyler Georgia staging environment
- Production Tyler ECF 5.0 systems
- Multiple certificate types and configurations

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- OpenSSL for certificate processing
- Network access to Tyler EFM services

### Tyler Requirements
- Valid Tyler EFM account and credentials
- PFX certificate file from Tyler Technologies
- Appropriate service URLs (staging or production)

## 🚀 Releases & Versioning

This package uses **optimized automated building** through GitHub Actions with cross-platform testing and fast build processes.

### Quick Release Guide

**Alpha/Development Releases**:
- Go to GitHub Actions → "Publish Python Package" → "Run workflow"
- Enter version like: `1.0.0a2`, `1.0.0b1`
- Publishes to TestPyPI first, then PyPI

**Production Releases**:
```bash
# Create a version tag and GitHub release
git tag v1.0.0
git push origin v1.0.0
# Then create GitHub Release using the tag
```

**Testing Releases**:
```bash
# Install from TestPyPI for validation
pip install -i https://test.pypi.org/simple/ tyler-efm-client
```

📖 **See [VERSIONING.md](./VERSIONING.md) for complete build and versioning guide**

### Build Features
- **Fast Builds**: Uses pre-compiled wheels to prevent timeout issues
- **Cross-Platform**: Tests on Windows and Linux
- **Integration Testing**: Real Tyler EFM credential testing via GitHub secrets
- **Security Scanning**: Automated vulnerability checks

## 🤝 Support

This SDK is based on the working implementation documented in the Tyler ECF integration project. For issues:

1. Check the examples for proper usage patterns
2. Verify your certificate and credentials
3. Ensure you're using the correct Tyler service URLs
4. Review the Tyler ECF 5.0 documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About Tyler Technologies

Tyler Technologies is a leading provider of integrated software and technology services to the public sector. Learn more at [tylertech.com](https://www.tylertech.com).

---

**Built with ❤️ for the Tyler ECF community**