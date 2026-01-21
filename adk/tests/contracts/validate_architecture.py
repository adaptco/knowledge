import json
import yaml
import os
import sys
from pathlib import Path

CONTRACTS_DIR = Path("contracts/v0")

def check_structure():
    print(f"Checking contracts in {CONTRACTS_DIR}...")
    if not CONTRACTS_DIR.exists():
        print("FAIL: Contracts directory not found.")
        sys.exit(1)

def validate_schemas():
    print("\n[Schemas]")
    schema_dir = CONTRACTS_DIR / "schemas"
    valid = 0
    errors = 0
    for schema_file in schema_dir.glob("*.json"):
        try:
            with open(schema_file, 'r') as f:
                json.load(f)
            print(f"  OK: {schema_file.name}")
            valid += 1
        except Exception as e:
            print(f"  FAIL: {schema_file.name} - {e}")
            errors += 1
    
    if errors > 0:
        return False
    return True

def validate_state_machine():
    print("\n[State Machine]")
    sm_dir = CONTRACTS_DIR / "state_machine"
    
    # Load States
    try:
        with open(sm_dir / "states.yaml", 'r') as f:
            states_doc = yaml.safe_load(f)
        state_names = {s['name'] for s in states_doc['states']}
        print(f"  Loaded {len(state_names)} states: {', '.join(state_names)}")
    except Exception as e:
        print(f"FAIL: Could not load states.yaml: {e}")
        return False

    # Load Transitions and Verify
    try:
        with open(sm_dir / "transitions.yaml", 'r') as f:
            transitions_doc = yaml.safe_load(f)
        
        errors = 0
        for idx, t in enumerate(transitions_doc['transitions']):
            t_from = t['from']
            t_to = t['to']
            
            # Handle list-based 'from' (e.g. from: [A, B])
            sources = t_from if isinstance(t_from, list) else [t_from]
            
            # Check From
            for src in sources:
                if src not in state_names:
                    print(f"  FAIL: Transition defines unknown source state '{src}'")
                    errors += 1
            
            # Check To
            if t_to not in state_names:
                print(f"  FAIL: Transition defines unknown target state '{t_to}'")
                errors += 1
        
        if errors == 0:
            print("  OK: All transitions reference valid states.")
            return True
        else:
            return False

    except Exception as e:
        print(f"FAIL: Error processing transitions.yaml: {e}")
        return False

def main():
    check_structure()
    s_ok = validate_schemas()
    sm_ok = validate_state_machine()
    
    if s_ok and sm_ok:
        print("\nSUCCESS: Model Architecture Verified.")
        sys.exit(0)
    else:
        print("\nFAILURE: Model Architecture Issues Found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
