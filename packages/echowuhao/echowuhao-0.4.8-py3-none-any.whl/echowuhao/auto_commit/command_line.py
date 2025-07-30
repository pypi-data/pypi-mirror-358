# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///
"""
Auto-commit script that generates commit messages using AI
Based on: https://github.com/zhufengme/GPTCommit/blob/main/gptcommit.sh
"""
import os
import subprocess
import requests

# Configuration
OPENAI_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
LLM_URL = "https://api.deepseek.com/v1/chat/completions"
HTTP_PROXY = os.getenv('HTTPS_PROXY', '')

def run_git_command(args, cwd=None, return_output=True):
    """Run git command and return output or success status"""
    try:
        result = subprocess.check_output(['git'] + args, text=True, cwd=cwd or os.getcwd())
        return result if return_output else True
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return "" if return_output else False

def get_changes(diff_type):
    """Get changes for given diff type (working or staged)"""
    return {
        'summary': run_git_command(['diff', '--stat'] + diff_type),
        'files': run_git_command(['diff', '--name-only'] + diff_type),
        'full': run_git_command(['diff'] + diff_type)
    }

def truncate_diff(diff, max_length=10000):
    """Intelligently truncate diff while preserving important information"""
    if len(diff) <= max_length:
        return diff
    
    lines = diff.split('\n')
    headers, context = [], []
    
    # Separate headers from context
    for line in lines:
        if any(line.startswith(prefix) for prefix in ['diff --git', '---', '+++', '@@', '+', '-']):
            headers.append(line)
        else:
            context.append(line)
    
    # Add all headers first, then context if space allows
    result = headers + context[:max_length//100]  # Rough estimate for context lines
    truncated = '\n'.join(result)
    
    if len(truncated) > max_length:
        truncated = truncated[:max_length-50] + "\n... (truncated)"
    
    print(f"Diff truncated from {len(diff)} to {len(truncated)} characters")
    return truncated

def generate_commit_message(content, changed_files=""):
    """Generate commit message using AI API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{
            "role": "user",
            "content": f"Write a concise commit message in plain text:\n\n{content}\n\nCommit message:"
        }],
        "max_tokens": 100,
        "temperature": 0.7,
    }
    
    proxies = {"https": HTTP_PROXY} if HTTP_PROXY else {}
    
    try:
        response = requests.post(LLM_URL, headers=headers, proxies=proxies, 
                               json=payload, timeout=20)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        print(f"API call failed: {e}")
        # Fallback to file-based commit message
        if changed_files:
            files = [f.strip() for f in changed_files.split('\n') if f.strip()]
            if files:
                file_list = ', '.join(files[:3])
                return f"Update {file_list}{'...' if len(files) > 3 else ''}"
        return "Update files"

def commit_and_push(commit_message):
    """Execute git add, commit, and push"""
    commands = [
        (['add', '.', '-A'], "Adding changes"),
        (['commit', '-m', commit_message], "Committing changes"),
        (['push'], "Pushing changes")
    ]
    
    for args, description in commands:
        print(f"{description}...")
        if not run_git_command(args, return_output=False):
            print(f"Failed to {description.lower()}")
            return False
    return True

def main():
    """Main execution flow"""
    print("Checking repository status...")
    if not run_git_command(['status'], return_output=False):
        return
    
    # Get all changes
    working = get_changes([])
    staged = get_changes(['--cached'])
    
    # Combine changes
    all_files = working['files'] + staged['files']
    all_summary = working['summary'] + staged['summary']
    all_diff = working['full'] + staged['full']
    
    if not all_diff.strip():
        print("No changes detected.")
        return
    
    # Prepare content for commit message generation
    if all_summary.strip():
        content = f"Changed files summary:\n{all_summary}\n\nChanged files:\n{all_files}"
    else:
        content = truncate_diff(all_diff)
    
    # Generate commit message
    commit_message = generate_commit_message(content, all_files)
    print(f"Generated commit message: {commit_message}")
    
    # Execute git operations
    if commit_and_push(commit_message):
        print("Successfully committed and pushed changes!")
    else:
        print("Failed to complete git operations.")

if __name__ == "__main__":
    main()