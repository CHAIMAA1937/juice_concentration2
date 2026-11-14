
import plotly.graph_objects as go


def create_concentration_graph(initial_concentration, final_concentration, duration):
    if initial_concentration <= 0 or final_concentration <= initial_concentration:
        raise ValueError("Valeurs de concentration invalides.")

    if duration <= 0:
        raise ValueError("La durée doit être positive.")

    time_points = [
        0,
        duration * 0.25,
        duration * 0.5,
        duration * 0.75,
        duration
    ]

    concentration_values = [
        initial_concentration
        + (final_concentration - initial_concentration) * t / duration
        for t in time_points
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time_points,
        y=concentration_values,
        mode="lines+markers",
        name="Concentration"
    ))

    fig.update_layout(
        title="Évolution de la concentration du jus",
        xaxis_title="Temps (minutes)",
        yaxis_title="Fraction soluble (%)",
        template="plotly_white"
    )

    return fig


def create_mass_flow_graph(results):
    stages = ["Jus initial", "Après filtration", "Après mélange", "Jus concentré", "Vapeur"]

    values = [
        results["m0"],
        results["m1"],
        results["m2"],
        results["m4"],
        results["mv"]
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=stages,
        y=values,
        name="Débit massique"
    ))

    fig.update_layout(
        title="Débits massiques du procédé",
        xaxis_title="Étapes du procédé",
        yaxis_title="Débit (kg/h)",
        template="plotly_white"
    )

    return fig


def create_thermal_power_graph(results):
    stages = ["Préchauffage", "Évaporation", "Refroidissement"]

    powers = [
        results["Q3"],
        results["Q4"],
        results["Q5"]
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=stages,
        y=powers,
        name="Puissance thermique"
    ))

    fig.update_layout(
        title="Puissances thermiques du procédé",
        xaxis_title="Opérations",
        yaxis_title="Puissance (kW)",
        template="plotly_white"
    )

    return fig
