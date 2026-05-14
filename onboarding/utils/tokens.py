import uuid
import secrets
import hashlib
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def generate_invitation_token(employee=None):
    """
    Generate a secure, unique invitation token for new joiner onboarding

    Args:
        employee: Employee object (optional, for logging)

    Returns:
        str: Unique invitation token (UUID format)
    """
    try:
        token = str(uuid.uuid4())
        if employee:
            logger.info(f"Generated invitation token for {employee.name}")
        return token
    except Exception as e:
        logger.error(f"Error generating invitation token: {str(e)}")
        return None


def generate_signature_token(invitation=None):
    """
    Generate a secure token for digital signature requests

    Args:
        invitation: OnboardingInvitation object (optional, for logging)

    Returns:
        str: Unique signature token
    """
    try:
        token = str(uuid.uuid4())
        if invitation:
            logger.info(f"Generated signature token for {invitation.employee.name}")
        return token
    except Exception as e:
        logger.error(f"Error generating signature token: {str(e)}")
        return None


def generate_secure_token():
    """
    Generate a cryptographically secure random token

    Returns:
        str: Secure random token (hex string)
    """
    try:
        return secrets.token_hex(32)  # 64 character hex string
    except Exception as e:
        logger.error(f"Error generating secure token: {str(e)}")
        return None


def verify_token(token, token_obj):
    """
    Verify if a token is valid (exists, not expired, correct status)

    Args:
        token: Token string to verify
        token_obj: Token object (OnboardingInvitation or DigitalSignature)

    Returns:
        dict: {
            'valid': bool,
            'error': str or None,
            'object': token_obj or None
        }
    """
    try:
        if not token:
            return {
                'valid': False,
                'error': 'Token is required',
                'object': None
            }

        if not token_obj:
            return {
                'valid': False,
                'error': 'Invalid token',
                'object': None
            }

        # Check if token is expired
        if hasattr(token_obj, 'is_expired') and token_obj.is_expired():
            return {
                'valid': False,
                'error': 'Token has expired',
                'object': None
            }

        # Check if token is valid (for tokens with is_valid method)
        if hasattr(token_obj, 'is_valid'):
            if not token_obj.is_valid():
                return {
                    'valid': False,
                    'error': 'Token is no longer valid',
                    'object': None
                }

        logger.info(f"Token verified successfully")
        return {
            'valid': True,
            'error': None,
            'object': token_obj
        }

    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return {
            'valid': False,
            'error': 'Error verifying token',
            'object': None
        }


def is_token_valid(token_obj):
    """
    Quick check if a token object is valid

    Args:
        token_obj: Token object (OnboardingInvitation or DigitalSignature)

    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        if not token_obj:
            return False

        # Check expiry
        if hasattr(token_obj, 'is_expired'):
            if token_obj.is_expired():
                return False

        # Check validity method
        if hasattr(token_obj, 'is_valid'):
            return token_obj.is_valid()

        return True

    except Exception as e:
        logger.error(f"Error checking token validity: {str(e)}")
        return False


def get_token_expiry_date(validity_days=None):
    """
    Calculate token expiry date

    Args:
        validity_days: Number of days until expiry (uses setting if not provided)

    Returns:
        datetime: Expiry datetime
    """
    try:
        if validity_days is None:
            validity_days = getattr(settings, 'INVITATION_VALIDITY_DAYS', 30)

        expiry_date = timezone.now() + timedelta(days=validity_days)
        return expiry_date

    except Exception as e:
        logger.error(f"Error calculating token expiry: {str(e)}")
        return timezone.now() + timedelta(days=30)  # Default fallback


def is_token_expired(expires_at):
    """
    Check if a token has expired based on expiry datetime

    Args:
        expires_at: Expiry datetime

    Returns:
        bool: True if expired, False if still valid
    """
    try:
        if not expires_at:
            return True

        return timezone.now() > expires_at

    except Exception as e:
        logger.error(f"Error checking expiry: {str(e)}")
        return True


def hash_token(token):
    """
    Hash a token for secure storage (one-way hashing)

    Args:
        token: Token to hash

    Returns:
        str: SHA-256 hash of token
    """
    try:
        if not token:
            return None

        return hashlib.sha256(token.encode()).hexdigest()

    except Exception as e:
        logger.error(f"Error hashing token: {str(e)}")
        return None


def validate_token_format(token, expected_format='uuid'):
    """
    Validate token format

    Args:
        token: Token to validate
        expected_format: 'uuid' or 'hex'

    Returns:
        bool: True if token format is valid
    """
    try:
        if not token or not isinstance(token, str):
            return False

        if expected_format == 'uuid':
            try:
                uuid.UUID(token)
                return True
            except ValueError:
                return False

        elif expected_format == 'hex':
            int(token, 16)
            return len(token) == 64  # 32 bytes = 64 hex chars
            return True

        return False

    except Exception as e:
        logger.error(f"Error validating token format: {str(e)}")
        return False


def regenerate_token(token_obj, new_validity_days=None):
    """
    Regenerate a token (useful for resending invitations)

    Args:
        token_obj: Token object to update
        new_validity_days: Days for new validity period

    Returns:
        str: New token, None if error
    """
    try:
        if hasattr(token_obj, 'invitation_token'):
            # OnboardingInvitation
            token_obj.invitation_token = generate_invitation_token(token_obj.employee)
        elif hasattr(token_obj, 'signature_token'):
            # DigitalSignature
            token_obj.signature_token = generate_signature_token(token_obj.invitation)

        if new_validity_days:
            token_obj.expires_at = get_token_expiry_date(new_validity_days)

        token_obj.save()
        logger.info(f"Token regenerated for object {token_obj}")
        return token_obj.invitation_token if hasattr(token_obj, 'invitation_token') else token_obj.signature_token

    except Exception as e:
        logger.error(f"Error regenerating token: {str(e)}")
        return None
