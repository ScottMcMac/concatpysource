# concatpysource
A(nother) Python script that concatinates your Python source files. This one recursively parses your main script and any dependencies to only include files actually required to run your program. This seems most useful for prompting web based LLMs.

Right now it outputs the concatinated text to the clipboard using Anthropic's suggested [format](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips#example-multi-document-structure).

## License

Copyright 2024 Scott Macdonell

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.