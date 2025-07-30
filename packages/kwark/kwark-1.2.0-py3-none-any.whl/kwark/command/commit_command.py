from wizlib.parser import WizParser

from kwark.command import KwarkCommand
from kwark.util import load_prompt
from kwark.ai import AI


class CommitCommand(KwarkCommand):
    """Generate a git commit message from diff output using AI.
    If there are no changes in the diff, use a dot as the commit message."""

    name = 'commit'
    prompt = load_prompt(name)

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('--api-key', '-k')

    def handle_vals(self):
        super().handle_vals()
        if not self.provided('api-key'):
            if key := self.app.config.get('kwark-api-anthropic-key'):
                self.api_key = key

    @KwarkCommand.wrap
    def execute(self):
        diff_text = self.app.stream.text
        prompt = self.prompt.format(text=diff_text)
        commit_message = AI(self.api_key).query(prompt).strip()

        self.status = f"Generated commit message from diff"
        return commit_message
