"""Framework-agnostic data access layer.

Each module exposes a thin network ``fetch_*`` function plus pure ``parse_*``
helpers.  Keeping parsing separate from I/O means the parsers can be unit
tested with captured fixtures and no internet connection.
"""
