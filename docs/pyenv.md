Based on CentOS.

## Install pyenv

> Simple Python Version Management: https://github.com/pyenv/pyenv

1. Install pyenv in **user00** home dir:
    ```bash
    curl https://pyenv.run | bash
    ```
2. Copy code below to `$HOME/.bashrc`:
    ```bash
    # Load pyenv automatically
    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    # Load pyenv-virtualenv automatically
    eval "$(pyenv virtualenv-init -)"
    ```

## Install Python-3.11.4

### 1. Install dependencies

> See https://devguide.python.org/getting-started/setup-building/#install-dependencies

```bash
yum groupinstall 'Development Tools'
yum install bzip2-devel -y
yum install libffi-devel -y
yum install readline-devel -y
yum install sqlite-devel -y
```

### 2. Install and switch to Python-3.11.4 release

```bash
pyenv install 3.11.4
pyenv global 3.11.4
```

> Install new package: `python -m pip install <Package>`

### 3. Install requirements.txt

> Automatically create *requirements.txt*: `pip freeze > requirements.txt`

- `python -m pip install -r requirements.txt`

## Run

`python app.py`