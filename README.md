# Habbit Backend.

## Installation without docker

clone the repositor
```bash
git clone git@github.com:ZEDUX-INC/Habit-Backend.git
```

Install python virtual environment
```bash
  python3 -m venv ./venv
```

install python requirement
```bash
  source ./venv/bin/activate
  pip install -r ./requirements.txt
```

Install precommit
```bash
  pre-commit install
```

Run Migrations
```bash
  python manage.py migrate
```
Lunch server
```bash
  python manage.py runserver
```

## Testing without docker
we use pytest for testing

```bash
  pytest ./tests
```

## Installation Using Docker
  ### Install dependencies
  Install docker
  https://docs.docker.com/desktop/install/windows-install/

  ### Build Container
  ```bash
    docker compose build
  ```

  ### Run Container
  ```bash
    docker compose up
  ```

  ### Run Test
  ```bash
    docker compose exec web sh
    pytest ./tests
  ```

## Contributing
Make a Pull Request to Staging Branch.
Ensure CI passes.
Request Code Review.

Please make sure to update tests as appropriate.
If PR affect django Models please ensure to provide migation. Also ensure migration is properly named.
If PR adds new dependecy update requirements.txt file
