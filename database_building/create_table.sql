-- Table des données nettoyées (colonnes de data/silver.csv, même nom que la table SQLite de l'application)
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    experience_level VARCHAR(64),
    employment_type VARCHAR(64),
    job_title VARCHAR(255),
    employee_residence VARCHAR(64),
    remote_ratio VARCHAR(64),
    company_location VARCHAR(64),
    company_size VARCHAR(64),
    salary_in_usd INT
);
