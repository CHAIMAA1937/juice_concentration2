import plotly.graph_objects as go


def create_process_diagram():
    fig = go.Figure()

    stages = [
        ("Réception du jus", 0, 5),
        ("Filtration", 1, 4),
        ("Préchauffage", 2, 3),
        ("Concentration", 3, 2),
        ("Refroidissement", 4, 1),
        ("Stockage", 5, 0)
    ]

    for name, x, y in stages:
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(
                    size=55,
                    color="#16834a",
                    line=dict(width=2, color="white")
                ),
                text=[name],
                textposition="bottom center",
                name=name,
                showlegend=False
            )
        )

    for i in range(len(stages) - 1):
        x1, y1 = stages[i][1], stages[i][2]
        x2, y2 = stages[i + 1][1], stages[i + 1][2]

        fig.add_annotation(
            x=x2,
            y=y2,
            ax=x1,
            ay=y1,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#555555"
        )

    fig.update_layout(
        title="Schéma du procédé de concentration du jus",
        template="plotly_white",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )

    return fig