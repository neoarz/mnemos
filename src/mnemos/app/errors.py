from __future__ import annotations


class MnemosError(Exception):
    pass


class ConfigError(MnemosError):
    pass


class InferenceError(MnemosError):
    pass


class StorageError(MnemosError):
    pass
