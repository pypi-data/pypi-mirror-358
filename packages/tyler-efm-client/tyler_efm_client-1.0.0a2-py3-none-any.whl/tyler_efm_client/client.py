"""
Tyler EFM Client - Main client implementation

This module provides the core TylerEFMClient class for authenticating with and 
calling Tyler EFM services.
"""

import os
import tempfile
import requests
import ssl
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass

from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from lxml import etree
import base64
import hashlib
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class TylerEFMError(Exception):
    """Base exception for Tyler EFM Client errors."""
    pass


class TylerAuthenticationError(TylerEFMError):
    """Exception raised for authentication failures."""
    pass


@dataclass
class AuthenticationResult:
    """Result from authentication request."""
    success: bool
    password_hash: Optional[str] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    expiration_date: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ServiceResponse:
    """Response from EFM service call."""
    success: bool
    status_code: int
    raw_xml: str
    json_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TylerEFMClient:
    """
    Tyler EFM Client for Electronic Court Filing (ECF) services.
    
    This client provides a simple interface for:
    1. Authentication with Tyler EFM services
    2. Making SOAP calls to any Tyler EFM service operation
    
    Key features:
    - Automatic certificate handling (PFX files)
    - WS-Security digital signatures (RSA-SHA1/SHA1 for Tyler compatibility)
    - Support for both User Service and Court Record Service operations
    - Flexible response formats (XML or JSON)
    
    Example usage:
        client = TylerEFMClient()
        
        # Authenticate
        auth_result = client.authenticate(
            base_url="https://georgia-stage.tylertech.cloud/EFM/EFMUserService.svc",
            pfx_file="certificate.pfx",
            pfx_password="password",
            user_email="user@example.com", 
            user_password="userpass"
        )
        
        if auth_result.success:
            # Call a service
            response = client.call_service(
                base_url="https://georgia-stage.tylertech.cloud/efm/v5/CourtRecordService.svc",
                password_hash=auth_result.password_hash,
                operation="GetCaseList",
                soap_body="<GetCaseListRequest>...</GetCaseListRequest>",
                return_json=True
            )
    """
    
    def __init__(self, debug=False, debug_dir="debug_artifacts"):
        """Initialize the Tyler EFM Client."""
        self.private_key = None
        self.certificate = None
        self.cert_pem_file = None
        self.key_pem_file = None
        self.session = None
        self.debug = debug
        self.debug_dir = debug_dir
        
    def authenticate(
        self,
        base_url: str,
        pfx_file: str,
        pfx_password: str,
        user_email: str,
        user_password: str
    ) -> AuthenticationResult:
        """
        Authenticate with Tyler EFM User Service.
        
        Args:
            base_url: Base URL for the EFM User Service (e.g., "https://server/EFM/EFMUserService.svc")
            pfx_file: Path to the PFX certificate file
            pfx_password: Password for the PFX certificate
            user_email: User's email address
            user_password: User's password
            
        Returns:
            AuthenticationResult with success status and authentication details
            
        Raises:
            TylerAuthenticationError: If authentication fails
            TylerEFMError: If there are other errors (certificate loading, network, etc.)
        """
        try:
            # Step 1: Load certificate
            if not self._load_certificate(pfx_file, pfx_password):
                return AuthenticationResult(
                    success=False,
                    error_code="CERT_LOAD_ERROR",
                    error_message="Failed to load certificate from PFX file"
                )
            
            # Step 2: Configure HTTP session
            if not self._configure_session():
                return AuthenticationResult(
                    success=False,
                    error_code="SESSION_CONFIG_ERROR", 
                    error_message="Failed to configure HTTP session"
                )
            
            # Step 3: Create temporary certificate files
            if not self._create_temp_pem_files():
                return AuthenticationResult(
                    success=False,
                    error_code="TEMP_FILES_ERROR",
                    error_message="Failed to create temporary certificate files"
                )
            
            try:
                # Step 4: Authenticate
                soap_envelope = self._create_auth_soap_envelope(user_email, user_password)
                
                headers = {
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': 'urn:tyler:efm:services/IEfmUserService/AuthenticateUser',
                    'User-Agent': 'Tyler-EFM-Client-Python/1.0',
                    'Accept': 'text/xml, application/soap+xml, */*'
                }
                
                # Save debug info if enabled
                self._save_debug_request(soap_envelope, headers, base_url, "AuthenticateUser")
                
                response = self.session.post(
                    base_url,
                    data=soap_envelope.encode('utf-8'),
                    headers=headers,
                    cert=(self.cert_pem_file, self.key_pem_file),
                    verify=True,
                    timeout=60
                )
                
                # Save debug response if enabled
                self._save_debug_response(response, "AuthenticateUser")
                
                if response.status_code == 200:
                    return self._parse_auth_response(response.text)
                else:
                    return AuthenticationResult(
                        success=False,
                        error_code=f"HTTP_{response.status_code}",
                        error_message=f"Authentication request failed: HTTP {response.status_code}"
                    )
                    
            finally:
                self._cleanup_temp_files()
                
        except Exception as e:
            self._cleanup_temp_files()
            raise TylerEFMError(f"Authentication error: {str(e)}") from e
    
    def call_service(
        self,
        base_url: str,
        password_hash: str,
        operation: str,
        soap_body: str,
        user_email: str = None,
        pfx_file: str = None,
        pfx_password: str = None,
        return_json: bool = False,
        soap_action: str = None
    ) -> ServiceResponse:
        """
        Call any Tyler EFM SOAP service operation.
        
        Args:
            base_url: Base URL for the EFM service (User Service or Court Record Service)
            password_hash: Password hash from successful authentication
            operation: Name of the SOAP operation (e.g., "GetCaseList", "GetCase")
            soap_body: SOAP body content as XML string
            user_email: User's email (required for Court Record Service operations)
            pfx_file: Path to PFX certificate (if not already loaded from authentication)
            pfx_password: PFX password (if not already loaded from authentication)
            return_json: If True, attempt to convert XML response to JSON
            soap_action: Custom SOAP action header (auto-generated if not provided)
            
        Returns:
            ServiceResponse with call results
            
        Raises:
            TylerEFMError: If the service call fails
        """
        try:
            # Load certificate if not already loaded
            if not self.certificate and pfx_file:
                if not self._load_certificate(pfx_file, pfx_password):
                    return ServiceResponse(
                        success=False,
                        status_code=0,
                        raw_xml="",
                        error_message="Failed to load certificate"
                    )
            
            if not self.certificate:
                return ServiceResponse(
                    success=False,
                    status_code=0,
                    raw_xml="",
                    error_message="No certificate loaded. Provide pfx_file or call authenticate() first."
                )
            
            # Configure session if needed
            if not self.session:
                if not self._configure_session():
                    return ServiceResponse(
                        success=False,
                        status_code=0,
                        raw_xml="",
                        error_message="Failed to configure HTTP session"
                    )
            
            # Create temp files if needed
            if not self.cert_pem_file:
                if not self._create_temp_pem_files():
                    return ServiceResponse(
                        success=False,
                        status_code=0,
                        raw_xml="",
                        error_message="Failed to create temporary certificate files"
                    )
            
            try:
                # Determine service type and create appropriate SOAP envelope
                if "CourtRecord" in base_url or "courtrecord" in base_url.lower():
                    # Court Record Service - requires UserNameHeader
                    if not user_email:
                        return ServiceResponse(
                            success=False,
                            status_code=0,
                            raw_xml="",
                            error_message="user_email is required for Court Record Service operations"
                        )
                    soap_envelope = self._create_court_record_soap_envelope(
                        user_email, password_hash, operation, soap_body
                    )
                else:
                    # User Service - standard WS-Security only
                    soap_envelope = self._create_user_service_soap_envelope(operation, soap_body)
                
                # Auto-generate SOAP action if not provided
                if not soap_action:
                    if "CourtRecord" in base_url:
                        soap_action = f"https://docs.oasis-open.org/legalxml-courtfiling/ns/v5.0WSDL/CourtRecordMDE/{operation}"
                    else:
                        soap_action = f"urn:tyler:efm:services/IEfmUserService/{operation}"
                
                headers = {
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': soap_action,
                    'User-Agent': 'Tyler-EFM-Client-Python/1.0',
                    'Accept': 'text/xml, application/soap+xml, */*'
                }
                
                # Save debug info if enabled
                self._save_debug_request(soap_envelope, headers, base_url, operation)
                
                response = self.session.post(
                    base_url,
                    data=soap_envelope.encode('utf-8'),
                    headers=headers,
                    cert=(self.cert_pem_file, self.key_pem_file),
                    verify=True,
                    timeout=60
                )
                
                # Save debug response if enabled
                self._save_debug_response(response, operation)
                
                # Parse response
                json_data = None
                if return_json and response.status_code == 200:
                    json_data = self._xml_to_json(response.text)
                
                return ServiceResponse(
                    success=(response.status_code == 200),
                    status_code=response.status_code,
                    raw_xml=response.text,
                    json_data=json_data,
                    error_message=None if response.status_code == 200 else f"HTTP {response.status_code}"
                )
                
            finally:
                # Keep temp files for subsequent calls, only cleanup when client is destroyed
                pass
                
        except Exception as e:
            raise TylerEFMError(f"Service call error: {str(e)}") from e
    
    def _load_certificate(self, pfx_file: str, pfx_password: str) -> bool:
        """Load certificate from PFX file."""
        try:
            with open(pfx_file, 'rb') as f:
                pfx_data = f.read()
            
            self.private_key, self.certificate, _ = pkcs12.load_key_and_certificates(
                pfx_data, pfx_password.encode()
            )
            
            return True
        except Exception:
            return False
    
    def _configure_session(self) -> bool:
        """Configure HTTP session with TLS settings."""
        try:
            self.session = requests.Session()
            
            adapter = HTTPAdapter(
                max_retries=Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[500, 502, 503, 504]
                )
            )
            self.session.mount('https://', adapter)
            
            return True
        except Exception:
            return False
    
    def _create_temp_pem_files(self) -> bool:
        """Create temporary PEM files for requests library."""
        try:
            # Cleanup old files first
            self._cleanup_temp_files()
            
            cert_fd, self.cert_pem_file = tempfile.mkstemp(suffix='.pem')
            with os.fdopen(cert_fd, 'wb') as f:
                f.write(self.certificate.public_bytes(serialization.Encoding.PEM))
            
            key_fd, self.key_pem_file = tempfile.mkstemp(suffix='.pem')
            with os.fdopen(key_fd, 'wb') as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            return True
        except Exception:
            return False
    
    def _cleanup_temp_files(self):
        """Clean up temporary PEM files."""
        try:
            if self.cert_pem_file and os.path.exists(self.cert_pem_file):
                os.unlink(self.cert_pem_file)
                self.cert_pem_file = None
            if self.key_pem_file and os.path.exists(self.key_pem_file):
                os.unlink(self.key_pem_file)
                self.key_pem_file = None
        except Exception:
            pass
    
    def _save_debug_request(self, soap_envelope: str, headers: Dict[str, str], url: str, operation: str):
        """Save the request payload to debug artifacts for analysis."""
        if not self.debug:
            return
            
        try:
            os.makedirs(self.debug_dir, exist_ok=True)
            
            # Save SOAP request
            soap_file = os.path.join(self.debug_dir, f"{operation.lower()}_request.xml")
            with open(soap_file, 'w', encoding='utf-8') as f:
                f.write(soap_envelope)
            
            # Save headers
            headers_file = os.path.join(self.debug_dir, f"{operation.lower()}_headers.txt")
            with open(headers_file, 'w', encoding='utf-8') as f:
                f.write(f"HTTP Headers used in {operation} request:\n")
                f.write("=" * 50 + "\n\n")
                for key, value in headers.items():
                    f.write(f"{key}: {value}\n")
                f.write(f"\nService URL: {url}\n")
                if self.certificate:
                    f.write(f"Certificate Subject: {self.certificate.subject}\n")
                f.write(f"Request Method: POST\n")
            
            print(f"💾 Debug: Request payload saved to: {soap_file}")
            print(f"💾 Debug: Request headers saved to: {headers_file}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not save debug request payload: {e}")

    def _save_debug_response(self, response, operation: str):
        """Save the response payload to debug artifacts for analysis."""
        if not self.debug:
            return
            
        try:
            os.makedirs(self.debug_dir, exist_ok=True)
            
            # Save response body
            response_file = os.path.join(self.debug_dir, f"{operation.lower()}_response.xml")
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Save response info
            response_info_file = os.path.join(self.debug_dir, f"{operation.lower()}_response_info.txt")
            with open(response_info_file, 'w', encoding='utf-8') as f:
                f.write(f"HTTP Response Information for {operation}:\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Status Code: {response.status_code}\n")
                f.write(f"Reason: {response.reason}\n")
                f.write(f"URL: {response.url}\n\n")
                f.write("Response Headers:\n")
                f.write("-" * 20 + "\n")
                for key, value in response.headers.items():
                    f.write(f"{key}: {value}\n")
            
            print(f"💾 Debug: Response saved to: {response_file}")
            print(f"💾 Debug: Response info saved to: {response_info_file}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not save debug response payload: {e}")
    
    def _get_certificate_base64(self) -> str:
        """Get certificate in base64 format."""
        cert_der = self.certificate.public_bytes(serialization.Encoding.DER)
        return base64.b64encode(cert_der).decode('utf-8')
    
    def _canonicalize_xml(self, xml_element) -> bytes:
        """Canonicalize XML element using exclusive C14N algorithm."""
        from lxml.etree import C14NError
        try:
            canonical_xml = etree.tostring(
                xml_element, 
                method='c14n', 
                exclusive=True,
                with_comments=False
            )
            return canonical_xml
        except C14NError as e:
            print(f"Error canonicalizing XML: {e}")
            return etree.tostring(xml_element, encoding='utf-8')
    
    def _compute_sha1_digest(self, data: Union[str, bytes]) -> bytes:
        """Compute SHA1 digest."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha1(data).digest()
    
    def _sign_data_rsa_sha1(self, data: Union[str, bytes]) -> bytes:
        """Sign data using RSA-SHA1."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        signature = self.private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        return signature
    
    def _create_auth_soap_envelope(self, email: str, password: str) -> str:
        """Create SOAP envelope for authentication."""
        if self.debug:
            print("🔐 Creating authentication SOAP envelope...")
            
        timestamp_id = "_0"
        token_id = f"X509-{str(uuid.uuid4())}"
        
        # Create timestamp
        now = datetime.now(timezone.utc)
        created = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        expires = (now + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        if self.debug:
            print(f"🔐 Timestamp ID: {timestamp_id}")
            print(f"🔐 Token ID: {token_id}")
            print(f"🔐 Created: {created}")
            print(f"🔐 Expires: {expires}")
        
        cert_base64 = self._get_certificate_base64()
        
        if self.debug:
            print(f"🔐 Certificate base64 length: {len(cert_base64)} chars")
        
        # Create SOAP envelope
        envelope = etree.Element(
            "{http://schemas.xmlsoap.org/soap/envelope/}Envelope",
            nsmap={
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'tns': 'urn:tyler:efm:services'
            }
        )
        
        # Header with WS-Security
        header = etree.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Header")
        security = etree.SubElement(
            header, 
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security",
            nsmap={
                'wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
                'wsu': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'
            }
        )
        security.set("{http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand", "1")
        
        # Timestamp
        timestamp = etree.SubElement(
            security,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Timestamp"
        )
        timestamp.set("{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id", timestamp_id)
        
        created_elem = etree.SubElement(
            timestamp,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Created"
        )
        created_elem.text = created
        
        expires_elem = etree.SubElement(
            timestamp,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Expires"
        )
        expires_elem.text = expires
        
        # Binary security token
        binary_token = etree.SubElement(
            security,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}BinarySecurityToken"
        )
        binary_token.set("ValueType", "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3")
        binary_token.set("EncodingType", "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary")
        binary_token.set("{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id", token_id)
        binary_token.text = cert_base64
        
        # Create digital signature using EXACT pattern from working getCaseList.py/auth_test.py
        try:
            timestamp_canonical = self._canonicalize_xml(timestamp)
            timestamp_digest = self._compute_sha1_digest(timestamp_canonical)
            timestamp_digest_b64 = base64.b64encode(timestamp_digest).decode('utf-8')
            
            if self.debug:
                print(f"🔐 Timestamp digest (SHA1, first 20 chars): {timestamp_digest_b64[:20]}...")
            
            # Create signature XML with exact same structure as working implementation
            signature_xml = f'''<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
  <ds:SignedInfo>
    <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
    <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
    <ds:Reference URI="#{timestamp_id}">
      <ds:Transforms>
        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      </ds:Transforms>
      <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
      <ds:DigestValue>{timestamp_digest_b64}</ds:DigestValue>
    </ds:Reference>
  </ds:SignedInfo>
  <ds:SignatureValue>PLACEHOLDER_SIGNATURE</ds:SignatureValue>
  <ds:KeyInfo>
    <wsse:SecurityTokenReference>
      <wsse:Reference ValueType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3" URI="#{token_id}"/>
    </wsse:SecurityTokenReference>
  </ds:KeyInfo>
</ds:Signature>'''
            
            signature_element = etree.fromstring(signature_xml.encode('utf-8'))
            security.append(signature_element)
            
            signed_info_element = signature_element.find('.//{http://www.w3.org/2000/09/xmldsig#}SignedInfo')
            
            if signed_info_element is not None:
                signed_info_canonical = self._canonicalize_xml(signed_info_element)
                signature_bytes = self._sign_data_rsa_sha1(signed_info_canonical)
                signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
                
                if self.debug:
                    print(f"🔐 RSA-SHA1 signature value (first 20 chars): {signature_b64[:20]}...")
                
                signature_value_element = signature_element.find('.//{http://www.w3.org/2000/09/xmldsig#}SignatureValue')
                if signature_value_element is not None:
                    signature_value_element.text = signature_b64
                else:
                    print("⚠️ Could not find SignatureValue element")
            else:
                print("⚠️ Could not find SignedInfo element")
            
            if self.debug:
                print("✓ WCF-compatible WS-Security XML signature created (RSA-SHA1/SHA1 - Tyler legacy)")
            
        except Exception as e:
            if self.debug:
                print(f"⚠️ Warning: Could not create XML signature: {e}")
                import traceback
                traceback.print_exc()
        
        # Body
        body = etree.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
        
        auth_user = etree.SubElement(body, "{urn:tyler:efm:services}AuthenticateUser")
        auth_request = etree.SubElement(auth_user, "{urn:tyler:efm:services}AuthenticateRequest")
        
        email_elem = etree.SubElement(auth_request, "Email")
        email_elem.set("xmlns", "urn:tyler:efm:services:schema:AuthenticateRequest")
        email_elem.text = email
        
        password_elem = etree.SubElement(auth_request, "Password")
        password_elem.set("xmlns", "urn:tyler:efm:services:schema:AuthenticateRequest")
        password_elem.text = password
        
        result = etree.tostring(envelope, encoding='utf-8', xml_declaration=True, pretty_print=False).decode('utf-8')
        
        if self.debug:
            print(f"🔐 Authentication SOAP envelope created ({len(result)} chars)")
            
        return result
    
    def _create_court_record_soap_envelope(self, email: str, password_hash: str, operation: str, soap_body: str) -> str:
        """Create SOAP envelope for Court Record Service operations."""
        timestamp_id = "_0"
        token_id = f"X509-{str(uuid.uuid4())}"
        
        # Create timestamp
        now = datetime.now(timezone.utc)
        created = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        expires = (now + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        cert_base64 = self._get_certificate_base64()
        
        # Create SOAP envelope with Tyler namespace as default (CRITICAL for Court Record Service)
        envelope = etree.Element(
            "{http://schemas.xmlsoap.org/soap/envelope/}Envelope",
            nsmap={
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'tns': 'https://docs.oasis-open.org/legalxml-courtfiling/ns/v5.0WSDL/CourtRecordMDE',
                'wrappers': 'https://docs.oasis-open.org/legalxml-courtfiling/ns/v5.0/wrappers',
                None: 'urn:tyler:efm:services'  # DEFAULT namespace for Tyler services
            }
        )
        
        # Header with UserNameHeader FIRST (CRITICAL!)
        header = etree.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Header")
        
        # UserNameHeader MUST be first and WITHOUT namespace prefix
        username_header = etree.SubElement(header, "UserNameHeader")
        username = etree.SubElement(username_header, "UserName")
        username.text = email
        password_header = etree.SubElement(username_header, "Password")
        password_header.text = password_hash
        
        # WS-Security as second header element
        security = etree.SubElement(
            header, 
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security",
            nsmap={
                'wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
                'wsu': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'
            }
        )
        security.set("{http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand", "1")
        
        # Timestamp
        timestamp = etree.SubElement(
            security,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Timestamp"
        )
        timestamp.set("{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id", timestamp_id)
        
        created_elem = etree.SubElement(
            timestamp,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Created"
        )
        created_elem.text = created
        
        expires_elem = etree.SubElement(
            timestamp,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Expires"
        )
        expires_elem.text = expires
        
        # Binary security token
        binary_token = etree.SubElement(
            security,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}BinarySecurityToken"
        )
        binary_token.set("ValueType", "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3")
        binary_token.set("EncodingType", "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary")
        binary_token.set("{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id", token_id)
        binary_token.text = cert_base64
        
        # Create digital signature using same pattern as working getCaseList.py
        try:
            timestamp_canonical = self._canonicalize_xml(timestamp)
            timestamp_digest = self._compute_sha1_digest(timestamp_canonical)
            timestamp_digest_b64 = base64.b64encode(timestamp_digest).decode('utf-8')
            
            signature_xml = f'''<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
  <ds:SignedInfo>
    <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
    <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
    <ds:Reference URI="#{timestamp_id}">
      <ds:Transforms>
        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      </ds:Transforms>
      <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
      <ds:DigestValue>{timestamp_digest_b64}</ds:DigestValue>
    </ds:Reference>
  </ds:SignedInfo>
  <ds:SignatureValue>PLACEHOLDER_SIGNATURE</ds:SignatureValue>
  <ds:KeyInfo>
    <wsse:SecurityTokenReference>
      <wsse:Reference ValueType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3" URI="#{token_id}"/>
    </wsse:SecurityTokenReference>
  </ds:KeyInfo>
</ds:Signature>'''
            
            signature_element = etree.fromstring(signature_xml.encode('utf-8'))
            security.append(signature_element)
            
            signed_info_element = signature_element.find('.//{http://www.w3.org/2000/09/xmldsig#}SignedInfo')
            
            if signed_info_element is not None:
                signed_info_canonical = self._canonicalize_xml(signed_info_element)
                signature_bytes = self._sign_data_rsa_sha1(signed_info_canonical)
                signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
                
                signature_value_element = signature_element.find('.//{http://www.w3.org/2000/09/xmldsig#}SignatureValue')
                if signature_value_element is not None:
                    signature_value_element.text = signature_b64
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create XML signature: {e}")
        
        # Body - parse and insert the provided SOAP body
        body = etree.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
        
        try:
            # Parse the provided SOAP body and add it to the envelope
            body_doc = etree.fromstring(soap_body.encode('utf-8'))
            body.append(body_doc)
        except Exception:
            # If parsing fails, add as text (fallback)
            body.text = soap_body
        
        return etree.tostring(envelope, encoding='utf-8', xml_declaration=True, pretty_print=False).decode('utf-8')
    
    def _create_user_service_soap_envelope(self, operation: str, soap_body: str) -> str:
        """Create SOAP envelope for User Service operations."""
        timestamp_id = "_0"
        token_id = f"X509-{str(uuid.uuid4())}"
        
        # Create timestamp
        now = datetime.now(timezone.utc)
        created = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        expires = (now + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        cert_base64 = self._get_certificate_base64()
        
        # Create SOAP envelope
        envelope = etree.Element(
            "{http://schemas.xmlsoap.org/soap/envelope/}Envelope",
            nsmap={
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'tns': 'urn:tyler:efm:services'
            }
        )
        
        # Header with WS-Security
        header = etree.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Header")
        security = etree.SubElement(
            header, 
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security",
            nsmap={
                'wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
                'wsu': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'
            }
        )
        security.set("{http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand", "1")
        
        # Timestamp
        timestamp = etree.SubElement(
            security,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Timestamp"
        )
        timestamp.set("{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id", timestamp_id)
        
        created_elem = etree.SubElement(
            timestamp,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Created"
        )
        created_elem.text = created
        
        expires_elem = etree.SubElement(
            timestamp,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Expires"
        )
        expires_elem.text = expires
        
        # Binary security token
        binary_token = etree.SubElement(
            security,
            "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}BinarySecurityToken"
        )
        binary_token.set("ValueType", "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3")
        binary_token.set("EncodingType", "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary")
        binary_token.set("{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id", token_id)
        binary_token.text = cert_base64
        
        # Create and add digital signature
        self._add_digital_signature(security, timestamp, timestamp_id, token_id)
        
        # Body - parse and insert the provided SOAP body
        body = etree.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
        
        try:
            # Parse the provided SOAP body and add it to the envelope
            body_doc = etree.fromstring(soap_body.encode('utf-8'))
            body.append(body_doc)
        except Exception:
            # If parsing fails, add as text (fallback)
            body.text = soap_body
        
        return etree.tostring(envelope, encoding='utf-8', xml_declaration=True, pretty_print=False).decode('utf-8')
    
    def _add_digital_signature(self, security_element, timestamp_element, timestamp_id: str, token_id: str):
        """Add WS-Security digital signature to the security element."""
        try:
            if self.debug:
                print("🔐 Creating digital signature...")
                
            # Canonicalize timestamp and compute digest
            timestamp_canonical = self._canonicalize_xml(timestamp_element)
            timestamp_digest = self._compute_sha1_digest(timestamp_canonical)
            timestamp_digest_b64 = base64.b64encode(timestamp_digest).decode('utf-8')
            
            if self.debug:
                print(f"🔐 Timestamp canonical length: {len(timestamp_canonical)} bytes")
                print(f"🔐 Timestamp digest (SHA1): {timestamp_digest_b64[:20]}...")
                print(f"🔐 Signing timestamp ID: #{timestamp_id}")
                print(f"🔐 Token reference ID: #{token_id}")
            
            # Create SignedInfo XML
            signed_info_xml = f'''<ds:SignedInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
  <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
  <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
  <ds:Reference URI="#{timestamp_id}">
    <ds:Transforms>
      <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
    </ds:Transforms>
    <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
    <ds:DigestValue>{timestamp_digest_b64}</ds:DigestValue>
  </ds:Reference>
</ds:SignedInfo>'''
            
            # Parse and canonicalize SignedInfo
            signed_info_element = etree.fromstring(signed_info_xml.encode('utf-8'))
            signed_info_canonical = self._canonicalize_xml(signed_info_element)
            
            if self.debug:
                print(f"🔐 SignedInfo canonical length: {len(signed_info_canonical)} bytes")
            
            # Sign the canonicalized SignedInfo
            signature_bytes = self._sign_data_rsa_sha1(signed_info_canonical)
            signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
            
            if self.debug:
                print(f"🔐 RSA-SHA1 signature length: {len(signature_bytes)} bytes")
                print(f"🔐 Signature base64: {signature_b64[:20]}...")
            
            # Create complete signature XML
            signature_xml = f'''<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
  <ds:SignedInfo>
    <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
    <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
    <ds:Reference URI="#{timestamp_id}">
      <ds:Transforms>
        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      </ds:Transforms>
      <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
      <ds:DigestValue>{timestamp_digest_b64}</ds:DigestValue>
    </ds:Reference>
  </ds:SignedInfo>
  <ds:SignatureValue>{signature_b64}</ds:SignatureValue>
  <ds:KeyInfo>
    <wsse:SecurityTokenReference>
      <wsse:Reference ValueType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3" URI="#{token_id}"/>
    </wsse:SecurityTokenReference>
  </ds:KeyInfo>
</ds:Signature>'''
            
            # Add signature to security element
            signature_element = etree.fromstring(signature_xml.encode('utf-8'))
            security_element.append(signature_element)
            
            if self.debug:
                print("🔐 Digital signature successfully added to security element")
            
        except Exception as e:
            # Signature creation failed, but continue without signature
            if self.debug:
                print(f"⚠️ Digital signature creation failed: {e}")
            pass
    
    def _parse_auth_response(self, response_text: str) -> AuthenticationResult:
        """Parse authentication response and extract user information."""
        try:
            # Handle multipart MIME response
            xml_content = response_text
            if '--uuid:' in response_text:
                xml_start = response_text.find('<s:Envelope')
                if xml_start == -1:
                    xml_start = response_text.find('<')
                if xml_start != -1:
                    xml_end = response_text.rfind('</s:Envelope>')
                    if xml_end != -1:
                        xml_end += len('</s:Envelope>')
                        xml_content = response_text[xml_start:xml_end]
            
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Extract authentication response data
            password_hash = None
            user_id = None
            first_name = None
            last_name = None
            email = None
            expiration_date = None
            error_code = None
            error_message = None
            
            # Look for password hash
            password_hash_elements = root.xpath('//*[local-name()="PasswordHash"]')
            if password_hash_elements:
                password_hash = password_hash_elements[0].text
            
            # Look for user ID
            user_id_elements = root.xpath('//*[local-name()="UserID"]')
            if user_id_elements:
                user_id = user_id_elements[0].text
            
            # Look for names
            first_name_elements = root.xpath('//*[local-name()="FirstName"]')
            if first_name_elements:
                first_name = first_name_elements[0].text
                
            last_name_elements = root.xpath('//*[local-name()="LastName"]')
            if last_name_elements:
                last_name = last_name_elements[0].text
            
            # Look for email
            email_elements = root.xpath('//*[local-name()="Email"]')
            if email_elements:
                email = email_elements[0].text
            
            # Look for expiration
            expiration_elements = root.xpath('//*[local-name()="ExpirationDateTime"]')
            if expiration_elements:
                expiration_date = expiration_elements[0].text
            
            # Look for errors
            error_code_elements = root.xpath('//*[local-name()="ErrorCode"]')
            if error_code_elements:
                error_code = error_code_elements[0].text
                
            error_text_elements = root.xpath('//*[local-name()="ErrorText"]')
            if error_text_elements:
                error_message = error_text_elements[0].text
            
            # Determine success
            success = password_hash is not None and (error_code is None or error_code == "0")
            
            return AuthenticationResult(
                success=success,
                password_hash=password_hash,
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                expiration_date=expiration_date,
                error_code=error_code,
                error_message=error_message
            )
            
        except Exception as e:
            return AuthenticationResult(
                success=False,
                error_code="PARSE_ERROR",
                error_message=f"Failed to parse authentication response: {str(e)}"
            )
    
    def _xml_to_json(self, xml_text: str) -> Optional[Dict[str, Any]]:
        """Convert XML response to JSON format."""
        try:
            # Handle multipart MIME response
            xml_content = xml_text
            if '--uuid:' in xml_text:
                xml_start = xml_text.find('<s:Envelope')
                if xml_start == -1:
                    xml_start = xml_text.find('<')
                if xml_start != -1:
                    xml_end = xml_text.rfind('</s:Envelope>')
                    if xml_end != -1:
                        xml_end += len('</s:Envelope>')
                        xml_content = xml_text[xml_start:xml_end]
            
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            def element_to_dict(element):
                """Convert XML element to dictionary."""
                result = {}
                
                # Add attributes
                for key, value in element.attrib.items():
                    result[f"@{key}"] = value
                
                # Add text content
                if element.text and element.text.strip():
                    if len(element) == 0:  # No child elements
                        return element.text.strip()
                    else:
                        result["#text"] = element.text.strip()
                
                # Add child elements
                for child in element:
                    child_name = child.tag.split('}')[-1]  # Remove namespace
                    child_value = element_to_dict(child)
                    
                    if child_name in result:
                        # Convert to list if multiple elements with same name
                        if not isinstance(result[child_name], list):
                            result[child_name] = [result[child_name]]
                        result[child_name].append(child_value)
                    else:
                        result[child_name] = child_value
                
                return result
            
            return element_to_dict(root)
            
        except Exception:
            return None
    
    def __del__(self):
        """Cleanup when client is destroyed."""
        self._cleanup_temp_files()