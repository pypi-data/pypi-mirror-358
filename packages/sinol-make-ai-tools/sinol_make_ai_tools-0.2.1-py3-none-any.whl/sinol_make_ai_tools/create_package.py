import subprocess
import os

def main(args):
    subprocess.run(["sm", "init", args.package_id, "-t", "https://git.staszic.waw.pl/top/template/default"])
    os.makedirs(args.package_id + "/in", exist_ok=True)
    os.makedirs(args.package_id + "/out", exist_ok=True)

    with open(args.package_id + "/description.txt", 'w') as description_file:
        description_file.write(f"Kod zadania: {args.package_id}.\n")

    with open(args.package_id + "/ai_file_blacklist.txt", 'w') as ai_blacklist_file:
        ai_blacklist_file.write("doc/spiral.cls\n")
        ai_blacklist_file.write("prog/oi.h\n")
    