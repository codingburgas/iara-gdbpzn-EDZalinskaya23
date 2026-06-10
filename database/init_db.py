import os
import sys

# Allow finding the "app" package and config.py from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import seed  # noqa: E402
import config  # noqa: E402


if __name__ == "__main__":
    seed.build_database()
    print("Done! Database created at:", config.Config.DATABASE)
