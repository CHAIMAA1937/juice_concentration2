
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


def export_results_to_excel(results):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Résultats"

    # Titre
    sheet.merge_cells("A1:C1")
    sheet["A1"] = "RAPPORT DE CONCENTRATION DU JUS"
    sheet["A1"].font = Font(bold=True, size=16, color="FFFFFF")
    sheet["A1"].fill = PatternFill(
        start_color="1F4E78",
        end_color="1F4E78",
        fill_type="solid"
    )
    sheet["A1"].alignment = Alignment(horizontal="center")

    # En-têtes
    sheet.append([])
    sheet.append(["Paramètre", "Valeur", "Unité"])

    headers = ["A3", "B3", "C3"]
    for cell in headers:
        sheet[cell].font = Font(bold=True, color="FFFFFF")
        sheet[cell].fill = PatternFill(
            start_color="4472C4",
            end_color="4472C4",
            fill_type="solid"
        )

    # Résultats
    data = [
        ("Débit initial", results["m0"], "kg/h"),
        ("Débit après filtration", results["m1"], "kg/h"),
        ("Débit après mélange", results["m2"], "kg/h"),
        ("Débit de jus concentré", results["m4"], "kg/h"),
        ("Débit de vapeur", results["mv"], "kg/h"),
        ("Fraction soluble après filtration", results["y1"], ""),
        ("Fraction soluble après mélange", results["y2"], ""),
        ("Fraction finale", results["x4"], ""),
        ("Puissance de chauffage", results["Q3"], "kW"),
        ("Puissance d'évaporation", results["Q4"], "kW"),
        ("Puissance de refroidissement", results["Q5"], "kW"),
        ("Entrées totales", results["entrees"], "kg/h"),
        ("Sorties totales", results["sorties"], "kg/h"),
        ("Écart du bilan global", results["ecart_global"], "kg/h"),
        ("Écart des matières solubles", results["ecart_solubles"], "kg/h"),
        ("Résidus théoriques", results["residus_theoriques"], "kg/h"),
        ("Écart des résidus", results["ecart_residus"], "kg/h"),
    ]

    for row in data:
        sheet.append(row)

    # Mise en forme
    for row in sheet.iter_rows(min_row=4, max_col=3):
        for cell in row:
            cell.alignment = Alignment(horizontal="center")
            cell.border = Border(
                bottom=Side(style="thin", color="D9E2F3")
            )

    sheet.column_dimensions["A"].width = 38
    sheet.column_dimensions["B"].width = 20
    sheet.column_dimensions["C"].width = 15

    # Créer le fichier en mémoire
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output.getvalue()
