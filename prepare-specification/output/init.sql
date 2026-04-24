CREATE TABLE activities (
    id BIGINT NOT NULL,
    name TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE cost_centers (
    id BIGINT NOT NULL,
    name TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE customers (
    id BIGINT NOT NULL,
    company_name TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE employees (
    id BIGINT NOT NULL,
    name TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE job_statuses (
    id BIGINT NOT NULL,
    color TEXT,
    name TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE labor_rates (
    id BIGINT NOT NULL,
    name TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE leads (
    id BIGINT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE quotes (
    id BIGINT NOT NULL,
    name TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE sections (
    id BIGINT NOT NULL,
    name TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE sites (
    id BIGINT NOT NULL,
    address_address TEXT,
    address_city TEXT,
    address_country TEXT,
    address_postal_code TEXT,
    address_state TEXT,
    name TEXT,
    date_modified TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);

CREATE TABLE schedules (
    id BIGINT NOT NULL,
    _date TIMESTAMP WITH TIME ZONE,
    date_modified TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    reference TEXT,
    staff_id BIGINT REFERENCES employees (id),
    _type TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE jobs (
    id BIGINT NOT NULL,
    customer_id BIGINT REFERENCES customers (id),
    date_modified TIMESTAMP WITH TIME ZONE,
    description TEXT,
    name TEXT,
    site_id BIGINT REFERENCES sites (id),
    stage TEXT,
    status_id BIGINT REFERENCES job_statuses (id),
    _type TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE activity_schedules (
    activity_id BIGINT NOT NULL REFERENCES activities (id),
    schedule_id BIGINT NOT NULL REFERENCES schedules (id),
    PRIMARY KEY (activity_id, schedule_id)
);

CREATE TABLE schedule_blocks (
    id BIGSERIAL NOT NULL,
    schedule_id BIGINT NOT NULL REFERENCES schedules (id),
    end_time TEXT,
    hrs NUMERIC,
    iso8601_end_time TIMESTAMP WITH TIME ZONE,
    iso8601_start_time TIMESTAMP WITH TIME ZONE,
    schedule_rate JSONB,
    start_time TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE job_cost_centers (
    id BIGINT NOT NULL,
    section_id BIGINT REFERENCES sections (id),
    cost_center_id BIGINT REFERENCES cost_centers (id),
    date_modified TIMESTAMP WITH TIME ZONE,
    job_id BIGINT REFERENCES jobs (id),
    name TEXT,
    _href TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE job_schedules (
    schedule_id BIGINT NOT NULL REFERENCES schedules (id),
    job_id BIGINT NOT NULL REFERENCES jobs (id),
    PRIMARY KEY (schedule_id, job_id)
);