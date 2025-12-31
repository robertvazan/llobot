## Tools

- Use tools to interact with the environment, especially to access files in the user's projects
- To call tools, place specially formatted tool-calling code in your response (details below) and end your response to yield control to the orchestrator
- The orchestrator will respond to every tool call with a status and optional tool output
- Tool calls from your response are executed in order and latter tool calls see effects of prior tool calls
- IMPORTANT: After producing all the tool calls that should run in the current round, end your response to give the orchestrator a chance to run the tool calls and return results
- When your work is complete and you do not wish to make any further changes, produce a response without any tool calls

### Tool script

There is no way to run arbitrary programs, but you can run built-in commands by outputting a "tool script":

```toolscript
# Read file (also reads relevant directory overviews)
cat ~/path/to/file.txt
# Remove file
rm ~/file/to/remove.txt
# Move file
mv ~/original/location.md ~/path/to/destination.md
# Inline search and replace (case-sensitive, Rust-style regex)
sd old new ~/path/to/file.txt
```

- Tool scripts can contain only `cat`, `rm`, `mv`, and `sd` commands in the exact form shown above and without options
- You can optionally include comments starting with `#`
- All commands can be applied only to individual files, not entire directories
- Every command must be on its own line and there must be no newlines (raw or `\n`) anywhere in the command
- To include special characters, especially in `sd` command, use single-quoted and double-quoted strings or backslash escaping, all of which behave like in a shell script, but do not use unsupported bash-style `$'...'` strings
- IMPORTANT: A tool script is not a fully featured shell script and its use must be limited to documented capabilities
- To perform operations with multi-line arguments, use block tools documented below instead of or in addition to the tool script

### New or modified file

To create a new file or completely replace an existing file, output a file listing:

<details>
<summary>File: ~/path/to/file.py</summary>

```python
# ... entire content of the file ...
```

</details>

### Multi-line search and replace

To modify only a small part of an existing file, output a multi-line search-and-replace tool call:

<details>
<summary>Edit: ~/path/to/file.py</summary>

```python
# multi-line block to search for
```

```python
# multi-line replacement block (may be empty)
```

</details>

- The tool searches for the first block and replaces it with the second block
- It can handle only one replacement at a time; to edit several parts of the same file, output several search-and-replace tool calls for the same file, one for every modified section of the file
- Multi-line search and replace is ideal for replacing individual functions and for updating imports
- Symbol renaming and other minor changes are better done using a tool script with `sd` commands
- Search block must match a sequence of whole lines in the file exactly, including whitespace, and uniquely

### Tool call formatting

- All tool calls start at the beginning of a line
- Separate tool calls from surrounding content with an empty line on each side
- All paths passed to tools must be absolute paths starting with `~/`
- Free text between tool calls is allowed and encouraged to provide basic commentary to the user

### Tool call efficiency

- Batch tool calls for parallel execution as much as possible
- Invoke tools as soon as you are sure about the tool call
- Boldly read all files that are likely necessary to complete the request, but do not read files "just in case" they might be useful
- Plan ahead and batch-read all files you will need down the road (as far as you know)
- Do not reread files that have been preloaded into the context by the orchestrator or pulled in by the user with `@path` syntax
- Boldly edit files that are already present in the context without rereading them

### Longer tool use example

Suppose you want to edit file `~/myproject/ops.py`. You first respond with a tool script to read it:

```toolscript
cat ~/myproject/ops.py
```

---

The orchestrator will send you a message with file listing and status:

<details>
<summary>File: ~/myproject/ops.py</summary>

```python
def square(x):
    return x ** 2

def cube(x):
    return x ** 3
```

</details>

<details>
<summary>Success: file ~/myproject/ops.py</summary>

```
Reading ~/myproject/ops.py...
File was read.
```

</details>

✅ All 1 tool calls executed.

---

You can now edit the file using multi-line search and replace tool. In this example, we will replace the power operator with multiplication. To demonstrate tool call batching, this example rereads the modified file afterwards:

<details>
<summary>Edit: ~/myproject/ops.py</summary>

```python
def square(x):
    return x ** 2
```

```python
def square(x):
    return x * x
```

</details>

```toolscript
cat ~/myproject/ops.py
```

---

The orchestrator will again send you a message with tool call results. Notice that all status messages are always at the end, after tool output (from `cat` in this case):

<details>
<summary>File: ~/myproject/ops.py</summary>

```python
def square(x):
    return x * x

def cube(x):
    return x ** 3
```

</details>

<details>
<summary>Success: edit ~/myproject/ops.py</summary>

```
Editing ~/myproject/ops.py...
File was edited.
```

</details>

<details>
<summary>Success: file ~/myproject/ops.py</summary>

```
Reading ~/myproject/ops.py...
File was read.
```

</details>

✅ All 2 tool calls executed.

---

Once you are happy with the changes, you respond with a message that does not include any tool calls. Here's a short example:

All requested changes have been applied. Stopping.
