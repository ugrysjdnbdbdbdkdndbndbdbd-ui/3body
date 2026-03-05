import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import app

print(f"{'METHOD':<10} {'PATH'}")
print("-" * 50)
for route in app.routes:
    if hasattr(route, "methods"):
        for method in route.methods:
            print(f"{method:<10} {route.path}")
    else:
        print(f"{'ANY':<10} {route.path}")
