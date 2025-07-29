"""PyConfBox PostgreSQL Storage Plugin.

This plugin provides PostgreSQL database storage support for PyConfBox.
"""

__version__ = "0.1.0"
__author__ = "Gabriel Ki"
__email__ = "edc1901@gmail.com"

from .storage import PostgreSQLStorage

__all__ = ["PostgreSQLStorage"]
