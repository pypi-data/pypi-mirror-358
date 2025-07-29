#
# src/pyvider/rpcplugin/crypto/debug.py
#

"""
Cryptographic Debugging Utilities.

This module provides functions to log detailed information about X.509 certificates
and private keys for debugging purposes within the Pyvider RPC Plugin crypto package.
"""

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from pyvider.rpcplugin.exception import CertificateError
from pyvider.telemetry import logger

from .types import PrivateKeyType


def display_cert_details(certificate: x509.Certificate) -> None:
    """
    Logs detailed information about the provided X.509 certificate.

    Extracts and logs:
      - Serial number (hexadecimal, colon-separated).
      - Subject and issuer distinguished names.
      - Validity period (Not Before, Not After).
      - Key Usage extension details.
      - Extended Key Usage extension details.
      - Basic Constraints (CA status, path length).
      - Public key algorithm, size/curve, and PEM representation.

    Args:
        certificate: The `cryptography.x509.Certificate` object to inspect.

    Raises:
      CertificateError: If any certificate detail cannot be extracted.
    """
    try:
        logger.debug(
            "📜📂🚀 display_cert_details: Starting extraction of certificate details."
        )

        serial_str = f"{certificate.serial_number:0x}"
        serial_number_hex = ":".join(
            serial_str[i : i + 2] for i in range(0, len(serial_str), 2)
        )
        logger.debug(f"  🔢 Serial Number: {serial_number_hex}")

        logger.debug(f"  🏷️ Subject: {certificate.subject.rfc4514_string()}")
        logger.debug(f"  📢 Issuer: {certificate.issuer.rfc4514_string()}")

        logger.debug(f"  📆 Valid From: {certificate.not_valid_before_utc.isoformat()}")
        logger.debug(f"  📆 Valid To: {certificate.not_valid_after_utc.isoformat()}")

        try:
            key_usage_ext_value = certificate.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.KEY_USAGE
            ).value
            if isinstance(key_usage_ext_value, x509.KeyUsage):
                usages = []
                if key_usage_ext_value.digital_signature:
                    usages.append("digital_signature")
                if key_usage_ext_value.content_commitment:
                    usages.append("content_commitment")
                if key_usage_ext_value.key_encipherment:
                    usages.append("key_encipherment")
                if key_usage_ext_value.data_encipherment:
                    usages.append("data_encipherment")
                if key_usage_ext_value.key_agreement:
                    usages.append("key_agreement")
                if key_usage_ext_value.key_cert_sign:
                    usages.append("key_cert_sign")
                if key_usage_ext_value.crl_sign:
                    usages.append("crl_sign")
                logger.debug(
                    f"  🔑 Key Usage: {', '.join(usages) if usages else 'None'}"
                )
            else:
                logger.debug(
                    "  🔑 Key Usage: Value is not a KeyUsage object or not present"
                )
        except x509.ExtensionNotFound:
            logger.debug("  🔑 Key Usage: Not present")

        try:
            ext_key_usage_ext_value = certificate.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.EXTENDED_KEY_USAGE
            ).value
            if isinstance(ext_key_usage_ext_value, x509.ExtendedKeyUsage):
                eku_oids = [oid.dotted_string for oid in ext_key_usage_ext_value]
                eku_names = [
                    getattr(oid, "name", oid.dotted_string)
                    for oid in ext_key_usage_ext_value
                ]
                logger.debug(
                    "  ✨ Extended Key Usage (OID): "
                    f"{', '.join(eku_oids) if eku_oids else 'None'}"
                )
                logger.debug(
                    "  ✨ Extended Key Usage (Name): "
                    f"{', '.join(eku_names) if eku_names else 'None'}"
                )
            else:
                logger.debug(
                    "  ✨ Extended Key Usage: Value is not an ExtendedKeyUsage "
                    "object or not present"
                )
        except x509.ExtensionNotFound:
            logger.debug("  ✨ Extended Key Usage: Not present")

        try:
            bc_ext_value = certificate.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.BASIC_CONSTRAINTS
            ).value
            if isinstance(bc_ext_value, x509.BasicConstraints):
                ca_info = "CA" if bc_ext_value.ca else "Not CA"
                path_length = (
                    f" (Path Length: {bc_ext_value.path_length})"
                    if bc_ext_value.path_length is not None
                    else ""
                )
                logger.debug(f"  ⛓️ Basic Constraints: {ca_info}{path_length}")
            else:
                logger.debug(
                    "  ⛓️ Basic Constraints: Value is not a BasicConstraints "
                    "object or not present"
                )
        except x509.ExtensionNotFound:
            logger.debug("  ⛓️ Basic Constraints: Not present")

        public_key_obj = certificate.public_key()
        key_type_str: str
        key_size_str: str | int

        match public_key_obj:
            case rsa.RSAPublicKey():
                key_type_str = "RSA"
                key_size_str = public_key_obj.key_size
            case ec.EllipticCurvePublicKey():
                key_type_str = "ECDSA"
                key_size_str = public_key_obj.curve.name
            case _:
                key_type_str = "Unknown"
                key_size_str = "Unknown"

        logger.debug(f"  🔑 Public Key: {key_type_str} ({key_size_str})")
        pem_public_key = public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
        logger.debug(f"  🔑 PEM Encoded Public Key:\n{pem_public_key}")

        logger.debug(
            "📜📂🚀 display_cert_details: Certificate details extracted successfully."
        )
    except Exception as e:
        logger.error(
            f"📜🚨 Could not extract certificate details: {e!s}",
            extra={"error": str(e)},
        )
        raise CertificateError("Could not extract certificate details") from e


def display_key_details(priv_key: PrivateKeyType | None) -> None:
    """
    Logs private key details in a structured format.

    Logs:
      - The key type and size/curve name.
      - The PEM-encoded private key (PKCS8 format).

    Args:
        priv_key: The private key object (RSAPrivateKey or
                  EllipticCurvePrivateKey), or None.

    Raises:
      CertificateError: If key details cannot be extracted when a key is provided.
    """
    if priv_key is None:
        logger.warning("🔑⚠️ display_key_details: No private key available to display.")
        return

    try:
        logger.debug(
            "🔑📂🚀 display_key_details: Starting extraction of private key details."
        )
        key_type_str: str
        key_size_info: str | int

        match priv_key:
            case rsa.RSAPrivateKey():
                key_type_str = "RSA"
                key_size_info = priv_key.key_size
            case ec.EllipticCurvePrivateKey():
                key_type_str = "ECDSA"
                key_size_info = priv_key.curve.name
            case _:
                key_type_str = "Unknown"
                key_size_info = "Unknown"

        logger.debug(f"  🔑 Key Type: {key_type_str}")
        logger.debug(f"  📏 Key Size/Curve: {key_size_info}")

        pem_key = priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
        logger.debug(f"  🔑 PEM Encoded Private Key:\n{pem_key}")
        logger.debug(
            "🔑📂🚀 display_key_details: Private key details extracted successfully."
        )
    except Exception as e:
        logger.error(
            f"🔑🚨 Could not extract key details: {e!s}",
            extra={"error": str(e)},
        )
        raise CertificateError("Could not extract key details") from e


# 🐍🏗️🔌
