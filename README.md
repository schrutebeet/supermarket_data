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
├── config/ # Configuration files (e.g., logging) 
├── database/ # Database models and utilities 
├── dependencies/ # Authentication and dependency management 
├── email_notifications/ # Email generation and templates 
├── src/ # Main application logic │ 
├── data_extractors/ # Extractors for different supermarkets 
├── utils/ # Utility functions and helpers 
├── Dockerfile # Docker configuration 
├── pyproject.toml # Poetry configuration 
├── README.md # Project documentation
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

