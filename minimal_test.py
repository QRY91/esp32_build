import time

print("ESP32-S3 MINIMAL TEST START")
print("If you see this, Python is running!")

for i in range(20):
    print(f"Count: {i}")
    time.sleep(0.5)

print("Test complete - Python working!")

while True:
    print("Heartbeat...")
    time.sleep(2)
