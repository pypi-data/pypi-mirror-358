# shit_env

A simple Python package to manage .env files, inspired by NodeJS dotenv.

## Installation

Just use pip:
```bash
pip install shit_env
```

## Usage

### Using the Env class
```python
import shit_env

env = shit_env.Env('.env')  # or just shit_env.Env('myenv')

# Get a variable
db_host = env.Get('DATABASE_HOST')

# Set a variable
env.Set('DATABASE_HOST', 'localhost')

# Get with default
db_user = env.Get('DATABASE_USER', 'root')
```

### Requiring a variable (crashes if missing or empty)
```python
import shit_env

# This will raise RuntimeError if DATABASE_HOST is missing or empty in .env
Var1 = shit_env.Required('DATABASE_HOST')

# You can also specify a custom env file
Var2 = shit_env.Required('DATABASE_USER', 'my.env')
```

## .env file format

```
DATABASE_HOST=localhost
DATABASE_USER=root
# Comments are supported
``` 