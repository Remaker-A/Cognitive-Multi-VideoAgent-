from src.infrastructure.config_manager import ConfigManager
from src.infrastructure.database import init_db
import os
import sys

# Add src to path if needed (though running as module is better, but this is a script)
sys.path.append(os.getcwd())

def test_config_lifecycle():
    print("Initializing DB...")
    init_db()
    
    # 1. Test clean state (or existing)
    key = "TEST_KEY_123"
    val = "TEST_VALUE_123"
    
    print(f"Setting config {key}={val}...")
    ConfigManager.set(key, val)
    
    # 2. Test Get from DB
    # Clear lru_cache if any (ConfigManager doesn't utilize it currently but good practice)
    retrieved = ConfigManager.get(key)
    print(f"Retrieved from DB: {retrieved}")
    assert retrieved == val
    
    # 3. Test Fallback (Non-existent key)
    os.environ["TEST_ENV_KEY"] = "ENV_VAL"
    retrieved_env = ConfigManager.get("TEST_ENV_KEY")
    print(f"Retrieved from ENV: {retrieved_env}")
    assert retrieved_env == "ENV_VAL"
    
    # 4. Test DB Priority over Env
    os.environ[key] = "ENV_SHOULD_BE_IGNORED"
    retrieved_prio = ConfigManager.get(key)
    print(f"Retrieved from DB (with ENV conflict): {retrieved_prio}")
    assert retrieved_prio == val
    
    print("ConfigManager verification PASS")

if __name__ == "__main__":
    test_config_lifecycle()
