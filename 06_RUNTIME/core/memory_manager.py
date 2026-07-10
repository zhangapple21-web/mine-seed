#!/usr/bin/env python3
import os, json
from pathlib import Path
from datetime import datetime


class MemoryManager:
    def __init__(self, mem_dir=None):
        if mem_dir is None:
            mem_dir = Path(__file__).parent.parent.parent / "02_MEMORY"
        self.mem_dir = Path(mem_dir)
        self.mem_dir.mkdir(parents=True, exist_ok=True)

    def get_memory(self, category, key=None):
        cat_dir = self.mem_dir / category
        if not cat_dir.exists():
            return None

        if key:
            file_path = cat_dir / f"{key}.json"
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    return json.load(f)
            return None

        memories = {}
        for f in cat_dir.iterdir():
            if f.suffix == ".json":
                try:
                    with open(f, encoding="utf-8") as fp:
                        memories[f.stem] = json.load(fp)
                except:
                    pass
        return memories

    def save_memory(self, category, key, data):
        cat_dir = self.mem_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        file_path = cat_dir / f"{key}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(file_path)

    def list_categories(self):
        categories = []
        for item in self.mem_dir.iterdir():
            if item.is_dir():
                categories.append(item.name)
        return sorted(categories)

    def clean_old(self, days=30):
        import time
        cutoff = time.time() - days * 24 * 60 * 60
        removed = 0

        for f in self.mem_dir.rglob("*.json"):
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
                    removed += 1
            except:
                pass

        return {"removed": removed}


def main():
    mm = MemoryManager()
    categories = mm.list_categories()
    print(f"Memory categories: {categories}")

    test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
    saved = mm.save_memory("test", "test_key", test_data)
    print(f"Saved to: {saved}")

    loaded = mm.get_memory("test", "test_key")
    print(f"Loaded: {loaded}")


if __name__ == "__main__":
    main()