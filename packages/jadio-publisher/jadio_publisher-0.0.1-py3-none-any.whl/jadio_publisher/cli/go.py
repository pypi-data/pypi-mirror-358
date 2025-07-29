import sys
from . import bump, build, pypi

def release_flow(args):
    print("\n🚀 Starting FULL RELEASE flow...\n")

    # 1️⃣ Bump
    print("🔹 Step 1: Bump version")
    bump.bump_version(args)

    # 2️⃣ Build
    print("\n🔹 Step 2: Build package")
    build.build_package(args)

    # 3️⃣ Publish
    print("\n🔹 Step 3: Publish to PyPI")
    pypi.upload_package(args)

    print("\n✅ FULL RELEASE COMPLETE! Your package is live on PyPI.\n")
