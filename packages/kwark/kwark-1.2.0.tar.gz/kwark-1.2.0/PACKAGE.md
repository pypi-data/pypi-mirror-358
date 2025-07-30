<!-- PACKAGE file - intended to be shown when a user browses the package in a registry, incuding PyPI. Content is focused on what a _consumer_ of the application might want to know. -->

# Kwark

## Tap into AI brilliance from a simple shell command

The tool currently has four commands:
- `doc`: Summarizes the conclusions from a discussion or thread for inclusion in technical documentation
- `branch`: Generates git branch names from input text
- `commit`: Generates git commit messages from diff output
- `models`: Lists available Anthropic AI models

All commands use the Anthropic API and require an API key.

## Usage (MacOS)

The `doc` command processes text from standard input and returns the summary to standard output.

```bash
pbpaste | kwark doc | pbcopy
```
The `branch` command generates a git branch name from input text. The branch name contains 1-4 relevant hyphen-separated words from the input text.

```bash
echo "Add ability for users to export their transaction history to PDF for quarterly tax reporting" | kwark branch
# Output: export-transaction-history-pdf
```

You can use it to create a new branch directly:

```bash
git checkout -b $(echo "Implement role-based access controls for admin dashboard" | kwark branch)
```

The `commit` command generates a concise, descriptive commit message from git diff output. If there are no changes in the diff, it uses a dot as the commit message.

```bash
git diff | kwark commit
# Output: Add user authentication feature
```

You can use it to create a commit directly:

```bash
git commit -m "$(git diff --staged | kwark commit)"
```

The `models` command lists all available Anthropic AI models that can be used with the other commands. The output is formatted as YAML.

```bash
kwark models
# Output:
# - created_at: '2024-10-22'
#   display_name: Claude 3.5 Sonnet
#   id: claude-3-5-sonnet-20241022
# - created_at: '2024-03-07'
#   display_name: Claude 3 Haiku
#   id: claude-3-haiku-20240307  
# - created_at: '2024-02-29'
#   display_name: Claude 3 Opus
#   id: claude-3-opus-20240229
```

(Note `pbcopy` and `pbpaste` are MacOS-specific commands.)

## Quick installation (MacOS)

```bash
brew install python@3.11
python3.11 -m pip install pipx
pipx install kwark
```

## Authentication and configuration

Kwark uses Claude 3.5 Sonnet through the Antropic API, and requires an API key.

There are three options for providing the API key to Kwark:

1. Set the default `ANTHROPIC_API_KEY` environment variable before running the `kwark` command
2. Provide the API key as a `--api-key` option to any kwark command (e.g., `kwark doc --api-key YOUR_KEY` or `kwark branch --api-key YOUR_KEY`)
3. Provide the API key in a configuration file using the [WizLib ConfigHandler](https://wizlib.steamwiz.io/api/config-handler) protocol

We recommend storing the key in a password manager such as 1Password, then using a config file to retrieve the key at runtime instead of storing the key itself in a file. For example, create a file at `~/.kwark.yml` with the following contents:

```yaml
kwark:
  api:
    anthropic:
      key: $(op read "op://Private/Anthropic/api-key")
```

<br/>

---

<br/>

<a href="https://www.flaticon.com/free-icons/particles">Particles icon by Freepik-Flaticon</a>
