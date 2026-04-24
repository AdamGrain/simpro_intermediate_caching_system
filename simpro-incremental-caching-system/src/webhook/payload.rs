use serde::{Serialize, Deserialize};
use super::variants::{Operation, Resource};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebhookPayload {
    #[serde(rename = "ID")]
    pub id: String,
    pub reference: WebhookReference,
    pub date_triggered: String,
}

impl WebhookPayload {
    pub fn resource(&self) -> Option<Resource> {
        self.id.split('.').find_map(|p| match p {
            "schedule" => Some(Resource::Schedule),
            "job" => Some(Resource::Job),
            "site" => Some(Resource::Site),
            _ => None,
        })
    }

    pub fn operation(&self) -> Option<Operation> {
        self.id.rsplit('.').next().and_then(|op| match op {
            "created" => Some(Operation::Created),
            "updated" => Some(Operation::Updated),
            "deleted" => Some(Operation::Deleted),
            _ => None,
        })
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebhookReference {
    #[serde(rename = "companyID")]
    pub company_id: Option<u64>,

    #[serde(rename = "costCenterID")]
    pub cost_center_id: Option<u64>,

    #[serde(rename = "jobID")]
    pub job_id: Option<u64>,

    #[serde(rename = "scheduleID")]
    pub schedule_id: Option<u64>,

    #[serde(rename = "sectionID")]
    pub section_id: Option<u64>,

    #[serde(rename = "siteID")]
    pub site_id: Option<u64>,
}

impl WebhookReference {
    pub fn id_for(
        &self,
        resource: &Resource,
    ) -> Option<u64> {
        match resource {
            Resource::Job => self.job_id,
            Resource::Site => self.site_id,
            Resource::Schedule => self.schedule_id,
            _ => None,
        }
    }
}