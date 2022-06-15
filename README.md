# Habbit Backend.

## Installation

clone the repositor
```bash
git clone git@github.com:ZEDUX-INC/Habit-Backend.git
```

Install precommit
```bash
  pre-commit install
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
Run Migrations
```bash
  python manage.py migrate
```
Lunch server
```bash
  python manage.py runserver
```

## Testing
we use pytest for testing

```bash
  pytest ./tests
```


## Contributing
Make a Pull Request to Staging Branch.
Ensure CI passes.
Request Code Review.

Please make sure to update tests as appropriate.
If PR affect django Models please ensure to provide migation. Also ensure migration is properly named.
If PR adds new dependecy update requirements.txt file
