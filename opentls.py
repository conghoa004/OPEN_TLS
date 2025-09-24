import os, sys, datetime, ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

CERT_DIR = "certs"
os.makedirs(CERT_DIR, exist_ok=True)

# ==== Utility functions ====

def create_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

def save_key(key, filename):
    with open(filename, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

def save_cert(cert, filename):
    with open(filename, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

def build_subject(common_name, org="MyIoT", country="VN", state="Hanoi", locality="Hanoi"):
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

def load_ca():
    with open(f"{CERT_DIR}/ca.key", "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)
    with open(f"{CERT_DIR}/ca.crt", "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())
    return ca_key, ca_cert

# ==== Create CA cert ====

def create_ca():
    key = create_key()
    subject = build_subject("MyRootCA", org="MyIoT-CA")
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    save_key(key, f"{CERT_DIR}/ca.key")
    save_cert(cert, f"{CERT_DIR}/ca.crt")
    print("✅ CA created: certs/ca.crt , certs/ca.key")

# ==== Create Server cert ====

def create_server_cert():
    if not (os.path.exists(f"{CERT_DIR}/ca.key") and os.path.exists(f"{CERT_DIR}/ca.crt")):
        print("⚠️ CA not found. Run: python cert_tool.py ca")
        return

    ca_key, ca_cert = load_ca()
    key = create_key()
    subject = build_subject("emqx.local", org="MyIoT-Server")

    san = x509.SubjectAlternativeName([
        x509.DNSName("localhost"),
        x509.DNSName("emqx.local"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(san, critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    save_key(key, f"{CERT_DIR}/server.key")
    save_cert(cert, f"{CERT_DIR}/server.crt")
    print("✅ Server cert created: certs/server.crt , certs/server.key")

# ==== Create Client cert ====

def create_client_cert(client_name="mqtt-client"):
    if not (os.path.exists(f"{CERT_DIR}/ca.key") and os.path.exists(f"{CERT_DIR}/ca.crt")):
        print("⚠️ CA not found. Run: python cert_tool.py ca")
        return

    ca_key, ca_cert = load_ca()
    key = create_key()
    subject = build_subject(client_name, org="MyIoT-Client")

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False)
        .sign(ca_key, hashes.SHA256())
    )

    key_path = f"{CERT_DIR}/{client_name}.key"
    crt_path = f"{CERT_DIR}/{client_name}.crt"

    save_key(key, key_path)
    save_cert(cert, crt_path)
    print(f"✅ Client cert created: {crt_path} , {key_path}")

# ==== Main ====

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python opentls.py [ca|server|client <name>]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "ca":
        create_ca()
    elif cmd == "server":
        create_server_cert()
    elif cmd == "client":
        if len(sys.argv) < 3:
            print("Usage: python opentls.py client <client_name>")
            sys.exit(1)
        create_client_cert(sys.argv[2])
    else:
        print("Unknown command:", cmd)