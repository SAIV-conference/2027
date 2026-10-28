#!/usr/bin/env python3
"""Validate the website's people registry and committee assignments.

Checks _data/people.yml and _data/committees.yml against their JSON schemas,
then the cross-file rules the schemas cannot express: unique ids, committee
members that exist, alphabetical ordering, photo files that exist with the
expected format, and no orphaned photos.

Usage: python3 scripts/validate_data.py   (exit status 1 on any error)
"""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PEOPLE = ROOT / "_data" / "people.yml"
COMMITTEES = ROOT / "_data" / "committees.yml"
PHOTO_DIR = ROOT / "assets" / "images" / "people"
PHOTO_SIZE = (320, 320)
PHOTO_MAX_BYTES = 64 * 1024


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as f:
        return dates_as_strings(yaml.safe_load(f))


def dates_as_strings(value):
    # YAML parses 2026-10-28 as a date; the schemas expect ISO strings.
    if isinstance(value, list):
        return [dates_as_strings(v) for v in value]
    if isinstance(value, dict):
        return {k: dates_as_strings(v) for k, v in value.items()}
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


def schema_errors(data, schema_name: str, label: str) -> list[str]:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [
        f"{label}: {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    ]


def photo_errors(photo: str) -> list[str]:
    path = PHOTO_DIR / photo
    if not path.is_file():
        return [f"photo {photo}: file missing in {PHOTO_DIR.relative_to(ROOT)}"]
    errors = []
    if path.stat().st_size > PHOTO_MAX_BYTES:
        errors.append(f"photo {photo}: {path.stat().st_size} bytes exceeds {PHOTO_MAX_BYTES}")
    try:
        from PIL import Image
    except ImportError:
        return errors  # size/format check needs Pillow; CI installs it
    with Image.open(path) as image:
        if image.format != "WEBP" or image.size != PHOTO_SIZE:
            errors.append(f"photo {photo}: expected {PHOTO_SIZE[0]}x{PHOTO_SIZE[1]} WEBP, got {image.size[0]}x{image.size[1]} {image.format}")
    return errors


def main() -> int:
    people = load_yaml(PEOPLE)
    committees = load_yaml(COMMITTEES)

    errors = schema_errors(people, "people.schema.json", "people.yml")
    errors += schema_errors(committees, "committees.schema.json", "committees.yml")
    if errors:
        print("\n".join(errors))
        return 1

    by_id = {}
    for person in people:
        if person["id"] in by_id:
            errors.append(f"people.yml: duplicate id {person['id']}")
        by_id[person["id"]] = person
        if person["photo"]:
            if person["photo"] != f"{person['id']}.webp":
                errors.append(f"people.yml: {person['id']}: photo should be named {person['id']}.webp")
            if not person["photo_source"]:
                errors.append(f"people.yml: {person['id']}: photo without photo_source")
            errors += photo_errors(person["photo"])

    group_ids = set()
    referenced = set()
    for group in committees:
        if group["id"] in group_ids:
            errors.append(f"committees.yml: duplicate group id {group['id']}")
        group_ids.add(group["id"])
        members = [m["person"] for m in group["members"]]
        for person_id in members:
            if person_id not in by_id:
                errors.append(f"committees.yml: {group['id']}: unknown person {person_id}")
        if len(set(members)) != len(members):
            errors.append(f"committees.yml: {group['id']}: a person is listed twice")
        referenced.update(members)
        if group["order"] == "alphabetical" and all(p in by_id for p in members):
            keys = [by_id[p]["sort_name"].casefold() for p in members]
            if keys != sorted(keys):
                expected = sorted(members, key=lambda p: by_id[p]["sort_name"].casefold())
                errors.append(f"committees.yml: {group['id']}: not alphabetical; expected order {expected}")

    for person_id in sorted(set(by_id) - referenced):
        errors.append(f"people.yml: {person_id} is not in any committee (remove the record or assign it)")

    known_photos = {p["photo"] for p in people if p["photo"]}
    for path in sorted(PHOTO_DIR.glob("*")):
        if path.name not in known_photos:
            errors.append(f"{path.relative_to(ROOT)}: not referenced by any person")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(people)} people, {len(committees)} committees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
