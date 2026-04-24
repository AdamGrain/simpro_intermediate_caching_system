#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ======================================================
# ENVIRONMENT VARIABLES
# ======================================================

ENV_FILE="$SCRIPT_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "Missing $ENV_FILE" >&2
  exit 1
fi

[[ -n "${POSTMAN_API_KEY:-}" ]] || {
  echo "POSTMAN_API_KEY NOT SET" >&2
  exit 1
}

# ======================================================
# DEPENDENCIES
# ======================================================

require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing dependency: $1" >&2
    exit 1
  }
}

require docker
require unzip
require jq
require curl

# ======================================================
# POSTMAN HTTP HELPERS
# ======================================================

postman_get() {
  local url="$1"

  curl -sS \
    --request GET \
    --header "X-Api-Key: $POSTMAN_API_KEY" \
    "$url"
}

postman_post() {
  local url="$1"

  curl -sS \
    --request POST \
    --header "X-Api-Key: $POSTMAN_API_KEY" \
    --header "Content-Type: application/json" \
    --data-binary @- \
    "$url"
}

# ==================================================================
# DOWNLOAD OFFICIAL SWAGGER SPECIFICATION (CLOUDFLARE-PROTECTED)
# ==================================================================

download_protected_file() {
  # Downloads a Cloudflare-protected file with `curl-impersonate`.
  # * https://curl.se/docs/manpage.html
  # * https://docs.docker.com/reference/cli/docker/container/run/
  # * https://github.com/lwthiker/curl-impersonate
  # * https://developer.simprogroup.com/apidoc/swagger.zip
  # * https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
  local download_url="$1"
  local downloaded_file="$2"
  local expected_contents="$3"

  local status_code
  status_code=$(
    docker run --rm \
      --volume "$PWD:/data" \
      --workdir /data \
      lwthiker/curl-impersonate:0.6-ff \
      curl_ff109 \
        --silent \
        --show-error \
        --location \
        --output "$downloaded_file" \
        --write-out "%{http_code}" \
        "$download_url"
  )

  [[ "$status_code" == "200" ]] || {
    rm -f "$downloaded_file"
    echo "Download Failed (HTTP $status_code)" >&2
    return 1
  }

  unzip -o "$downloaded_file" >/dev/null
  rm -f "$downloaded_file"

  [[ -f "$expected_contents" ]] || {
    echo "Expected '$expected_contents' not found after unzip" >&2
    return 1
  }
}

# ======================================================
# IS TIMESTAMP STALE
# ======================================================

is_stale() {
  local timestamp="$1"
  local max_days="$2"

  [[ -z "$timestamp" || "$timestamp" == "null" ]] && return 1

  local now ts
  now=$(date -u +%s)
  ts=$(date -u -d "$timestamp" +%s 2>/dev/null) || return 1

  (( (now - ts) > max_days * 86400 ))
}

# ======================================================
# MAIN ACQUIRE
# ======================================================

acquire_openapi_file() {

  local openapi_file="openapi.json"
  if [[ -f "$openapi_file" ]]; then
    echo "$openapi_file exists in directory."
    return 0
  fi

  local postman_url="https://api.getpostman.com"
  local max_days=10
  local collection_uid=""
  local collection_updated=""

  # --------------------------------------
  # DOWNLOAD SWAGGER FILE
  # --------------------------------------

  local swagger_file="swagger.json"
  if [[ ! -f "$swagger_file" ]]; then
    echo "== Downloading Swagger =="
    download_protected_file \
      "https://developer.simprogroup.com/apidoc/swagger.zip" \
      "swagger.zip" \
      "$swagger_file"
  fi

  # -----------------------------------------
  # GET POSTMAN COLLECTION
  # -----------------------------------------

  echo "== Checking Collection Exists =="

  local collection_name="simPRO_API_Collection"
  local collections_response
  collections_response="$(postman_get "$postman_url/collections")"

  local existing_collection
  existing_collection="$(jq -c --arg name "$collection_name" '
    (.collections // [])
    | map(select(.name == $name))
    | .[0] // empty
  ' <<<"$collections_response")"

  if [[ -n "$existing_collection" ]]; then
    collection_uid="$(jq -r '.uid // empty' <<<"$existing_collection")"
    collection_updated="$(jq -r '.updatedAt // empty' <<<"$existing_collection")"
  fi

  echo "Collection UID: ${collection_uid:-none}"
  echo "Collection Updated: ${collection_updated:-none}"

  if [[ -n "$collection_uid" ]] && ! is_stale "$collection_updated" "$max_days"; then
    echo "Reusing Existing Collection"
  else

    # --------------------------------------
    # GET POSTMAN WORKSPACE
    # --------------------------------------

    local workspace_name="simPRO_API_Workspace"

    echo "== Checking Workspace Exists =="

    local workspaces_response
    workspaces_response="$(postman_get "$postman_url/workspaces")"

    local workspace_id
    workspace_id="$(jq -r --arg name "$workspace_name" '
      (.workspaces // [])
      | map(select(.name == $name))
      | .[0].id // empty
    ' <<<"$workspaces_response")"

    if [[ -z "$workspace_id" ]]; then

      # -----------------------------------------
      # CREATE POSTMAN WORKSPACE
      # -----------------------------------------

      echo "== Creating Postman Workspace '$workspace_name' =="

      jq -n --arg name "$workspace_name" '{
        workspace: {
          name: $name,
          type: "personal",
          description: "Auto-created workspace"
        }
      }' | postman_post "$postman_url/workspaces" \
        | jq -r '.workspace.id' \
        > /tmp/workspace_id

      workspace_id="$(cat /tmp/workspace_id)"
      rm -f /tmp/workspace_id
    fi

    [[ -n "$workspace_id" ]] || {
      echo "Failed to obtain workspace ID" >&2
      exit 1
    }

    # -----------------------------------------------------------------
    # CREATE POSTMAN COLLECTION
    # -----------------------------------------------------------------

    echo "== Creating Postman Collection '$collection_name' =="

    local create_collection_response
    create_collection_response="$(
      jq -n \
        --arg name "$collection_name" \
        --slurpfile file "$swagger_file" \
        '{type:"json", input: ($file[0] | .info.title=$name)}' \
      | postman_post "$postman_url/import/openapi?workspace=$workspace_id"
    )"

    collection_uid="$(jq -r '.collections[]?.uid // empty' <<<"$create_collection_response")"

    [[ -n "$collection_uid" ]] || {
      echo "Collection creation failed:" >&2
      jq . <<<"$create_collection_response" >&2
      exit 1
    }
  fi

  # --------------------------------------------------------------
  # EXPORT TO OPENAPI3 (JSON)
  # --------------------------------------------------------------

  echo "== Exporting to OpenAPI3 =="

  local transform_response
  transform_response="$(
    postman_get "$postman_url/collections/$collection_uid/transformations"
  )"

  jq -r '.output | fromjson' <<<"$transform_response" > "$openapi_file"

  #rm -f "$swagger_file"
  echo "OpenAPI written to '$openapi_file'"
}

# ======================================================
# RUN
# ======================================================

acquire_openapi_file