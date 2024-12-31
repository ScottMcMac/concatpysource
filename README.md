# concatpysource
A(nother) Python script that concatinates your Python source files. This one recursively parses your main script and any dependencies to only include files actually required to run your program.

Right now it outputs the concatinated text to the clipboard using Anthropic's suggested [format](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips#example-multi-document-structure).
