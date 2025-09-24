# 🔐 OpenTLS – Công cụ tạo chứng chỉ cho MQTT/EMQX

`opentls.py` là một script Python giúp bạn tự tạo **CA (Certificate Authority)**, **server certificate** và **client certificate** để sử dụng trong môi trường bảo mật TLS/SSL, ví dụ với **EMQX MQTT Broker**.

## 📂 Cấu trúc thư mục

Sau khi chạy script, các chứng chỉ sẽ được lưu trong thư mục `certs/`:

```
certs/
 ├── ca.crt        # Root CA certificate
 ├── ca.key        # Root CA private key
 ├── server.crt    # Server certificate (signed by CA)
 ├── server.key    # Server private key
 ├── client1.crt   # Client certificate (signed by CA)
 ├── client1.key   # Client private key
```

## ⚙️ Cách sử dụng

### 1. Tạo CA (Root Certificate Authority)

```bash
python opentls.py ca
```

Sinh ra:
- `certs/ca.crt`
- `certs/ca.key`

### 2. Tạo chứng chỉ Server

```bash
python opentls.py server
```

Sinh ra:
- `certs/server.crt`
- `certs/server.key`

📌 SAN (Subject Alternative Name) đã được cấu hình sẵn:
- `localhost`
- `emqx.local`
- `127.0.0.1`

### 3. Tạo chứng chỉ Client

```bash
python opentls.py client <client_name>
```

Ví dụ:

```bash
python opentls.py client mqtt-client1
```

Sinh ra:
- `certs/mqtt-client1.crt`
- `certs/mqtt-client1.key`

### 4. Sử dụng với EMQX / MQTT Broker

Trong file cấu hình EMQX (hoặc broker MQTT khác), chỉ định:

```ini
listener.ssl.external.keyfile = /path/to/certs/server.key
listener.ssl.external.certfile = /path/to/certs/server.crt
listener.ssl.external.cacertfile = /path/to/certs/ca.crt
```

Ở client (ví dụ Python `paho-mqtt`):

```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.tls_set(
    ca_certs="certs/ca.crt",
    certfile="certs/mqtt-client1.crt",
    keyfile="certs/mqtt-client1.key"
)
client.connect("emqx.local", 8883)
client.loop_start()
```

## 📌 Yêu cầu

- Python 3.8+
- Thư viện [cryptography](https://cryptography.io/)

Cài đặt bằng:

```bash
pip install cryptography
```

## 📖 Các lệnh hỗ trợ

```bash
python opentls.py ca              # Tạo Root CA
python opentls.py server          # Tạo server cert
python opentls.py client <name>   # Tạo client cert với tên tùy chọn
```

---

✅ Với OpenTLS, bạn có thể nhanh chóng tạo hệ thống chứng chỉ bảo mật TLS/SSL cho MQTT broker & client.
