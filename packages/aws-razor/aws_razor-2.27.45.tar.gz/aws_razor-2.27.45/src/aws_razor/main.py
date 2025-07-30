import argparse
import json
import logging
from typing import (
    Any,
    Generator,
)

from awscli.autocomplete.main import (  # type: ignore[import-untyped]
    create_autocompleter,
)
from awscli.autoprompt.prompttoolkit import (  # type: ignore[import-untyped]
    Completer,
    PromptToolkitCompleter,
    ThreadedCompleter,
)
from awscli.clidriver import create_clidriver  # type: ignore[import-untyped]
from prompt_toolkit.completion.base import (
    CompleteEvent,
)
from prompt_toolkit.document import Document

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="aws-razor",
        description="General purpose awscli command line completions. "
        "The environment variables COMP_LINE and COMMAND_LINE are read "
        "for the command line contents, but are superseded by the --text argument if given.",
    )

    parser.add_argument(
        "--command-line",
        "-c",
        required=True,
        type=str,
        help="The command to complete",
    )

    parser.add_argument(
        "--position",
        "-p",
        type=int,
        help="Position of the cursor in the given text",
    )

    return parser.parse_args()


def get_completions(
    completer: Completer, doc: Document, event: CompleteEvent
) -> Generator[dict[str, Any], None, None]:
    results = completer.get_completions(doc, event)

    for result in results:
        comp_result = {
            "text": result.text,
            "start_position": result.start_position,
            "display_text": result.display_text,
            "display_meta": result.display_meta_text,
        }

        if LOGGER.isEnabledFor(logging.DEBUG):
            logging.debug(f"result: {comp_result}")

        yield comp_result


def main() -> None:
    args = get_args()

    cli_driver = create_clidriver()
    completer = ThreadedCompleter(
        PromptToolkitCompleter(create_autocompleter(driver=cli_driver))
    )

    command_index = args.position or len(args.command_line)

    # the completer expects `aws` to be omitted
    if args.command_line.startswith("aws "):
        args.command_line = args.command_line[4:]
        command_index = max(0, command_index - 4)

    doc = Document(args.command_line, command_index)
    event = CompleteEvent(completion_requested=True)

    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug(f"command_line: {args.command_line}")

    try:
        for comp in get_completions(completer, doc, event):
            print(json.dumps(comp))
    except KeyboardInterrupt:
        # If the user hits Ctrl+C, we don't want to print
        # a traceback to the user.
        return


if __name__ == "__main__":
    main()
