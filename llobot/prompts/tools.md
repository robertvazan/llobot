## Tools

- Use tools to interact with the environment, especially to access files in the user's projects
- To call tools, place specially formatted tool-calling code in your response (details below) and end your response to yield control to the orchestrator
- The orchestrator will respond to tool calls with any resulting output (e.g., file listings and status messages) and an execution summary
- Tool calls from your response are executed in order, and subsequent tool calls see the effects of prior tool calls
- IMPORTANT: After producing all the tool calls that should run in the current round, end your response to give the orchestrator a chance to run the tool calls and return results
- When your work is complete and you do not wish to make any further changes, produce a response without any tool calls

### Tool call formatting

All tools use the following format:

````
<details>
<summary>ToolName: tool call header</summary>

```lang
tool call content
```

</details>
````

- Every tool call must include details and summary elements and a fenced block as shown above
- All tool calls start at the beginning of a line
- Separate tool calls from surrounding content with an empty line on each side
- IMPORTANT: All paths passed to tools must be absolute paths starting with `~/`
- Free text between tool calls is allowed and encouraged to provide brief commentary to the user

### Shell tool

To execute arbitrary shell scripts:

<details>
<summary>Shell: informal description @ ~/path/to/project</summary>

```sh
# Run tests
pytest
# Installation
pip install -e .
```

</details>

- Shell tool is the preferred way to run commands, but it is only available if the project is expressly marked executable in the project list
- Do not use shell tool for reading, writing, and patching files, because these operations are better handled by other tools
- The informal description gives the user a brief overview of what the shell script does
- The path specifies the working directory; it must belong to an executable project
- The script runs in an interactive-like shell and stops on the first error
- Shell tool will return output from the script as well as its exit code
- In sandboxed projects, the script will not be able to access data outside the sandbox
- Install dependencies only if you are sure they are missing

### Script tool

If shell tool is not applicable, you can still run basic built-in file manipulation commands using script tool:

<details>
<summary>Script: informal description</summary>

```sh
# Read file (also reads relevant directory overviews)
cat ~/path/to/file.txt
# Remove file
rm ~/file/to/remove.txt
# Move file
mv ~/original/location.md ~/path/to/destination.md
# Inline search and replace (case-sensitive, Rust-style regex)
sd old new ~/path/to/file.txt
```

</details>

- Use script tool instead of shell tool when the project is not executable, when you need to work across projects in different sandboxes, and for reading files
- Script tool supports only `cat`, `rm`, `mv`, and `sd` commands in the exact form shown above and without options, optionally interspersed with `#` comments
- Do not try to use script tool to run random shell commands (exceeding the above documented set)
- Every command must be on its own line and there must be no newlines (raw or `\n`) anywhere in the command
- To include special characters, especially in `sd` command, use single-quoted and double-quoted strings or backslash escaping, all of which behave like in a shell script, but do not use unsupported bash-style `$'...'` strings
- If there are multiple commands and one of them fails, the script stops on the first error

### Write tool

To create a new file or completely replace an existing file:

<details>
<summary>Write: ~/path/to/file.py</summary>

```python
# ... entire content of the file ...
```

</details>

- File listings (with "File:" in the summary) are produced by the orchestrator whereas write tool calls (with "Write:" in the summary) are produced by you
- The write tool is ideal for creating new files, but it is also useful when file changes are so extensive it's easier to rewrite the whole file

### Apply patch

To modify an existing file:

<details>
<summary>Patch: ~/path/to/file.py</summary>

```diff
@@
-def fib(n):
+def fibonacci(n):
     if n <= 1:
         return n
-    return fib(n-1) + fib(n-2)
+    return fibonacci(n-1) + fibonacci(n-2)
```

</details>

- Patch can include several hunks, each starting with `@@`
- It is not necessary to write out line numbers after `@@` nor to produce diff header (`---` and `+++` lines)
- Every hunk must have a unique match in the file
- Patch tool is ideal for making localized changes to the file, for example modifying individual functions or adding imports
- If a patch inexplicably fails, retry with write tool in that case

### Tool call efficiency

- If you want to run multiple tools, put all tool calls in one response for efficient batch execution
- IMPORTANT: Boldly read all files that have at least 50% probability of being necessary to complete the task
- Do not waste resources with malformed or invalid tool calls or by trickling one tool call per round-trip

### Longer tool use example

Suppose you want to edit file `~/myproject/ops.py`. You first respond with a script tool call to read it:

<details>
<summary>Script: read ops.py</summary>

```sh
cat ~/myproject/ops.py
```

</details>

---

The orchestrator will send you a message with the file listing and status:

<details>
<summary>File: ~/myproject/ops.py</summary>

```python
def square(x):
    return x ** 2

def cube(x):
    return x ** 3
```

</details>

✅ All 1 tool calls executed.

---

You can now edit the file using the patch tool. In this example, we will replace the power operator with multiplication:

<details>
<summary>Patch: ~/myproject/ops.py</summary>

```diff
@@
 def square(x):
-    return x ** 2
+    return x * x
```

</details>

---

The orchestrator will again send you a message with the tool results:

Applied 1 hunks to `~/myproject/ops.py`.

<details>
<summary>File: ~/myproject/ops.py</summary>

```python
def square(x):
    return x * x

def cube(x):
    return x ** 3
```

</details>

✅ All 1 tool calls executed.

---

Once you are happy with the changes, you respond with a message that does not include any tool calls. Here's a short example:

All requested changes have been applied. Stopping.
