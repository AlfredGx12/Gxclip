FROM python:3.9-slim

# تثبيت المتطلبات الأساسية
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# تثبيت إصدار محدد من Google Chrome يتوافق مع ChromeDriver
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable=114.0.5735.198-1 && \
    rm -rf /var/lib/apt/lists/*

# تثبيت ChromeDriver 114
RUN wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

# إنشاء مجلد التطبيق
WORKDIR /app

# نسخ الملفات المطلوبة
COPY requirements.txt .
COPY app.py .
COPY templates ./templates
COPY cookies.txt .

# إنشاء مجلد التحميلات
RUN mkdir -p downloads

# تثبيت متطلبات Python
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل التطبيق
CMD ["python", "app.py"]
