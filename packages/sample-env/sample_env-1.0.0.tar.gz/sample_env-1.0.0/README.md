<h1 align="center" style="border-bottom: none;">sample-env</h1>
<h3 align="center">A CLI tool for generating sample env files from <a href="">pydantic_settings.BaseSettings</a>.</h3>

# Installation

```
pip install sample-env
```

# Command-line usage

Let's assume the following [`BaseSettings`](https://docs.pydantic.dev/latest/usage/pydantic_settings/).

```python
from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    DEBUG: bool = True
    POSTGRES_HOST: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_DB: str = "db"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_PORT: str = "5432"
```

You can generate a `.env.sample` file with this command:

```shell script
sample-env example.Environment
```

Output

```dotenv
DEBUG=True
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_DB=db
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
```
