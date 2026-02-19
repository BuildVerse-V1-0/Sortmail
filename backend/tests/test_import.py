
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Attempting to import IngestionService...")
    from core.ingestion.sync_service import IngestionService
    print("✅ Success!")
except ImportError as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
