from vaultseal.crypto import encrypt, decrypt

def test_encrypt_decrypt_roundtrip():
    message = "testing123"
    password = "secrettest"
    blob = encrypt(message, password)
    result = decrypt(blob, password)
    assert result == message
