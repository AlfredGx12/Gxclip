FROM python:3.9-slim

# تثبيت المتطلبات الأساسية
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# تثبيت Chrome و ChromeDriver متوافقين
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable=114.0.5735.198-1 && \
    rm -rf /var/lib/apt/lists/*

# تثبيت ChromeDriver متوافق مع إصدار Chrome
RUN wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

# إعداد بيئة العمل
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
