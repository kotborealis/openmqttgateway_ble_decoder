"""Helpers for bleparser"""


def to_mac(addr: bytes) -> str:
    """Return formatted MAC address"""
    return ":".join(f"{i:02X}" for i in addr)


def to_unformatted_mac(addr: bytes) -> str:
    """Return unformatted MAC address"""
    return "".join(f"{i:02X}" for i in addr[:])
