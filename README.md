# Analytics Dashboards

Dashboards used for model validation and diagnostics as well as signal detection in external data. 

## Installation on M1

We are using Rosetta 2 to emulate x64, if you don't have Rosseta 2 installed, install it thorugh

```properties
softwareupdate --install-rosetta
```

Install x64 brew

```properties
arch -x86_64 zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
alias ibrew="arch -x86_64 /usr/local/bin/brew"
echo alias ibrew="arch -x86_64 /usr/local/bin/brew" >> ~/.zshrc
```

Use ibrew (brew running on emulated x64) to install python

```properties
ibrew install python
```

Verify that python is use x64 architecture

```properties
file /usr/local/Cellar/python@3.9/3.9.5/bin/python3.9
```

output should be

```
arch -x86_64 /usr/local/Cellar/python@3.9/3.9.5/bin/python3.9: Mach-O 64-bit executable x86_64
```


Create a x86 python virtual env

```properties
. .env/bin/activate
file $(which python3)
```

Result should be

```
../.env/bin/python3: Mach-O 64-bit executable x86_64
```

## Installation

  
### pre-commit

Pre-commit can be used to verify formatting etc..
```
pre-commit install
```

Copy the pre-push hook
```
cp .githooks/pre-push .git/hooks/pre-push
```

1. Poetry
Install poetry preview (with plugin support) and pypi keyring plugin

```
curl -sSL https://install.python-poetry.org | POETRY_PREVIEW=1 python3 -
poetry plugin add keyrings.google-artifactregistry-auth
```

Install python libraries using poetry:
```
poetry install
```

## Running a Panel dashboard
1. All existing dashboards have a seperate folder e.g. `analytics_dashboards`. New dashboards should be setup in a new folder.
2. To run an existing dashboard:

    - import and call the function that creates a servable panel template for the dashboard into `dashboard_runner.py` e.g.

        ```python
        from analytics_dashboards.dashboard import load_dashboard
        load_dashboard().servable()
        ```
   - serve the dashboard using the panel serve function on the terminal
        ```
        panel serve dashboard_runner.py
        ```
### Dashboard dependencies: 
1. The existing panel dashboard `analytics_dashboards` connects to an Azure PostgreSQL server. If running the `dashboard_runner.py` script outside the Azure cloud environment you will need to enable ssh connectivity by setting the following option in `/configuration/config.json`
    ```json
    "local_connection": true
    ```
2. Connecting to the PostrgeSQL database

The  paths to your database credentials, config.json and ssh private key files need to be provided under  `/analytics_dashboards/common/get_data.py`
```python
        # setup connection
         secrets_path = os.path.join(
         os.path.dirname(__file__), "../../../", "secrets", "analytics_staging_db.json")
         with open(secrets_path) as f:
              secret_analytics_staging_db = json.load(f)

         # load config
        config_path = os.path.join(
            os.path.dirname(__file__), "../../", "configuration", "config.json"
        )
        with open(config_path) as config_file:
            config = json.load(config_file)

        # ssh private-key
        ssh_private_key_path = os.path.join(
            os.path.dirname(__file__), "../../../", "secrets", "id_rsa"
        )
```

References:
- [Configuring the panel template](https://panel.holoviz.org/reference/templates/FastListTemplate.html)
- [Deploying and exporting a panel app](https://panel.holoviz.org/user_guide/Deploy_and_Export.html)
- [Cloud server deployment of a panel app](https://panel.holoviz.org/user_guide/Server_Deployment.html) 