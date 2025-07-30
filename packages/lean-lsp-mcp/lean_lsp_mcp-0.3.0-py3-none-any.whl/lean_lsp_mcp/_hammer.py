@mcp.tool("lean_hammer_premise")
@rate_limited("hammer_premise", max_requests=3, per_seconds=30)
def hammer_premise(
    ctx: Context, file_path: str, line: int, column: int, num_results: int = 32
) -> List[dict] | str:
    """Search for relevant premises based on proof state using the lean hammer premise selection API.

    Note:
        This tool only works on imported premises. Add more imports if needed.

    Args:
        file_path (str): The absolute path to the Lean file
        line (int): The line number to search (1-indexed)
        column (int): The column number to search (1-indexed)
        num_results (int, optional): The maximum number of results to return. Defaults to 32.

    Returns:
        List[dict] | str: List of relevant premises or error message
    """
    rel_path = setup_client_for_file(ctx, file_path)
    if not rel_path:
        return "No valid lean file path found. Could not set up client and load file."

    file_content = update_file(ctx, rel_path)
    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    goal = client.get_goal(rel_path, line - 1, column - 1)

    if not goal:
        return "No valid goal found. Correct line and column?"

    # Retrieve indexed premises from server if not already in context
    hammer_premises = ctx.request_context.lifespan_context.hammer_premises
    if not hammer_premises:
        try:
            req = urllib.request.Request(
                "http://leanpremise.net/indexed-premises",
                headers={"User-Agent": "lean-lsp-mcp/0.1"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                hammer_premises = json.loads(response.read().decode("utf-8"))
            ctx.request_context.lifespan_context.hammer_premises = hammer_premises
        except Exception as e:
            return "Failed to retrieve indexed premises, cannot use hammer premise."

    # # Find all indexed premises that are available based on the imports
    # pattern = re.compile(r'import\s+([\w\.]+)', re.MULTILINE)
    # imports = pattern.findall(file_content)
    # local_premises = [i for i, premise in enumerate(hammer_premises) if premise.startswith(tuple(imports))]

    data = {
        "state": goal["goals"][0],
        "local_premises": list(range(len(hammer_premises))),
        "new_premises": [],
        "k": num_results,
    }

    # Write to file for debug
    with open("hammer_premises.json", "w") as f:
        json.dump(data, f)

    try:
        req = urllib.request.Request(
            "http://leanpremise.net/retrieve",
            headers={
                "User-Agent": "lean-lsp-mcp/0.1",
                "Content-Type": "application/json",
            },
            method="POST",
            data=json.dumps(data).encode("utf-8"),
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            results = json.loads(response.read().decode("utf-8"))

        return [result["name"] for result in results]
    except Exception as e:
        return f"lean hammer premise error:\n{str(e)}"
