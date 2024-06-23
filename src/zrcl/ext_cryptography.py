import datetime
import typing
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)
from cryptography.exceptions import InvalidSignature


def generate_keys():
    """
    Generates a pair of RSA keys - a private key and a corresponding public key.

    Returns:
        Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]: The generated private and public keys.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=1024, backend=default_backend()
    )
    public_key = private_key.public_key()

    return private_key, public_key


def serialize_public_key(public_key: typing.Union[rsa.RSAPublicKey, rsa.RSAPrivateKey]):
    """
    Serialize a public key into a PEM-encoded byte string.

    Args:
        public_key (typing.Union[rsa.RSAPublicKey, rsa.RSAPrivateKey]): The public key to serialize.

    Returns:
        bytes: The serialized public key in PEM format.

    Raises:
        None

    This function takes a public key as input and serializes it into a PEM-encoded byte string. If the input key is an instance of `rsa.RSAPrivateKey`, it is first converted to a public key using the `public_key()` method. The serialization is done using the `public_bytes()` method of the `rsa.RSAPublicKey` class, with the `encoding` parameter set to `serialization.Encoding.PEM` and the `format` parameter set to `serialization.PublicFormat.SubjectPublicKeyInfo`.

    Example usage:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())
        public_key = private_key.public_key()
        serialized_public_key = serialize_public_key(public_key)
        print(serialized_public_key)
    """
    if isinstance(public_key, rsa.RSAPrivateKey):
        public_key = public_key.public_key()

    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def serialize_private_key(
    private_key: rsa.RSAPrivateKey, encryptionPassword: bytes = b"Placeholder"
):
    """
    Serialize a private key into a PEM-encoded byte string.

    Args:
        private_key (rsa.RSAPrivateKey): The private key to serialize.
        encryptionPassword (bytes, optional): The password to use for encryption. Defaults to b"Placeholder".

    Returns:
        bytes: The serialized private key in PEM format.

    This function takes a private key as input and serializes it into a PEM-encoded byte string. The serialization is done using the `private_bytes()` method of the `rsa.RSAPrivateKey` class, with the `encoding` parameter set to `serialization.Encoding.PEM`, the `format` parameter set to `serialization.PrivateFormat.PKCS8`, and the `encryption_algorithm` parameter set to `serialization.BestAvailableEncryption(encryptionPassword)`.

    Example usage:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())
        serialized_private_key = serialize_private_key(private_key, b"my_password")
        print(serialized_private_key)
    """
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(encryptionPassword),
    )

    return private_bytes


def serialize_keys(
    private_key: rsa.RSAPrivateKey,
    public_key: rsa.RSAPublicKey = None,
    encryptionPassword: bytes = b"Placeholder",
):
    """
    Serialize a pair of RSA keys into PEM-encoded byte strings.

    Args:
        private_key (rsa.RSAPrivateKey): The private key to serialize.
        public_key (rsa.RSAPublicKey, optional): The public key to serialize. If not provided, it is derived from the private key.
        encryptionPassword (bytes, optional): The password to use for encryption. Defaults to b"Placeholder".

    Returns:
        Tuple[bytes, bytes]: The serialized private key and public key in PEM format.
    """
    if public_key is None:
        public_key = private_key.public_key()

    private_bytes = serialize_private_key(private_key, encryptionPassword)
    public_bytes = serialize_public_key(public_key)

    return private_bytes, public_bytes


def deserialize_public_key(public_bytes: bytes):
    """
    Deserialize a public key from a PEM-encoded byte string.

    Args:
        public_bytes (bytes): The PEM-encoded byte string representing the public key.

    Returns:
        rsa.RSAPublicKey: The deserialized public key.

    This function takes a PEM-encoded byte string as input and deserializes it into an `rsa.RSAPublicKey` object. It uses the `load_pem_public_key` function from the `cryptography` library to perform the deserialization. The function returns the deserialized public key.

    Example usage:
        public_key_bytes = b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyX6Klx9QY1t3+5Xnvj\n...\n-----END PUBLIC KEY-----\n"
        public_key = deserialize_public_key(public_key_bytes)
        print(public_key)
    """
    public_key = load_pem_public_key(
        public_bytes,
        backend=default_backend(),
    )

    return public_key


def deserialize_private_key(
    private_bytes: bytes, encryptionPassword: bytes = b"Placeholder"
):
    """
    Deserialize a private key from a PEM-encoded byte string with optional encryption password.

    Args:
        private_bytes (bytes): The PEM-encoded byte string representing the private key.
        encryptionPassword (bytes, optional): The password used for encryption. Defaults to b"Placeholder".

    Returns:
        The deserialized private key.
    """
    private_key = load_pem_private_key(
        private_bytes,
        password=encryptionPassword,
        backend=default_backend(),
    )

    return private_key


def deserialize_keys(
    private_bytes: bytes,
    public_bytes: bytes = None,
    encryptionPassword: bytes = b"Placeholder",
):
    """
    Deserialize a pair of RSA keys from PEM-encoded byte strings.

    Args:
        private_bytes (bytes): The PEM-encoded byte string representing the private key.
        public_bytes (bytes, optional): The PEM-encoded byte string representing the public key. Defaults to None.
        encryptionPassword (bytes, optional): The password used for encryption. Defaults to b"Placeholder".

    Returns:
        Tuple[rsa.RSAPrivateKey, Optional[rsa.RSAPublicKey]]: The deserialized private key and public key.

    This function takes PEM-encoded byte strings representing the private and optional public key, and deserializes them into `rsa.RSAPrivateKey` and `rsa.RSAPublicKey` objects respectively. If `public_bytes` is None, the function returns the deserialized private key and None for the public key. Otherwise, it deserializes the public key using the `deserialize_public_key` function and returns both the private and public keys.

    Example usage:
        private_key_bytes = b"-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCv13cQ\n...\n-----END PRIVATE KEY-----\n"
        public_key_bytes = b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyX6Klx9QY1t3+5Xnvj\n...\n-----END PUBLIC KEY-----\n"
        private_key, public_key = deserialize_keys(private_key_bytes, public_key_bytes)
        print(private_key)
        print(public_key)
    """
    if public_bytes is None:
        public_key = None
    else:
        public_key = deserialize_public_key(public_bytes)

    private_key = deserialize_private_key(private_bytes, encryptionPassword)

    return private_key, public_key


def sign_data(data: bytes, private_key: rsa.RSAPrivateKey):
    """
    Sign data using the given private key.

    Args:
        data (bytes): The data to be signed.
        private_key (rsa.RSAPrivateKey): The private key to use for signing.

    Returns:
        bytes: The signature of the data.
    """
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )

    return signature


def verify_signature(data: bytes, signature: bytes, public_key: rsa.RSAPublicKey):
    """
    Verify the signature of the given data using the given public key.

    Args:
        data (bytes): The data to be verified.
        signature (bytes): The signature of the data.
        public_key (rsa.RSAPublicKey): The public key to use for verification.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

        return True
    except InvalidSignature:
        return False


def sign_with_timestamp(
    data: bytes, timestamp: float = None, key: rsa.RSAPrivateKey = None
):
    """
    Sign data with a timestamp using the provided private key.

    Args:
        data (bytes): The data to be signed.
        timestamp (float, optional): The timestamp to be included in the signature. If not provided, current timestamp will be used.
        key (rsa.RSAPrivateKey, optional): The private key to sign the data with.

    Returns:
        bytes: The signature of the data.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now().timestamp()

    if key is None:
        raise ValueError("No private key provided.")

    concat = {"timestamp": timestamp, "data": data}
    data = str(concat).encode()

    return sign_data(data, key)


def verify_with_timestamp(
    data: bytes,
    signature: bytes,
    timestamp: float = None,
    key: rsa.RSAPublicKey = None,
):
    """
    Verify the signature of the given data using the given public key.

    Args:
        data (bytes): The data to be verified.
        signature (bytes): The signature of the data.
        public_key (rsa.RSAPublicKey): The public key to use for verification.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now().timestamp()

    if key is None:
        raise ValueError("No public key provided.")

    concat = {"timestamp": timestamp, "data": data}
    data = str(concat).encode()

    return verify_signature(data, signature, key)


def same_privatekey(k: rsa.RSAPrivateKey, dk: rsa.RSAPrivateKey):
    """
    Check if two private keys are the same.

    Args:
        k (rsa.RSAPrivateKey): The first private key.
        dk (rsa.RSAPrivateKey): The second private key.

    Returns:
        bool: True if the private keys are the same, False otherwise.
    """
    assert type(k) == type(dk)

    # Extract public components from both the original and deserialized keys
    original_public_numbers = k.public_key().public_numbers()
    deserialized_public_numbers = dk.public_key().public_numbers()

    # Compare the public components
    assert (
        original_public_numbers.n == deserialized_public_numbers.n
    ), "Modulus mismatch"
    assert (
        original_public_numbers.e == deserialized_public_numbers.e
    ), "Public exponent mismatch"

    # If the keys include private components, compare those too
    if isinstance(k, rsa.RSAPrivateKey) and isinstance(dk, rsa.RSAPrivateKey):
        assert (
            k.private_numbers().d == dk.private_numbers().d
        ), "Private exponent mismatch"
        assert k.private_numbers().p == dk.private_numbers().p, "Prime 1 mismatch"
        assert k.private_numbers().q == dk.private_numbers().q, "Prime 2 mismatch"
