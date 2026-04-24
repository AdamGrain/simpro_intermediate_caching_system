
WSL2 Enable:
https://learn.microsoft.com/en-us/windows/wsl/install

WSL2 Ubuntu
https://apps.microsoft.com/detail/9pdxgncfsczv?hl=en-US&gl=GB

Docker Install
https://docs.docker.com/engine/install/ubuntu/

```sh
sudo usermod -aG docker $USER
```
```sh
cd /mnt/c/Users/AdamSixsmith/Projects/simpro
```

Prerequisites:
```sh
sudo apt install unzip jq curl
```

Acquire or update the file `openapi.json`:
```sh
bash acquire.sh
```

Validate the specification:
https://openapi-generator.tech/docs/installation/
```sh
docker run --rm \
  -v "${PWD}:/local" \
  openapitools/openapi-generator-cli \
  validate \
  -i /local/openapi.json
```

Prepare the file for SDK/SQL:
```sh
cd prepare-specification
pip install -r required
py main.py
```

API client wrapper `api.rs`:
- Copy `openapi.yaml` into `simpro-incremental-caching-system`
```sh
cd simpro-incremental-caching-system
cargo build
```

Database query builders:
- You will need pgsql 'libpq.dll' 
- https://www.enterprisedb.com/download-postgresql-binaries

The following assumes pgsql is exported into 'C:\pgsql\bin;%PATH%'

```sh
docker compose up --build
cargo install diesel_cli --no-default-features --features postgres
set DATABASE_URL=postgres://postgres:postgres@localhost:15432/simpro
set PATH=C:\pgsql\bin;%PATH%
```

Removing/resetting:
```sh
docker compose down -v
docker compose up --build
```

Printing:
```sh
diesel print-schema > simpro-incremental-caching-system/src/db/table.rs
```

