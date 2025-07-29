from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp.server.fastmcp.resources import DirectoryResource
from pathlib import Path
import os
from markitdown import MarkItDown

md = MarkItDown()

# Initialize the FastMCP server
mcp = FastMCP("DocumentBrain", dependencies=["markitdown[all]"])

@mcp.tool(
    annotations={
        "title": "Read Any Document",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def read_any_document(file_path: str) -> str:
    """Read any supported document and return its text content, including OCR for images.
    Args:
        file_path: Path to the document to process.
    Returns:
        Extracted text content as a string.
    """
    try:
        expanded_path = os.path.expanduser(file_path)
        return md.convert(expanded_path).text_content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool(
    annotations={
        "title": "Save File to PC",
        "readOnlyHint": False,
        "openWorldHint": True
    }
)
def save_file_to_pc(filepath: str, content: str) -> str:
    """
    Save content to a file on the desktop.
    Args:
        filename: Name of the file to save (can include subdirectory)
        content: Content to write to the file
    Returns:
        A success or error message
    """
    try:
        # Expand the desktop path
        desktop_path = os.path.expanduser(filepath)
        # Ensure the filename doesn't contain any path traversal attempts
        safe_filename = os.path.basename(filepath)
        # Create the full file path
        full_path = os.path.join(desktop_path, safe_filename)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        # Write the content to the file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File successfully saved to {full_path}"
    except Exception as e:
        return f"Error saving file: {str(e)}"


# Now add a resource
# Define the path to the current directory
documents_path = Path(".").resolve()

# Create a DirectoryResource to list files in the current directory
documents_resource = DirectoryResource(
    uri="docs://files",
    path=documents_path,
    name="Local Document Directory",
    description="Lists all files in the current working directory.",
    recursive=False  # Set to True if you want to include subdirectories
)

# Add the resource to your FastMCP server
mcp.add_resource(documents_resource)

@mcp.resource("docs://file/{filename}")
def get_document_content(filename: str) -> str:
    """Retrieve the content of a specified document."""
    try:
        file_path = documents_path / filename
        if not file_path.exists():
            return f"File not found: {filename}"
        return md.convert(str(file_path)).text_content
    except Exception as e:
        return f"Error reading file {filename}: {str(e)}"

# Prompt: Summarize document
@mcp.prompt()
def analyze_data(text: str) -> list[base.Message]:
    """Prompt to generate a summary of the provided document text.
    Args:
        text: The content of the document to be summarized.
    Returns:
        A list of messages guiding the LLM to produce a summary.
    """
    return [
        base.Message(
            role="user",
            content=[
                base.TextContent(
                    text=f"Assume the role of a data analyst specializing in academic research. \
                    Your task is to critically analyze the data presented in the file of the attached academic document. \
                    Start by summarizing the key data points and notable findings. Identify any patterns, trends, correlations, or anomalies within the dataset.:\n\n{text}"
                )
            ]
        )
    ]

def main():
    """Entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()