import subprocess
import os
import argparse

# Ensure certs directory exists
CERT_DIR = "certs"
if not os.path.exists(CERT_DIR):
    os.makedirs(CERT_DIR)

# Function to run shell commands
def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

# Create CA (root CA)
def create_ca():
    subj_ca = "/C=VN/ST=VinhLong/L=VinhLong/O=Hoaze/OU=IOT/CN=EMQX-CA/emailAddress=conghoa247@gmail.com"
    key_path = os.path.join(CERT_DIR, "rootCA.key") 
    crt_path = os.path.join(CERT_DIR, "rootCA.crt") 
    print("Creating Root CA...")
    run(f"openssl genrsa -des3 -out {key_path} 2048")
    run(f"openssl req -x509 -new -nodes -key {key_path} -sha256 -days 3650 -out {crt_path} -subj \"{subj_ca}\"")
    print(f"Root CA created: {crt_path}, key: {key_path}")

# Create server certificate
def create_server():
    subj_server = "/C=VN/ST=VinhLong/L=VinhLong/O=Hoaze/OU=IOT/CN=localhost/emailAddress=conghoa247@gmail.com"
    print("Creating Server certificate...")
    run(f"openssl genrsa -out {CERT_DIR}/server.key 2048")
    run(f"openssl req -new -key {CERT_DIR}/server.key -out {CERT_DIR}/server.csr -subj \"{subj_server}\"")
    run(f"openssl x509 -req -in {CERT_DIR}/server.csr -CA {CERT_DIR}/rootCA.crt -CAkey {CERT_DIR}/rootCA.key -CAcreateserial -out {CERT_DIR}/server.crt -days 365 -sha256")
    print(f"Server certificate created: {CERT_DIR}/server.crt, key: {CERT_DIR}/server.key")

# Create client certificates
def create_client(names):
    for name in names:
        subj_client = f"/C=VN/ST=VinhLong/L=VinhLong/O=Hoaze/OU=IOT/CN={name}/emailAddress=conghoa247@gmail.com"
        print(f"Creating Client certificate for {name}...")
        run(f"openssl genrsa -out {CERT_DIR}/{name}.key 2048")
        run(f"openssl req -new -key {CERT_DIR}/{name}.key -out {CERT_DIR}/{name}.csr -subj \"{subj_client}\"")
        run(f"openssl x509 -req -in {CERT_DIR}/{name}.csr -CA {CERT_DIR}/rootCA.crt -CAkey {CERT_DIR}/rootCA.key -CAcreateserial -out {CERT_DIR}/{name}.crt -days 365 -sha256")
        print(f"Client certificate created: {CERT_DIR}/{name}.crt, key: {CERT_DIR}/{name}.key")

# Parse command line arguments
parser = argparse.ArgumentParser(description="Tool to create CA/Server/Client certificates for EMQX")
parser.add_argument("-ca", action="store_true", help="Create CA certificate")
parser.add_argument("-server", action="store_true", help="Create Server certificate")
parser.add_argument("-client", nargs="+", help="Create Client certificate(s), provide client name(s) after -client")
args = parser.parse_args()

if __name__ == "__main__":
    if args.ca:
        create_ca()
    if args.server:
        create_server()
    if args.client:
        create_client(args.client)
    print(f"Certificates and keys have been created in folder: {CERT_DIR}")
