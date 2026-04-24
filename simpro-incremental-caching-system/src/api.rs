#[allow(unused_imports)]
pub use progenitor_client::{ByteStream, ClientInfo, Error, ResponseValue};
#[allow(unused_imports)]
use progenitor_client::{encode_path, ClientHooks, OperationInfo, RequestBuilderExt};
/// Types used as operation parameters and responses.
#[allow(clippy::all)]
pub mod types {
    /// Error types.
    pub mod error {
        /// Error from a `TryFrom` or `FromStr` implementation.
        pub struct ConversionError(::std::borrow::Cow<'static, str>);
        impl ::std::error::Error for ConversionError {}
        impl ::std::fmt::Display for ConversionError {
            fn fmt(
                &self,
                f: &mut ::std::fmt::Formatter<'_>,
            ) -> Result<(), ::std::fmt::Error> {
                ::std::fmt::Display::fmt(&self.0, f)
            }
        }
        impl ::std::fmt::Debug for ConversionError {
            fn fmt(
                &self,
                f: &mut ::std::fmt::Formatter<'_>,
            ) -> Result<(), ::std::fmt::Error> {
                ::std::fmt::Debug::fmt(&self.0, f)
            }
        }
        impl From<&'static str> for ConversionError {
            fn from(value: &'static str) -> Self {
                Self(value.into())
            }
        }
        impl From<String> for ConversionError {
            fn from(value: String) -> Self {
                Self(value.into())
            }
        }
    }
    ///`Activity`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Activity {
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl Activity {
        pub fn builder() -> builder::Activity {
            Default::default()
        }
    }
    ///`Address`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "Address",
    ///    "City",
    ///    "Country",
    ///    "PostalCode"
    ///  ],
    ///  "properties": {
    ///    "Address": {
    ///      "type": "string"
    ///    },
    ///    "City": {
    ///      "type": "string"
    ///    },
    ///    "Country": {
    ///      "type": "string"
    ///    },
    ///    "PostalCode": {
    ///      "type": "string"
    ///    },
    ///    "State": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Address {
        #[serde(rename = "Address")]
        pub address: ::std::string::String,
        #[serde(rename = "City")]
        pub city: ::std::string::String,
        #[serde(rename = "Country")]
        pub country: ::std::string::String,
        #[serde(rename = "PostalCode")]
        pub postal_code: ::std::string::String,
        #[serde(
            rename = "State",
            default,
            skip_serializing_if = "::std::option::Option::is_none"
        )]
        pub state: ::std::option::Option<::std::string::String>,
    }
    impl Address {
        pub fn builder() -> builder::Address {
            Default::default()
        }
    }
    ///`CostCenter`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct CostCenter {
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl CostCenter {
        pub fn builder() -> builder::CostCenter {
            Default::default()
        }
    }
    ///`Customer`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "CompanyName",
    ///    "ID"
    ///  ],
    ///  "properties": {
    ///    "CompanyName": {
    ///      "type": "string"
    ///    },
    ///    "ID": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Customer {
        #[serde(rename = "CompanyName")]
        pub company_name: ::std::string::String,
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
    }
    impl Customer {
        pub fn builder() -> builder::Customer {
            Default::default()
        }
    }
    ///`Employee`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    },
    ///    "Position": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Employee {
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
        #[serde(
            rename = "Position",
            default,
            skip_serializing_if = "::std::option::Option::is_none"
        )]
        pub position: ::std::option::Option<::std::string::String>,
    }
    impl Employee {
        pub fn builder() -> builder::Employee {
            Default::default()
        }
    }
    ///`Job`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "Customer",
    ///    "DateModified",
    ///    "ID",
    ///    "Name",
    ///    "Reference",
    ///    "Site",
    ///    "Stage",
    ///    "Status",
    ///    "Type"
    ///  ],
    ///  "properties": {
    ///    "Customer": {
    ///      "$ref": "#/components/schemas/Customer"
    ///    },
    ///    "DateModified": {
    ///      "type": "string"
    ///    },
    ///    "Description": {
    ///      "type": "string"
    ///    },
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    },
    ///    "Site": {
    ///      "$ref": "#/components/schemas/JobSite"
    ///    },
    ///    "Stage": {
    ///      "type": "string"
    ///    },
    ///    "Status": {
    ///      "$ref": "#/components/schemas/JobStatus"
    ///    },
    ///    "Type": {
    ///      "type": "string",
    ///      "enum": [
    ///        "Project",
    ///        "Service",
    ///        "Prepaid"
    ///      ]
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Job {
        #[serde(rename = "Customer")]
        pub customer: Customer,
        #[serde(rename = "DateModified")]
        pub date_modified: ::std::string::String,
        #[serde(
            rename = "Description",
            default,
            skip_serializing_if = "::std::option::Option::is_none"
        )]
        pub description: ::std::option::Option<::std::string::String>,
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
        #[serde(rename = "Reference")]
        pub reference: ::serde_json::Value,
        #[serde(rename = "Site")]
        pub site: JobSite,
        #[serde(rename = "Stage")]
        pub stage: ::std::string::String,
        #[serde(rename = "Status")]
        pub status: JobStatus,
        #[serde(rename = "Type")]
        pub type_: JobType,
    }
    impl Job {
        pub fn builder() -> builder::Job {
            Default::default()
        }
    }
    ///`JobSite`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct JobSite {
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl JobSite {
        pub fn builder() -> builder::JobSite {
            Default::default()
        }
    }
    ///`JobStatus`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "Color",
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "Color": {
    ///      "type": "string"
    ///    },
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct JobStatus {
        #[serde(rename = "Color")]
        pub color: ::std::string::String,
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl JobStatus {
        pub fn builder() -> builder::JobStatus {
            Default::default()
        }
    }
    ///`JobType`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "string",
    ///  "enum": [
    ///    "Project",
    ///    "Service",
    ///    "Prepaid"
    ///  ]
    ///}
    /// ```
    /// </details>
    #[derive(
        ::serde::Deserialize,
        ::serde::Serialize,
        Clone,
        Copy,
        Debug,
        Eq,
        Hash,
        Ord,
        PartialEq,
        PartialOrd
    )]
    pub enum JobType {
        Project,
        Service,
        Prepaid,
    }
    impl ::std::fmt::Display for JobType {
        fn fmt(&self, f: &mut ::std::fmt::Formatter<'_>) -> ::std::fmt::Result {
            match *self {
                Self::Project => f.write_str("Project"),
                Self::Service => f.write_str("Service"),
                Self::Prepaid => f.write_str("Prepaid"),
            }
        }
    }
    impl ::std::str::FromStr for JobType {
        type Err = self::error::ConversionError;
        fn from_str(
            value: &str,
        ) -> ::std::result::Result<Self, self::error::ConversionError> {
            match value {
                "Project" => Ok(Self::Project),
                "Service" => Ok(Self::Service),
                "Prepaid" => Ok(Self::Prepaid),
                _ => Err("invalid value".into()),
            }
        }
    }
    impl ::std::convert::TryFrom<&str> for JobType {
        type Error = self::error::ConversionError;
        fn try_from(
            value: &str,
        ) -> ::std::result::Result<Self, self::error::ConversionError> {
            value.parse()
        }
    }
    impl ::std::convert::TryFrom<&::std::string::String> for JobType {
        type Error = self::error::ConversionError;
        fn try_from(
            value: &::std::string::String,
        ) -> ::std::result::Result<Self, self::error::ConversionError> {
            value.parse()
        }
    }
    impl ::std::convert::TryFrom<::std::string::String> for JobType {
        type Error = self::error::ConversionError;
        fn try_from(
            value: ::std::string::String,
        ) -> ::std::result::Result<Self, self::error::ConversionError> {
            value.parse()
        }
    }
    ///`Lead`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Lead {
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl Lead {
        pub fn builder() -> builder::Lead {
            Default::default()
        }
    }
    ///`Quote`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Quote {
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl Quote {
        pub fn builder() -> builder::Quote {
            Default::default()
        }
    }
    ///`Schedule`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "Blocks",
    ///    "Date",
    ///    "DateModified",
    ///    "ID",
    ///    "Name",
    ///    "Notes",
    ///    "Reference",
    ///    "Staff",
    ///    "Type"
    ///  ],
    ///  "properties": {
    ///    "Blocks": {
    ///      "type": "array",
    ///      "items": {
    ///        "$ref": "#/components/schemas/ScheduleBlock"
    ///      }
    ///    },
    ///    "Date": {
    ///      "type": "string"
    ///    },
    ///    "DateModified": {
    ///      "type": "string"
    ///    },
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Notes": {
    ///      "type": "string"
    ///    },
    ///    "Reference": {
    ///      "type": "string"
    ///    },
    ///    "Staff": {
    ///      "$ref": "#/components/schemas/Staff"
    ///    },
    ///    "Type": {
    ///      "type": "string",
    ///      "enum": [
    ///        "lead",
    ///        "quote",
    ///        "job",
    ///        "activity"
    ///      ]
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Schedule {
        #[serde(rename = "Blocks")]
        pub blocks: ::std::vec::Vec<ScheduleBlock>,
        #[serde(rename = "Date")]
        pub date: ::std::string::String,
        #[serde(rename = "DateModified")]
        pub date_modified: ::std::string::String,
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::serde_json::Value,
        #[serde(rename = "Notes")]
        pub notes: ::std::string::String,
        #[serde(rename = "Reference")]
        pub reference: ::std::string::String,
        #[serde(rename = "Staff")]
        pub staff: Staff,
        #[serde(rename = "Type")]
        pub type_: ScheduleType,
    }
    impl Schedule {
        pub fn builder() -> builder::Schedule {
            Default::default()
        }
    }
    ///`ScheduleBlock`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ISO8601EndTime",
    ///    "ISO8601StartTime",
    ///    "ScheduleRate"
    ///  ],
    ///  "properties": {
    ///    "EndTime": {
    ///      "type": "string"
    ///    },
    ///    "Hrs": {
    ///      "type": "number"
    ///    },
    ///    "ISO8601EndTime": {
    ///      "type": "string"
    ///    },
    ///    "ISO8601StartTime": {
    ///      "type": "string"
    ///    },
    ///    "ScheduleRate": {
    ///      "$ref": "#/components/schemas/ScheduleRate"
    ///    },
    ///    "StartTime": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct ScheduleBlock {
        #[serde(
            rename = "EndTime",
            default,
            skip_serializing_if = "::std::option::Option::is_none"
        )]
        pub end_time: ::std::option::Option<::std::string::String>,
        #[serde(
            rename = "Hrs",
            default,
            skip_serializing_if = "::std::option::Option::is_none"
        )]
        pub hrs: ::std::option::Option<f64>,
        #[serde(rename = "ISO8601EndTime")]
        pub iso8601_end_time: ::std::string::String,
        #[serde(rename = "ISO8601StartTime")]
        pub iso8601_start_time: ::std::string::String,
        #[serde(rename = "ScheduleRate")]
        pub schedule_rate: ScheduleRate,
        #[serde(
            rename = "StartTime",
            default,
            skip_serializing_if = "::std::option::Option::is_none"
        )]
        pub start_time: ::std::option::Option<::std::string::String>,
    }
    impl ScheduleBlock {
        pub fn builder() -> builder::ScheduleBlock {
            Default::default()
        }
    }
    ///`ScheduleRate`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct ScheduleRate {
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl ScheduleRate {
        pub fn builder() -> builder::ScheduleRate {
            Default::default()
        }
    }
    ///`ScheduleType`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "string",
    ///  "enum": [
    ///    "lead",
    ///    "quote",
    ///    "job",
    ///    "activity"
    ///  ]
    ///}
    /// ```
    /// </details>
    #[derive(
        ::serde::Deserialize,
        ::serde::Serialize,
        Clone,
        Copy,
        Debug,
        Eq,
        Hash,
        Ord,
        PartialEq,
        PartialOrd
    )]
    pub enum ScheduleType {
        #[serde(rename = "lead")]
        Lead,
        #[serde(rename = "quote")]
        Quote,
        #[serde(rename = "job")]
        Job,
        #[serde(rename = "activity")]
        Activity,
    }
    impl ::std::fmt::Display for ScheduleType {
        fn fmt(&self, f: &mut ::std::fmt::Formatter<'_>) -> ::std::fmt::Result {
            match *self {
                Self::Lead => f.write_str("lead"),
                Self::Quote => f.write_str("quote"),
                Self::Job => f.write_str("job"),
                Self::Activity => f.write_str("activity"),
            }
        }
    }
    impl ::std::str::FromStr for ScheduleType {
        type Err = self::error::ConversionError;
        fn from_str(
            value: &str,
        ) -> ::std::result::Result<Self, self::error::ConversionError> {
            match value {
                "lead" => Ok(Self::Lead),
                "quote" => Ok(Self::Quote),
                "job" => Ok(Self::Job),
                "activity" => Ok(Self::Activity),
                _ => Err("invalid value".into()),
            }
        }
    }
    impl ::std::convert::TryFrom<&str> for ScheduleType {
        type Error = self::error::ConversionError;
        fn try_from(
            value: &str,
        ) -> ::std::result::Result<Self, self::error::ConversionError> {
            value.parse()
        }
    }
    impl ::std::convert::TryFrom<&::std::string::String> for ScheduleType {
        type Error = self::error::ConversionError;
        fn try_from(
            value: &::std::string::String,
        ) -> ::std::result::Result<Self, self::error::ConversionError> {
            value.parse()
        }
    }
    impl ::std::convert::TryFrom<::std::string::String> for ScheduleType {
        type Error = self::error::ConversionError;
        fn try_from(
            value: ::std::string::String,
        ) -> ::std::result::Result<Self, self::error::ConversionError> {
            value.parse()
        }
    }
    ///`Section`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Section {
        #[serde(
            rename = "ID",
            default,
            skip_serializing_if = "::std::option::Option::is_none"
        )]
        pub id: ::std::option::Option<::std::string::String>,
        #[serde(
            rename = "Name",
            default,
            skip_serializing_if = "::std::option::Option::is_none"
        )]
        pub name: ::std::option::Option<::std::string::String>,
    }
    impl ::std::default::Default for Section {
        fn default() -> Self {
            Self {
                id: Default::default(),
                name: Default::default(),
            }
        }
    }
    impl Section {
        pub fn builder() -> builder::Section {
            Default::default()
        }
    }
    ///`Site`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "Address",
    ///    "DateModified",
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "Address": {
    ///      "$ref": "#/components/schemas/Address"
    ///    },
    ///    "DateModified": {
    ///      "type": "string"
    ///    },
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Site {
        #[serde(rename = "Address")]
        pub address: Address,
        #[serde(rename = "DateModified")]
        pub date_modified: ::std::string::String,
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl Site {
        pub fn builder() -> builder::Site {
            Default::default()
        }
    }
    ///`Staff`
    ///
    /// <details><summary>JSON schema</summary>
    ///
    /// ```json
    ///{
    ///  "type": "object",
    ///  "required": [
    ///    "ID",
    ///    "Name"
    ///  ],
    ///  "properties": {
    ///    "ID": {
    ///      "type": "string"
    ///    },
    ///    "Name": {
    ///      "type": "string"
    ///    }
    ///  }
    ///}
    /// ```
    /// </details>
    #[derive(::serde::Deserialize, ::serde::Serialize, Clone, Debug)]
    pub struct Staff {
        #[serde(rename = "ID")]
        pub id: ::std::string::String,
        #[serde(rename = "Name")]
        pub name: ::std::string::String,
    }
    impl Staff {
        pub fn builder() -> builder::Staff {
            Default::default()
        }
    }
    /// Types for composing complex structures.
    pub mod builder {
        #[derive(Clone, Debug)]
        pub struct Activity {
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for Activity {
            fn default() -> Self {
                Self {
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl Activity {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Activity> for super::Activity {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Activity,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::Activity> for Activity {
            fn from(value: super::Activity) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Address {
            address: ::std::result::Result<::std::string::String, ::std::string::String>,
            city: ::std::result::Result<::std::string::String, ::std::string::String>,
            country: ::std::result::Result<::std::string::String, ::std::string::String>,
            postal_code: ::std::result::Result<
                ::std::string::String,
                ::std::string::String,
            >,
            state: ::std::result::Result<
                ::std::option::Option<::std::string::String>,
                ::std::string::String,
            >,
        }
        impl ::std::default::Default for Address {
            fn default() -> Self {
                Self {
                    address: Err("no value supplied for address".to_string()),
                    city: Err("no value supplied for city".to_string()),
                    country: Err("no value supplied for country".to_string()),
                    postal_code: Err("no value supplied for postal_code".to_string()),
                    state: Ok(Default::default()),
                }
            }
        }
        impl Address {
            pub fn address<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.address = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for address: {e}")
                    });
                self
            }
            pub fn city<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.city = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for city: {e}")
                    });
                self
            }
            pub fn country<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.country = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for country: {e}")
                    });
                self
            }
            pub fn postal_code<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.postal_code = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for postal_code: {e}")
                    });
                self
            }
            pub fn state<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::option::Option<::std::string::String>>,
                T::Error: ::std::fmt::Display,
            {
                self.state = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for state: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Address> for super::Address {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Address,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    address: value.address?,
                    city: value.city?,
                    country: value.country?,
                    postal_code: value.postal_code?,
                    state: value.state?,
                })
            }
        }
        impl ::std::convert::From<super::Address> for Address {
            fn from(value: super::Address) -> Self {
                Self {
                    address: Ok(value.address),
                    city: Ok(value.city),
                    country: Ok(value.country),
                    postal_code: Ok(value.postal_code),
                    state: Ok(value.state),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct CostCenter {
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for CostCenter {
            fn default() -> Self {
                Self {
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl CostCenter {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<CostCenter> for super::CostCenter {
            type Error = super::error::ConversionError;
            fn try_from(
                value: CostCenter,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::CostCenter> for CostCenter {
            fn from(value: super::CostCenter) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Customer {
            company_name: ::std::result::Result<
                ::std::string::String,
                ::std::string::String,
            >,
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for Customer {
            fn default() -> Self {
                Self {
                    company_name: Err("no value supplied for company_name".to_string()),
                    id: Err("no value supplied for id".to_string()),
                }
            }
        }
        impl Customer {
            pub fn company_name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.company_name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for company_name: {e}")
                    });
                self
            }
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
        }
        impl ::std::convert::TryFrom<Customer> for super::Customer {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Customer,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    company_name: value.company_name?,
                    id: value.id?,
                })
            }
        }
        impl ::std::convert::From<super::Customer> for Customer {
            fn from(value: super::Customer) -> Self {
                Self {
                    company_name: Ok(value.company_name),
                    id: Ok(value.id),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Employee {
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
            position: ::std::result::Result<
                ::std::option::Option<::std::string::String>,
                ::std::string::String,
            >,
        }
        impl ::std::default::Default for Employee {
            fn default() -> Self {
                Self {
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                    position: Ok(Default::default()),
                }
            }
        }
        impl Employee {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
            pub fn position<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::option::Option<::std::string::String>>,
                T::Error: ::std::fmt::Display,
            {
                self.position = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for position: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Employee> for super::Employee {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Employee,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                    position: value.position?,
                })
            }
        }
        impl ::std::convert::From<super::Employee> for Employee {
            fn from(value: super::Employee) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                    position: Ok(value.position),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Job {
            customer: ::std::result::Result<super::Customer, ::std::string::String>,
            date_modified: ::std::result::Result<
                ::std::string::String,
                ::std::string::String,
            >,
            description: ::std::result::Result<
                ::std::option::Option<::std::string::String>,
                ::std::string::String,
            >,
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
            reference: ::std::result::Result<::serde_json::Value, ::std::string::String>,
            site: ::std::result::Result<super::JobSite, ::std::string::String>,
            stage: ::std::result::Result<::std::string::String, ::std::string::String>,
            status: ::std::result::Result<super::JobStatus, ::std::string::String>,
            type_: ::std::result::Result<super::JobType, ::std::string::String>,
        }
        impl ::std::default::Default for Job {
            fn default() -> Self {
                Self {
                    customer: Err("no value supplied for customer".to_string()),
                    date_modified: Err(
                        "no value supplied for date_modified".to_string(),
                    ),
                    description: Ok(Default::default()),
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                    reference: Err("no value supplied for reference".to_string()),
                    site: Err("no value supplied for site".to_string()),
                    stage: Err("no value supplied for stage".to_string()),
                    status: Err("no value supplied for status".to_string()),
                    type_: Err("no value supplied for type_".to_string()),
                }
            }
        }
        impl Job {
            pub fn customer<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<super::Customer>,
                T::Error: ::std::fmt::Display,
            {
                self.customer = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for customer: {e}")
                    });
                self
            }
            pub fn date_modified<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.date_modified = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for date_modified: {e}")
                    });
                self
            }
            pub fn description<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::option::Option<::std::string::String>>,
                T::Error: ::std::fmt::Display,
            {
                self.description = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for description: {e}")
                    });
                self
            }
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
            pub fn reference<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::serde_json::Value>,
                T::Error: ::std::fmt::Display,
            {
                self.reference = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for reference: {e}")
                    });
                self
            }
            pub fn site<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<super::JobSite>,
                T::Error: ::std::fmt::Display,
            {
                self.site = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for site: {e}")
                    });
                self
            }
            pub fn stage<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.stage = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for stage: {e}")
                    });
                self
            }
            pub fn status<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<super::JobStatus>,
                T::Error: ::std::fmt::Display,
            {
                self.status = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for status: {e}")
                    });
                self
            }
            pub fn type_<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<super::JobType>,
                T::Error: ::std::fmt::Display,
            {
                self.type_ = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for type_: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Job> for super::Job {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Job,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    customer: value.customer?,
                    date_modified: value.date_modified?,
                    description: value.description?,
                    id: value.id?,
                    name: value.name?,
                    reference: value.reference?,
                    site: value.site?,
                    stage: value.stage?,
                    status: value.status?,
                    type_: value.type_?,
                })
            }
        }
        impl ::std::convert::From<super::Job> for Job {
            fn from(value: super::Job) -> Self {
                Self {
                    customer: Ok(value.customer),
                    date_modified: Ok(value.date_modified),
                    description: Ok(value.description),
                    id: Ok(value.id),
                    name: Ok(value.name),
                    reference: Ok(value.reference),
                    site: Ok(value.site),
                    stage: Ok(value.stage),
                    status: Ok(value.status),
                    type_: Ok(value.type_),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct JobSite {
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for JobSite {
            fn default() -> Self {
                Self {
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl JobSite {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<JobSite> for super::JobSite {
            type Error = super::error::ConversionError;
            fn try_from(
                value: JobSite,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::JobSite> for JobSite {
            fn from(value: super::JobSite) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct JobStatus {
            color: ::std::result::Result<::std::string::String, ::std::string::String>,
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for JobStatus {
            fn default() -> Self {
                Self {
                    color: Err("no value supplied for color".to_string()),
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl JobStatus {
            pub fn color<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.color = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for color: {e}")
                    });
                self
            }
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<JobStatus> for super::JobStatus {
            type Error = super::error::ConversionError;
            fn try_from(
                value: JobStatus,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    color: value.color?,
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::JobStatus> for JobStatus {
            fn from(value: super::JobStatus) -> Self {
                Self {
                    color: Ok(value.color),
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Lead {
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for Lead {
            fn default() -> Self {
                Self {
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl Lead {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Lead> for super::Lead {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Lead,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::Lead> for Lead {
            fn from(value: super::Lead) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Quote {
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for Quote {
            fn default() -> Self {
                Self {
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl Quote {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Quote> for super::Quote {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Quote,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::Quote> for Quote {
            fn from(value: super::Quote) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Schedule {
            blocks: ::std::result::Result<
                ::std::vec::Vec<super::ScheduleBlock>,
                ::std::string::String,
            >,
            date: ::std::result::Result<::std::string::String, ::std::string::String>,
            date_modified: ::std::result::Result<
                ::std::string::String,
                ::std::string::String,
            >,
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::serde_json::Value, ::std::string::String>,
            notes: ::std::result::Result<::std::string::String, ::std::string::String>,
            reference: ::std::result::Result<
                ::std::string::String,
                ::std::string::String,
            >,
            staff: ::std::result::Result<super::Staff, ::std::string::String>,
            type_: ::std::result::Result<super::ScheduleType, ::std::string::String>,
        }
        impl ::std::default::Default for Schedule {
            fn default() -> Self {
                Self {
                    blocks: Err("no value supplied for blocks".to_string()),
                    date: Err("no value supplied for date".to_string()),
                    date_modified: Err(
                        "no value supplied for date_modified".to_string(),
                    ),
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                    notes: Err("no value supplied for notes".to_string()),
                    reference: Err("no value supplied for reference".to_string()),
                    staff: Err("no value supplied for staff".to_string()),
                    type_: Err("no value supplied for type_".to_string()),
                }
            }
        }
        impl Schedule {
            pub fn blocks<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::vec::Vec<super::ScheduleBlock>>,
                T::Error: ::std::fmt::Display,
            {
                self.blocks = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for blocks: {e}")
                    });
                self
            }
            pub fn date<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.date = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for date: {e}")
                    });
                self
            }
            pub fn date_modified<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.date_modified = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for date_modified: {e}")
                    });
                self
            }
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::serde_json::Value>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
            pub fn notes<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.notes = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for notes: {e}")
                    });
                self
            }
            pub fn reference<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.reference = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for reference: {e}")
                    });
                self
            }
            pub fn staff<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<super::Staff>,
                T::Error: ::std::fmt::Display,
            {
                self.staff = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for staff: {e}")
                    });
                self
            }
            pub fn type_<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<super::ScheduleType>,
                T::Error: ::std::fmt::Display,
            {
                self.type_ = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for type_: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Schedule> for super::Schedule {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Schedule,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    blocks: value.blocks?,
                    date: value.date?,
                    date_modified: value.date_modified?,
                    id: value.id?,
                    name: value.name?,
                    notes: value.notes?,
                    reference: value.reference?,
                    staff: value.staff?,
                    type_: value.type_?,
                })
            }
        }
        impl ::std::convert::From<super::Schedule> for Schedule {
            fn from(value: super::Schedule) -> Self {
                Self {
                    blocks: Ok(value.blocks),
                    date: Ok(value.date),
                    date_modified: Ok(value.date_modified),
                    id: Ok(value.id),
                    name: Ok(value.name),
                    notes: Ok(value.notes),
                    reference: Ok(value.reference),
                    staff: Ok(value.staff),
                    type_: Ok(value.type_),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct ScheduleBlock {
            end_time: ::std::result::Result<
                ::std::option::Option<::std::string::String>,
                ::std::string::String,
            >,
            hrs: ::std::result::Result<
                ::std::option::Option<f64>,
                ::std::string::String,
            >,
            iso8601_end_time: ::std::result::Result<
                ::std::string::String,
                ::std::string::String,
            >,
            iso8601_start_time: ::std::result::Result<
                ::std::string::String,
                ::std::string::String,
            >,
            schedule_rate: ::std::result::Result<
                super::ScheduleRate,
                ::std::string::String,
            >,
            start_time: ::std::result::Result<
                ::std::option::Option<::std::string::String>,
                ::std::string::String,
            >,
        }
        impl ::std::default::Default for ScheduleBlock {
            fn default() -> Self {
                Self {
                    end_time: Ok(Default::default()),
                    hrs: Ok(Default::default()),
                    iso8601_end_time: Err(
                        "no value supplied for iso8601_end_time".to_string(),
                    ),
                    iso8601_start_time: Err(
                        "no value supplied for iso8601_start_time".to_string(),
                    ),
                    schedule_rate: Err(
                        "no value supplied for schedule_rate".to_string(),
                    ),
                    start_time: Ok(Default::default()),
                }
            }
        }
        impl ScheduleBlock {
            pub fn end_time<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::option::Option<::std::string::String>>,
                T::Error: ::std::fmt::Display,
            {
                self.end_time = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for end_time: {e}")
                    });
                self
            }
            pub fn hrs<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::option::Option<f64>>,
                T::Error: ::std::fmt::Display,
            {
                self.hrs = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for hrs: {e}")
                    });
                self
            }
            pub fn iso8601_end_time<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.iso8601_end_time = value
                    .try_into()
                    .map_err(|e| {
                        format!(
                            "error converting supplied value for iso8601_end_time: {e}"
                        )
                    });
                self
            }
            pub fn iso8601_start_time<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.iso8601_start_time = value
                    .try_into()
                    .map_err(|e| {
                        format!(
                            "error converting supplied value for iso8601_start_time: {e}"
                        )
                    });
                self
            }
            pub fn schedule_rate<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<super::ScheduleRate>,
                T::Error: ::std::fmt::Display,
            {
                self.schedule_rate = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for schedule_rate: {e}")
                    });
                self
            }
            pub fn start_time<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::option::Option<::std::string::String>>,
                T::Error: ::std::fmt::Display,
            {
                self.start_time = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for start_time: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<ScheduleBlock> for super::ScheduleBlock {
            type Error = super::error::ConversionError;
            fn try_from(
                value: ScheduleBlock,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    end_time: value.end_time?,
                    hrs: value.hrs?,
                    iso8601_end_time: value.iso8601_end_time?,
                    iso8601_start_time: value.iso8601_start_time?,
                    schedule_rate: value.schedule_rate?,
                    start_time: value.start_time?,
                })
            }
        }
        impl ::std::convert::From<super::ScheduleBlock> for ScheduleBlock {
            fn from(value: super::ScheduleBlock) -> Self {
                Self {
                    end_time: Ok(value.end_time),
                    hrs: Ok(value.hrs),
                    iso8601_end_time: Ok(value.iso8601_end_time),
                    iso8601_start_time: Ok(value.iso8601_start_time),
                    schedule_rate: Ok(value.schedule_rate),
                    start_time: Ok(value.start_time),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct ScheduleRate {
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for ScheduleRate {
            fn default() -> Self {
                Self {
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl ScheduleRate {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<ScheduleRate> for super::ScheduleRate {
            type Error = super::error::ConversionError;
            fn try_from(
                value: ScheduleRate,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::ScheduleRate> for ScheduleRate {
            fn from(value: super::ScheduleRate) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Section {
            id: ::std::result::Result<
                ::std::option::Option<::std::string::String>,
                ::std::string::String,
            >,
            name: ::std::result::Result<
                ::std::option::Option<::std::string::String>,
                ::std::string::String,
            >,
        }
        impl ::std::default::Default for Section {
            fn default() -> Self {
                Self {
                    id: Ok(Default::default()),
                    name: Ok(Default::default()),
                }
            }
        }
        impl Section {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::option::Option<::std::string::String>>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::option::Option<::std::string::String>>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Section> for super::Section {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Section,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::Section> for Section {
            fn from(value: super::Section) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Site {
            address: ::std::result::Result<super::Address, ::std::string::String>,
            date_modified: ::std::result::Result<
                ::std::string::String,
                ::std::string::String,
            >,
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for Site {
            fn default() -> Self {
                Self {
                    address: Err("no value supplied for address".to_string()),
                    date_modified: Err(
                        "no value supplied for date_modified".to_string(),
                    ),
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl Site {
            pub fn address<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<super::Address>,
                T::Error: ::std::fmt::Display,
            {
                self.address = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for address: {e}")
                    });
                self
            }
            pub fn date_modified<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.date_modified = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for date_modified: {e}")
                    });
                self
            }
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Site> for super::Site {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Site,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    address: value.address?,
                    date_modified: value.date_modified?,
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::Site> for Site {
            fn from(value: super::Site) -> Self {
                Self {
                    address: Ok(value.address),
                    date_modified: Ok(value.date_modified),
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
        #[derive(Clone, Debug)]
        pub struct Staff {
            id: ::std::result::Result<::std::string::String, ::std::string::String>,
            name: ::std::result::Result<::std::string::String, ::std::string::String>,
        }
        impl ::std::default::Default for Staff {
            fn default() -> Self {
                Self {
                    id: Err("no value supplied for id".to_string()),
                    name: Err("no value supplied for name".to_string()),
                }
            }
        }
        impl Staff {
            pub fn id<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.id = value
                    .try_into()
                    .map_err(|e| format!("error converting supplied value for id: {e}"));
                self
            }
            pub fn name<T>(mut self, value: T) -> Self
            where
                T: ::std::convert::TryInto<::std::string::String>,
                T::Error: ::std::fmt::Display,
            {
                self.name = value
                    .try_into()
                    .map_err(|e| {
                        format!("error converting supplied value for name: {e}")
                    });
                self
            }
        }
        impl ::std::convert::TryFrom<Staff> for super::Staff {
            type Error = super::error::ConversionError;
            fn try_from(
                value: Staff,
            ) -> ::std::result::Result<Self, super::error::ConversionError> {
                Ok(Self {
                    id: value.id?,
                    name: value.name?,
                })
            }
        }
        impl ::std::convert::From<super::Staff> for Staff {
            fn from(value: super::Staff) -> Self {
                Self {
                    id: Ok(value.id),
                    name: Ok(value.name),
                }
            }
        }
    }
}
#[derive(Clone, Debug)]
/**Client for simPRO_API_Collection

Version: 1.0.0*/
pub struct Client {
    pub(crate) baseurl: String,
    pub(crate) client: reqwest::Client,
}
impl Client {
    /// Create a new client.
    ///
    /// `baseurl` is the base URL provided to the internal
    /// `reqwest::Client`, and should include a scheme and hostname,
    /// as well as port and a path stem if applicable.
    pub fn new(baseurl: &str) -> Self {
        #[cfg(not(target_arch = "wasm32"))]
        let client = {
            let dur = ::std::time::Duration::from_secs(15u64);
            reqwest::ClientBuilder::new().connect_timeout(dur).timeout(dur)
        };
        #[cfg(target_arch = "wasm32")]
        let client = reqwest::ClientBuilder::new();
        Self::new_with_client(baseurl, client.build().unwrap())
    }
    /// Construct a new client with an existing `reqwest::Client`,
    /// allowing more control over its configuration.
    ///
    /// `baseurl` is the base URL provided to the internal
    /// `reqwest::Client`, and should include a scheme and hostname,
    /// as well as port and a path stem if applicable.
    pub fn new_with_client(baseurl: &str, client: reqwest::Client) -> Self {
        Self {
            baseurl: baseurl.to_string(),
            client,
        }
    }
}
impl ClientInfo<()> for Client {
    fn api_version() -> &'static str {
        "1.0.0"
    }
    fn baseurl(&self) -> &str {
        self.baseurl.as_str()
    }
    fn client(&self) -> &reqwest::Client {
        &self.client
    }
    fn inner(&self) -> &() {
        &()
    }
}
impl ClientHooks<()> for &Client {}
impl Client {
    /**List all customers

List all customers.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/customers/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_customers()
    .company_id(company_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_customers(&self) -> builder::GetCustomers<'_> {
        builder::GetCustomers::new(self)
    }
    /**List all employees

List all employees.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/employees/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_employees()
    .company_id(company_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_employees(&self) -> builder::GetEmployees<'_> {
        builder::GetEmployees::new(self)
    }
    /**List all cost centers

List all cost centers.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/setup/accounts/costCenters/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_cost_centers()
    .company_id(company_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_cost_centers(&self) -> builder::GetCostCenters<'_> {
        builder::GetCostCenters::new(self)
    }
    /**List all jobs

List all jobs.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/jobs/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_jobs()
    .company_id(company_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_jobs(&self) -> builder::GetJobs<'_> {
        builder::GetJobs::new(self)
    }
    /**List all schedules

List all schedules.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/schedules/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `job_id`: Filter schedules by job ID. Supports operators: lt(), le(), gt(), ge(), ne(), between(), in(), !in().
- `lead_id`: Filter schedules by lead ID. Supports operators: lt(), le(), gt(), ge(), ne(), between(), in(), !in().
- `quote_id`: Filter schedules by quote ID. Supports operators: lt(), le(), gt(), ge(), ne(), between(), in(), !in().
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_schedules()
    .company_id(company_id)
    .job_id(job_id)
    .lead_id(lead_id)
    .quote_id(quote_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_schedules(&self) -> builder::GetSchedules<'_> {
        builder::GetSchedules::new(self)
    }
    /**List all activities

List all activities.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/setup/activities/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_activities()
    .company_id(company_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_activities(&self) -> builder::GetActivities<'_> {
        builder::GetActivities::new(self)
    }
    /**List all sites

List all sites.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/sites/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_sites()
    .company_id(company_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_sites(&self) -> builder::GetSites<'_> {
        builder::GetSites::new(self)
    }
    /**List all leads

List all leads.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/leads/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_leads()
    .company_id(company_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_leads(&self) -> builder::GetLeads<'_> {
        builder::GetLeads::new(self)
    }
    /**List all quotes

List all quotes.

Sends a `GET` request to `/api/v1.0/companies/{companyID}/quotes/`

Arguments:
- `company_id`: (Required) A build with Multi-company setup may have companyID >= 0, other builds use 0 by default.<br />
For more information about Multi-company, see:<br />
https://helpguide.simprogroup.com/Content/Service-and-Enterprise/Multi-company.htm
- `columns`: When listing or searching a resource, specify which columns to be displayed
- `limit`: Set the limit of number of records in a request
- `orderby`: Set the order of the requested records, by prefixing '-' on the column name you can get records by descending order. Comma separated list can also be provided.
- `page`: Set the page number on paginated request
- `page_size`: The maximum number of results to be returned by a request.
- `search`: Search result must have a match on all provided fields or a match on any of the provided fields.
```ignore
let response = client.get_quotes()
    .company_id(company_id)
    .columns(columns)
    .limit(limit)
    .orderby(orderby)
    .page(page)
    .page_size(page_size)
    .search(search)
    .send()
    .await;
```*/
    pub fn get_quotes(&self) -> builder::GetQuotes<'_> {
        builder::GetQuotes::new(self)
    }
}
/// Types for composing operation parameters.
#[allow(clippy::all)]
pub mod builder {
    use super::types;
    #[allow(unused_imports)]
    use super::{
        encode_path, ByteStream, ClientInfo, ClientHooks, Error, OperationInfo,
        RequestBuilderExt, ResponseValue,
    };
    /**Builder for [`Client::get_customers`]

[`Client::get_customers`]: super::Client::get_customers*/
    #[derive(Debug, Clone)]
    pub struct GetCustomers<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetCustomers<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/customers/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::Customer>>, Error<()>> {
            let Self {
                client,
                company_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/customers/", client.baseurl, encode_path(&
                company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_customers",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
    /**Builder for [`Client::get_employees`]

[`Client::get_employees`]: super::Client::get_employees*/
    #[derive(Debug, Clone)]
    pub struct GetEmployees<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetEmployees<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/employees/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::Employee>>, Error<()>> {
            let Self {
                client,
                company_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/employees/", client.baseurl, encode_path(&
                company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_employees",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
    /**Builder for [`Client::get_cost_centers`]

[`Client::get_cost_centers`]: super::Client::get_cost_centers*/
    #[derive(Debug, Clone)]
    pub struct GetCostCenters<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetCostCenters<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/setup/accounts/costCenters/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::CostCenter>>, Error<()>> {
            let Self {
                client,
                company_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/setup/accounts/costCenters/", client.baseurl,
                encode_path(& company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_cost_centers",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
    /**Builder for [`Client::get_jobs`]

[`Client::get_jobs`]: super::Client::get_jobs*/
    #[derive(Debug, Clone)]
    pub struct GetJobs<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetJobs<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/jobs/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::Job>>, Error<()>> {
            let Self {
                client,
                company_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/jobs/", client.baseurl, encode_path(&
                company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_jobs",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
    /**Builder for [`Client::get_schedules`]

[`Client::get_schedules`]: super::Client::get_schedules*/
    #[derive(Debug, Clone)]
    pub struct GetSchedules<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        job_id: Result<Option<::std::string::String>, String>,
        lead_id: Result<Option<::std::string::String>, String>,
        quote_id: Result<Option<::std::string::String>, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetSchedules<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                job_id: Ok(None),
                lead_id: Ok(None),
                quote_id: Ok(None),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn job_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.job_id = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for job_id failed"
                        .to_string()
                });
            self
        }
        pub fn lead_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.lead_id = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for lead_id failed"
                        .to_string()
                });
            self
        }
        pub fn quote_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.quote_id = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for quote_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/schedules/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::Schedule>>, Error<()>> {
            let Self {
                client,
                company_id,
                job_id,
                lead_id,
                quote_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let job_id = job_id.map_err(Error::InvalidRequest)?;
            let lead_id = lead_id.map_err(Error::InvalidRequest)?;
            let quote_id = quote_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/schedules/", client.baseurl, encode_path(&
                company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("JobID", &job_id))
                .query(&progenitor_client::QueryParam::new("LeadID", &lead_id))
                .query(&progenitor_client::QueryParam::new("QuoteID", &quote_id))
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_schedules",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
    /**Builder for [`Client::get_activities`]

[`Client::get_activities`]: super::Client::get_activities*/
    #[derive(Debug, Clone)]
    pub struct GetActivities<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetActivities<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/setup/activities/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::Activity>>, Error<()>> {
            let Self {
                client,
                company_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/setup/activities/", client.baseurl,
                encode_path(& company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_activities",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
    /**Builder for [`Client::get_sites`]

[`Client::get_sites`]: super::Client::get_sites*/
    #[derive(Debug, Clone)]
    pub struct GetSites<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetSites<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/sites/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::Site>>, Error<()>> {
            let Self {
                client,
                company_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/sites/", client.baseurl, encode_path(&
                company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_sites",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
    /**Builder for [`Client::get_leads`]

[`Client::get_leads`]: super::Client::get_leads*/
    #[derive(Debug, Clone)]
    pub struct GetLeads<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetLeads<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/leads/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::Lead>>, Error<()>> {
            let Self {
                client,
                company_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/leads/", client.baseurl, encode_path(&
                company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_leads",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
    /**Builder for [`Client::get_quotes`]

[`Client::get_quotes`]: super::Client::get_quotes*/
    #[derive(Debug, Clone)]
    pub struct GetQuotes<'a> {
        client: &'a super::Client,
        company_id: Result<::std::string::String, String>,
        columns: Result<Option<::std::string::String>, String>,
        limit: Result<Option<::std::string::String>, String>,
        orderby: Result<Option<::std::string::String>, String>,
        page: Result<Option<::std::string::String>, String>,
        page_size: Result<Option<::std::string::String>, String>,
        search: Result<Option<::std::string::String>, String>,
    }
    impl<'a> GetQuotes<'a> {
        pub fn new(client: &'a super::Client) -> Self {
            Self {
                client: client,
                company_id: Err("company_id was not initialized".to_string()),
                columns: Ok(None),
                limit: Ok(None),
                orderby: Ok(None),
                page: Ok(None),
                page_size: Ok(None),
                search: Ok(None),
            }
        }
        pub fn company_id<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.company_id = value
                .try_into()
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for company_id failed"
                        .to_string()
                });
            self
        }
        pub fn columns<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.columns = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for columns failed"
                        .to_string()
                });
            self
        }
        pub fn limit<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.limit = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for limit failed"
                        .to_string()
                });
            self
        }
        pub fn orderby<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.orderby = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for orderby failed"
                        .to_string()
                });
            self
        }
        pub fn page<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page failed"
                        .to_string()
                });
            self
        }
        pub fn page_size<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.page_size = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for page_size failed"
                        .to_string()
                });
            self
        }
        pub fn search<V>(mut self, value: V) -> Self
        where
            V: std::convert::TryInto<::std::string::String>,
        {
            self.search = value
                .try_into()
                .map(Some)
                .map_err(|_| {
                    "conversion to `:: std :: string :: String` for search failed"
                        .to_string()
                });
            self
        }
        ///Sends a `GET` request to `/api/v1.0/companies/{companyID}/quotes/`
        pub async fn send(
            self,
        ) -> Result<ResponseValue<::std::vec::Vec<types::Quote>>, Error<()>> {
            let Self {
                client,
                company_id,
                columns,
                limit,
                orderby,
                page,
                page_size,
                search,
            } = self;
            let company_id = company_id.map_err(Error::InvalidRequest)?;
            let columns = columns.map_err(Error::InvalidRequest)?;
            let limit = limit.map_err(Error::InvalidRequest)?;
            let orderby = orderby.map_err(Error::InvalidRequest)?;
            let page = page.map_err(Error::InvalidRequest)?;
            let page_size = page_size.map_err(Error::InvalidRequest)?;
            let search = search.map_err(Error::InvalidRequest)?;
            let url = format!(
                "{}/api/v1.0/companies/{}/quotes/", client.baseurl, encode_path(&
                company_id.to_string()),
            );
            let mut header_map = ::reqwest::header::HeaderMap::with_capacity(1usize);
            header_map
                .append(
                    ::reqwest::header::HeaderName::from_static("api-version"),
                    ::reqwest::header::HeaderValue::from_static(
                        super::Client::api_version(),
                    ),
                );
            #[allow(unused_mut)]
            let mut request = client
                .client
                .get(url)
                .header(
                    ::reqwest::header::ACCEPT,
                    ::reqwest::header::HeaderValue::from_static("application/json"),
                )
                .query(&progenitor_client::QueryParam::new("columns", &columns))
                .query(&progenitor_client::QueryParam::new("limit", &limit))
                .query(&progenitor_client::QueryParam::new("orderby", &orderby))
                .query(&progenitor_client::QueryParam::new("page", &page))
                .query(&progenitor_client::QueryParam::new("pageSize", &page_size))
                .query(&progenitor_client::QueryParam::new("search", &search))
                .headers(header_map)
                .build()?;
            let info = OperationInfo {
                operation_id: "get_quotes",
            };
            client.pre(&mut request, &info).await?;
            let result = client.exec(request, &info).await;
            client.post(&result, &info).await?;
            let response = result?;
            match response.status().as_u16() {
                200u16 => ResponseValue::from_response(response).await,
                _ => Err(Error::UnexpectedResponse(response)),
            }
        }
    }
}
/// Items consumers will typically use such as the Client.
pub mod prelude {
    pub use self::super::Client;
}
