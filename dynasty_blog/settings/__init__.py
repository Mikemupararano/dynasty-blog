from decouple import config

env = config("DJANGO_ENV", default="local").lower().strip()

if env in ("prod", "production"):
    from .prod import *  # noqa
else:
    from .local import *  # noqa
