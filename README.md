# Rides Project

This project is a RESTful API application that allows an admin user to consult Rides or trips, this project uses JWT authentication.

This project was built using a Django template I already have, which can be accessed at this link [django_template](https://github.com/andresprzh/django_template)

## Features

- **Django**
- **Django REST Framework (DRF)**
- **JWT Authentication**
- **drf-yasg**
- **debugpy**
- **pytest, pytest-django, pytest-cov**

## Development Environment

- **VS Code Debugging**: The project is set up to allow remote debugging with VS Code using `debugpy`. When running in debug mode, the server listens on port 4000 for debugger attachments. Simply use the provided VS Code launch configuration to attach to the running container or process.

- **Docker & Docker Compose**: This project includes a `Dockerfile` and `docker-compose.yml` for easy local development and deployment. Environment variables are managed via `.env` files (excluded from version control).


## Project Structure

- `ride_project/` - Main Django project code
- `ride_project/custom_settings/` - Modular settings for different environments (e.g., `dev.py`, `base.py`)
- `requirements_admin/requirements.txt` - All Python dependencies
- `docker-compose.yml` and `Dockerfile` - Containerization setup
- `tests/` - Example and template tests using pytest
- `.github/` - GitHub Copilot configuration:
  - `copilot-instructions.md` - Coding guidelines applied whenever Python code is added, to keep it consistent with the project structure
  - `skills/add_new_app/` - Skill to scaffold a new Django app inside the `apps/` folder
  - `skills/rename_project/` - Skill to rename the Django project and update all references

## Quick Start

1. **Clone the repository.**

2. **Configure environment variables:**
   - Create a `.env` file in the folder `conf/environments/.env` (this path is required by the Docker Compose setup).
   - The `.env` file should contain the following variables:
     - `USE_SQLITE` (set to `True` to use SQLite, or `False` to use PostgreSQL)
     - `SECRET_KEY` (your Django secret key)
     - `DEBUG` (set to `True` or `False`)
     - `DOMAIN_URL` (your domain, optional)
     - If using PostgreSQL (`USE_SQLITE=False`), also set:
       - `POSTGRES_DB` (database name)
       - `POSTGRES_USER` (database user)
       - `POSTGRES_PASSWORD` (database password)
       - `DB_HOST` (database host, e.g. `db` or `localhost`)
       - `DB_PORT` (database port, usually `5432`)

   - If `USE_SQLITE` is set to `True`, the project will use a local SQLite database. If set to `False`, it will use a PostgreSQL database and require the above environment variables to be set.

    Example `.env` for SQLite:"

   ```
   USE_SQLITE=True
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ```

   Example `.env` for PostgreSQL:

   ```
   USE_SQLITE=False
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   POSTGRES_DB=your_db_name
   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   DB_HOST=db
   DB_PORT=5432
   ```

   **Note**: You can use this command in the web service to create the secret key for local development if you don't have one:

   ```bash
   docker compose run --rm web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```


3. **Build and start the services:**
   ```bash
   docker compose up --build
   ```

4. **Run tests:**
   ```bash
   docker compose run --rm web pytest
   ```

5. **Attach VSCode debugger** to port 4000 if needed.

7. **Fixture  test data**

   I add testing data for local environment in this project you can run  it with  this command, the test admin user from this fixture data is :

      - user: test@test.com
      - password: test12345

   ```bash
   docker compose run --rm web python manage.py loaddata apps/user/fixtures/users.json apps/ride/fixtures/rides.json apps/ride/fixtures/ride_events.json
   ```

6. **Create super user**

   You can also create a super user with the Django command:

   ```bash
   docker compose run --rm web python manage.py createsuperuser
   ```

8. **Django Admin**

   This project has Django admin configured, so if you created a superuser, you can use it to access it. 

   [http://localhost:9000/admin](http://localhost:9000/admin)

## SQL report

This SQL  report show the number of rides where the duration from pickup to dropoff is greter than 1 hour. For this, I  assume that the correct date for pickup is  the one in the `ride_rideevent`  table and not the one in the `ride_ride` table.

```sql
WITH ride_times AS (
    SELECT
        rides.id,
        rides.id_driver_id,
        MIN(CASE
                WHEN events.description ILIKE '%pickup%'
                THEN events.created_at
            END) AS pickup_time,
        MAX(CASE
                WHEN events.description ILIKE '%dropoff%'
                THEN events.created_at
            END) AS dropoff_time
    FROM ride_rideevent events
    INNER JOIN ride_ride rides
        ON rides.id = events.id_ride_id
    WHERE rides.status = 'dropoff'
    GROUP BY rides.id, rides.id_driver_id
),
ride_duration AS (
	SELECT
	    ride_times.id,
	    ride_times.id_driver_id,
	    ride_times.pickup_time,
	    ride_times.dropoff_time,
	    ROUND(
	        EXTRACT(EPOCH FROM (dropoff_time - pickup_time)) / 3600.0,
	        2
	    ) AS duration_hours
	FROM ride_times
)
SELECT
    TO_CHAR(ride_duration.pickup_time, 'YYYY-MM') AS month,
    CONCAT(driver.first_name, ' ', driver.last_name) AS driver_name,
    COUNT(*) AS rides_over_1_hour
FROM ride_duration
INNER JOIN user_user driver
    ON driver.id = ride_duration.id_driver_id
where ride_duration.duration_hours > 1
group by (
	TO_CHAR(ride_duration.pickup_time, 'YYYY-MM'),
    driver.id,
    driver.first_name,
    driver.last_name
); 

```