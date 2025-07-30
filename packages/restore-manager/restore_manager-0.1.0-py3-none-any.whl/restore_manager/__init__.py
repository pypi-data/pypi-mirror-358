#!/usr/bin/env python3

import argparse
import os
import datetime
import uuid
import base64
import sys

try:
    import xattr
except ImportError:
    print("Error: The 'xattr' library is not installed.")
    print("Please install it using: pip install xattr")
    sys.exit(1)

UUID_ATTRIBUTE = "com.apple.metadata:kMDItemUUID"
RESTORE_FILE_PREFIX = ".restore-"

def get_file_uuid(filepath):
    try:
        file_uuid = xattr.getxattr(filepath, UUID_ATTRIBUTE).decode('utf-8')
        return file_uuid
    except (IOError, KeyError):
        # If no UUID, generate one and set it
        new_uuid = str(uuid.uuid4())
        xattr.setxattr(filepath, UUID_ATTRIBUTE, new_uuid.encode('utf-8'))
        return new_uuid

def get_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return base64.b64encode(f.read().encode('utf-8')).decode('utf-8')
    except Exception:
        return None # Not a text file or cannot be read

def create_snapshot(root_path, exclude_all=False, exclude_specific=None, include_specific=None):
    print("Starting snapshot...")
    snapshot_data = []
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_filename = f"{RESTORE_FILE_PREFIX}{current_time}.md"
    snapshot_filepath = os.path.join(root_path, snapshot_filename)

    if exclude_specific is None:
        exclude_specific = []
    if include_specific is None:
        include_specific = []

    # Convert relative paths to absolute for easier comparison
    exclude_specific_abs = [os.path.abspath(os.path.join(root_path, p)) for p in exclude_specific]
    include_specific_abs = [os.path.abspath(os.path.join(root_path, p)) for p in include_specific]

    file_count = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Exclude the snapshot file itself
        if snapshot_filename in filenames:
            filenames.remove(snapshot_filename)

        # Handle directory exclusions/inclusions
        if exclude_all and os.path.abspath(dirpath) != os.path.abspath(root_path):
            dirnames[:] = [] # Don't recurse into subdirectories
            continue

        # Filter dirnames for specific exclusions/inclusions
        dirs_to_remove = []
        for d in dirnames:
            abs_d_path = os.path.abspath(os.path.join(dirpath, d))
            if abs_d_path.startswith(os.path.abspath(root_path)): # Ensure path is within root
                if any(abs_d_path == ex_path or abs_d_path.startswith(ex_path + os.sep) for ex_path in exclude_specific_abs):
                    dirs_to_remove.append(d)
                elif include_specific_abs and not any(abs_d_path == inc_path or abs_d_path.startswith(inc_path + os.sep) for inc_path in include_specific_abs) and os.path.abspath(dirpath) != os.path.abspath(root_path):
                    # If include_specific is set, and this dir is not explicitly included (and not root), exclude it
                    dirs_to_remove.append(d)

        for d in dirs_to_remove:
            dirnames.remove(d)

        print(f"Scanning: {os.path.relpath(dirpath, root_path)}")

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            abs_file_path = os.path.abspath(file_path)

            # Skip if it's a restore file
            if filename.startswith(RESTORE_FILE_PREFIX):
                continue

            # Apply include/exclude logic for files
            if exclude_all and os.path.abspath(dirpath) != os.path.abspath(root_path):
                continue # Already handled by dirnames[:] = [] but good for safety

            if any(abs_file_path.startswith(ex_path + os.sep) or abs_file_path == ex_path for ex_path in exclude_specific_abs):
                continue

            if include_specific_abs:
                # If include_specific is set, only include files within those paths or in the root
                if not any(abs_file_path.startswith(inc_path + os.sep) or abs_file_path == inc_path for inc_path in include_specific_abs) and os.path.abspath(dirpath) != os.path.abspath(root_path):
                    continue

            file_uuid = get_file_uuid(file_path)
            file_size = os.path.getsize(file_path)
            file_content = get_file_content(file_path) # Only for text-editable files

            relative_path = os.path.relpath(file_path, root_path)
            snapshot_data.append({
                "uuid": file_uuid,
                "path": relative_path,
                "size": file_size,
                "content": file_content
            })
            file_count += 1

    with open(snapshot_filepath, 'w', encoding='utf-8') as f:
        for item in snapshot_data:
            f.write(f"{item['uuid']}	{item['path']}	{item['size']}	{item['content'] or ''}
")

    print(f"
Snapshot complete. {file_count} files backed up.")
    print(f"Restore file created: {snapshot_filename}")

def restore_from_snapshot(root_path):
    print("Starting restore...")
    available_snapshots = [f for f in os.listdir(root_path) if f.startswith(RESTORE_FILE_PREFIX) and f.endswith(".md")]

    if not available_snapshots:
        print("No restore files found in the current directory. Aborting.")
        return

    if len(available_snapshots) > 1:
        print("Multiple restore files found:")
        for i, snapshot in enumerate(available_snapshots):
            print(f"  {i + 1}. {snapshot}")
        try:
            choice = int(input("Enter the number of the snapshot to restore from: ")) - 1
            restore_filename = available_snapshots[choice]
        except (ValueError, IndexError):
            print("Invalid selection. Aborting.")
            return
    else:
        restore_filename = available_snapshots[0]

    print(f"Using snapshot: {restore_filename}")
    restore_filepath = os.path.join(root_path, restore_filename)

    # --- Parse Restore File ---
    snapshots = []
    with open(restore_filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split('	')
            if len(parts) == 4:
                snapshots.append({
                    "uuid": parts[0],
                    "path": parts[1],
                    "size": int(parts[2]),
                    "content": parts[3] or None
                })

    # --- Map Current State ---
    print("Mapping current file state...")
    uuid_to_current_path = {}
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.startswith(RESTORE_FILE_PREFIX):
                continue
            file_path = os.path.join(dirpath, filename)
            try:
                file_uuid = xattr.getxattr(file_path, UUID_ATTRIBUTE).decode('utf-8')
                uuid_to_current_path[file_uuid] = file_path
            except (IOError, KeyError):
                continue

    # --- Execute Restore Plan ---
    restored_count = 0
    created_count = 0
    error_count = 0

    for snap in snapshots:
        target_path = os.path.abspath(os.path.join(root_path, snap['path']))

        if snap['uuid'] in uuid_to_current_path:
            # File exists, move it if necessary
            current_path = uuid_to_current_path[snap['uuid']]
            if current_path != target_path:
                try:
                    print(f"Moving: {os.path.relpath(current_path, root_path)} -> {os.path.relpath(target_path, root_path)}")
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    os.rename(current_path, target_path)
                    restored_count += 1
                except OSError as e:
                    print(f"Error moving {snap['path']}: {e}")
                    error_count += 1
            else:
                # Already in the correct place
                pass
        else:
            # File was deleted, restore from content
            if snap['content']:
                try:
                    print(f"Creating: {snap['path']}")
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    content = base64.b64decode(snap['content']).decode('utf-8')
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    # Re-apply UUID
                    xattr.setxattr(target_path, UUID_ATTRIBUTE, snap['uuid'].encode('utf-8'))
                    created_count += 1
                except Exception as e:
                    print(f"Error creating {snap['path']}: {e}")
                    error_count += 1
            else:
                print(f"Warning: Cannot restore deleted file {snap['path']}. No content was saved (likely a binary file).")
                error_count += 1

    print("
Restore complete.")
    print(f"  - Files moved/verified: {restored_count}")
    print(f"  - Files created from backup: {created_count}")
    print(f"  - Errors: {error_count}")

def run_interactive_mode():
    """Runs the script in a conversational, interactive mode."""
    print("Hi, I'm Restore Manager!")

    while True:
        action = input("Do you want to (b)ackup or (r)estore? (or 'q' to quit) ").lower()
        if action in ['b', 'backup']:
            print("OK, great! Let's back up the current directory.")
            exclude_specific = None
            if input("Do you want to exclude any specific subfolders? (y/n) ").lower() == 'y':
                paths_str = input("Please enter the paths to exclude, separated by spaces: ")
                exclude_specific = paths_str.split()
            create_snapshot(root_path=".", exclude_specific=exclude_specific)
            break
        elif action in ['r', 'restore']:
            restore_from_snapshot(root_path=".")
            break
        elif action in ['q', 'quit']:
            print("Goodbye!")
            break
        else:
            print("Sorry, I didn't understand that. Please type 'b', 'r', or 'q'.")

# --- Main Execution ---

def main():
    # If run without arguments, start interactive mode
    if len(sys.argv) == 1:
        run_interactive_mode()
        return

    parser = argparse.ArgumentParser(
        description="A command-line tool to snapshot and restore a folder's state.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Backup Command ---
    parser_backup = subparsers.add_parser("backup", help="Create a new snapshot of the current directory.")
    group = parser_backup.add_mutually_exclusive_group()
    group.add_argument(
        "-xf", "--exclude-all-subfolders",
        action="store_true",
        help="Exclude all subfolders. Only files in the root directory will be backed up."
    )
    group.add_argument(
        "-xfs", "--exclude-specific-subfolders",
        nargs='+',
        metavar="PATH",
        help="Exclude specific subfolders from the backup."
    )
    group.add_argument(
        "-s", "--include-specific-subfolders",
        nargs='+',
        metavar="PATH",
        help="Include only specific subfolders in the backup (root files are always included)."
    )

    # --- Restore Command ---
    parser_restore = subparsers.add_parser("restore", help="Restore the directory from a previously created snapshot.")

    args = parser.parse_args()

    if args.command == "backup":
        create_snapshot(
            root_path=".",
            exclude_all=args.exclude_all_subfolders,
            exclude_specific=args.exclude_specific_subfolders,
            include_specific=args.include_specific_subfolders
        )
    elif args.command == "restore":
        restore_from_snapshot(root_path=".")

if __name__ == "__main__":
    main()
