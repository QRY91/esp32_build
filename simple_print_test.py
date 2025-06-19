import time

print("=== SIMPLE TEST START ===")
print("If you see this, CircuitPython is working!")

for i in range(10):
    print(f"Count: {i}")
    time.sleep(1)

print("=== TEST COMPLETE ===")
print("Press Ctrl+C to stop, Ctrl+D to reload")

# Keep running so we can enter REPL
while True:
    time.sleep(1)
