use crate::api::types as record;
use diesel::prelude::*;
use diesel_derive_enum::DbEnum;

#[derive(Debug, Clone, Copy, PartialEq, Eq, DbEnum)]
#[ExistingTypePath = "crate::db::table::sql_types::ScheduleType"]
#[DbValueStyle = "snake_case"]
pub enum ScheduleType {
    Lead,
    Quote,
    Job,
    Activity,
}

impl From<record::ScheduleType> for ScheduleType  {
    fn from(t: record::ScheduleType) -> Self {
        match t {
            record::ScheduleType::Lead => ScheduleType::Lead,
            record::ScheduleType::Quote => ScheduleType::Quote,
            record::ScheduleType::Job => ScheduleType ::Job,
            record::ScheduleType::Activity => ScheduleType ::Activity,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, DbEnum)]
#[ExistingTypePath = "crate::db::table::sql_types::JobType"]
#[DbValueStyle = "PascalCase"]
pub enum JobType {
    Project,
    Service,
    Prepaid,
}

impl From<record::JobType> for JobType  {
    fn from(t: record::JobType) -> Self {
        match t {
            record::JobType::Project => JobType::Project,
            record::JobType::Service => JobType::Service,
            record::JobType::Prepaid => JobType ::Prepaid,
        }
    }
}