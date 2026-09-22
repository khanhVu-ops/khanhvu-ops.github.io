# KV Apps - iOS Landing Page & App Store URLs

Thư mục này chứa toàn bộ mã nguồn website tĩnh dùng cho việc:
1. **Duyệt ứng dụng trên App Store Connect:** Cung cấp link **Privacy Policy** và **Support**.
2. **Xác thực Google AdMob:** Chứa file **`app-ads.txt`** ở root domain để hiển thị quảng cáo không bị giới hạn.
3. **Giới thiệu ứng dụng:** Landing page hiện đại, hỗ trợ mobile, dark mode.

---

## 📁 Cấu trúc thư mục

```text
KVApps-Landing/
├── index.html        # Trang chủ giới thiệu app
├── privacy.html      # Chính sách bảo mật (Chuẩn Apple Review 5.1.1 & AdMob)
├── support.html      # Trang trung tâm hỗ trợ & FAQ
├── app-ads.txt       # File xác thực Google AdMob
├── .gitignore
└── README.md
```

---

## 🚀 Hướng dẫn triển khai lên GitHub Pages (5 phút)

### Bước 1: Tạo Repository trên GitHub
1. Vào [GitHub](https://github.com/new) tạo một repo mới (ví dụ đặt tên là `apps-landing` hoặc `kvapps-landing`).
2. Chọn chế độ **Public** (để dùng GitHub Pages miễn phí).

### Bước 2: Đẩy code lên GitHub
Mở Terminal và chạy lệnh:
```bash
cd /Users/khanhvu/personal/KVApps-Landing
git init
git add .
git commit -m "feat: initial landing page, privacy, support and app-ads.txt"
git branch -M main
git remote add origin https://github.com/khanhVu-ops/<TÊN_REPO_VỪA_TẠO>.git
git push -u origin main
```

### Bước 3: Kích hoạt GitHub Pages
1. Vào repo trên GitHub $\rightarrow$ chọn **Settings** $\rightarrow$ **Pages** (ở menu bên trái).
2. Tại mục **Build and deployment**:
   - **Source**: Chọn `Deploy from a branch`
   - **Branch**: Chọn `main` và thư mục `/ (root)`
   - Bấm **Save**.
3. Chờ khoảng 1–2 phút, website của bạn sẽ online tại địa chỉ:
   `https://<username>.github.io/<tên-repo>/`

---

## 🌐 Gắn Domain riêng (Tùy chọn)

Nếu bạn đã mua domain (ví dụ `kvapps.dev` hoặc `khanhvu.io`):
1. Tạo 1 file tên `CNAME` trong thư mục này, nội dung chỉ gồm tên domain:
   ```text
   kvapps.dev
   ```
2. Cấu hình DNS tại nhà cung cấp tên miền (Cloudflare / Namecheap / Porkbun):
   - **Bản ghi CNAME**: Host `www` $\rightarrow$ Target `<username>.github.io`
   - **Bản ghi A**: Host `@` $\rightarrow$ Trỏ về 4 IP của GitHub Pages:
     - `185.199.108.153`
     - `185.199.109.153`
     - `185.199.110.153`
     - `185.199.111.153`
3. Trong GitHub Pages Settings, tick chọn **Enforce HTTPS**.

---

## 📋 Điền link vào App Store Connect & Google AdMob

Sau khi web chạy (ví dụ domain là `https://yourdomain.com` hoặc `https://username.github.io/repo`):

| Nền tảng | Vị trí điền | URL cần điền |
|---|---|---|
| **App Store Connect** | **Privacy Policy URL** | `https://yourdomain.com/privacy.html` |
| **App Store Connect** | **Support URL** | `https://yourdomain.com/support.html` |
| **App Store Connect** | **Marketing URL** *(Tùy chọn)* | `https://yourdomain.com/` |
| **Google AdMob** | Tự động quét | AdMob sẽ đọc Marketing URL trên App Store và tự tìm tới `https://yourdomain.com/app-ads.txt` |
