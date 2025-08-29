import subprocess

# Define thresholds and splits
thresholds = [round(x, 1) for x in [i*0.1 for i in range(1, 10)]]

splits = [
    [2],        # train 12, AL 3456
    [2, 3],     # train 123, AL 456
    [2, 3, 4],  # train 1234, AL 56
    [2, 3, 4, 5]  # train 12345, AL 6
]

for split in splits:
    active_str = ",".join(map(str, split))
    for thr in thresholds:
        print(f"\n=== Running split {split} with threshold {thr} ===\n")
        subprocess.run([
            "python", "Active_learning.py",
            "--active", active_str,
            "--threshold", str(thr)
        ])
