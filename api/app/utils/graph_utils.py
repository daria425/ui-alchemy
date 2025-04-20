from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles


def display_graph(graph, file_path):
    png=graph.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
    with open(file_path, "wb") as f:
        f.write(png)
    print(f"Graph saved to {file_path}")

def get_graph_code(graph, file_path="graph.mmd"):
    mermaid_code = graph.get_graph().draw_mermaid()  # returns raw Mermaid string
    with open(file_path, "w") as f:
        f.write(mermaid_code)
