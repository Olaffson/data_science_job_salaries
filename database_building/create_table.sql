CREATE TABLE IF NOT EXISTS salaries (
    id SERIAL PRIMARY KEY,
    work_year INT,
    experience_level VARCHAR(64),
    employment_type VARCHAR(64),
    job_title VARCHAR(255),
    salary INT,
    salary_currency VARCHAR(64),
    salary_in_usd INT,
    employee_residence VARCHAR(64),
    remote_ratio VARCHAR(64),
    company_location VARCHAR(64),
    company_size VARCHAR(64)
);
