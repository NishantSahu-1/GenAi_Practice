# GenAi_Practice

## React Dynamic Website

This project now includes a React frontend in `frontend/` and a Python API backend at `api.py`.

### Run the backend API

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with MySQL credentials:
   ```text
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=your_user
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=your_database
   ```
3. Start the API server:
   ```bash
   uvicorn api:app --reload
   ```

### Populate sample data if the DB is empty

If the `students` table is empty, run:
```bash
python seed_students.py
```

### Run the React frontend

1. Change into the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the frontend:
   ```bash
   npm run dev
   ```

### Optional Streamlit frontend

If you prefer the existing Streamlit app, run:
```bash
streamlit run app.py
```

### What it does

- Accepts a natural language query about the `students` table
- Generates a MySQL query using the pipeline
- Executes the query against the configured database
- Presents generated SQL, query results, and an AI summary

### Notes

- The React frontend posts requests to `http://localhost:8000/query` by default.
- Set `VITE_API_URL` in `frontend/.env` if you need a custom API address.
