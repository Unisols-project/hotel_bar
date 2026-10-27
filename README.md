# Hotel Bar Billing

This project uses separate frontend and backend servers. The frontend is a static HTML, CSS, and JavaScript application; the backend is a Flask API connected to MySQL.

## Project structure

```
hotel_bar_mysql/
├── backend/             Flask API and MySQL database files (port 5000)
│   ├── app.py
│   ├── wsgi.py
│   ├── database.sql
│   ├── requirements.txt
│   └── .env.example
└── frontend/            Static application files (port 8000)
    ├── index.html       Dashboard
    ├── products.html
    ├── vendors.html
    ├── purchase.html
    ├── tables.html
    ├── table_order.html
    ├── bill_form.html
    ├── bills.html
    ├── bill_view.html
    ├── report.html
    └── static/
```

## Run the application

### 1. Start MySQL and the backend

```bash
cd backend
mysql -u root -p < database.sql
copy .env.example .env
pip install -r requirements.txt
python app.py
```

Update `DB_PASSWORD` and any other required settings in `backend/.env` before starting the backend. The API runs at `http://127.0.0.1:5000`.

### Existing database upgrade

If you already created the database before the invoice fields were added, run this command once before starting the backend:

```bash
mysql -u root -p hotel_bar_db < add_invoice_fields.sql
```

The invoice header uses `APP_NAME`, `HOTEL_PHONE`, `HOTEL_ADDRESS`, and `HOTEL_GSTIN` from `backend/.env`.

### 2. Start the frontend

Open a second terminal:

```bash
cd frontend
python serve.py
```

Open `http://127.0.0.1:8000` in your browser.

If the backend runs on another host or port, update `frontend/static/config.js` with its API address.

## Production

Run the Flask application through Gunicorn with multiple workers:

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Troubleshooting

| Problem | Resolution |
|---|---|
| Backend not reachable | Ensure the backend is running and the API address in `config.js` is correct. |
| MySQL access denied | Check the database username and `DB_PASSWORD` in `.env`. |
| CORS error | Set `FRONTEND_ORIGIN` in `backend/.env` to the exact frontend URL. |
