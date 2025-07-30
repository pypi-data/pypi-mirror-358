"""
Shared SSL certificate management service for CodeGuard.

This service provides SSL certificate generation and management for all
CodeGuard services that need HTTPS endpoints. It creates a local CA
certificate that users can install to trust all CodeGuard services.
"""

import logging
import ssl
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    x509 = None
    hashes = None
    serialization = None
    rsa = None
    NameOID = None
    ExtendedKeyUsageOID = None

logger = logging.getLogger(__name__)


class SSLServiceError(Exception):
    """Raised when SSL service operations fail."""

    pass


class CodeGuardSSLService:
    """
    Shared SSL certificate management for all CodeGuard services.

    This service manages:
    - CA certificate generation and storage
    - Service-specific certificate generation
    - SSL context creation for servers
    - Certificate export for user installation
    """

    def __init__(self, base_cert_dir: Optional[Path] = None):
        """
        Initialize SSL service.

        Args:
            base_cert_dir: Base directory for certificate storage.
                          Defaults to ~/.codeguard/ssl
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise SSLServiceError(
                "cryptography library is required but not installed. "
                "Install with: pip install cryptography"
            )

        self.cert_dir = base_cert_dir or Path.home() / ".codeguard" / "ssl"
        self.cert_dir.mkdir(parents=True, exist_ok=True)

        # CA certificate paths
        self.ca_cert_path = self.cert_dir / "codeguard-ca.crt"
        self.ca_key_path = self.cert_dir / "codeguard-ca.key"

        # Service certificate cache
        self._service_certs: Dict[str, Tuple[Path, Path]] = {}

        logger.info(f"SSL service initialized with cert directory: {self.cert_dir}")

    def ensure_ca_exists(self) -> bool:
        """
        Ensure CA certificate exists, create if needed.

        Returns:
            True if CA was created or already exists, False on error.
        """
        try:
            if self.ca_cert_path.exists() and self.ca_key_path.exists():
                logger.debug("CA certificate already exists")
                return True

            logger.info("Generating new CodeGuard CA certificate...")
            self._generate_ca_certificate()
            logger.info(f"CA certificate created: {self.ca_cert_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to ensure CA exists: {e}")
            return False

    def generate_service_cert(self, service_name: str, hosts: List[str]) -> Tuple[Path, Path]:
        """
        Generate certificate for a CodeGuard service.

        Args:
            service_name: Name of the service (e.g., 'llm_proxy', 'mcp_server')
            hosts: List of hostnames/IPs the certificate should be valid for

        Returns:
            Tuple of (certificate_path, private_key_path)

        Raises:
            SSLServiceError: If certificate generation fails
        """
        # Validate service_name parameter
        if not service_name or not service_name.strip():
            raise SSLServiceError("Service name cannot be empty or None")

        service_name = service_name.strip()
        cache_key = f"{service_name}_{hash(tuple(sorted(hosts)))}"

        if cache_key in self._service_certs:
            cert_path, key_path = self._service_certs[cache_key]
            if cert_path.exists() and key_path.exists():
                logger.debug(f"Using cached certificate for {service_name}")
                return cert_path, key_path

        try:
            # Ensure CA exists
            if not self.ensure_ca_exists():
                raise SSLServiceError("Failed to ensure CA certificate exists")

            # Generate service certificate
            cert_path = self.cert_dir / f"{service_name}.crt"
            key_path = self.cert_dir / f"{service_name}.key"

            logger.info(f"Generating SSL certificate for {service_name} with hosts: {hosts}")
            self._generate_service_certificate(service_name, hosts, cert_path, key_path)

            # Cache the result
            self._service_certs[cache_key] = (cert_path, key_path)

            logger.info(f"Service certificate created: {cert_path}")
            return cert_path, key_path

        except Exception as e:
            logger.error(f"Failed to generate certificate for {service_name}: {e}")
            raise SSLServiceError(f"Certificate generation failed: {e}")

    def export_ca_certificate(self) -> Path:
        """
        Export CA certificate for user installation.

        Returns:
            Path to the CA certificate file

        Raises:
            SSLServiceError: If CA certificate doesn't exist
        """
        if not self.ca_cert_path.exists():
            if not self.ensure_ca_exists():
                raise SSLServiceError("Failed to create CA certificate")

        return self.ca_cert_path

    def get_ssl_context(self, service_name: str, hosts: List[str]) -> ssl.SSLContext:
        """
        Get SSL context for a service with full certificate chain.

        Args:
            service_name: Name of the service
            hosts: List of hostnames/IPs for the certificate

        Returns:
            Configured SSL context

        Raises:
            SSLServiceError: If SSL context creation fails
        """
        try:
            cert_path, key_path = self.generate_service_cert(service_name, hosts)

            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

            # Load the service certificate and CA certificate as a chain
            # This is critical for Node.js applications
            cert_chain_path = self._create_cert_chain(cert_path)
            context.load_cert_chain(str(cert_chain_path), str(key_path))

            # Set additional options for Node.js compatibility
            context.set_ciphers("HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA")
            context.options |= (
                ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            )

            logger.debug(f"SSL context created for {service_name} with certificate chain")
            return context

        except Exception as e:
            logger.error(f"Failed to create SSL context for {service_name}: {e}")
            raise SSLServiceError(f"SSL context creation failed: {e}")

    def generate_domain_cert(self, domain: str) -> Tuple[Path, Path]:
        """
        Generate certificate for a specific domain (for MITM proxy).

        Args:
            domain: Domain name to generate certificate for (e.g., 'api.anthropic.com')

        Returns:
            Tuple of (certificate_path, private_key_path)

        Raises:
            SSLServiceError: If certificate generation fails
        """
        # Validate domain parameter
        if not domain or not domain.strip():
            raise SSLServiceError("Domain cannot be empty or None")

        domain = domain.strip()
        service_name = f"domain_{domain.replace('.', '_').replace(':', '_')}"
        cache_key = f"domain_{domain}"

        if cache_key in self._service_certs:
            cert_path, key_path = self._service_certs[cache_key]
            if cert_path.exists() and key_path.exists():
                logger.debug(f"Using cached certificate for domain {domain}")
                return cert_path, key_path

        try:
            # Ensure CA exists
            if not self.ensure_ca_exists():
                raise SSLServiceError("Failed to ensure CA certificate exists")

            # Generate domain certificate
            cert_path = self.cert_dir / f"{service_name}.crt"
            key_path = self.cert_dir / f"{service_name}.key"

            logger.info(f"Generating SSL certificate for domain: {domain}")
            self._generate_service_certificate(service_name, [domain], cert_path, key_path)

            # Cache the result
            self._service_certs[cache_key] = (cert_path, key_path)

            logger.info(f"Domain certificate created: {cert_path}")
            return cert_path, key_path

        except Exception as e:
            logger.error(f"Failed to generate certificate for domain {domain}: {e}")
            raise SSLServiceError(f"Domain certificate generation failed: {e}")

    def clear_certificates(self) -> bool:
        """
        Clear all existing certificates to force regeneration.
        Useful after certificate generation changes.

        Returns:
            True if certificates were cleared successfully
        """
        try:
            import glob

            cert_files = (
                glob.glob(str(self.cert_dir / "*.crt"))
                + glob.glob(str(self.cert_dir / "*.key"))
                + glob.glob(str(self.cert_dir / "*.chain.crt"))
            )

            for cert_file in cert_files:
                Path(cert_file).unlink(missing_ok=True)
                logger.debug(f"Removed certificate file: {cert_file}")

            # Clear cache
            self._service_certs.clear()

            logger.info(f"Cleared {len(cert_files)} certificate files")
            return True

        except Exception as e:
            logger.error(f"Failed to clear certificates: {e}")
            return False

    def get_ca_info(self) -> Dict[str, str]:
        """
        Get information about the CA certificate.

        Returns:
            Dictionary with CA certificate information
        """
        if not self.ca_cert_path.exists():
            return {"status": "not_created", "path": str(self.ca_cert_path)}

        try:
            with open(self.ca_cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())

            return {
                "status": "exists",
                "path": str(self.ca_cert_path),
                "subject": cert.subject.rfc4514_string(),
                "issuer": cert.issuer.rfc4514_string(),
                "not_valid_before": cert.not_valid_before.isoformat(),
                "not_valid_after": cert.not_valid_after.isoformat(),
                "serial_number": str(cert.serial_number),
            }

        except Exception as e:
            logger.error(f"Failed to read CA certificate info: {e}")
            return {"status": "error", "error": str(e), "path": str(self.ca_cert_path)}

    def _generate_ca_certificate(self) -> None:
        """Generate CodeGuard CA certificate and private key."""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Create certificate
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CodeGuard Testing"),
                x509.NameAttribute(NameOID.COMMON_NAME, "CodeGuard Testing Root CA"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow() - timedelta(days=2))
            .not_valid_after(datetime.utcnow() + timedelta(days=3650))  # 10 years
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(private_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                # Add extended key usage for CA like mitmproxy
                x509.ExtendedKeyUsage(
                    [
                        ExtendedKeyUsageOID.SERVER_AUTH,
                        ExtendedKeyUsageOID.CLIENT_AUTH,
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        # Write certificate
        with open(self.ca_cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Write private key
        with open(self.ca_key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # Set restrictive permissions on private key
        self.ca_key_path.chmod(0o600)

    def _generate_service_certificate(
        self, service_name: str, hosts: List[str], cert_path: Path, key_path: Path
    ) -> None:
        """Generate service certificate signed by CA."""
        # Load CA certificate and key
        with open(self.ca_cert_path, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())

        with open(self.ca_key_path, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)

        # Generate private key for service
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Create certificate
        # Ensure we have a valid common name (cannot be empty string)
        common_name = ""
        if hosts and hosts[0].strip():
            common_name = hosts[0].strip()
        elif service_name.strip():
            common_name = service_name.strip()
        else:
            common_name = "localhost"  # Fallback to localhost if everything else is empty

        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CodeGuard Testing"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ]
        )

        # Build SAN (Subject Alternative Names) - mitmproxy style
        san_list = []
        for host in hosts:
            # Normalize the host first
            host = host.strip().lower()
            if not host:
                continue

            # Try to parse as IP address first
            try:
                import ipaddress

                ip_addr = ipaddress.ip_address(host)
                san_list.append(x509.IPAddress(ip_addr))
                logger.debug(f"Added IP address to SAN: {host}")
            except ValueError:
                # Not a valid IP, treat as DNS name
                # Remove port numbers if present
                if ":" in host and not host.startswith("["):  # IPv6 addresses start with [
                    host = host.split(":")[0]

                # Validate DNS name format - allow localhost and other valid hostnames
                if host and len(host) <= 253:
                    san_list.append(x509.DNSName(host))
                    logger.debug(f"Added DNS name to SAN: {host}")
                else:
                    logger.warning(f"Skipping invalid hostname: {host}")

        # Always add common localhost entries for development
        localhost_entries = [
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            x509.IPAddress(ipaddress.ip_address("::1")),
        ]

        for entry in localhost_entries:
            if entry not in san_list:
                san_list.append(entry)

        cert_builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(ca_cert.subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow() - timedelta(days=2))
            .not_valid_after(datetime.utcnow() + timedelta(days=365))  # 1 year
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage(
                    [
                        ExtendedKeyUsageOID.SERVER_AUTH,
                        ExtendedKeyUsageOID.CLIENT_AUTH,
                    ]
                ),
                critical=False,
            )
        )

        # Add SAN extension - always include even if empty for Node.js compatibility
        if san_list:
            cert_builder = cert_builder.add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            )
        else:
            # Even with no custom hosts, add localhost for testing
            cert_builder = cert_builder.add_extension(
                x509.SubjectAlternativeName(
                    [x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
                ),
                critical=False,
            )

        cert = cert_builder.sign(ca_key, hashes.SHA256())

        # Write certificate
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Write private key
        with open(key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # Set restrictive permissions on private key
        key_path.chmod(0o600)

    def _create_cert_chain(self, service_cert_path: Path) -> Path:
        """
        Create a certificate chain file with service cert + CA cert.
        This is required for proper Node.js certificate validation.

        Args:
            service_cert_path: Path to the service certificate

        Returns:
            Path to the certificate chain file
        """
        chain_path = service_cert_path.with_suffix(".chain.crt")

        try:
            # Read service certificate
            with open(service_cert_path, "rb") as f:
                service_cert_data = f.read()

            # Read CA certificate
            with open(self.ca_cert_path, "rb") as f:
                ca_cert_data = f.read()

            # Write chain file (service cert first, then CA cert)
            with open(chain_path, "wb") as f:
                f.write(service_cert_data)
                f.write(b"\n")
                f.write(ca_cert_data)

            logger.debug(f"Certificate chain created: {chain_path}")
            return chain_path

        except Exception as e:
            logger.error(f"Failed to create certificate chain: {e}")
            # Fallback to service certificate only
            return service_cert_path

    def validate_certificate_compatibility(self, cert_path: Path) -> Dict[str, any]:
        """
        Validate certificate compatibility with Node.js and other clients.

        Args:
            cert_path: Path to certificate to validate

        Returns:
            Dictionary with validation results
        """
        if not cert_path.exists():
            return {"valid": False, "error": "Certificate file not found"}

        try:
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())

            issues = []
            warnings = []

            # Check validity period
            now = datetime.utcnow()
            if cert.not_valid_before > now:
                issues.append("Certificate not yet valid (clock skew issue)")
            if cert.not_valid_after < now:
                issues.append("Certificate expired")

            # Check for proper extensions
            try:
                basic_constraints = cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.BASIC_CONSTRAINTS
                )
            except x509.ExtensionNotFound:
                issues.append("Missing Basic Constraints extension")

            try:
                key_usage = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE)
            except x509.ExtensionNotFound:
                issues.append("Missing Key Usage extension")

            try:
                ext_key_usage = cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.EXTENDED_KEY_USAGE
                )
            except x509.ExtensionNotFound:
                warnings.append("Missing Extended Key Usage extension")

            # Check SAN extension for server certificates
            try:
                san = cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
            except x509.ExtensionNotFound:
                warnings.append("Missing Subject Alternative Name extension")

            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "subject": cert.subject.rfc4514_string(),
                "not_valid_before": cert.not_valid_before.isoformat(),
                "not_valid_after": cert.not_valid_after.isoformat(),
            }

        except Exception as e:
            return {"valid": False, "error": f"Certificate validation failed: {e}"}


# Global SSL service instance
_ssl_service: Optional[CodeGuardSSLService] = None


def get_ssl_service() -> CodeGuardSSLService:
    """
    Get the global SSL service instance.

    Returns:
        Shared SSL service instance
    """
    global _ssl_service
    if _ssl_service is None:
        _ssl_service = CodeGuardSSLService()
    return _ssl_service
