from wizlib.parser import WizParser

from kwark.command import KwarkCommand
from kwark.util import load_prompt
from kwark.ai import AI


class BranchCommand(KwarkCommand):
    """Generate a git branch name from input text using AI.
    The branch name will be hyphen-separated, lowercase, starting with
    the current date in YYYYMMDD format, followed by 1-4 important words
    from the input text."""

    name = 'branch'
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
        input_text = self.app.stream.text
        if not input_text.strip():
            self.status = "Error: No input text provided"
            return

        prompt = self.prompt.format(text=input_text)
        branch_name = AI(self.api_key).query(prompt).strip()

        self.status = f"Generated branch name from input text"
        return branch_name
