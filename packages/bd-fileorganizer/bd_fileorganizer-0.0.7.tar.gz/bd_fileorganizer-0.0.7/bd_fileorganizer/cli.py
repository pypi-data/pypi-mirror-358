import argparse
from bd_fileorganizer.organizer import organize_folder


def main():
    parser = argparse.ArgumentParser(description="Organize your messy folder by file types.")
    parser.add_argument("path", help="Path to folder to organize")
    parser.add_argument("--dry", action="store_true", help="Dry run - show what will be moved")

    args = parser.parse_args()
    actions = organize_folder(args.path, dry_run=args.dry)

    if not actions:
        print("No files found.")
    else:
        for src, dst in actions:
            print(f"{'[DRY] ' if args.dry else ''}Move {src.name} → {dst.parent.name}/")

if __name__ == "__main__":
    main()
