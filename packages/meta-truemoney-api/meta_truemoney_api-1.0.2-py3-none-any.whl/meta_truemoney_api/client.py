import requests
from decimal import Decimal, ROUND_HALF_UP

class MetaTrueMoneyAPI:
    def __init__(self, api_key: str, phone: str):
        self.api_key = api_key
        self.phone = phone
        self.endpoint = "https://api.xznp.store/api/wallet/topup"

    def redeem(self, voucher_url: str) -> dict:
        if not voucher_url.startswith("https://gift.truemoney.com/campaign/?v="):
            return {"status": False, "error": "ลิงก์ไม่ถูกต้อง"}

        payload = {
            "phone": self.phone,
            "vouch": voucher_url
        }
        headers = {
            "X-API-Key": self.api_key
        }

        try:
            res = requests.post(self.endpoint, json=payload, headers=headers, timeout=15)
            res.raise_for_status()
            data = res.json()

            if not data.get("status"):
                return {"status": False, "error": "ลิงก์ไม่ถูกต้องหรือถูกใช้ไปแล้ว"}

            amount = Decimal(str(data['message']['my_ticket']['amount_baht'])).quantize(Decimal("0.01"), ROUND_HALF_UP)

            return {
                "status": True,
                "amount": amount,
                "credited": amount,
                "raw": data
            }

        except Exception as e:
            return {"status": False, "error": str(e)}