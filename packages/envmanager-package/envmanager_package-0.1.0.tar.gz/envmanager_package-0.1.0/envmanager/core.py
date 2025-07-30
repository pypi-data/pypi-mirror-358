import os

class EnvManager:
    def __init__(self, env_path='.env'):
        self.env_path = env_path
        self.env = {}
        if os.path.exists(self.env_path):
            self.load()

    def load(self):
        self.env = {}
        with open(self.env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    self.env[key.strip()] = value.strip()

    def save(self):
        with open(self.env_path, 'w') as f:
            for key, value in self.env.items():
                f.write(f'{key}={value}\n')

    def add(self, key, value):
        self.env[key] = value
        self.save()

    def remove(self, key):
        if key in self.env:
            del self.env[key]
            self.save()

    def validate(self, required_keys):
        missing = [k for k in required_keys if k not in self.env]
        return missing

    def generate_from_template(self, template_path):
        with open(template_path, 'r') as f:
            with open(self.env_path, 'w') as out:
                out.write(f.read())
        self.load() 