use crate::api::types as record;
use super::table;
use anyhow::{Result, anyhow};
use chrono::{DateTime, FixedOffset, Utc};
use diesel::prelude::{AsChangeset, Insertable};
use diesel::{PgConnection, QueryResult};
use crate::db::table::*;
use crate::db::enums::{ScheduleType, JobType};

/// ```sql
/// INSERT INTO table_name (col1, col2, col3)
///    VALUES (val1, val2, val3)
///    ON CONFLICT (unique_column)
///    DO UPDATE
///    SET col2 = EXCLUDED.col2,   
///        col3 = EXCLUDED.col3;
/// ```
#[macro_export]
macro_rules! update {
    ($($col:ident),+ $(,)?) => {
        (
            $( $col.eq(diesel::upsert::excluded($col)) ),+
        )
    };
}
pub use update;

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = schedules)]
pub struct Schedule {
    pub id: i64,
    pub date_modified: DateTime<Utc>,
    pub notes: String,
    pub staff_id: i64,
    pub schedule_type: ScheduleType,
    // Derived from 'Reference'
    pub job_id: Option<i64>,
    pub cost_center_id: Option<i64>,
    pub activity_id: Option<i64>,
    pub quote_id: Option<i64>,
    pub lead_id: Option<i64>,
}

impl TryFrom<record::Schedule> for Schedule {
    type Error = anyhow::Error;
    fn try_from(record: record::Schedule) -> anyhow::Result<Self> {
        fn parse_splittable(s: &str, delimiter: &char) -> (Option<i64>, Option<i64>) {
            s.split_once(*delimiter)
                .map(|(a, b)| (a.parse().ok(), b.parse().ok()))
                .unwrap_or((None, None))
        }
        // We need the corresponding records
        // to map metadata to our events
        let mut activity_id: Option<i64> = None;
        let mut lead_id: Option<i64> = None;
        let mut job_id: Option<i64> = None;
        let mut cost_center_id: Option<i64> = None;
        let mut quote_id: Option<i64> = None;
        match record.type_ {
            record::ScheduleType::Activity => {
                activity_id = Some(record.reference.parse::<i64>()?);
                // Retrieve corresponding 'Activity' from simPRO
                // Add to the database table 'activities'
                // The row MUST EXIST before a foreign key references it
            }
            record::ScheduleType::Lead => {
                lead_id = Some(record.reference.parse::<i64>()?);
            }
            record::ScheduleType::Job => {
                (job_id, cost_center_id) = parse_splittable(&record.reference, &'-');
            }
            record::ScheduleType::Quote => {
                (quote_id, cost_center_id) = parse_splittable(&record.reference, &'-');
            }
        }
        Ok(Self {
            id: record.id.parse::<i64>()?,
            date_modified: DateTime::parse_from_rfc3339(&record.date_modified)?.with_timezone(&Utc),
            notes: record.notes,
            staff_id: record.staff.id.parse::<i64>()?,
            schedule_type: record.type_.into(),
            activity_id, job_id, cost_center_id, quote_id, lead_id // -- OPTIONAL FOREIGN KEYS
        })
    }
}


#[derive(Insertable, AsChangeset)]
#[diesel(table_name = activities)]
pub struct Activity {
    pub id: i64,
    pub name: String,
}

impl TryFrom<record::Activity> for Activity {
    type Error = anyhow::Error;

    fn try_from(record: record::Activity) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            name: record.name,
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = cost_centers)]
pub struct CostCenter {
    pub id: i64,
    pub name: String,
}

impl TryFrom<record::CostCenter> for CostCenter {
    type Error = anyhow::Error;

    fn try_from(record: record::CostCenter) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            name: record.name,
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = employees)]
pub struct Employee {
    pub id: i64,
    pub name: String,
}

impl TryFrom<record::Employee> for Employee {
    type Error = anyhow::Error;

    fn try_from(record: record::Employee) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            name: record.name,
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = leads)]
pub struct Lead {
    pub id: i64,
    pub name: String,
}

impl TryFrom<record::Lead> for Lead {
    type Error = anyhow::Error;

    fn try_from(record: record::Lead) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            name: record.name,
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = quotes)]
pub struct Quote {
    pub id: i64,
    pub name: String,
}

impl TryFrom<record::Quote> for Quote {
    type Error = anyhow::Error;

    fn try_from(record: record::Quote) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            name: record.name,
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = schedule_rates)]
pub struct ScheduleRate {
    pub id: i64,
    pub name: String,
}

impl TryFrom<record::ScheduleRate> for ScheduleRate {
    type Error = anyhow::Error;

    fn try_from(record: record::ScheduleRate) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            name: record.name,
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = job_statuses)]
pub struct JobStatus {
    pub id: i64,
    pub name: String,
    pub color: String,
}

impl TryFrom<record::JobStatus> for JobStatus {
    type Error = anyhow::Error;

    fn try_from(record: record::JobStatus) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            name: record.name,
            color: record.color,
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = sites)]
pub struct Site {
    pub id: i64,
    pub address_address: String,
    pub address_city: String,
    pub address_country: String,
    pub address_postal_code: String,
    pub date_modified: DateTime<Utc>,
}

impl TryFrom<record::Site> for Site {
    type Error = anyhow::Error;

    fn try_from(record: record::Site) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            address_address: record.address.address,
            address_city: record.address.city,
            address_country: record.address.country,
            address_postal_code: record.address.postal_code,
            date_modified: DateTime::parse_from_rfc3339(&record.date_modified)?
                .with_timezone(&Utc),
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = jobs)]
pub struct Job {
    pub id: i64,
    pub customer_company_name: String,
    pub date_modified: DateTime<Utc>,
    pub description: String,
    pub name: String,
    pub site_id: i64,
    pub stage: String,
    pub status_id: i64,
    pub job_type: JobType,
}

impl TryFrom<record::Job> for Job {
    type Error = anyhow::Error;

    fn try_from(record: record::Job) -> Result<Self> {
        Ok(Self {
            id: record.id.parse::<i64>()?,
            customer_company_name: record.customer.company_name,
            date_modified: DateTime::parse_from_rfc3339(&record.date_modified)?
                .with_timezone(&Utc),
            description: record.description.unwrap_or_default(),
            name: record.name,
            site_id: record.site.id.parse::<i64>()?,
            stage: record.stage,
            status_id: record.status.id.parse::<i64>()?,
            job_type: record.type_.into(),
        })
    }
}

#[derive(Insertable, AsChangeset)]
#[diesel(table_name = schedule_blocks)]
pub struct ScheduleBlock {
    pub schedule_id: i64,
    pub iso8601_start_time: DateTime<Utc>,
    pub iso8601_end_time: DateTime<Utc>,
    pub schedule_rate: i64,
}

impl TryFrom<(record::ScheduleBlock, i64)> for ScheduleBlock {
    type Error = anyhow::Error;

    fn try_from((record, schedule_id): (record::ScheduleBlock, i64)) -> Result<Self> {
        Ok(Self {
            schedule_id,
            iso8601_start_time: DateTime::parse_from_rfc3339(&record.iso8601_start_time)?.with_timezone(&Utc),
            iso8601_end_time: DateTime::parse_from_rfc3339(&record.iso8601_end_time)?.with_timezone(&Utc),
            schedule_rate: record.schedule_rate.id.parse::<i64>()?,
        })
    }
}