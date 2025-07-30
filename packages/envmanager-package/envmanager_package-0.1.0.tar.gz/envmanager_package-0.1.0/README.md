# EnvManager

A simple CLI tool to create, edit, validate, and manage `.env` files for Python projects.

## Features
- Add/remove keys in `.env` files
- Validate required environment variables
- Generate `.env` files from a template

## Installation
```bash
pip install .
```

## Usage
```bash
envmanager add KEY VALUE
envmanager remove KEY
envmanager validate --required KEY1 KEY2
envmanager generate --template template.env
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT 