
def calculate_concentration(
    m0,
    x0,
    y0,
    meau,
    mResidus,
    mR,
    xr,
    Cp,
    T2,
    T3,
    x4,
    T4,
    T5,
    lambda_v
):
    """
    Simulation complète du procédé de concentration du jus.
    Toutes les masses sont en kg/h.
    Les puissances sont en kW.
    """

    # 1. Vérification des paramètres
    if min(m0, mR, Cp, lambda_v) <= 0:
        raise ValueError("Les débits, Cp et lambda_v doivent être positifs.")

    fractions = [x0, y0, meau, xr, x4]

    if any(not 0 <= f <= 1 for f in fractions):
        raise ValueError("Les fractions massiques doivent être entre 0 et 1.")

    if abs(x0 + y0 + meau - 1) > 0.000001:
        raise ValueError("x0 + y0 + meau doit être égal à 1.")

    if not 0 <= mResidus <= m0:
        raise ValueError("Le débit des résidus est invalide.")

    if T3 <= T2:
        raise ValueError("T3 doit être supérieure à T2.")

    if T4 < T5:
        raise ValueError("T4 doit être supérieure ou égale à T5.")

    if x4 <= 0:
        raise ValueError("x4 doit être supérieur à zéro.")

    # 2. Opération unitaire 1 : Filtration

    m1 = m0 - mResidus

    y1 = (y0 * m0) / m1

    # 3. Opération unitaire 2 : Mélange

    m2 = m1 + mR

    y2 = (m1 * y1 + mR * xr) / m2

    if x4 <= y2:
        raise ValueError(
            "La fraction finale x4 doit être supérieure à y2."
        )

    # 4. Opération unitaire 3 : Chauffage

    Q3 = m2 * Cp * (T3 - T2) / 3600

    # 5. Opération unitaire 4 : Évaporation

    m4 = (m2 * y2) / x4

    mv = m2 - m4

    Q4 = (mv * lambda_v) / 3600

    # 6. Opération unitaire 5 : Refroidissement

    Q5 = m4 * Cp * (T4 - T5) / 3600

    # 7. Bilan global de matière

    entrees = m0 + mR

    sorties = mResidus + mv + m4

    ecart_global = entrees - sorties

    # 8. Bilan des matières solubles

    solubles_entrantes = (m0 * y0) + (mR * xr)

    solubles_sortantes = m4 * x4

    ecart_solubles = solubles_entrantes - solubles_sortantes

    # 9. Vérification de la filtration

    residus_theoriques = m0 * x0

    ecart_residus = mResidus - residus_theoriques

    
    return {
        "m0": m0,
        "m1": m1,
        "m2": m2,
        "m4": m4,
        "mv": mv,
        "y1": y1,
        "y2": y2,
        "x4": x4,
        "Q3": Q3,
        "Q4": Q4,
        "Q5": Q5,
        "entrees": entrees,
        "sorties": sorties,
        "ecart_global": ecart_global,
        "solubles_entrantes": solubles_entrantes,
        "solubles_sortantes": solubles_sortantes,
        "ecart_solubles": ecart_solubles,
        "residus_theoriques": residus_theoriques,
        "ecart_residus": ecart_residus
    }
