import os
import csv
from typing import List

class CategoryManager:
    def __init__(self, folder_path: str):
        # folder_path should be an absolute path (we will pass it from app.py)
        self.folder_path = folder_path

    def get_available_categories(self) -> List[str]:
        # If folder doesn't exist, return empty list instead of crashing Flask
        if not os.path.isdir(self.folder_path):
            return []

        files = os.listdir(self.folder_path)
        categories = [f[:-4] for f in files if f.lower().endswith(".csv")]
        categories.sort()
        return categories

    def get_words_from_category(self, category_name: str) -> List[str]:
        # Whitelist validation: only allow categories that exist in the folder
        available = set(self.get_available_categories())
        if category_name not in available:
            return []

        file_path = os.path.join(self.folder_path, f"{category_name}.csv")
        if not os.path.exists(file_path):
            return []

        words: List[str] = []

        try:
            # utf-8-sig handles Excel "BOM" files cleanly
            with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
                # Detect header style vs simple one-column file
                first_line = f.readline()
                f.seek(0)
                has_header = "answer" in first_line.lower()

                if has_header:
                    reader = csv.DictReader(f)
                    for row in reader:
                        val = (row.get("answer") or "").strip()
                        if val:
                            words.append(val)
                else:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and row[0].strip():
                            words.append(row[0].strip())

        except Exception as e:
            print(f"Error reading category '{category_name}' from {file_path}: {e}")
            return []

        # De-duplicate while preserving order
        seen = set()
        deduped = []
        for w in words:
            key = w.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(w)

        return deduped
