import json

def dumps(obj):
    # Sort the keys in the dictionary to ensure a consistent order
    return json.dumps(obj, indent=None, separators=(",", ":"), sort_keys=True)
