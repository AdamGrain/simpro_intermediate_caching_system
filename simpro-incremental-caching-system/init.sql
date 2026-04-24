-- derived from Schedules
CREATE TABLE employees (
    id BIGINT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE sites (
    id BIGINT NOT NULL,
    address_address TEXT,
    address_city TEXT,
    address_country TEXT,
    address_postal_code TEXT NOT NULL,
    date_modified TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);

CREATE TABLE activities (
    id BIGINT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

-- These will need to be retrieved in bulk
-- To avoid slowing down simPRO service
CREATE TABLE quotes (
    id BIGINT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE leads (
    id BIGINT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

-- Cost Centers apply to 'Job' and 'Quote' Schedules
-- The second ID in the '-' delimited Reference
CREATE TABLE cost_centers (
    id BIGINT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE job_statuses (
    id BIGINT NOT NULL,
    color TEXT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TYPE job_type AS ENUM (
    'Project',
    'Service', 
    'Prepaid'
);

CREATE TABLE jobs (
    id BIGINT NOT NULL,
    customer_company_name TEXT NOT NULL,
    date_modified TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT NOT NULL,
    name TEXT NOT NULL,
    site_id BIGINT NOT NULL REFERENCES sites (id),
    stage TEXT NOT NULL,
    status_id BIGINT NOT NULL REFERENCES job_statuses (id),
    job_type job_type NOT NULL,
    PRIMARY KEY (id)
);

CREATE TYPE schedule_type AS ENUM (
    'lead',
    'quote',
    'job',
    'activity'
);

CREATE TABLE schedule_rates (
    id BIGINT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE schedules (
    id BIGINT NOT NULL,
    date_modified TIMESTAMP WITH TIME ZONE NOT NULL,
    staff_id BIGINT NOT NULL REFERENCES employees(id), -- required
    schedule_type schedule_type NOT NULL, -- required enum
    notes TEXT, -- optional
    --reference
    job_id BIGINT REFERENCES jobs (id), -- optional
    cost_center_id BIGINT REFERENCES cost_centers (id),
    activity_id BIGINT REFERENCES activities (id), -- optional
    quote_id BIGINT REFERENCES quotes (id), -- optional
    lead_id BIGINT REFERENCES leads (id), -- optional
    PRIMARY KEY (id)
);

CREATE TABLE schedule_blocks (
    id BIGSERIAL NOT NULL,
    schedule_id BIGINT NOT NULL REFERENCES schedules (id),
    iso8601_end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    iso8601_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    schedule_rate BIGINT NOT NULL REFERENCES schedule_rates (id),
    PRIMARY KEY (id)
);
