"""Clean up _* inspection files in data/hardneg."""
from pathlib import Path
out_dir = Path('/home/maher/maher_ws/src/Recognition-of-Different-Colored-Cubes/data/hardneg')
removed = 0
for p in out_dir.glob('_*'):
    if p.is_file():
        p.unlink()
        removed += 1
print(f'removed {removed} inspection files')
