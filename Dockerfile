FROM python:3.9-slim

# تثبيت الأدوات الأساسية ومكتبات دعم Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# تثبيت أحدث Google Chrome
RUN mkdir -p /etc/apt/keyrings && \
    curl -sSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# تثبيت ChromeDriver المتوافق تلقائيًا
RUN LATEST_VERSION=$(curl -sSL https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | grep -oP '"linux64":{"version":"\K[^"]+') && \
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${LATEST_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# إعداد مجلد العمل
WORKDIR /app

# نسخ الملفات
COPY requirements.txt .
COPY app.py .
COPY templates ./templates
COPY cookies.txt .

# إنشاء مجلد التحميل
RUN mkdir -p downloads

# تثبيت مكتبات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل التطبيق
CMD ["python", "app.py"]
