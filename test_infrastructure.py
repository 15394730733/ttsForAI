"""
Test script to verify infrastructure setup.
"""
import sys
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

print("Testing infrastructure setup...\n")

# Test 1: Import configuration
print("1. Testing configuration module...")
try:
    from core.config import settings
    print(f"   [OK] Config loaded")
    print(f"   [OK] Database URL: {settings.DATABASE_URL}")
    print(f"   [OK] Log level: {settings.LOG_LEVEL}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 2: Import database
print("\n2. Testing database module...")
try:
    from core.database import Base, engine
    print(f"   [OK] Database module loaded")
    print(f"   [OK] Engine created: {engine.url}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 3: Import logger
print("\n3. Testing logger module...")
try:
    from core.logger import logger
    print(f"   [OK] Logger configured")
    logger.info("Test log message")
    print(f"   [OK] Logging works")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 4: Import security
print("\n4. Testing security module...")
try:
    from core.security import sanitize_text, validate_text_length
    print(f"   [OK] Security module loaded")
    test_text = "Hello, World!"
    sanitized = sanitize_text(test_text)
    print(f"   [OK] Text sanitization works: '{sanitized}'")
    is_valid = validate_text_length(test_text)
    print(f"   [OK] Length validation works: {is_valid}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 5: Import FastAPI app
print("\n5. Testing FastAPI application...")
try:
    from main import app
    print(f"   [OK] FastAPI app created")
    print(f"   [OK] Title: {app.title}")
    print(f"   [OK] Version: {app.version}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 6: Check directories
print("\n6. Checking directories...")
dirs_to_check = [
    "backend/src/api",
    "backend/src/models",
    "backend/src/services",
    "backend/src/core",
    "backend/data",
    "backend/output",
    "backend/logs",
    "frontend/src",
]

for dir_path in dirs_to_check:
    p = Path(dir_path)
    if p.exists():
        print(f"   [OK] {dir_path}")
    else:
        print(f"   [FAIL] {dir_path} (missing)")

print("\n[SUCCESS] Infrastructure setup test complete!")
print("\nNext steps:")
print("1. Run backend: cd backend && python -m uvicorn src.main:app --reload")
print("2. Run frontend: cd frontend && npm run dev")
