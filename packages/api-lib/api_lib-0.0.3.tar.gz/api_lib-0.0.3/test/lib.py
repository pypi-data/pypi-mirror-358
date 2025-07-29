import os


class EnvVarContext:
    def __init__(self, env_var, value):
        self.env_var = env_var
        self.value = value

    def __enter__(self):
        os.environ[self.env_var] = self.value

    def __exit__(self, exc_type, exc_value, traceback):
        os.environ.pop(self.env_var, None)
