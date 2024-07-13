# SinaSuite-dl
Webapp for data loading in SINASUITE.

# Getting Started
### Prerequisites
1. Download [Python](https://www.python.org/downloads/release/python-3120/?ref=upstract.com) (version 3.12 is recommended)
    
    - On Windows 11:
        ```powershell
        winget install Python.Python.3.12
        ```
    
    - On Linux:
        ```bash
        sudo apt-get install python3.12 python3.12-venv
        ```

2. Download [Microsoft ODBC 17 for SQL SERVER](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)

    - On Windows 11, download [Here]((https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16))

    - On Linux:
        ```bash
        sudo apt-get update && apt-get install -y --no-install-recommends curl gnupg unixodbc-dev unixodbc
        ```
        
        ```bash
        curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
        curl -sSL https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
        ```
      
        ```bash
        sudo apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17
        ```

3. Download [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/) and [Docker Compose](https://docs.docker.com/compose/install/). (Restart PC required)

    - On Windows 11:
        ```powershell
        winget install Docker.DockerDesktop Docker.DockerCompose
        ```
    
    - On Linux:
        ```bash
        sudo apt-get install docker docker-compose docker-compose-plugin
        ```

4. Download [Git](https://git-scm.com/download/win)

    - On Windows 11:
        ```powershell
        winget install Git.Git
        ```
    
    - On Linux:
        ```bash
        sudo apt-get install git
        ```

### Setting up the project
1. Clone the Github repository:

```bash
git clone https://github.com/kaidewu/sinasuite-dl.git
cd sinasuite-dl
```

2. Build and run the Docker containers using Docker Compose:

```bash
docker compose up -d
```

3. Access the application:

   - Open your browser and go to http://localhost:3000.

## Automated Docker Setup
You can use the provided PowerShell (setup-docker.ps1) and Bash (setup-docker.sh) scripts to automate the Docker setup process.

### PowerShell Script (setup-docker.ps1)
Run the PowerShell script:
```powershell
.\script\setup-docker.ps1
```

### Bash Script (setup-docker.sh)
Create a setup-docker.sh file with the following content:

Make the Bash script executable:
```bash
chmod +x setup-docker.sh && ./script/setup-docker.sh
```