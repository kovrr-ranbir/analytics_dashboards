# Analytics Dashboards

Dashboards used for model validation and diagnostics as well as signal detection in external data. 

# Installation on M1

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

# Installation

  
## pre-commit

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