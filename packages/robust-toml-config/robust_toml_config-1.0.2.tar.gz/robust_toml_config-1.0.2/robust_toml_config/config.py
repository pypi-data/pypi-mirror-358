from tomlkit import parse, dump, TOMLDocument, table, nl, dumps
from tomlkit.items import Table
from pathlib import Path
import contextlib
from typing import Any, Dict, Optional, Union, Type


class TOMLConfig:
    """
    Robust TOML configuration manager with support for dot-path access,
    auto-saving, and format preservation.

    Features:
    - Preserves TOML formatting, comments, and ordering
    - Handles encoding issues automatically
    - Supports dot-path access (e.g., "section.key")
    - Auto-saves changes to file (configurable)
    - Batch update context manager
    - Type safety checks
    - Section-based operations
    """

    def __init__(self, file_path: Union[str, Path], autosave: bool = False,
                 create_if_missing: bool = True, default_data: Optional[dict] = None,
                 encoding: str = "utf-8"):
        """
        Initialize the configuration manager.

        :param file_path: Path to the TOML file
        :param autosave: Automatically save changes (default: True)
        :param create_if_missing: Create file if it doesn't exist (default: True)
        :param default_data: Default data structure if creating new file
        :param encoding: File encoding (default: 'utf-8')
        """
        self._file_path = Path(file_path)
        self._autosave = autosave
        self._create_if_missing = create_if_missing
        self._default_data = default_data or {}
        self._encoding = encoding

        # Initialize the document
        if self._file_path.exists():
            file_data = self._read_file()
            self._doc = self._read_file()  if file_data else self._create_default_document()
        else:
            if self._create_if_missing:
                self._doc = self._create_default_document()
                self.save()
            else:
                raise FileNotFoundError(f"Config file not found: {self._file_path}")

    def _read_file(self) -> TOMLDocument:
        """Read TOML file, handling encoding issues."""
        try:
            with self._file_path.open("r", encoding=self._encoding) as f:
                return parse(f.read())
        except UnicodeDecodeError:
            # Try common UTF-8 variants
            for enc in ["utf-8", "utf-8-sig"]:
                try:
                    with self._file_path.open("r", encoding=enc) as f:
                        return parse(f.read())
                except UnicodeDecodeError:
                    continue
            raise

    def _create_default_document(self) -> TOMLDocument:
        """Create a new document with default data."""
        doc = TOMLDocument()
        doc.add(nl())
        self._merge_data(doc, self._default_data)
        return doc

    def _merge_data(self, target: Union[TOMLDocument, Table], data: dict):
        """Recursively merge data into TOML document."""
        for key, value in data.items():
            if isinstance(value, dict):
                if key not in target:
                    nested = table()
                    target[key] = nested
                else:
                    nested = target[key]
                self._merge_data(nested, value)
            else:
                target[key] = value

    @property
    def autosave(self) -> bool:
        """Get the current autosave status."""
        return self._autosave

    @autosave.setter
    def autosave(self, value: bool):
        """Set the autosave status."""
        self._autosave = value

    def save(self, file_path: Optional[Union[str, Path]] = None):
        """
        Save configuration to file.

        :param file_path: Optional alternative save path
        """
        save_path = Path(file_path) if file_path else self._file_path
        with save_path.open("w", encoding=self._encoding) as f:
            dump(self._doc, f)

    def reload(self):
        """Reload configuration from disk."""
        if self._file_path.exists():
            self._doc = self._read_file()

    def get(self, key_path: str, default: Any = None, create_missing: bool = False) -> Any:
        """
        Get a configuration value using dot-path notation.

        :param key_path: Dot-separated path (e.g., "database.port")
        :param default: Default value if key doesn't exist
        :param create_missing: Create missing tables in path
        :return: Configuration value or default
        """
        keys = key_path.split('.')
        current = self._doc

        try:
            for k in keys:
                if k not in current:
                    if create_missing:
                        new_table = table()
                        current[k] = new_table
                        current = new_table
                    else:
                        return default
                else:
                    current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any, create_missing: bool = True):
        """
        Set a configuration value using dot-path notation.

        :param key_path: Dot-separated path (e.g., "database.port")
        :param value: Value to set
        :param create_missing: Create missing tables in path
        """
        keys = key_path.split('.')
        current = self._doc

        # Traverse to parent of final key
        for k in keys[:-1]:
            if k not in current:
                if create_missing:
                    new_table = table()
                    current[k] = new_table
                    current = new_table
                else:
                    raise KeyError(f"Path '{key_path}' does not exist")
            else:
                current = current[k]

        # Set the final value
        current[keys[-1]] = value

        # Auto-save if enabled
        if self._autosave:
            self.save()

    def get_section(self, section: str, default: Optional[dict] = None) -> dict:
        """
        Get an entire configuration section as a dictionary.

        :param section: Section name
        :param default: Default value if section doesn't exist
        :return: Section dictionary
        """
        section_data = self.get(section, default={})
        return section_data if isinstance(section_data, dict) else default or {}

    def update_section(self, section: str, data: dict, create_missing: bool = True):
        """
        Update an entire configuration section.

        :param section: Section name
        :param data: Dictionary of key-value pairs
        :param create_missing: Create section if it doesn't exist
        """
        if create_missing or section in self:
            for key, value in data.items():
                self.set(f"{section}.{key}", value, create_missing=create_missing)

    def ensure_type(self, key_path: str, expected_type: Type, default: Any):
        """
        Ensure a configuration value is of the expected type.

        If the value is not the correct type, it will be set to the default.

        :param key_path: Dot-separated path
        :param expected_type: Expected type (e.g., int, str, float)
        :param default: Default value to set if type doesn't match
        :return: The value (either existing or new default)
        """
        current = self.get(key_path)

        if not isinstance(current, expected_type):
            self.set(key_path, default)
            return default

        return current

    def to_dict(self) -> dict:
        """Convert the TOML document to a standard Python dictionary."""
        return self._doc.unwrap()

    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access for top-level keys."""
        return self._doc[key]

    def __setitem__(self, key: str, value: Any):
        """Dictionary-style set for top-level keys."""
        self._doc[key] = value
        if self._autosave:
            self.save()

    def __contains__(self, key: str) -> bool:
        """Check if a top-level key exists."""
        return key in self._doc

    def __str__(self) -> str:
        """Return the TOML document as a string."""
        return dumps(self._doc)

    def __repr__(self) -> str:
        return f"<TOMLConfig file='{self._file_path}' encoding='{self._encoding}'>"

    @contextlib.contextmanager
    def batch_update(self):
        """
        Context manager for batch updates.

        Disables autosave during the context and saves once when exiting.

        Example:
        with config.batch_update():
            config.set("key1", "value1")
            config.set("key2", "value2")
        """
        original_autosave = self.autosave
        self.autosave = False
        try:
            yield self
        finally:
            self.autosave = original_autosave
            self.save()