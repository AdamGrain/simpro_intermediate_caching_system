// @generated automatically by Diesel CLI.

pub mod sql_types {
    #[derive(diesel::sql_types::SqlType)]
    #[diesel(postgres_type(name = "job_type"))]
    pub struct JobType;

    #[derive(diesel::sql_types::SqlType)]
    #[diesel(postgres_type(name = "schedule_type"))]
    pub struct ScheduleType;
}

diesel::table! {
    activities (id) {
        id -> Int8,
        name -> Text,
    }
}

diesel::table! {
    cost_centers (id) {
        id -> Int8,
        name -> Text,
    }
}

diesel::table! {
    employees (id) {
        id -> Int8,
        name -> Text,
    }
}

diesel::table! {
    job_statuses (id) {
        id -> Int8,
        color -> Text,
        name -> Text,
    }
}

diesel::table! {
    use diesel::sql_types::*;
    use super::sql_types::JobType;

    jobs (id) {
        id -> Int8,
        customer_company_name -> Text,
        date_modified -> Timestamptz,
        description -> Text,
        name -> Text,
        site_id -> Int8,
        stage -> Text,
        status_id -> Int8,
        job_type -> JobType,
    }
}

diesel::table! {
    leads (id) {
        id -> Int8,
        name -> Text,
    }
}

diesel::table! {
    quotes (id) {
        id -> Int8,
        name -> Text,
    }
}

diesel::table! {
    schedule_blocks (id) {
        id -> Int8,
        schedule_id -> Int8,
        iso8601_end_time -> Timestamptz,
        iso8601_start_time -> Timestamptz,
        schedule_rate -> Int8,
    }
}

diesel::table! {
    schedule_rates (id) {
        id -> Int8,
        name -> Text,
    }
}

diesel::table! {
    use diesel::sql_types::*;
    use super::sql_types::ScheduleType;

    schedules (id) {
        id -> Int8,
        date_modified -> Timestamptz,
        staff_id -> Int8,
        schedule_type -> ScheduleType,
        notes -> Nullable<Text>,
        job_id -> Nullable<Int8>,
        cost_center_id -> Nullable<Int8>,
        activity_id -> Nullable<Int8>,
        quote_id -> Nullable<Int8>,
        lead_id -> Nullable<Int8>,
    }
}

diesel::table! {
    sites (id) {
        id -> Int8,
        address_address -> Nullable<Text>,
        address_city -> Nullable<Text>,
        address_country -> Nullable<Text>,
        address_postal_code -> Text,
        date_modified -> Nullable<Timestamptz>,
    }
}

diesel::joinable!(jobs -> job_statuses (status_id));
diesel::joinable!(jobs -> sites (site_id));
diesel::joinable!(schedule_blocks -> schedule_rates (schedule_rate));
diesel::joinable!(schedule_blocks -> schedules (schedule_id));
diesel::joinable!(schedules -> activities (activity_id));
diesel::joinable!(schedules -> cost_centers (cost_center_id));
diesel::joinable!(schedules -> employees (staff_id));
diesel::joinable!(schedules -> jobs (job_id));
diesel::joinable!(schedules -> leads (lead_id));
diesel::joinable!(schedules -> quotes (quote_id));

diesel::allow_tables_to_appear_in_same_query!(
    activities,
    cost_centers,
    employees,
    job_statuses,
    jobs,
    leads,
    quotes,
    schedule_blocks,
    schedule_rates,
    schedules,
    sites,
);
