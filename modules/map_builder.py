"""
map_builder.py — Build the dungeon map from repo data.

build_map(repo_data) → game dict | raises ValueError

Constants:
  MIN_FILES_FOR_ROOM = 3   (PRD v3.0)
  MAX_ROOMS = 12           (Spec v5.1 / API Spec Rev 4)

Rooms are built from real folders.
Boss is the room containing the largest file.
Keys come from dependencies.
Monsters come from open issues (or guardian files if no issues).
Connectivity check verifies all rooms and boss are reachable from start.
"""

from __future__ import annotations
import os
import re

MIN_FILES_FOR_ROOM = 3
MAX_ROOMS = 12


def _slugify(name: str) -> str:
    """Turn folder path into a clean room ID slug."""
    clean = re.sub(r"[^a-zA-Z0-9_\-]", "-", name).strip("-")
    return f"room-{clean}" if clean else "readme-hall"


def _parent_folder(folder_path: str) -> str:
    """Return parent folder path, or '' if top-level."""
    if "/" in folder_path:
        return folder_path.rsplit("/", 1)[0]
    return ""


def build_map(repo_data: dict) -> dict:
    """
    Build deterministic game map from repo_data.
    repo_data: {
      "owner": str, "repo": str, "language": str,
      "description": str, "readme": str, "tree": list[dict],
      "issues": list[dict], "dependencies": list[str] | None,
      "dep_filename": str | None, "warnings": list[str]
    }
    Raises ValueError if map cannot be connected or lacks rooms.
    """
    tree = repo_data.get("tree", [])
    if not tree:
        raise ValueError("Cannot build map: empty tree")

    files = [item for item in tree if item.get("type") == "blob"]
    if not files:
        raise ValueError("Cannot build map: no files in tree")

    # 1. Group files by folder path
    folder_files: dict[str, list[dict]] = {}
    for f in files:
        path = f.get("path", "")
        folder = path.rsplit("/", 1)[0] if "/" in path else ""
        folder_files.setdefault(folder, []).append(f)

    # 2. Determine which folders get their own rooms
    # Root folder ("") is always the start room ("readme-hall")
    rooms_by_folder: dict[str, str] = {"": "readme-hall"}
    folder_mapping: dict[str, str] = {"": ""}  # folder -> room's assigned folder

    for folder, flist in folder_files.items():
        if folder == "":
            continue
        if len(flist) >= MIN_FILES_FOR_ROOM:
            room_id = _slugify(folder)
            rooms_by_folder[folder] = room_id
            folder_mapping[folder] = folder
        else:
            # Merge small folder into parent folder
            parent = _parent_folder(folder)
            while parent != "" and parent not in rooms_by_folder:
                parent = _parent_folder(parent)
            folder_mapping[folder] = parent

    # Re-assign files to their merged room folder
    merged_folder_files: dict[str, list[dict]] = {}
    for folder, flist in folder_files.items():
        assigned = folder_mapping.get(folder, "")
        merged_folder_files.setdefault(assigned, []).extend(flist)

    # 3. Cap rooms at MAX_ROOMS (12) by merging smallest non-root rooms into parent
    while len(rooms_by_folder) > MAX_ROOMS:
        # Find smallest non-root room
        non_root_folders = [f for f in rooms_by_folder.keys() if f != ""]
        if not non_root_folders:
            break
        smallest = min(
            non_root_folders, key=lambda f: len(merged_folder_files.get(f, []))
        )
        parent = _parent_folder(smallest)
        # Target folder for merge
        target = parent if parent in rooms_by_folder else ""

        # Merge smallest files into target
        merged_folder_files.setdefault(target, []).extend(
            merged_folder_files.pop(smallest, [])
        )
        del rooms_by_folder[smallest]
        # Update mappings
        for f, mapped in list(folder_mapping.items()):
            if mapped == smallest:
                folder_mapping[f] = target

    # 4. Create room dicts and build bidirectional exits
    room_nodes: dict[str, dict] = {}
    folder_to_room: dict[str, str] = {}

    for folder, room_id in rooms_by_folder.items():
        folder_to_room[folder] = room_id
        room_nodes[room_id] = {
            "folder": folder,
            "exits": set(),
            "keys": [],
            "monsters": [],
            "files": [item["path"] for item in merged_folder_files.get(folder, [])],
        }

    # Connect child room to nearest ancestor room
    for folder, room_id in rooms_by_folder.items():
        if folder == "":
            continue
        parent = _parent_folder(folder)
        while parent != "" and parent not in rooms_by_folder:
            parent = _parent_folder(parent)
        parent_room_id = rooms_by_folder.get(parent, "readme-hall")

        # Bidirectional link
        room_nodes[room_id]["exits"].add(parent_room_id)
        room_nodes[parent_room_id]["exits"].add(room_id)

    # 5. Determine Boss Room (room holding the largest file by size)
    largest_file = max(files, key=lambda f: f.get("size", 0) or 0)
    largest_file_path = largest_file.get("path", "")
    largest_file_folder = (
        largest_file_path.rsplit("/", 1)[0] if "/" in largest_file_path else ""
    )
    boss_assigned_folder = folder_mapping.get(largest_file_folder, "")
    boss_room_id = rooms_by_folder.get(boss_assigned_folder, "readme-hall")

    # If only 1 room exists, fallback: keep it or split
    if len(room_nodes) < 2 and len(folder_files) > 1:
        # Force top folders to be rooms if available
        for f in folder_files.keys():
            if f != "" and len(room_nodes) < MAX_ROOMS:
                rid = _slugify(f)
                rooms_by_folder[f] = rid
                room_nodes[rid] = {
                    "folder": f,
                    "exits": {"readme-hall"},
                    "keys": [],
                    "monsters": [],
                    "files": [item["path"] for item in folder_files[f]],
                }
                room_nodes["readme-hall"]["exits"].add(rid)

    # 6. Place Keys (from dependencies)
    dependencies = repo_data.get("dependencies") or []
    dep_filename = repo_data.get("dep_filename") or "requirements.txt"
    keys_dict: dict[str, dict] = {}

    available_rooms = [rid for rid in room_nodes.keys() if rid != "readme-hall"]
    if not available_rooms:
        available_rooms = list(room_nodes.keys())

    for idx, dep in enumerate(dependencies):
        keys_dict[dep] = {"source": dep_filename}
        target_room = available_rooms[idx % len(available_rooms)]
        room_nodes[target_room]["keys"].append(dep)

    # 7. Place Monsters (Issues or Guardian Files)
    issues = repo_data.get("issues") or []
    monsters_dict: dict[str, dict] = {}

    if issues:
        # Match issues to rooms via heuristic scoring
        for idx, issue in enumerate(issues):
            monster_id = f"issue-{issue.get('number', idx + 1)}"
            title = issue.get("title", "")
            body = issue.get("body", "")
            labels = issue.get("labels", [])

            best_room = "readme-hall"
            best_score = -1
            best_reason = "fallback"

            for rid, rdata in room_nodes.items():
                folder = rdata["folder"]
                score = 0
                reason = "fallback"

                # Strong: issue text mentions file in this room
                for fpath in rdata["files"]:
                    fname = os.path.basename(fpath)
                    if fpath in body or fpath in title or fname in body:
                        score = 3
                        reason = "file mention"
                        break

                # Medium: issue label matches folder name
                if score < 3 and folder:
                    folder_name = os.path.basename(folder).lower()
                    for label in labels:
                        if label.lower() == folder_name:
                            score = 2
                            reason = "label"
                            break

                # Weak: keyword overlap with folder
                if score < 2 and folder:
                    folder_name = os.path.basename(folder).lower()
                    if folder_name in title.lower() or folder_name in body.lower():
                        score = 1
                        reason = "keyword"

                if score > best_score:
                    best_score = score
                    best_room = rid
                    best_reason = reason

            # If no score, place in room with fewest monsters
            if best_score <= 0:
                best_room = min(room_nodes.keys(), key=lambda r: len(room_nodes[r]["monsters"]))
                best_reason = "fallback"

            monsters_dict[monster_id] = {
                "kind": "issue",
                "title": title,
                "url": issue.get("url"),
                "placed_by": best_reason,
                "file": None,
            }
            room_nodes[best_room]["monsters"].append(monster_id)

    else:
        # NO ISSUES -> Guardian Monsters from largest files (excluding boss file)
        guardian_candidates = [
            f for f in files if f.get("path") != largest_file_path
        ]
        guardian_candidates.sort(key=lambda f: f.get("size", 0) or 0, reverse=True)

        # Pick up to 4 guardian files
        guardians = guardian_candidates[:4]
        for idx, gfile in enumerate(guardians):
            monster_id = f"guardian-{idx + 1}"
            fpath = gfile["path"]

            # Place in the room that holds this guardian file
            gfolder = fpath.rsplit("/", 1)[0] if "/" in fpath else ""
            assigned_gfolder = folder_mapping.get(gfolder, "")
            g_room_id = rooms_by_folder.get(assigned_gfolder, "readme-hall")

            monsters_dict[monster_id] = {
                "kind": "guardian",
                "title": f"Guardian of {fpath}",
                "url": None,
                "placed_by": "fallback",
                "file": fpath,
            }
            room_nodes[g_room_id]["monsters"].append(monster_id)

    # Convert room exits sets to sorted lists
    cleaned_rooms = {}
    for rid, rdata in room_nodes.items():
        cleaned_rooms[rid] = {
            "folder": rdata["folder"],
            "exits": sorted(list(rdata["exits"])),
            "keys": rdata["keys"],
            "monsters": rdata["monsters"],
        }

    game_map = {
        "repo": f"{repo_data.get('owner', '')}/{repo_data.get('repo', '')}".strip("/"),
        "language": repo_data.get("language", "Unknown"),
        # GitHub's repository description is the user-facing explanation of
        # purpose. Keep it separate from internal paths used to build the map.
        "description": repo_data.get("description", ""),
        "warnings": repo_data.get("warnings", []),
        "start": "readme-hall",
        "boss": boss_room_id,
        "rooms": cleaned_rooms,
        "monsters": monsters_dict,
        "keys": keys_dict,
        "narration": None,
        "quiz": None,
    }

    # 8. Connectivity Check
    seen = set()
    todo = [game_map["start"]]
    while todo:
        curr = todo.pop()
        if curr in seen:
            continue
        seen.add(curr)
        todo.extend(cleaned_rooms[curr]["exits"])

    if seen != set(cleaned_rooms.keys()):
        raise ValueError("Map connectivity check failed: unreachable rooms exist")

    if boss_room_id not in seen:
        raise ValueError("Map connectivity check failed: boss room unreachable")

    return game_map
