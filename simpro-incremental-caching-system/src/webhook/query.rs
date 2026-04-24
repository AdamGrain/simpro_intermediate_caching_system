use super::variants::Resource;
use crate::APIClient;
use crate::AppState;
use crate::api::types as record;
use crate::api::types::Schedule;
use crate::db;
use crate::update;
use diesel::ExpressionMethods;
use diesel::RunQueryDsl;
use diesel::pg::PgConnection;
use diesel::r2d2::ConnectionManager;
use r2d2::PooledConnection;
use std::collections::HashSet;
use std::sync::Arc;

impl Resource {
    /// These correspond to those filtered 'prepare-specification'
    /// * [Activity](https://developer.simprogroup.com/apidoc/?page=d78ed35383108fb6c04c16d0a11b20fe#tag/Activities/operation/c88605b27f7e8a3873047d9af3a93574)
    /// * [Site](https://developer.simprogroup.com/apidoc/?page=3faa64303d5f5bcd043bb88f6768e603#tag/Sites/operation/101d05972386dfa7536b58fe655d382e)
    /// * [Job](https://developer.simprogroup.com/apidoc/?page=12ceff2290bb9039beaa8f36d5dec226#tag/Jobs/operation/9ca8d728df9f031d2828e79cbb093702)
    /// * [Employee](https://developer.simprogroup.com/apidoc/?page=eb626c94531ec554f93b2b78a77c8b1b#tag/Employees/operation/ad2cdcfe3653fce4e460e4468acc2867)
    /// * [Schedule](https://developer.simprogroup.com/apidoc/?page=ccdb7bf9d93e5652b57cabcc8c41e061#tag/Schedules/operation/4a005958478750b0f96cb00b3c9da0f6)
    pub fn columns_to_include(
        &self,
    ) -> &'static [&'static str] {
        match self {
            Resource::Activity => &["ID", "Name"],
            Resource::Site => {
                &["ID", "Name", "DateModified", "Address"]
            }
            Resource::Job => &[
                "ID",
                "Name",
                "Description",
                "DateModified",
                "Type",
                "Site",
                "Notes",
                "Stage",
                "Status",
            ],
            Resource::Employee => {
                &["ID", "Name", "Position", "DateModified"]
            }
            Resource::Schedule => &[
                "ID",
                "Type",
                "Notes",
                "Reference",
                "TotalHours",
                "Staff",
                "Blocks",
                "DateModified",
            ],
            Resource::Quote => &[
                "ID",
                "Name"
            ],
            Resource::CostCenter => &[
                "ID",
                "Name"
            ],
            Resource::Lead => &[
                "ID",
                "Name"
            ]
        }
    }
    #[allow(unused)]
    #[tracing::instrument(skip(self, ids))]
    pub async fn getter(
        &self,
        ids: &[i64],
        app: Arc<AppState>,
    ) -> anyhow::Result<()> {

        let id_search: String = format!(
            "ID=in({})",
            ids.iter()
                .map(|id| id.to_string())
                .collect::<Vec<_>>()
                .join(",")
        );

        let query_columns: String =
            self.columns_to_include().join(",");

        let mut connection: PooledConnection<
            ConnectionManager<PgConnection>,
        > = app.db_connection_pool.get()?;

        match self {
            Resource::Schedule => {
                // -----------------------------------------------------
                use crate::db::{row, table::schedules::dsl::*};
                // -----------------------------------------------------
                let records: Vec<record::Schedule> = app
                    .api
                    .get_schedules()
                    .search(id_search)
                    .send()
                    .await
                    .map_err(|err| {tracing::error!(?err, "Failed to fetch 'Schedule'"); err})?
                    .into_inner();
                // -----------------------------------------------------
                let rows: Vec<row::Schedule> = records
                    .into_iter()
                    .map(row::Schedule::try_from)
                    .collect::<Result<Vec<_>, _>>()?;
                // -----------------------------------------------------
                // FK dependencies // -----------------------------------------------------
                let mut activity_ids = HashSet::new();
                let mut job_ids = HashSet::new();
                let mut cost_center_ids = HashSet::new();
                let mut quote_ids = HashSet::new();
                let mut lead_ids = HashSet::new();
                // -----------------------------------------------------
                for s in &rows {
                    if let Some(_id) = s.activity_id { activity_ids.insert(_id); }
                    if let Some(_id) = s.job_id { job_ids.insert(_id); }
                    if let Some(_id) = s.cost_center_id { cost_center_ids.insert(_id); }
                    if let Some(_id) = s.quote_id { quote_ids.insert(_id); }
                    if let Some(_id) = s.lead_id { lead_ids.insert(_id); }
                }
                // -----------------------------------------------------
                let fk_groups = [
                    (&activity_ids, Resource::Activity),
                    (&job_ids, Resource::Job),
                    (&cost_center_ids, Resource::CostCenter),
                    (&quote_ids, Resource::Quote),
                    (&lead_ids, Resource::Lead),
                ];
                // -----------------------------------------------------
                for (ids, resource) in fk_groups {
                    if !ids.is_empty() {
                        // Ensure the referenced records are added
                        // via recursive call
                        let ids = &ids.iter().copied().collect::<Vec<i64>>();
                        Box::pin(resource.getter(&ids, app.clone())).await?;
                    }
                }
                // -----------------------------------------------------
                diesel::insert_into(schedules)
                    .values(rows)
                    .on_conflict(id)
                    .do_update().set(update!(date_modified, staff_id, schedule_type, notes, job_id, cost_center_id, activity_id, quote_id, lead_id))
                    .execute(&mut connection)?;
            }
            Resource::CostCenter => {
                use crate::db::row;
                use crate::db::table::cost_centers::dsl::*;
                let records: Vec<record::CostCenter> = app
                    .api
                    .get_cost_centers()
                    .search(id_search)
                    .send()
                    .await
                    .inspect_err(|err| tracing::error!(?err, "Failed to fetch 'Cost Center'"))?
                    .into_inner();
            }
            Resource::Quote => {
                use crate::db::row;
                use crate::db::table::quotes::dsl::*;
                let records: Vec<record::Quote> = app
                    .api
                    .get_quotes()
                    .search(id_search)
                    .send()
                    .await
                    .inspect_err(|err| tracing::error!(?err, "Failed to fetch 'Cost Center'"))?
                    .into_inner();
            }
            Resource::Lead => {
                use crate::db::row;
                use crate::db::table::quotes::dsl::*;
                let records: Vec<record::Lead> = app
                    .api
                    .get_leads()
                    .search(id_search)
                    .send()
                    .await
                    .inspect_err(|err| tracing::error!(?err, "Failed to fetch 'Cost Center'"))?
                    .into_inner();
            }
            Resource::Job => {
                use crate::db::row;
                use crate::db::table::jobs::dsl::*;

                let records: Vec<record::Job> = app
                    .api
                    .get_jobs()
                    .search(id_search)
                    .send()
                    .await
                    .inspect_err(|err| tracing::error!(?err, "Failed to fetch 'Schedule'"))?
                    .into_inner();

                diesel::insert_into(jobs)
                    .values(
                        records
                            .into_iter()
                            .map(row::Job::try_from)
                            .collect::<Result<Vec<_>, _>>()?,
                    )
                    .on_conflict(id)
                    .do_update()
                    .set(update!(
                        name,
                        customer_company_name,
                        date_modified,
                        description,
                        site_id,
                        stage,
                        status_id,
                        job_type
                    ))
                    .execute(&mut connection)?;
            }
            Resource::Site => {
                use crate::db::row;
                use crate::db::table::sites::dsl::*;

                let records: Vec<record::Site> = app
                    .api
                    .get_sites()
                    .search(id_search)
                    .send()
                    .await
                    .map_err(|err| {
                        tracing::error!(
                            ?err,
                            "Failed to fetch 'Schedule'"
                        );
                        err
                    })?
                    .into_inner();

                diesel::insert_into(sites)
                    .values(
                        records
                            .into_iter()
                            .map(row::Site::try_from)
                            .collect::<Result<Vec<_>, _>>()?,
                    )
                    .on_conflict(id)
                    .do_update()
                    .set(update!(
                        address_address, address_city, address_country, address_postal_code, date_modified
                    ))
                    .execute(&mut connection)?;
            }
            Resource::Employee => {
                use crate::db::row;
                use crate::db::table::employees::dsl::*;

                let records: Vec<record::Employee> = app
                    .api
                    .get_employees()
                    .search(id_search)
                    .send()
                    .await
                    .map_err(|err| {tracing::error!(?err, "Failed to fetch 'Employee'"); err})?
                    .into_inner();

                diesel::insert_into(employees)
                    .values(
                        records
                            .into_iter()
                            .map(row::Employee::try_from)
                            .collect::<Result<Vec<_>, _>>()?,
                    )
                    .on_conflict(id)
                    .do_update()
                    .set(update!(
                        id, name
                    ))
                    .execute(&mut connection)?;
            }
            Resource::Activity => {
                use crate::db::row;
                use crate::db::table::activities::dsl::*;

                let records: Vec<record::Activity> = app
                    .api
                    .get_activities()
                    .search(id_search)
                    .send()
                    .await
                    .map_err(|err| {tracing::error!(?err, "Failed to fetch 'Activity'"); err})?
                    .into_inner();

                diesel::insert_into(activities)
                    .values(
                        records
                            .into_iter()
                            .map(row::Activity::try_from)
                            .collect::<Result<Vec<_>, _>>()?,
                    )
                    .on_conflict(id)
                    .do_update()
                    .set(update!(
                        id, name
                    ))
                    .execute(&mut connection)?;
            }
        }

        Ok(())
    }
}
