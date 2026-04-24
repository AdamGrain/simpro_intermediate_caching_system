use strum_macros::{EnumCount, EnumIter};

#[repr(u8)]
#[derive(EnumIter, EnumCount, Debug, Copy, Clone)]
pub enum Resource {
    Job = 0,
    Site = 1,
    Schedule = 2,
    Activity = 3,
    Employee = 4,
    CostCenter = 5,
    Quote = 6,
    Lead = 7
}

#[repr(u8)]
#[derive(EnumIter, EnumCount, Debug, Copy, Clone)]
pub enum Operation {
    Created = 0,
    Updated = 1,
    Deleted = 2,
}

