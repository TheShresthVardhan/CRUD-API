CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN DEFAULT FALSE,
    -- In a real app, tasks belong to users.
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_title ON tasks(title);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN DEFAULT FALSE
);

-- Seed data so it behaves like the old in-memory list
INSERT INTO tasks (title, done) VALUES 
    ('Setup Postgres', true),
    ('Connect FastAPI', false),
    ('Write Docker Compose', false);

    -- EXTRA: Add an index on the title column to speed up text searches
CREATE INDEX idx_tasks_title ON tasks(title);

