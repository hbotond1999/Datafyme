from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph.state import CompiledStateGraph


def save_graph_png(graph: CompiledStateGraph, name: str):
    png_data = graph.get_graph(xray=True).draw_mermaid_png(draw_method=MermaidDrawMethod.API,)
    output_path = f"{name}.png"
    with open(output_path, "wb") as file:
        file.write(png_data)
