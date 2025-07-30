1. Make your code changes
   Edit files under `src/mcp_snowflake_server/`, `pyproject.toml`, etc.

2. Bump the version
   Open `pyproject.toml` and update the version field, for example:
   version = "0.4.X"

3. Build the package (optional)
   Run:
   uv build --no-sources

To test locally (optional):
uvx --from dist/mcp\_snowflake\_server\_readonly\_sysprompt-0.4.6-py3-none-any.whl --help

4. Commit, tag, and push
   git add .
   git commit -m "v0.4.X: update version"
   git tag v0.4.X
   git push origin v0.4.X

5. Publish the release
   Go to [https://github.com/sgriffin-magnoliacap/mcp-snowflake-server-no-write-system-prompt/releases/new](https://github.com/sgriffin-magnoliacap/mcp-snowflake-server-no-write-system-prompt/releases/new)
   Select tag v0.4.6
   Set title: v0.4.6
   Click "Publish release"

6. Confirm it's live
   Run:
   uvx mcp\_snowflake\_server\_readonly\_sysprompt\@0.4.6 --help
