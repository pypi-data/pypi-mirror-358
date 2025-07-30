# setup.py
from setuptools import setup, find_packages
import os

# Read version from terraback/__init__.py
version = {}
version_file = os.path.join(os.path.dirname(__file__), "terraback", "__init__.py")
with open(version_file) as f:
    exec(f.read(), version)

# Read README for long description
long_description = ""
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()

# Read requirements from requirements.txt
requirements = []
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh 
                       if line.strip() and not line.startswith("#")]

# Detect build tier
TIER = os.environ.get('TERRABACK_TIER', 'community')

# Tier-specific configurations
TIER_CONFIGS = {
    'community': {
        'name': 'terraback',
        'description': 'Multi-Cloud Infrastructure as Code - Community Edition',
        'packages': find_packages(exclude=['terraback.enterprise*', 'tests.enterprise*']),
        'install_requires_extra': [],
        'entry_points': {
            'console_scripts': [
                'terraback=terraback.cli.main:app',
            ],
        },
    },
    'migration': {
        'name': 'terraback-migration',
        'description': 'Multi-Cloud Infrastructure as Code - Migration Pass',
        'packages': find_packages(exclude=['terraback.enterprise*', 'tests.enterprise*']),
        'install_requires_extra': [
            'pyjwt>=2.6.0',  # For license validation
            'cryptography>=3.4.0',
        ],
        'entry_points': {
            'console_scripts': [
                'terraback=terraback.cli.main:app',
            ],
        },
    },
    'enterprise': {
        'name': 'terraback-enterprise',
        'description': 'Multi-Cloud Infrastructure as Code - Enterprise Edition',
        'packages': find_packages(),
        'install_requires_extra': [
            'pyjwt>=2.6.0',
            'cryptography>=3.4.0',
            'python-ldap>=3.4.0',  # SSO support
            'prometheus_client>=0.15.0',  # Metrics
        ],
        'entry_points': {
            'console_scripts': [
                'terraback=terraback.cli.main:app',
            ],
        },
    }
}

# Get configuration for current tier
tier_config = TIER_CONFIGS[TIER]

setup(
    name=tier_config['name'],
    version=version['__version__'],
    description=tier_config['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    packages=tier_config['packages'],
    install_requires=requirements + tier_config['install_requires_extra'],
    extras_require={
        'aws': [
            'boto3>=1.38.21',
            'botocore>=1.38.21',
            's3transfer>=0.12.0',
        ],
        'azure': [
            'azure-identity>=1.15.0',
            'azure-mgmt-resource>=23.1.0',
            'azure-mgmt-compute>=31.0.0',
            'azure-mgmt-network>=27.0.0',
            'azure-mgmt-storage>=21.2.0',
            'azure-mgmt-web>=7.3.0',
            'azure-mgmt-sql>=4.0.0',
            'azure-mgmt-keyvault>=10.3.0',
            'azure-mgmt-monitor>=6.0.0',
            'azure-core>=1.30.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
    },
    entry_points=tier_config['entry_points'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    author='Reops Tech',
    author_email='hello@terraback.io',
    url='https://github.com/bmoldo/terraback',
    project_urls={
        'Bug Reports': 'https://github.com/bmoldo/terraback/issues',
        'Source': 'https://github.com/bmoldo/terraback',
        'Website': 'https://www.terraback.dev.io',
    },
)