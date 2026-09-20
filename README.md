# YouTube Downloader AR — GitHub + Vercel

هذا مستودع جاهز لرفع موقع تحميل برنامج Windows على Vercel، مع GitHub Actions يبني برنامج Tkinter ومثبت Windows تلقائيًا على خادم Windows.

## ماذا يحدث تلقائيًا؟

عند رفع المشروع إلى فرع `main` أو `master`:

1. GitHub Actions يشغّل Windows Runner.
2. يثبت Python و`yt-dlp` وPyInstaller.
3. ينزّل FFmpeg ويضمّنه داخل التطبيق.
4. يبني `YouTubeDownloaderAR.exe`.
5. يبني `YouTubeDownloaderSetup.exe` باستخدام Inno Setup.
6. يرفع المثبّت كـ GitHub Release وArtifact.
7. ينسخ المثبّت إلى `downloads/YouTubeDownloaderSetup.exe`.
8. يعمل Commit تلقائيًا، فيعيد Vercel نشر الموقع ويصبح زر التحميل فعالًا.

## الخطوات المطلوبة مرة واحدة

### 1. إنشاء مستودع GitHub

أنشئ مستودعًا جديدًا، ويفضل أن يكون **Public** لأن الزوار سيحمّلون ملف التثبيت من رابط Vercel.

### 2. رفع الملفات

من داخل هذا المجلد نفّذ:

```bash
git init
git branch -M main
git add .
git commit -m "Initial YouTube Downloader website and Windows build"
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

استبدل `USERNAME/REPOSITORY` ببيانات مستودعك.

### 3. ربط Vercel

في Vercel اختر **Add New Project**، ثم اختر مستودع GitHub. اترك إعدادات Build فارغة لأن الموقع Static، واضغط **Deploy**.

بعد نجاح GitHub Actions ستتم إضافة الملف تلقائيًا إلى `downloads/`، وسيعيد Vercel النشر. إذا لم يتم النشر، افتح Vercel ثم اضغط **Redeploy** مرة واحدة.

## تشغيل البناء يدويًا

من GitHub افتح تبويب **Actions**، اختر **Build Windows installer**، ثم اضغط **Run workflow**.

## ملفات مهمة

- `index.html` و`styles.css`: صفحة الموقع.
- `desktop/app.py`: برنامج Tkinter.
- `desktop/YouTubeDownloaderAR.spec`: إعداد PyInstaller.
- `desktop/installer/YouTubeDownloaderSetup.iss`: إعداد Inno Setup.
- `.github/workflows/build-windows.yml`: البناء والنشر التلقائي.
- `downloads/`: الملف الذي يحمّله زائر الموقع بعد نجاح أول Build.

## ملاحظات مهمة

- لا يمكن تشغيل GitHub Actions من زر Vercel؛ البناء يتم داخل GitHub Actions.
- يجب إعطاء GitHub Actions صلاحية كتابة محتوى المستودع، وهي مضبوطة في workflow عبر `contents: write`.
- أول تشغيل قد يستغرق عدة دقائق.
- استخدم البرنامج فقط مع المحتوى الذي تملك حق تنزيله أو لديك إذن باستخدامه.
- GitHub قد يطلب التحقق من البريد أو الحساب قبل تشغيل بعض Workflows.
