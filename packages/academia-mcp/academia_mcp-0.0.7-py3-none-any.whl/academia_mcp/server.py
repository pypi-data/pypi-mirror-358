import fire  # type: ignore
import uvicorn
from mcp.server.fastmcp import FastMCP

from .tools.arxiv_search import arxiv_search
from .tools.arxiv_download import arxiv_download
from .tools.s2_citations import s2_citations
from .tools.hf_datasets_search import hf_datasets_search
from .tools.anthology_search import anthology_search

server = FastMCP("Academia MCP", stateless_http=True)

server.add_tool(arxiv_search)
server.add_tool(arxiv_download)
server.add_tool(s2_citations)
server.add_tool(hf_datasets_search)
server.add_tool(anthology_search)

http_app = server.streamable_http_app()


def run(host: str = "0.0.0.0", port: int = 5050) -> None:
    uvicorn.run(http_app, host=host, port=port)


if __name__ == "__main__":
    fire.Fire(run)
