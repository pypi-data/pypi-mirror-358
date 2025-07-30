import os
import jwt
import json
import requests
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import typer

# This will be replaced by the build process. Defaults to 'community' for local dev.
try:
    from terraback._build_info import BUILD_EDITION
except ImportError:
    BUILD_EDITION = "community"

# API Configuration
API_BASE_URL = os.environ.get('TERRABACK_API_URL', 'https://jaejtnxq15.execute-api.us-east-1.amazonaws.com/v1')
ACTIVATION_ENDPOINT = f"{API_BASE_URL}/activate"

# --- PUBLIC KEY ---
# IMPORTANT: Replace this with your actual 4096-bit RSA public key
# Generated with: openssl rsa -in private-key.pem -pubout -out public-key.pem
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAl47KZZNZTWDLp2kD732a
5ijj4sXanQSiuRhIv5Bs9x8qNwSt4MvxYi0UU9OKfIftteITEPzwfDzRIxEdHJ97
HfN6qwlADHwnCK+88nvZjKkC767c4DpL56zltT4EnDEWLuNPRaXHiOswFyP5Gglw
Tgg7DUpMpSUnh/HpT93ZB6CajvSTn9vqZU8Y5n89QhHeTfdDpAfKTRtC4hsx/vk7
oSiEUUv+oi/WK5APJagqDDM/9/6J7zs4NCRGxy57JIFUM+rl1KKDn3/ht5oZ7eFl
AwLfRAoC4xjkRLslPIKuH4xp1KdpXzn2h2CC4izLytYh6vxQ70fjoa8VBuoXn8pd
0HkNRr67yvKsA1Y2YZH/QfKZvZS76Vg66p1rIajFpdTn6a79DRZ6V1NuX6a+/Hyy
DTzgjcsYKlwZUmYggerGT3HYeQitkTePkX6KFRwC62kF7MfFm0dNsJXBsK4IOvwY
WgGT01IS/NICEjedUgT04Lr8h2uC13V5ClkBrZpSUZFtzpsLXsaR4vy8jwwzZH2K
Ix95zMXEEF6ein5epVkRXlz7rDSbCxWAmE9Q8W4JLcFQrcOcKskzoN1bPtTXy30q
Ev5KTDWwxozgail7Cw8FgxjUD/LUYQX2xbRTObHsjwXKlOgCB6CYZkp9NhByU7xJ
aGFJVexH2FRpADyYw5Hx1ocCAwEAAQ==
-----END PUBLIC KEY-----"""

# Tier Definitions
class Tier:
    COMMUNITY = "community"
    PROFESSIONAL = "professional"  # Match Lambda function
    ENTERPRISE = "enterprise"
    ALL = [COMMUNITY, PROFESSIONAL, ENTERPRISE]

# Legacy aliases for backward compatibility
class LegacyTier:
    PRO = "professional"  # Alias for PROFESSIONAL
    MIGRATION = "professional"  # Migration Pass maps to Professional

# In-memory cache for the validated license to avoid repeated file I/O
_license_cache: Optional[Dict[str, Any]] = None
_license_checked = False

def get_license_path() -> Path:
    """Finds the license.key file, prioritizing the user's home directory."""
    return Path.home() / ".terraback" / "license.jwt"  # Changed to .jwt for clarity

def get_metadata_path() -> Path:
    """Path for storing license metadata (email, expiry, etc)"""
    return Path.home() / ".terraback" / "license_metadata.json"

def normalize_license_key(key: str) -> str:
    """Normalize user input: remove spaces, dashes, uppercase"""
    return key.upper().replace('-', '').replace(' ', '').strip()

def format_license_key(normalized_key: str) -> Optional[str]:
    """Format normalized key back to XXXX-XXXX-XXXX-XXXX"""
    if len(normalized_key) != 16:
        return None
    return '-'.join([normalized_key[i:i+4] for i in range(0, 16, 4)])

def _decode_and_validate(jwt_token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates the JWT license key using RS256 and the public key.
    """
    if not PUBLIC_KEY or "-----BEGIN PUBLIC KEY-----" not in PUBLIC_KEY:
        # Safety check: if the public key isn't populated, validation must fail.
        typer.secho("Error: Public key for license validation is not configured.", fg=typer.colors.RED)
        return None
    try:
        # Verify the JWT signature using the public key.
        # The 'exp' (expiry) and 'iat' (issued at) claims are checked automatically.
        data = jwt.decode(jwt_token, PUBLIC_KEY, algorithms=["RS256"])
    except jwt.ExpiredSignatureError:
        typer.secho("Error: License key has expired.", fg=typer.colors.RED)
        return None
    except jwt.InvalidTokenError:
        typer.secho("Error: Invalid license key format or signature.", fg=typer.colors.RED)
        return None
    except Exception as e:
        typer.secho(f"Error: License validation failed: {e}", fg=typer.colors.RED)
        return None

    # Additional validation for custom claims within the token
    if not isinstance(data, dict) or "tier" not in data or data["tier"] not in Tier.ALL:
        typer.secho("Error: Invalid license tier or malformed license data.", fg=typer.colors.RED)
        return None

    # Add formatted expiry date for display
    if 'exp' in data:
        try:
            expiry_date = datetime.fromtimestamp(data['exp'])
            data['expiry'] = expiry_date.strftime('%Y-%m-%d %H:%M:%S UTC')
        except (ValueError, TypeError):
            data['expiry'] = 'Unknown'

    return data

def get_active_license() -> Optional[Dict[str, Any]]:
    """Reads, validates, and caches the active license from the license file."""
    global _license_cache, _license_checked
    if _license_checked:
        return _license_cache

    license_path = get_license_path()
    jwt_token = None
    if license_path.exists():
        try:
            jwt_token = license_path.read_text().strip()
        except IOError:
            jwt_token = None
    
    _license_cache = _decode_and_validate(jwt_token) if jwt_token else None
    _license_checked = True
    return _license_cache

def activate_license(key: str) -> bool:
    """
    Activates a new license by exchanging the user-friendly key for a JWT via API.
    
    Args:
        key: User-friendly license key (e.g., XXXX-XXXX-XXXX-XXXX)
        
    Returns:
        bool: True if activation successful, False otherwise
    """
    try:
        # Clean up the key (user might paste with extra spaces)
        key = key.strip()
        
        # Show progress
        typer.echo("🔄 Contacting license server...")
        
        # Call activation API
        response = requests.post(
            ACTIVATION_ENDPOINT,
            json={"license_key": key},
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"Terraback-CLI/{BUILD_EDITION}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            jwt_token = data.get('jwt_token')
            
            if not jwt_token:
                typer.secho("Error: Invalid response from license server.", fg=typer.colors.RED)
                return False
            
            # Validate the JWT before saving
            license_data = _decode_and_validate(jwt_token)
            if not license_data:
                return False
            
            # Save the JWT
            license_path = get_license_path()
            try:
                license_path.parent.mkdir(parents=True, exist_ok=True)
                license_path.write_text(jwt_token)
                
                # Save metadata for quick access
                metadata = {
                    'email': data.get('email') or license_data.get('email'),
                    'expires_at': data.get('expires_at') or license_data.get('expiry'),
                    'activated_at': datetime.utcnow().isoformat(),
                    'friendly_key': format_license_key(normalize_license_key(key))  # Store formatted key
                }
                metadata_path = get_metadata_path()
                metadata_path.write_text(json.dumps(metadata, indent=2))
                
                # Invalidate cache so it's re-read on the next check
                global _license_cache, _license_checked
                _license_cache = license_data
                _license_checked = True
                
                typer.secho("✅ License activated successfully!", fg=typer.colors.GREEN, bold=True)
                return True
                
            except IOError as e:
                typer.secho(f"Error: Could not save license: {e}", fg=typer.colors.RED)
                return False
                
        elif response.status_code == 400:
            error = response.json().get('error', 'Invalid license key format')
            typer.secho(f"❌ Error: {error}", fg=typer.colors.RED)
            typer.echo("Please check your license key format (XXXX-XXXX-XXXX-XXXX)")
            return False
            
        elif response.status_code == 403:
            error = response.json().get('error', 'License validation failed')
            typer.secho(f"❌ Error: {error}", fg=typer.colors.RED)
            return False
            
        elif response.status_code == 404:
            typer.secho("❌ Error: License key not found.", fg=typer.colors.RED)
            typer.echo("Please check that you've entered the correct key.")
            return False
            
        else:
            typer.secho(f"❌ Error: Unexpected response from license server (status {response.status_code})", 
                       fg=typer.colors.RED)
            return False
            
    except requests.exceptions.Timeout:
        typer.secho("❌ Error: Connection to license server timed out.", fg=typer.colors.RED)
        typer.echo("Please check your internet connection and try again.")
        return False
        
    except requests.exceptions.ConnectionError:
        typer.secho("❌ Error: Could not connect to license server.", fg=typer.colors.RED)
        typer.echo("Please check your internet connection and try again.")
        return False
        
    except requests.exceptions.RequestException as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        return False
        
    except Exception as e:
        typer.secho(f"❌ Unexpected error: {e}", fg=typer.colors.RED)
        return False

def get_active_tier() -> str:
    """
    Determines the current active feature tier. It prioritizes the build-time
    edition for licensed binaries; otherwise, it checks for a valid license key.
    """
    # Map legacy build editions to new tier names
    build_tier_map = {
        'pro': Tier.PROFESSIONAL,
        'professional': Tier.PROFESSIONAL,
        'migration': Tier.PROFESSIONAL,  # Migration Pass = Professional tier
        'enterprise': Tier.ENTERPRISE,
        'community': Tier.COMMUNITY
    }
    
    if BUILD_EDITION.lower() in build_tier_map and BUILD_EDITION.lower() != 'community':
        return build_tier_map[BUILD_EDITION.lower()]

    license_data = get_active_license()
    if license_data:
        tier = license_data.get("tier", Tier.COMMUNITY)
        # Ensure tier is valid
        return tier if tier in Tier.ALL else Tier.COMMUNITY
    
    return Tier.COMMUNITY

def require_tier(required_tier: str) -> Callable:
    """Decorator factory to restrict functions to a minimum license tier."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            active_tier = get_active_tier()
            tier_levels = {
                Tier.COMMUNITY: 0, 
                Tier.PROFESSIONAL: 1, 
                Tier.ENTERPRISE: 2
            }
            
            if tier_levels.get(active_tier, -1) >= tier_levels.get(required_tier, 99):
                return func(*args, **kwargs)
            else:
                typer.secho(f"Error: This feature requires a '{required_tier.capitalize()}' license.", fg=typer.colors.RED, bold=True)
                typer.echo(f"Your current tier: {active_tier.capitalize()}")
                
                if required_tier == Tier.PROFESSIONAL:
                    typer.echo("To upgrade, visit https://terraback.io/pricing for the Migration Pass.")
                elif required_tier == Tier.ENTERPRISE:
                    typer.echo("To upgrade, contact sales@terraback.io for Enterprise licensing.")
                else:
                    typer.echo("To upgrade, visit https://terraback.io/pricing")
                    
                typer.echo("Or use 'terraback license activate <key>' if you already have a license.")
                raise typer.Exit(code=1)
        return wrapper
    return decorator

# Convenience decorators for Professional and Enterprise tiers
require_professional = require_tier(Tier.PROFESSIONAL)
require_enterprise = require_tier(Tier.ENTERPRISE)

# Legacy aliases for backward compatibility
require_pro = require_professional  # For existing code that uses @require_pro

def check_feature_access(feature_tier: str) -> bool:
    """Check if current tier has access to a feature without raising errors."""
    active_tier = get_active_tier()
    tier_levels = {
        Tier.COMMUNITY: 0, 
        Tier.PROFESSIONAL: 1, 
        Tier.ENTERPRISE: 2
    }
    return tier_levels.get(active_tier, -1) >= tier_levels.get(feature_tier, 99)

def get_license_status() -> Dict[str, Any]:
    """Get comprehensive license status information."""
    active_tier = get_active_tier()
    license_data = get_active_license()
    
    status = {
        'active_tier': active_tier,
        'has_license': license_data is not None,
        'license_valid': license_data is not None,
        'build_edition': BUILD_EDITION
    }
    
    if license_data:
        status.update({
            'email': license_data.get('email'),
            'tier': license_data.get('tier'),
            'expires': license_data.get('expiry'),
            'order_id': license_data.get('order_id')
        })
        
        # Try to get the friendly key from metadata
        try:
            metadata_path = get_metadata_path()
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                status['friendly_key'] = metadata.get('friendly_key')
        except:
            pass
    
    return status