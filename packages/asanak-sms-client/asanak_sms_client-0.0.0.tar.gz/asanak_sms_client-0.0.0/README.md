# 📦 Asanak SMS Client (Python)

یک کلاینت پایتونی برای ارسال پیامک از طریق API Asanak

## 🚀 نصب پکیج

### از PyPI:
```bash
pip install asanak-sms-client
```

### از GitHub:
```bash
pip install git+https://github.com/Asanak-Team/python-sms-client
```

## 📚 استفاده از کلاینت

```python
from asanak_sms_client import AsanakSMSClient

client = AsanakSMSClient("username", "password")

```

1- ارسال پیامک تکی یا چند مقصدی
```python

try:
    data = client.send_sms("9821X", "0912000000", "کد تست 1234")
    print(data)
except Exception as e:
    print(e)
```

2- ارسال پیامک نظیر به نظیر (P2P)
```python

try:
    data = client.send_p2p(["9821XX1", "9821XX2"], ["0912000000", "0912000001"], ["کد تست 1234", "کد تست 4567"], [True, False])
    print(data)
except Exception as e:
    print(e)
```

3-  ارسال پیامک خدماتی با قالب (OTP)
```python

try:
    data = client.send_template(1234, {"code": "1234"}, "0912000000", True)
    print(data)
except Exception as e:
    print(e)
```

4-  استعلام وضعیت پیامک
```python

try:
    data = client.msg_status(['12345678', '12345679'])
    print(data)
except Exception as e:
    print(e)
```

5-  مشاهده موجودی اعتبار پیامکی
```python

try:
    data = client.get_credit()
    print(data["credit"])
except Exception as e:
    print(e)
```

6-  مشاهده موجودی اعتبار پیامکی (ریال)
```python

try:
    data = client.get_rial_credit()
    print(data["credit"])
except Exception as e:
    print(e)
```

7-  دریافت لیست قالب‌های پیامک
```python

try:
    data = client.get_templates()
    print(data)
except Exception as e:
    print(e)
```

## 📝 پارامتر‌های ورودی

- `username`: نام کاربری از API Asanak
- `password`: رمز عبور از API Asanak
- `base_url`: آدرس سرور API Asanak (پیش‌فرض: `https://sms.asanak.ir`)

## 📝 پارامتر‌های خروجی
```json
{
    "meta": {
        "status": int,
        "message": string
    },
    "data": list
}
```