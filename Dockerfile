# ใช้ Python เวอร์ชันที่เป็นทางการ
FROM python:3.13-slim

# ติดตั้ง FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# ตั้งค่าพื้นที่ทำงาน
WORKDIR /app

# คัดลอกไฟล์ requirements เข้าไป
COPY requirements.txt .

# ติดตั้งไลบรารีต่างๆ
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดบอททั้งหมดเข้าไป
COPY . .

# สั่งรันบอท
CMD ["python", "main.py"]
