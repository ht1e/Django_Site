# Hướng dẫn sử dụng License Verification API

## Tổng quan
API công khai để xác thực license key cho ứng dụng GTA License Server.

## Base URL
```
http://your-domain.com/api/
```

## Authentication
API sử dụng API Key để xác thực. Bạn có thể gửi API key theo 2 cách:
1. **Header**: `X-API-Key: your-secret-api-key-2024`
2. **Query Parameter**: `?api_key=your-secret-api-key-2024`

**Lưu ý**: API key mặc định là `your-secret-api-key-2024`. Hãy thay đổi trong `license_server/settings.py` trước khi deploy production.

## Endpoints

### 1. Xác thực License
**URL**: `/api/verify-license/`  
**Method**: `GET` hoặc `POST`  
**Authentication**: Required (API Key)

#### Parameters:
- `license_key` (required): Mã license cần xác thực
- `hardware_id` (optional): ID phần cứng của thiết bị
- `api_key` (required): API key (có thể gửi qua header `X-API-Key`)

#### Ví dụ sử dụng:

**GET Request:**
```bash
curl "http://localhost:8000/api/verify-license/?license_key=ABC123&hardware_id=HW001&api_key=your-secret-api-key-2024"
```

**POST Request với Header:**
```bash
curl -X POST http://localhost:8000/api/verify-license/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-2024" \
  -d '{"license_key": "ABC123", "hardware_id": "HW001"}'
```

**POST Request với JSON:**
```bash
curl -X POST "http://localhost:8000/api/verify-license/?api_key=your-secret-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"license_key": "ABC123", "hardware_id": "HW001"}'
```

#### Response khi thành công:
```json
{
  "success": true,
  "valid": true,
  "message": "License hợp lệ",
  "license_key": "ABC123",
  "status": "active",
  "expiration_date": "2024-12-31",
  "hardware_id": "HW001",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Response khi license không hợp lệ:
```json
{
  "success": false,
  "valid": false,
  "error": "License not found",
  "message": "License không tồn tại",
  "license_key": "INVALID123"
}
```

#### Response khi license hết hạn:
```json
{
  "success": false,
  "valid": false,
  "error": "License expired",
  "message": "License đã hết hạn",
  "license_key": "ABC123",
  "expiration_date": "2023-12-31",
  "current_date": "2024-01-01"
}
```

#### Response khi API key không hợp lệ:
```json
{
  "success": false,
  "error": "Invalid API key",
  "message": "API key không hợp lệ"
}
```

### 2. Thông tin API
**URL**: `/api/info/`  
**Method**: `GET`  
**Authentication**: Không cần

#### Ví dụ:
```bash
curl http://localhost:8000/api/info/
```

#### Response:
```json
{
  "api_name": "License Verification API",
  "version": "1.0.0",
  "endpoints": {
    "verify_license": "/api/verify-license/",
    "api_info": "/api/info/"
  },
  "authentication": {
    "method": "API Key",
    "header": "X-API-Key",
    "query_param": "api_key"
  }
}
```

## Ví dụ sử dụng với JavaScript (Fetch API)

```javascript
// Sử dụng GET request
async function verifyLicense(licenseKey, hardwareId) {
  const apiKey = 'your-secret-api-key-2024';
  const url = `http://localhost:8000/api/verify-license/?license_key=${licenseKey}&hardware_id=${hardwareId}&api_key=${apiKey}`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Sử dụng POST request với header
async function verifyLicensePost(licenseKey, hardwareId) {
  const apiKey = 'your-secret-api-key-2024';
  const url = 'http://localhost:8000/api/verify-license/';
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey
      },
      body: JSON.stringify({
        license_key: licenseKey,
        hardware_id: hardwareId
      })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## Ví dụ sử dụng với Python (requests)

```python
import requests

def verify_license(license_key, hardware_id=None):
    api_key = 'your-secret-api-key-2024'
    url = 'http://localhost:8000/api/verify-license/'
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    data = {
        'license_key': license_key,
        'hardware_id': hardware_id
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Sử dụng
result = verify_license('ABC123', 'HW001')
print(result)
```

## Cấu hình Production

1. **Thay đổi API Key**: Sửa `API_KEY` trong `license_server/settings.py` hoặc sử dụng biến môi trường
2. **Cấu hình ALLOWED_HOSTS**: Giới hạn các domain được phép truy cập
3. **Tắt DEBUG**: Đặt `DEBUG = False` trong production
4. **Cấu hình CORS**: Chỉ cho phép các domain cần thiết trong `CORS_ALLOWED_ORIGINS`

## Lưu ý bảo mật

- Luôn sử dụng HTTPS trong production
- Không commit API key vào Git
- Sử dụng biến môi trường cho API key
- Giới hạn rate limiting để tránh abuse
- Log các request để theo dõi


