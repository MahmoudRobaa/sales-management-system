# Deployment Guide | دليل التثبيت

## نظام إدارة المبيعات - Sales Management System

---

## المتطلبات | Prerequisites

### 1. Install Docker Desktop | تثبيت Docker Desktop

Download and install Docker Desktop from:
قم بتحميل وتثبيت Docker Desktop من:

**https://www.docker.com/products/docker-desktop/**

> [!IMPORTANT]
> During installation, enable **"Start Docker Desktop when you sign in"**
> أثناء التثبيت، فعّل خيار **"Start Docker Desktop when you sign in"**

---

## التثبيت | Installation

### Step 1: Extract the Project | استخراج المشروع

Extract the project folder to any location (e.g., `C:\SalesSystem`)
استخرج مجلد المشروع إلى أي مكان (مثلاً `C:\SalesSystem`)

### Step 2: Start the System | تشغيل النظام

**Double-click** on `start-sales-system.bat`
**انقر مرتين** على ملف `start-sales-system.bat`

The first time may take 5-10 minutes to download and build.
المرة الأولى قد تستغرق 5-10 دقائق للتحميل والبناء.

### Step 3: Access the Application | الوصول للتطبيق

Open your browser and go to:
افتح المتصفح واذهب إلى:

```
http://localhost:8888
```

---

## التشغيل التلقائي | Auto-Start on Boot

To make the system start automatically when Windows starts:
لجعل النظام يعمل تلقائياً عند تشغيل Windows:

1. **Press** `Win + R`
2. **Type** `shell:startup` and press Enter
3. **Copy** the `start-sales-system.bat` file shortcut to this folder
4. **Done!** The system will start automatically on boot

---

## الإيقاف | Stopping the System

To stop the system, open Command Prompt and run:
لإيقاف النظام، افتح موجه الأوامر وشغّل:

```cmd
cd C:\path\to\project
docker-compose -f docker-compose.prod.yml down
```

---

## حل المشاكل | Troubleshooting

### Problem: "Docker is not running"
**Solution:** Start Docker Desktop from the Start menu and wait until the Docker icon shows "Docker Desktop is running"

### المشكلة: "Docker غير مشغل"
**الحل:** شغّل Docker Desktop من قائمة Start وانتظر حتى تظهر أيقونة Docker بحالة "Docker Desktop is running"

---

### Problem: Port 8888 is already in use
**Solution:** Run this command to stop existing containers:
```cmd
docker-compose -f docker-compose.prod.yml down
```

---

### Problem: Application shows errors
**Solution:** Rebuild the containers:
```cmd
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build
```

> [!CAUTION]
> The `-v` flag will **delete all data**! Use only if you want to start fresh.
> استخدام `-v` سيحذف **جميع البيانات**! استخدمه فقط إذا أردت البدء من جديد.

---

## النسخ الاحتياطي | Backup

### Backup Database | نسخ احتياطي للقاعدة

```cmd
docker exec sales_db pg_dump -U salesadmin sales_management > backup.sql
```

### Restore Database | استعادة القاعدة

```cmd
docker exec -i sales_db psql -U salesadmin sales_management < backup.sql
```

---

## معلومات تقنية | Technical Info

| Component | Port | Container Name |
|-----------|------|----------------|
| Frontend  | 8888 | sales_frontend |
| Backend   | 8000 | sales_backend  |
| Database  | 5432 | sales_db       |

---

**Developed by Mazen | تم التطوير بواسطة مازن**
