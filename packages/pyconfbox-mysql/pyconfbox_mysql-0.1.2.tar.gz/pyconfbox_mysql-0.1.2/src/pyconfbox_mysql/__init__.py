"""PyConfBox MySQL Storage Plugin.

This plugin provides MySQL database storage support for PyConfBox.
"""

__version__ = "0.1.0"
__author__ = "Gabriel Ki"
__email__ = "edc1901@gmail.com"

from .storage import MySQLStorage

__all__ = ["MySQLStorage"]
