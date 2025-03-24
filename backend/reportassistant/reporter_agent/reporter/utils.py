import base64

from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph.state import CompiledStateGraph


def save_graph_png(graph: CompiledStateGraph, name: str):
    try:
        png_data = graph.get_graph(xray=True).draw_mermaid_png(draw_method=MermaidDrawMethod.API,)
        output_path = f"{name}.png"
        with open(output_path, "wb") as file:
            file.write(png_data)
    except:
        print("Save graph image failed.")


def png_to_base64(file_path):
    """
    Converts a PNG file to a base64 encoded string.

    Parameters:
        file_path (str): Path to the PNG file

    Returns:
        str: Base64 encoded string of the PNG file
    """

    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
