# Ora News Backend

Ora News adalah aplikasi berita digital. Repository ini berisi backend API yang dibangun dengan FastAPI dan PostgreSQL untuk mendukung fitur-fitur utama aplikasi berita.

## Fitur Utama
- [x] Autentikasi & otorisasi JWT
- [x] Manajemen user
- [ ] Manajemen berita/artikel
- [ ] Kategori berita
- [x] Pagination API
- [x] Dokumentasi otomatis (Swagger/OpenAPI)

## Requirements
- Python 3.12 atau lebih baru
- PostgreSQL
- [Poetry](https://python-poetry.org/) (opsional, untuk manajemen dependensi)

## Instalasi
1. Clone repository:
    ```sh
    git clone https://github.com/ahmaadn/ora-news-backend.git
    cd ora-news-backend
    ```
2. Buat virtual environment:
    ```sh
    python -m venv venv
    ```
3. Aktifkan virtual environment:
    - Windows:
        ```sh
        venv\Scripts\activate
        ```
    - macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
4. Install dependensi:
    ```sh
    pip install -r requirements.txt
    # or
    uv install
    ```

## Konfigurasi Environment
1. Buat file `.env` di root project. Contoh isi:
    ```env
    DATABASE_URL=postgresql://user:password@localhost:5432/ora_news
    SECRET_KEY=your_secret_key
    MAIL_USERNAME=your_email
    MAIL_PASSWORD=your_email_password
    MAIL_FROM=your_email
    MAIL_PORT=587
    MAIL_SERVER=smtp.gmail.com
    ````

## Migrasi Database
Jalankan migrasi database menggunakan Alembic:
```sh
alembic upgrade head
```

## Menjalankan Server
1. Jalankan server FastAPI:
    ```sh
    uvicorn app.main:app --reload
    # or
    fastapi dev
    ```
2. Dokumentasi API tersedia di: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Menjalankan Test
Jalankan seluruh test dengan pytest:
```sh
pytest
```

## Troubleshooting
Jika mengalami kendala, silakan buat issue di repository ini.

## License

This project is licensed under the MIT License.
