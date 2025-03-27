# Supermarket Data Extractor :apple::bread::egg:

This project is a Python-based application designed to extract, process, and store product data from various supermarket APIs. The extracted data is stored in a PostgreSQL database, and email notifications are sent after a successful data extraction and storage.

## Features

- **Data Extraction**:
  - Extracts product data from supermarket APIs, including:
    - Mercadona
    - El Corte Inglés
  - Handles pagination and category-based data extraction.

- **Database Management**:
  - Automatically creates database schemas and tables for storing extracted data.
  - Inserts extracted data into the PostgreSQL database.
  - Supports dynamic table creation for new categories.

- **Email Notifications**:
  - Sends email notifications upon successful data extraction and storage.
  - Customizable email templates for different categories.

- **Logging**:
  - Logs information, warnings, and errors during the data extraction and storage process.
  - Supports both console and file-based logging.

- **Backup**:
  - Optionally creates a backup of the database on specific days (e.g., Mondays).

## Project Structure
```
supermarket_data/ 
supermarket_data/
├── src/                                # Main application logic
│   ├── main.py                         # Entry point of the application
│   ├── data_extractors/                # Data extraction modules
│   │   ├── corte_ingles/
│   │   │   ├── eci_generic_extractor.py
│   │   │   ├── eci_supermarket_extractor.py
│   │   ├── mercadona/
│   │       ├── mercadona_extractor.py
├── database/                           # Database-related functionality
│   ├── models.py                       # Database models (e.g., ECISupermarket, Mercadona)
│   ├── connection.py                   # Database connection settings
│   ├── utils_db.py                     # Utility functions for database operations
├── utils/                              # Utility modules
│   ├── default_columns.py              # Default column definitions for database tables
├── email_notifications/                # Email notification functionality
│   ├── email_generator.py              # Email generation and sending logic
├── config/                             # Configuration files (not explicitly shown but likely exists)
│   ├── log_config.py                   # Logging configuration (inferred)
├── dependencies/                       # Dependency management (inferred)
│   ├── authenticator.py                # Handles authentication (e.g., database credentials)
│   ├── postgres_keys.yaml              # Database credentials (inferred)
├── Dockerfile                          # Docker configuration (inferred)
├── pyproject.toml                      # Poetry configuration for dependencies
├── README.md                           # Project documentation (to be created)
```


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/supermarket_data.git
   cd supermarket_data
   ```
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Set up the PostgreSQL database:
    Create a database and configure the credentials in `dependencies/authenticator.py` (postgres_keys.yaml).
4. Configure environment variables:
    - Set LOGS_PATH for logging.
    - Set DATABASE_HOST for database connection.

## Usage
Running the Application
To run the application, execute the following command:

### Running with Docker
1. Build the Docker image:
   ```bash
   docker build -t supermarket_data .
   ```

2. Run the Docker container:
   ```bash
   docker run -e LOGS_PATH=/logs -e DATABASE_HOST=host.docker.internal supermarket_data
   ```

### Scheduled Execution
Use `supermarket_cronjob.sh` (Linux) or `run_supermarkets.bat` (Windows) to schedule periodic execution of the application.


## Configuration
- **Database**: Configure database credentials in `dependencies/authenticator.py`.
- **Logging**: Modify logging settings in config/log_config.py.
- **Email Notifications**: Update email credentials and templates in `email_notifications/`.


## Dependencies
The project uses the following Python libraries:

   ```bash
    pandas
    sqlalchemy
    requests
    psycopg2
    bs4
    pyyaml
   ```
Refer to the `pyproject.toml` for the complete list.

