"""
Tyler EFM Client - Python SDK for Tyler Technologies Electronic Filing Manager (EFM) Services

This package provides a simple, production-ready interface for integrating with Tyler's
ECF (Electronic Court Filing) services, including authentication and SOAP service calls.

Author: Tyler Technologies ECF Integration Team
License: MIT
"""

from .client import TylerEFMClient, TylerEFMError, TylerAuthenticationError, AuthenticationResult, ServiceResponse

__version__ = "1.0.0"
__author__ = "Tyler Technologies ECF Integration Team"
__email__ = "ecf-support@tylertech.com"
__description__ = "Python SDK for Tyler Technologies EFM Services"

__all__ = [
    'TylerEFMClient',
    'TylerEFMError', 
    'TylerAuthenticationError',
    'AuthenticationResult',
    'ServiceResponse'
]