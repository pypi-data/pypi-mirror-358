from datetime import date
import json
import os
from dateutil.parser import parse
import pandas as pd

current_directory = os.path.dirname(os.path.abspath(__file__))
coeffs_atrd_path = os.path.join(current_directory, 'coefficients_gaz_ATRD.json')
coeffs_atrt_path = os.path.join(current_directory, 'coefficients_gaz_ATRT.json')

class input_Facture:
    def __init__(self, start, end, kWh_total=0):
        if not isinstance(start, date):
            start = parse(start).date()
        if not isinstance(end, date):
            end = parse(end).date()
        self.start = start
        self.end = end
        self.kWh_total = kWh_total

class input_Tarif:
    def __init__(self, prix_kWh=0.0, abonnement_annuel_fournisseur=0.0, cta_rate=0.0771, ticgn_rate=0.00837):
        self.prix_kWh = prix_kWh
        self.abonnement_annuel_fournisseur = abonnement_annuel_fournisseur
        self.cta_rate = cta_rate
        self.ticgn_rate = ticgn_rate

class input_Contrat:
    def __init__(self, type_tarif_acheminement='T1',CJA_MWh_j=0, capacite=None, distance=None):
        self.type_tarif_acheminement = type_tarif_acheminement
        self.CAR=None
        self.profil=None
        self.capacite = capacite  # en kWh/jour
        self.distance = distance  # en km
        self.CJA_MWh_j=CJA_MWh_j #Capacité Journalière Annualisée
       

def find_atrd_coeff(contrat, facture):
    with open(coeffs_atrd_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for coef in data["coefficients"]:
        if (
            coef["type_tarif_acheminement"] == contrat.type_tarif_acheminement
            and parse(coef["start_date"]).date() <= facture.start <= parse(coef["end_date"]).date()
        ):
            return coef
    raise ValueError("Aucun coefficient ATRD trouvé pour cette période et ce type de tarif.")

def find_atrt_coeff(contrat, facture):
    with open(coeffs_atrt_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for coef in data["coefficients"]:
        # On ne filtre plus sur la version, seulement sur la période
        if (
            "start_date" in coef and "end_date" in coef
            and parse(coef["start_date"]).date() <= facture.start <= parse(coef["end_date"]).date()
        ):
            return coef
    raise ValueError("Aucun coefficient ATRT trouvé pour cette période.")

def calcul_prix_molecule_gaz(facture, tarif):
    """
    Calcule le prix de la molécule de gaz (part fournisseur) en euros.
    :param facture: instance de input_Facture
    :param tarif: instance de input_Tarif (prix_kWh doit être renseigné)
    :return: montant en euros
    """
    return round(facture.kWh_total * tarif.prix_kWh, 2)

class ATRD_calculation:
    """Calcul de la part distribution (ATRD) pour le gaz naturel."""
    def __init__(self, contrat, facture,tarif=None):
        self.contrat = contrat
        self.facture = facture
        self.tarif = tarif
        self.coeff = find_atrd_coeff(contrat, facture)
        self.nb_jour = (self.facture.end - self.facture.start).days + 1
        self.euro_molecule_gaz = 0.0

        # Résultats
        self.euro_ATRD_fixe= 0.0
        self.euro_ATRD_variable = 0.0
        self.euro_terme_souscription_CJA = 0.0
        self.euro_terme_distance = 0.0
        self.euro_CTA = 0.0
        self.euro_an_CTA = 0.0
        self.euro_TICGN = 0.0
        self.euro_total_HTVA = 0.0
        self.euro_total_TTC = 0.0
        self.taxes_contributions = 0.0

        # sur l'année
        self.euro_an_ATRD_fixe = 0.0
        self.euro_an_ATRD_variable = 0.0
        self.euro_an_ATRD_total = 0.0


    def calculate(self):
        
        # Abonnement (proratisé)
        self.euro_an_ATRD_fixe = self.coeff["ATRD_fixe"]
        print("self.euro_an_ATRD_fixe",self.euro_an_ATRD_fixe)
        self.euro_an_ATRD_variable = self.coeff["prix_proportionnel_euro_kWh"]*self.facture.kWh_total
        print("self.euro_an_ATRD_variable",self.euro_an_ATRD_variable)
        self.euro_an_ATRD_total = self.euro_an_ATRD_fixe + self.euro_an_ATRD_variable
        print("self.euro_an_ATRD_total",self.euro_an_ATRD_total)

        self.euro_ATRD_fixe= round(self.coeff["ATRD_fixe"] * self.nb_jour / 365.0, 2)
        self.euro_ATRD_variable = round(self.coeff["prix_proportionnel_euro_kWh"] * self.facture.kWh_total, 2)
        self.euro_ATRD_total = round(self.euro_ATRD_fixe + self.euro_ATRD_variable, 2)
        # T1, T2, T3 : abonnement fixe uniquement
        if self.contrat.type_tarif_acheminement in ["T1", "T2", "T3"]:
            self.euro_terme_souscription_CJA = 0.0
            self.euro_terme_distance = 0.0
            euro_cta_base = self.euro_ATRD_fixe
            euro_an_cta_base = self.euro_an_ATRD_fixe

        # T4 : abonnement + capacité journalière
        elif self.contrat.type_tarif_acheminement == "T4":
            CJA_MWh_j = self.contrat.CJA_MWh_j or 0
            if CJA_MWh_j > 500:
                tarif_capacite = self.coeff["souscription_annuelle_capacite_euro_kWh_j_supp500"]
            else:
                tarif_capacite = self.coeff["souscription_annuelle_capacite_euro_kWh_j_inf500"]
            self.euro_terme_souscription_CJA = round(CJA_MWh_j*1000 * tarif_capacite, 2)
            print("self.euro_terme_souscription_CJA",self.euro_terme_souscription_CJA)

            self.euro_an_ATRD_fixe=self.euro_an_ATRD_fixe+self.euro_terme_souscription_CJA

            self.euro_terme_distance = 0.0
            euro_cta_base = self.euro_ATRD_fixe+ self.euro_terme_souscription_CJA
            euro_an_cta_base = self.euro_an_ATRD_fixe +  self.euro_terme_souscription_CJA

        # TP : abonnement + capacité + distance
        elif self.contrat.type_tarif_acheminement == "TP":
            CJA_MWh_j = self.contrat.CJA_MWh_j or 0
            dist = self.contrat.distance or 0
            tarif_capacite = self.coeff["tarif_capacite"]
            tarif_distance = self.coeff["tarif_distance"]
            self.euro_terme_souscription_CJA = round(CJA_MWh_j * tarif_capacite * self.nb_jour, 2)
            self.euro_terme_distance = round(dist * (tarif_distance / 365) * self.nb_jour, 2)
            euro_cta_base = self.euro_ATRD_fixe+ self.euro_terme_souscription_CJA + self.euro_terme_distance
            euro_an_cta_base = self.euro_an_ATRD_fixe + self.euro_terme_souscription_CJA + self.euro_terme_distance

        else:
            raise ValueError("Type de tarif inconnu")
        
        if self.tarif is not None:
            print("Calcul du prix de la molécule de gaz...")
            print(f"Facture kWh total: {self.facture.kWh_total}, Prix kWh: {self.tarif.prix_kWh}")
            self.euro_molecule_gaz = round(self.facture.kWh_total * self.tarif.prix_kWh, 2)


        # CTA
        self.euro_CTA = round(euro_cta_base * self.coeff["cta_rate"], 2)
        self.euro_an_CTA = round(euro_an_cta_base * self.coeff["cta_rate"], 2)
        # TICGN
        self.euro_TICGN = round(self.facture.kWh_total * self.coeff["ticgn_rate"], 2)
        # Total HTVA
        self.euro_total_HTVA = round(
            self.euro_ATRD_fixe+ self.euro_terme_souscription_CJA + self.euro_terme_distance + self.euro_CTA + self.euro_TICGN+self.euro_molecule_gaz, 2
        )
        # TVA (5,5% sur abonnement+CTA, 20% sur le reste)
        self.euro_TVA_5_5 = round((self.euro_ATRD_fixe+ self.euro_CTA) * 0.055, 2)
        # TVA 20% est appliquée sur l'achat de molecule, sur la part variable de l'abonnement et sur la TICGN
        self.euro_TVA_20 = round((self.euro_ATRD_variable+self.euro_molecule_gaz+ self.euro_TICGN) * 0.20, 2)
        self.euro_TVA = self.euro_TVA_5_5 + self.euro_TVA_20
        # Total TTC
        self.euro_total_TTC = round(self.euro_total_HTVA + self.euro_TVA, 2)

        # somme CTA et TICFE
        self.taxes_contributions = round(self.euro_CTA + self.euro_TICGN, 2)

    def resume(self):
        return pd.DataFrame([
            ("Abonnement mensuel total (€) : ", self.euro_ATRD_total),
            ("- Abonnement mensuel fixe (€) ", self.euro_ATRD_fixe),
            ("- Abonnement mensuel variable (€) ", self.euro_ATRD_variable),
            ("Terme Souscription de capacité CJA_MWh_j (€)  ", self.euro_terme_souscription_CJA),
            ("Terme distance (€)  ", self.euro_terme_distance),
            ("Taxes et contributions (€) : ", self.taxes_contributions),
            ("- CTA (€)", self.euro_CTA),
            ("- TICGN (€)", self.euro_TICGN),
            ("Total HTVA (€)", self.euro_total_HTVA),
            ("TVA 5,5% (€)", self.euro_TVA_5_5),
            ("TVA 20% (€)", self.euro_TVA_20),
            ("Total TVA (€)", self.euro_TVA),
            ("Total TTC (€)", self.euro_total_TTC),
            ("Prix de la molécule de gaz (€)", self.euro_molecule_gaz),
            ("Annuel ATRD total (€)", self.euro_an_ATRD_total),
            ("Annuel ATRD fixe (€)", self.euro_an_ATRD_fixe),
            ("Annuel ATRD variable (€)", self.euro_an_ATRD_variable),
            ("CTA annuel (€)", self.euro_an_CTA),
        ], columns=["Composante", "Montant (€)"])

class ATRT_calculation:
    """Calcul de la part transport (ATRT) pour le gaz naturel."""
    def __init__(self, contrat, facture):
        self.contrat = contrat
        self.facture = facture
        self.coeff = find_atrt_coeff(contrat, facture)
        self.nb_jour = (self.facture.end - self.facture.start).days + 1

        # Résultats
        self.euro_ATRT = 0.0

    def calculate(self):
        coef_ATRT = self.coeff["coef_ATRT"]
        self.euro_ATRT = round(self.facture.kWh_total * coef_ATRT, 2)

    def resume(self):
        return pd.DataFrame([
            ("ATRT (€)", self.euro_ATRT)
        ], columns=["Composante", "Montant (€)"])