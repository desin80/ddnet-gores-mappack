#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


DIFFICULTIES = ("easy", "main", "hard", "insane", "extreme", "mod", "solo")
DISPLAY_NAMES = {
    "easy": "Easy",
    "main": "Main",
    "hard": "Hard",
    "insane": "Insane",
    "extreme": "Extreme",
    "mod": "Mod",
    "solo": "Solo",
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(root: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    maplist_names: dict[str, str] = {}
    counts: Counter[str] = Counter()

    maps_dir = root / "maps"
    maplists_dir = root / "maplists"
    metadata_dir = root / "metadata"

    for difficulty in DIFFICULTIES:
        if not (maps_dir / difficulty).is_dir():
            fail(errors, f"missing maps/{difficulty}/")

    for path in sorted(maps_dir.glob("*.map")):
        fail(errors, f"flat map is not allowed: {path.relative_to(root)}")

    for difficulty in DIFFICULTIES:
        maplist_path = maplists_dir / f"{difficulty}.json"
        if not maplist_path.exists():
            fail(errors, f"missing {maplist_path.relative_to(root)}")
            continue
        data = load_json(maplist_path)
        if not isinstance(data, list):
            fail(errors, f"{maplist_path.relative_to(root)} must be a JSON list")
            continue
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                fail(errors, f"{maplist_path.relative_to(root)}[{index}] must be an object")
                continue
            name = item.get("name")
            if not isinstance(name, str) or not name:
                fail(errors, f"{maplist_path.relative_to(root)}[{index}] has invalid name")
                continue
            if "/" in name or "\\" in name:
                fail(errors, f"{maplist_path.relative_to(root)} contains path-like map name: {name}")
            previous = maplist_names.get(name)
            if previous is not None:
                fail(errors, f"map {name!r} is listed in both {previous} and {difficulty}")
            maplist_names[name] = difficulty
            counts[difficulty] += 1
            expected_path = maps_dir / difficulty / f"{name}.map"
            if not expected_path.exists():
                fail(errors, f"missing map for {difficulty}/{name}: {expected_path.relative_to(root)}")

    for path in sorted(maps_dir.rglob("*.map")):
        rel = path.relative_to(maps_dir)
        if len(rel.parts) != 2:
            fail(errors, f"map must be exactly one difficulty below maps/: {path.relative_to(root)}")
            continue
        difficulty, filename = rel.parts
        if difficulty not in DIFFICULTIES:
            fail(errors, f"unknown difficulty directory: {path.relative_to(root)}")
            continue
        name = path.stem
        expected_difficulty = maplist_names.get(name)
        if expected_difficulty is None:
            fail(errors, f"map is not present in any maplist: {path.relative_to(root)}")
        elif expected_difficulty != difficulty:
            fail(errors, f"map {name!r} is in maps/{difficulty}/ but maplist says {expected_difficulty}")

    stats_path = metadata_dir / "stats.json"
    if stats_path.exists():
        stats = load_json(stats_path)
        if isinstance(stats, dict):
            by_difficulty = stats.get("by_difficulty", {})
            total = stats.get("total_maps")
            if total != sum(counts.values()):
                fail(errors, f"metadata/stats.json total_maps={total!r}, expected {sum(counts.values())}")
            if isinstance(by_difficulty, dict):
                for difficulty, display_name in DISPLAY_NAMES.items():
                    expected = counts[difficulty]
                    actual = by_difficulty.get(display_name)
                    if actual != expected:
                        fail(errors, f"metadata/stats.json {display_name}={actual!r}, expected {expected}")
            else:
                fail(errors, "metadata/stats.json by_difficulty must be an object")
        else:
            fail(errors, "metadata/stats.json must be an object")
    else:
        fail(errors, "missing metadata/stats.json")

    return errors, dict(counts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DDNet gores mappack difficulty layout.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    root = args.root.resolve()
    errors, counts = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"validation failed: {len(errors)} errors")
        return 1

    total = sum(counts.values())
    print(f"validation ok: {total} maps")
    for difficulty in DIFFICULTIES:
        print(f"{difficulty}: {counts.get(difficulty, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
