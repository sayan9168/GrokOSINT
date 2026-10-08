PLUGIN = {"id": "example_echo", "name": "Example Echo", "description": "Demo plugin"}

def run(target: str):
    return {"target": target, "echo": (target or "").upper()}
