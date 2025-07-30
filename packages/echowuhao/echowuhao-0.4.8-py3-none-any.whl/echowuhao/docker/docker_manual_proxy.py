#!/usr/bin/env python3
"""
Docker Manual Proxy Script

This script helps you pull, tag, and push Docker images to a local proxy registry.
It automates the process of making Docker images available in your local registry.
"""

import subprocess
import sys
import re
from typing import Optional, Tuple


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
    
    return result


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value."""
    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def parse_image_name(image_name: str) -> Tuple[str, str]:
    """Parse image name to extract repository and tag."""
    # Handle different formats: image, image:tag, repo/image, repo/image:tag
    if ':' in image_name:
        parts = image_name.rsplit(':', 1)
        repo = parts[0]
        tag = parts[1]
    else:
        repo = image_name
        tag = 'latest'
    
    return repo, tag


def check_image_exists(image_name: str) -> bool:
    """Check if a Docker image exists locally."""
    try:
        result = run_command(f"docker images {image_name} --format '{{{{.Repository}}}}:{{{{.Tag}}}}'", check=False)
        return bool(result.stdout.strip())
    except:
        return False


def main():
    """Main function to handle Docker image operations."""
    print("🐳 Docker Manual Proxy Script")
    print("=" * 40)
    
    # Get local registry address
    local_registry = get_user_input("Enter local registry address", "192.168.0.100:5555")
    
    # Get source image name
    source_image = get_user_input("Enter Docker image name (e.g., golang:1.23-alpine, alpine:latest)")
    
    if not source_image:
        print("❌ No image name provided. Exiting.")
        sys.exit(1)
    
    # Parse image name
    repo, tag = parse_image_name(source_image)
    print(f"📦 Repository: {repo}")
    print(f"🏷️  Tag: {tag}")
    
    # Check if image exists locally
    if not check_image_exists(source_image):
        print(f"⚠️  Image {source_image} not found locally. Pulling...")
        try:
            run_command(f"docker pull {source_image}")
            print(f"✅ Successfully pulled {source_image}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to pull {source_image}: {e}")
            sys.exit(1)
    else:
        print(f"✅ Image {source_image} found locally")
    
    # Create target image name
    target_image = f"{local_registry}/{repo}:{tag}"
    print(f"🎯 Target image: {target_image}")
    
    # Tag the image
    print("🏷️  Tagging image...")
    try:
        run_command(f"docker tag {source_image} {target_image}")
        print(f"✅ Successfully tagged {source_image} as {target_image}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to tag image: {e}")
        sys.exit(1)
    
    # Push the image
    print("📤 Pushing image to local registry...")
    try:
        run_command(f"docker push {target_image}")
        print(f"✅ Successfully pushed {target_image} to local registry")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push image: {e}")
        sys.exit(1)
    
    print("\n🎉 Operation completed successfully!")
    print(f"Image {target_image} is now available in your local registry.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
