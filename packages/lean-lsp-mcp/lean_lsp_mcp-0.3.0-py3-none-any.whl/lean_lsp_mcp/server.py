from curses import wrapper
import os
import time
from typing import List, Optional, Dict
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import urllib
import json
import functools

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger
from leanclient import LeanLSPClient, DocumentContentChange

from lean_lsp_mcp.client_utils import setup_client_for_file
from lean_lsp_mcp.file_utils import get_file_contents, update_file
from lean_lsp_mcp.instructions import INSTRUCTIONS
from lean_lsp_mcp.utils import (
    OutputCapture,
    extract_range,
    find_start_position,
    format_diagnostics,
    format_goal,
)


logger = get_logger(__name__)


# Server and context
@dataclass
class AppContext:
    lean_project_path: str | None
    client: LeanLSPClient | None
    file_content_hashes: Dict[str, str]
    rate_limit: Dict[str, List[int]]


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    try:
        lean_project_path = os.environ.get("LEAN_PROJECT_PATH", "").strip()
        if not lean_project_path:
            lean_project_path = None
        else:
            lean_project_path = os.path.abspath(lean_project_path)

        context = AppContext(
            lean_project_path=lean_project_path,
            client=None,
            file_content_hashes={},
            rate_limit={"leansearch": [], "loogle": [], "lean_state_search": []},
        )
        yield context
    finally:
        logger.info("Closing Lean LSP client")
        if context.client:
            context.client.close()


mcp = FastMCP(
    name="Lean LSP",
    instructions=INSTRUCTIONS,
    dependencies=["leanclient"],
    lifespan=app_lifespan,
    env_vars={
        "LEAN_PROJECT_PATH": {
            "description": "Path to the Lean project root. If not set, this is inferred automatically using file paths. Use this only if the automatic system fails to find the project.",
            "required": False,
        }
    },
)


# Rate limiting: n requests per m seconds
def rate_limited(category: str, max_requests: int, per_seconds: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rate_limit = kwargs["ctx"].request_context.lifespan_context.rate_limit
            current_time = int(time.time())
            rate_limit[category] = [
                timestamp
                for timestamp in rate_limit[category]
                if timestamp > current_time - per_seconds
            ]
            if len(rate_limit[category]) >= max_requests:
                return f"Tool limit exceeded: {max_requests} requests per {per_seconds} s. Try again later."
            rate_limit[category].append(current_time)
            return func(*args, **kwargs)

        wrapper.__doc__ = f"Limit: {max_requests}req/{per_seconds}s. " + wrapper.__doc__
        return wrapper

    return decorator


# Project level tools
@mcp.tool("lean_build")
def lsp_build(ctx: Context) -> str:
    """Build the Lean project and restart the LSP Server.

    Use only when necessary (e.g. imports).

    Returns:
        str: Build output or error message.
    """
    lean_project_path = ctx.request_context.lifespan_context.lean_project_path
    try:
        client: LeanLSPClient = ctx.request_context.lifespan_context.client
        client.close()

        with OutputCapture() as output:
            ctx.request_context.lifespan_context.client = LeanLSPClient(
                lean_project_path,
                initial_build=True,
                print_warnings=False,
            )
        build_output = output.get_output()
    except Exception as e:
        return f"Error during build:\n{str(e)}\n{build_output}"
    return build_output


# File level tools
@mcp.tool("lean_file_contents")
def file_contents(ctx: Context, file_path: str, annotate_lines: bool = True) -> str:
    """Get the text contents of a Lean file.

    IMPORTANT! Look up the file_contents for the currently open file including line number annotations.
    Use this during the proof process to keep updated on the line numbers and the current state of the file.

    Args:
        file_path (str): Absolute path to the Lean file.
        annotate_lines (bool, optional): Annotate lines with line numbers. Defaults to False.

    Returns:
        str: Text contents of the Lean file or None if file does not exist.
    """
    try:
        data = get_file_contents(file_path)
    except FileNotFoundError:
        return (
            f"File `{file_path}` does not exist. Please check the path and try again."
        )

    if annotate_lines:
        data = data.split("\n")
        max_digits = len(str(len(data)))
        annotated = ""
        for i, line in enumerate(data):
            annotated += f"{i + 1}{' ' * (max_digits - len(str(i + 1)))}: {line}\n"
        return annotated
    else:
        return data


@mcp.tool("lean_diagnostic_messages")
def diagnostic_messages(ctx: Context, file_path: str) -> List[str] | str:
    """Get all diagnostic messages for a Lean file.

    Attention:
        "no goals to be solved" indicates some code needs to be removed. Keep going!

    Args:
        file_path (str): Absolute path to the Lean file.

    Returns:
        List[str] | str: Diagnostic messages or error message.
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."

    update_file(ctx, rel_path)

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    diagnostics = client.get_diagnostics(rel_path)
    return format_diagnostics(diagnostics)


@mcp.tool("lean_goal")
def goal(ctx: Context, file_path: str, line: int, column: Optional[int] = None) -> str:
    """Get the proof goals at a specific location or line in a Lean file.

    VERY USEFUL AND CHEAP! This is your main tool to understand the proof state and its evolution!!
    Use this multiple times after every edit to the file!

    Solved proof state returns "no goals".

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed)
        column (int, optional): Column number (1-indexed). Defaults to None => Both before and after the line.

    Returns:
        str: Goal at the specified location or error message.
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."

    content = update_file(ctx, rel_path)
    client: LeanLSPClient = ctx.request_context.lifespan_context.client

    if column is None:
        lines = content.splitlines()
        if line < 1 or line > len(lines):
            return "Line number out of range. Try again?"
        column_end = len(lines[line - 1])
        column_start = next(
            (i for i, c in enumerate(lines[line - 1]) if not c.isspace()), 0
        )
        goal_start = client.get_goal(rel_path, line - 1, column_start)
        goal_end = client.get_goal(rel_path, line - 1, column_end)

        if goal_start is None and goal_end is None:
            return "No goals found on line. Try another position?"

        start_text = format_goal(goal_start, "No goal found at the start of the line.")
        end_text = format_goal(goal_end, "No goal found at the end of the line.")
        if start_text == end_text:
            return start_text
        return f"Before:\n{start_text}\nAfter:\n{end_text}"

    else:
        goal = client.get_goal(rel_path, line - 1, column - 1)
        return format_goal(goal, "Not a valid goal position. Try again?")


@mcp.tool("lean_term_goal")
def term_goal(
    ctx: Context, file_path: str, line: int, column: Optional[int] = None
) -> str:
    """Get the term goal at a specific location in a Lean file.

    Use this to get a better understanding of the proof state.

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed)
        column (int, optional): Column number (1-indexed). Defaults to None => end of line.

    Returns:
        str: Term goal at the specified location or error message.
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."

    content = update_file(ctx, rel_path)
    if column is None:
        column = len(content.splitlines()[line - 1])

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    term_goal = client.get_term_goal(rel_path, line - 1, column - 1)
    if term_goal is None:
        return "Not a valid term goal position. Try again?"
    rendered = term_goal.get("goal", None)
    if rendered is not None:
        rendered = rendered.replace("```lean\n", "").replace("\n```", "")
    return rendered


@mcp.tool("lean_hover_info")
def hover(ctx: Context, file_path: str, line: int, column: int) -> str:
    """Get the hover information at a specific location in a Lean file.

    Hover information provides documentation about any lean syntax, variables, functions, etc. in your code.

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed)
        column (int): Column number (1-indexed). Make sure to use the start or within the term, not the end.

    Returns:
        str: Hover information at the specified location or error message.
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."

    file_content = update_file(ctx, rel_path)
    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    hover_info = client.get_hover(rel_path, line - 1, column - 1)
    if hover_info is None:
        return "No hover information available. Try another position?"

    # Get the symbol and the hover information
    h_range = hover_info.get("range")
    symbol = extract_range(file_content, h_range)
    info = hover_info["contents"].get("value", "No hover information available.")
    info = info.replace("```lean\n", "").replace("\n```", "").strip()
    return f"Hover info `{symbol}`:\n{info}"


@mcp.tool("lean_completions")
def completions(
    ctx: Context, file_path: str, line: int, column: int, max_completions: int = 100
) -> List[str] | str:
    """Find possible code completions at a location in a Lean file.

    Check available identifiers and imports:
    - Dot Completion: Displays relevant identifiers after typing a dot (e.g., `Nat.`, `x.`, or `.`).
    - Identifier Completion: Suggests matching identifiers after typing part of a name.
    - Import Completion: Lists importable files after typing import at the beginning of a file.

    Only use this on incomplete lines/statements to get suggestions for completing the code.

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed)
        column (int): Column number (1-indexed).
        max_completions (int, optional): Maximum number of completions to return. Defaults to 100.

    Returns:
        List[str] | str: List of possible completions or error message.
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."
    update_file(ctx, rel_path)

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    completions = client.get_completions(rel_path, line - 1, column - 1)

    formatted = []
    for completion in completions:
        label = completion.get("label", None)
        if label is not None:
            formatted.append(label)

    if not formatted:
        return "No completions available. Try another position?"

    if len(formatted) > max_completions:
        formatted = formatted[:max_completions] + [
            f"{len(formatted) - max_completions} more, start typing and check again..."
        ]
    return formatted


@mcp.tool("lean_declaration_file")
def declaration_file(ctx: Context, file_path: str, symbol: str) -> str:
    """Get the file contents where a symbol/lemma/class/structure/... is declared.

    Note:
        Symbol has to be in the file already. Add it first if necessary.
        Lean files can be large, use `lean_hover_info` before this tool.

    Args:
        file_path (str): Absolute path to the Lean file.
        symbol (str): Symbol to look up the declaration for. Case sensitive!

    Returns:
        str: Contents of the file where the symbol is declared or error message.
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."
    orig_file_content = update_file(ctx, rel_path)

    # Find the first occurence of the symbol (line and column) in the file,
    position = find_start_position(orig_file_content, symbol)
    if not position:
        return f"Symbol `{symbol}` (case sensitive) not found in file `{rel_path}`. Add it first, then try again."

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    declaration = client.get_declarations(
        rel_path, position["line"], position["column"]
    )

    if len(declaration) == 0:
        return f"No declaration available for `{symbol}`."

    # Load the declaration file
    declaration = declaration[0]
    uri = declaration.get("targetUri")
    if not uri:
        uri = declaration.get("uri")

    abs_path = client._uri_to_abs(uri)
    if not os.path.exists(abs_path):
        return f"Could not open declaration file `{abs_path}` for `{symbol}`."

    with open(abs_path, "r") as f:
        file_content = f.read()

    return f"Declaration of `{symbol}`:\n{file_content}"


@mcp.tool("lean_multi_attempt")
def multi_attempt(
    ctx: Context, file_path: str, line: int, snippets: List[str]
) -> List[str] | str:
    """Attempt multiple lean code snippets and return goal state and diagnostics for each snippet.

    This tool is useful to screen different tactics/approaches to help pick the most promising one.
    Use this in your diagnostic process.
    A new line is inserted at the specified line number and each attempt is tried before resetting the line.

    Note:
        Each snippet has to include the full line including correct initial indentation!
        Only single line snippets are supported!
        Recommended: Snippets without comments.

    USE RARELY! Keep the user in the loop by editing files instead.

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed) to attempt.
        snippets (list[str]): List of snippets to try on the line. 3+ snippets are recommended.

    Returns:
        List[str] | str: Diagnostics and goal state for each snippet or error message.
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."
    update_file(ctx, rel_path)
    client: LeanLSPClient = ctx.request_context.lifespan_context.client

    client.open_file(rel_path)

    results = []
    snippets[0] += "\n"  # Extra newline for the first snippet
    for snippet in snippets:
        # Create a DocumentContentChange for the snippet
        change = DocumentContentChange(
            snippet + "\n",
            [line - 1, 0],
            [line, 0],
        )
        # Apply the change to the file, capture diagnostics and goal state
        diag = client.update_file(rel_path, [change])
        formatted_diag = "\n".join(format_diagnostics(diag, select_line=line - 1))
        goal = client.get_goal(rel_path, line - 1, len(snippet))
        formatted_goal = format_goal(goal, "Missing goal")
        results.append(f"{snippet}:\n {formatted_goal}\n\n{formatted_diag}")

    # Make sure it's clean after the attempts
    client.close_files([rel_path])
    return results


@mcp.tool("lean_run_code")
def run_code(ctx: Context, code: str) -> List[str] | str:
    """Run/compile a complete Lean code snippet and return its diagnostic messages.

    This tool is useful to test whether a code snippet compiles and runs correctly.
    Use cases include testing definitions/statements, tactics, or other Lean code snippets.

    The snippet has to be self-contained, i.e. it has to include all imports and definitions.
    Use `import Mathlib` when in doubt instead of specific Mathlib imports.

    Only use this to test snippets separate from open files! Keep the user in the loop by editing files instead.

    Args:
        code (str): Complete Lean code snippet to run.

    Returns:
        List[str] | str: Diagnostics messages or error message.
    """
    lean_project_path = ctx.request_context.lifespan_context.lean_project_path
    if lean_project_path is None:
        return "No valid Lean project path found. Run another tool (e.g. `lean_diagnostic_messages`) first to set it up or set the LEAN_PROJECT_PATH environment variable."

    rel_path = "temp_snippet.lean"
    abs_path = os.path.join(lean_project_path, rel_path)

    try:
        with open(abs_path, "w") as f:
            f.write(code)
    except Exception as e:
        return f"Error writing code snippet to file `{abs_path}`:\n{str(e)}"

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    diagnostics = format_diagnostics(client.get_diagnostics(rel_path))
    client.close_files([rel_path])

    try:
        os.remove(abs_path)
    except Exception as e:
        return f"Error removing temporary file `{abs_path}`:\n{str(e)}"

    return (
        diagnostics
        if diagnostics
        else "No diagnostics found for the code snippet (compiled successfully)."
    )


@mcp.tool("lean_leansearch")
@rate_limited("leansearch", max_requests=3, per_seconds=30)
def leansearch(ctx: Context, query: str, num_results: int = 5) -> List[Dict] | str:
    """Search for Lean theorems, definitions, and tactics using leansearch.net API.

    Query patterns:
      - Natural language: "If there exist injective maps of sets from A to B and from B to A, then there exists a bijective map between A and B."
      - Mixed natural/Lean: "natural numbers. from: n < m, to: n + 1 < m + 1", "n + 1 <= m if n < m"
      - Concept names: "Cauchy Schwarz"
      - Lean identifiers: "List.sum", "Finset induction"
      - Lean term: "{f : A → B} {g : B → A} (hf : Injective f) (hg : Injective g) : ∃ h, Bijective h"

    Args:
        query (str): Search query
        num_results (int, optional): Max results. Defaults to 5.

    Returns:
        List[Dict] | str: List of search results or error message
    """
    try:
        headers = {"User-Agent": "lean-lsp-mcp/0.1", "Content-Type": "application/json"}
        payload = json.dumps(
            {"num_results": str(num_results), "query": [query]}
        ).encode("utf-8")

        req = urllib.request.Request(
            "https://leansearch.net/search",
            data=payload,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            results = json.loads(response.read().decode("utf-8"))

        if not results or not results[0]:
            return "No results found."
        results = results[0][:num_results]
        results = [r["result"] for r in results]

        for result in results:
            result.pop("docstring")
            result["module_name"] = ".".join(result["module_name"])
            result["name"] = ".".join(result["name"])

        return results
    except Exception as e:
        return f"leansearch error:\n{str(e)}"


@mcp.tool("lean_loogle")
@rate_limited("loogle", max_requests=3, per_seconds=30)
def loogle(ctx: Context, query: str, num_results: int = 8) -> List[dict] | str:
    """Search for definitions and theorems using the loogle API.

    Query patterns:
      - By constant: Real.sin  # finds lemmas mentioning Real.sin
      - By lemma name: "differ"  # finds lemmas with "differ" in the name
      - By subexpression: _ * (_ ^ _)  # finds lemmas with a product and power
      - Non-linear: Real.sqrt ?a * Real.sqrt ?a
      - By type shape: (?a -> ?b) -> List ?a -> List ?b
      - By conclusion: |- tsum _ = _ * tsum _
      - By conclusion w/hyps: |- _ < _ → tsum _ < tsum _

    Args:
        query (str): Search query
        num_results (int, optional): The maximum number of results to return. Defaults to 8.

    Returns:
        List[dict] | str: List of search results or error message
    """
    try:
        req = urllib.request.Request(
            f"https://loogle.lean-lang.org/json?q={urllib.parse.quote(query)}",
            headers={"User-Agent": "lean-lsp-mcp/0.1"},
            method="GET",
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            results = json.loads(response.read().decode("utf-8"))

        if "hits" not in results:
            return "No results found."

        results = results["hits"][:num_results]
        for result in results:
            result.pop("doc")
        return results
    except Exception as e:
        return f"loogle error:\n{str(e)}"


@mcp.tool("lean_state_search")
@rate_limited("lean_state_search", max_requests=3, per_seconds=30)
def state_search(
    ctx: Context, file_path: str, line: int, column: int, num_results: int = 5
) -> List[dict] | str:
    """Search for applicable theorems based on proof state using premise-search.com API.

    Note:
        Only uses first goal.

    Args:
        file_path (str): The absolute path to the Lean file
        line (int): The line number to search (1-indexed)
        column (int): The column number to search (1-indexed)
        num_results (int, optional): The maximum number of results to return. Defaults to 5.

    Returns:
        List[dict] | str: List of applicable theorems or error message
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."

    update_file(ctx, rel_path)
    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    goal = client.get_goal(rel_path, line - 1, column - 1)

    if not goal:
        return "No valid goal found. Correct line and column?"

    goal = urllib.parse.quote(goal["goals"][0])

    try:
        req = urllib.request.Request(
            f"https://premise-search.com/api/search?query={goal}&results={num_results}&rev=v4.17.0-rc1",
            headers={"User-Agent": "lean-lsp-mcp/0.1"},
            method="GET",
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            results = json.loads(response.read().decode("utf-8"))

        for result in results:
            result.pop("rev")
        return results
    except Exception as e:
        return f"lean state search error:\n{str(e)}"


if __name__ == "__main__":
    mcp.run()
