# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'main'
BUILD_TIME = '2025-06-28T20:17:39Z'
BUILD_COMMIT = '0a363a67ac006309680e7280be80a0b78c4aaf55'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
