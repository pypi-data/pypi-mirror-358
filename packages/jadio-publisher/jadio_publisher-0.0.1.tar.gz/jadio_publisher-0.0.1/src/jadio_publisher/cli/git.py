import sys
import subprocess

def run_git_command(args_list):
    try:
        result = subprocess.run(["git"] + args_list, check=True, capture_output=True, text=True)
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed:\n{e.stderr.strip()}")
        sys.exit(1)

def git_cli(args):
    if not args:
        print("⚠️  No git subcommand provided. Try -status, -add, -commit, -push, -pull, -repo, -log")
        return

    if "-add" in args:
        print("🗂️  Running: git add .")
        run_git_command(["add", "."])
        print("✔️  Staged all changes.")

    elif "-commit" in args:
        try:
            message_index = args.index("-commit") + 1
            commit_message = args[message_index]
        except IndexError:
            print("❌ Please provide a commit message after -commit.")
            sys.exit(1)

        print(f"📝 Running: git commit -m \"{commit_message}\"")
        run_git_command(["commit", "-m", commit_message])
        print(f"✔️  Committed with message: \"{commit_message}\"")

    elif "-push" in args:
        print("🚀 Running: git push")
        run_git_command(["push"])
        print("✔️  Pushed to remote.")

    elif "-pull" in args:
        print("⬇️  Running: git pull")
        run_git_command(["pull"])
        print("✔️  Pulled latest changes.")

    elif "-repo" in args:
        print("🔗 Running: git remote get-url origin")
        run_git_command(["remote", "get-url", "origin"])

    elif "-status" in args:
        print("📦 Running: git status")
        run_git_command(["status"])

    elif "-log" in args:
        print("🕑 Running: git log --oneline -n 10")
        run_git_command(["log", "--oneline", "-n", "10"])

    else:
        print(f"❌ Unknown git subcommand: {' '.join(args)}")
