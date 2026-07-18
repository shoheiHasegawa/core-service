CREATE TABLE activity_logs (
    task_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    area_id VARCHAR(255) NOT NULL,
    estimated_minutes INT NOT NULL,
    actual_minutes INT NOT NULL,
    worked_date DATE NOT NULL,
    is_completed BOOLEAN NOT NULL,
    UNIQUE (task_id, worked_date)
);
