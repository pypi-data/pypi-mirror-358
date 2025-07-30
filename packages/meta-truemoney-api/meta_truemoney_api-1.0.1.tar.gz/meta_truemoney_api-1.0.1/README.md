# 🧧 meta-truemoney-api

โมดูล Python สำหรับเชื่อม API ซองอั่งเปา TrueMoney แบบไม่คิดค่าธรรมเนียม  
เหมาะสำหรับใช้งานร่วมกับ Discord Bot, Backend Web, และอื่น ๆ

## 🔧 ติดตั้ง
```bash
pip install meta-truemoney-api
```

## 🧠 วิธีใช้

```python
from meta_truemoney_api.client import MetaTrueMoneyAPI

api = MetaTrueMoneyAPI(api_key="YOUR_API_KEY", phone="0800000000")
result = api.redeem("https://gift.truemoney.com/campaign/?v=xxxxxx")

if result["status"]:
    print("เติมสำเร็จ:", result["credited"], "บาท")
else:
    print("ผิดพลาด:", result["error"])
```
