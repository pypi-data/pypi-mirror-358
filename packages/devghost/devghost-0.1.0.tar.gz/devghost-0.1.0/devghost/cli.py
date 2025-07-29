import os
import click
import configparser
import subprocess
import requests

CONFIG_PATH = os.path.expanduser('~/.devghost')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

def save_config(github_token, gemini_api_key):
    config = configparser.ConfigParser()
    config['AUTH'] = {
        'github_token': github_token,
        'gemini_api_key': gemini_api_key
    }
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        return None
    config.read(CONFIG_PATH)
    return config['AUTH']

@click.group()
def cli():
    """DevGhost: Generate smart commit messages using AI and GitHub context."""
    pass

@cli.command()
def setup():
    """Setup your GitHub and Gemini API keys.\n\nFor GitHub, generate a Personal Access Token (classic) with 'repo' scope at https://github.com/settings/tokens (set expiration up to 1 year)."""
    github_token = click.prompt('Enter your GitHub Personal Access Token (classic, repo scope, 1 year expiry recommended)', hide_input=True)
    gemini_api_key = click.prompt('Enter your Gemini API Key', hide_input=True)
    save_config(github_token, gemini_api_key)
    click.echo('Configuration saved!')

@cli.command()
def suggest():
    """Suggest a commit message based on current git diff using Gemini AI."""
    config = load_config()
    if not config:
        click.echo('Please run `devghost setup` first.')
        return
    gemini_api_key = config.get('gemini_api_key')
    if not gemini_api_key:
        click.echo('Gemini API key not found. Please run `devghost setup` again.')
        return
    try:
        try:
            diff = subprocess.check_output(['git', 'diff', 'HEAD'], stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as e:
            output = e.output.decode('utf-8')
            if 'unknown revision or path not in the working tree' in output or 'ambiguous argument' in output:
                diff = subprocess.check_output(['git', 'diff'], stderr=subprocess.STDOUT).decode('utf-8')
                click.secho('No commits found. Suggesting initial commit message.', fg='yellow')
            else:
                click.echo('Error getting git diff:')
                click.echo(output)
                return
        if not diff.strip():
            click.echo('No changes detected in the working directory.')
            return
        max_diff_len = 4000
        if len(diff) > max_diff_len:
            diff = diff[:max_diff_len] + '\n...[diff truncated]'
        click.echo('Generating commit message with Gemini...')
        prompt = f"""
You are an AI assistant that writes concise, clear, and conventional Git commit messages.
Given the following git diff, generate a single-sentence commit message that describes the change:

{diff}
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        response = requests.post(
            f"{GEMINI_API_URL}?key={gemini_api_key}",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            try:
                message = data['candidates'][0]['content']['parts'][0]['text'].strip()
                click.echo('\nSuggested commit message:')
                click.secho(message, fg='green')
                click.echo('Press Enter to commit with this message, or Ctrl+C to cancel.')
                input()  # Wait for user to hit Enter
                try:
                    subprocess.check_call(['git', 'add', '-A'])
                    subprocess.check_call(['git', 'commit', '-m', message])
                    click.secho('Committed successfully!', fg='cyan')
                except subprocess.CalledProcessError as e:
                    click.echo('Git commit failed:')
                    click.echo(str(e))
            except (KeyError, IndexError):
                click.echo('Gemini response format error.')
        else:
            click.echo(f'Gemini API error: {response.status_code} {response.text}')
    except subprocess.CalledProcessError as e:
        click.echo('Error getting git diff:')
        click.echo(e.output.decode('utf-8'))
    except Exception as e:
        click.echo(f'Error: {e}') 