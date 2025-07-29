import pytest
from obfuscator_ai import obfuscate, ObfuscatorAI


def test_obfuscate_basic():
    """Test basic obfuscation"""
    source = "x = 1 + 2"
    result = obfuscate(source)
    assert isinstance(result, str)


def test_obfuscator_class():
    """Test ObfuscatorAI class"""
    obf = ObfuscatorAI()
    assert hasattr(obf, 'obfuscate')
