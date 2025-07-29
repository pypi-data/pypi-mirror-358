def show_help(args):
    print("""
✅ JPUB - Jadio Publisher CLI

Available commands:

🔹 jpub init
    ➜ Initialize jpubconfig.json in jadio_config/

🔹 jpub bump
    ➜ Show current version, prompt for new version, update __init__.py and jpubconfig.json

🔹 jpub show
    ➜ Show current version from __init__.py and last_built_version from jpubconfig.json

🔹 jpub build
    ➜ Clean old builds, ensure version bumped, run python -m build

🔹 jpub pypi
    ➜ Upload existing dist/ to PyPI using Twine

🔹 jpub go
    ➜ Full release: bump ➜ build ➜ publish in one command

🔹 jpub git -add
    ➜ git add .

🔹 jpub git -commit "message"
    ➜ git commit with a message

🔹 jpub git -push
    ➜ git push to remote

🔹 jpub git -pull
    ➜ git pull from remote

🔹 jpub git -repo
    ➜ Show remote repo URL

🔹 jpub git -status
    ➜ Show git status

🔹 jpub git -log
    ➜ Show last 10 commits

🟢 Example usage:
    jpub bump
    jpub build
    jpub pypi
    jpub go
    jpub git -commit "Initial commit"

✅ Happy publishing!
""")
