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
    def __init__(self, prix_kWh=0.0, abonnement_annuel_fournisseur=0.0, distribution_cta_rate=0.0771, ticgn_rate=0.00837):
        self.prix_kWh = prix_kWh
        self.abonnement_annuel_fournisseur = abonnement_annuel_fournisseur
        self.distribution_cta_rate = distribution_cta_rate
        self.ticgn_rate = ticgn_rate

class input_Contrat:
    def __init__(self, type_tarif_acheminement='T1',CJA_MWh_j=0,CAR_MWh=0,station_meteo="PARIS-MONTSOURIS",profil="P016",reseau_transport="GRTgaz",niv_tarif_region=2, distance=None):
        self.type_tarif_acheminement = type_tarif_acheminement
        self.profil=profil
     
        self.distance = distance  # en km
        self.CJA_MWh_j=CJA_MWh_j #Capacité Journalière Annualisée
        self.CAR_MWh=CAR_MWh  # Capacité Annuelle Réservée en MWh
        self.station_meteo = station_meteo  # Station météo pour le calcul des coefficients
        self.niv_tarif_region = niv_tarif_region  # Niveau tarifaire de la région (1, 2 ou 3)
        self.reseau_transport = reseau_transport  # Réseau de transport (GRTgaz ou Terega)  
       

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
        if (
            "start_date" in coef and "end_date" in coef
            and parse(coef["start_date"]).date() <= facture.start <= parse(coef["end_date"]).date()
        ):
            # Recherche du coefficient Zi
            station = getattr(contrat, "station_meteo", None)
            profil = getattr(contrat, "profil", None)
            zi_value = None
            for zi in coef.get("coefficient_zi", []):
                if zi.get("station_meteo") == station and profil in zi:
                    zi_value = zi[profil]
                    break
            if zi_value is None:
                raise ValueError(f"Pas de coefficient Zi pour la station {station} et le profil {profil}.")
            return coef, zi_value
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



        # T1, T2, T3 : abonnement fixe uniquement
        if self.contrat.type_tarif_acheminement in ["T1", "T2", "T3"]:
            self.euro_terme_souscription_CJA = 0.0
            self.euro_terme_distance = 0.0
            self.euro_cta_base = self.euro_ATRD_fixe
            self.euro_an_cta_base = self.euro_an_ATRD_fixe

            self.euro_ATRD_fixe= round(self.euro_an_ATRD_fixe * self.nb_jour / 365.0, 2)

                                # CTA
            self.euro_CTA = round(self.euro_ATRD_fixe * (self.coeff["distribution_cta_rate"]), 2)
            self.euro_an_CTA = round(self.euro_an_ATRD_fixe * self.coeff["distribution_cta_rate"], 2)

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
            self.euro_ATRD_fixe= round(self.euro_an_ATRD_fixe * self.nb_jour / 365.0, 2)

            self.euro_terme_distance = 0.0
            self.euro_cta_base = self.euro_ATRD_fixe
            self.euro_an_cta_base = self.euro_an_ATRD_fixe 
            print("self.euro_cta_base",self.euro_cta_base)
            print('self.euro_an_cta_base',self.euro_an_cta_base)

                    # CTA
            self.euro_CTA = round(self.euro_ATRD_fixe * (self.coeff["distribution_cta_rate"]+self.coeff["transport_cta_rate"]*self.coeff["coefficient_proportionnalite_cta"]), 2)
            self.euro_an_CTA = round(self.euro_an_ATRD_fixe * self.coeff["distribution_cta_rate"], 2)

        # TP : abonnement + capacité + distance
        elif self.contrat.type_tarif_acheminement == "TP":
            CJA_MWh_j = self.contrat.CJA_MWh_j or 0
            dist = self.contrat.distance or 0
            tarif_capacite = self.coeff["tarif_capacite"]
            tarif_distance = self.coeff["tarif_distance"]
            self.euro_terme_souscription_CJA = round(CJA_MWh_j * tarif_capacite * self.nb_jour, 2)
            self.euro_terme_distance = round(dist * (tarif_distance / 365) * self.nb_jour, 2)

            self.euro_an_ATRD_fixe=self.euro_an_ATRD_fixe+self.euro_terme_souscription_CJA

            self.euro_cta_base = self.euro_ATRD_fixe + self.euro_terme_distance
            self.euro_an_cta_base = self.euro_an_ATRD_fixe + self.euro_terme_distance

        else:
            raise ValueError("Type de tarif inconnu")
        
        if self.tarif is not None:
            print("Calcul du prix de la molécule de gaz...")
            print(f"Facture kWh total: {self.facture.kWh_total}, Prix kWh: {self.tarif.prix_kWh}")
            self.euro_molecule_gaz = round(self.facture.kWh_total * self.tarif.prix_kWh, 2)
        
        #calcul de l'abonnement ATRD Total
        self.euro_an_ATRD_total = self.euro_an_ATRD_fixe + self.euro_an_ATRD_variable
        print("self.euro_an_ATRD_total",self.euro_an_ATRD_total)
        # Abonnement mensuel
        
        self.euro_ATRD_variable = round(self.coeff["prix_proportionnel_euro_kWh"] * self.facture.kWh_total, 2)
        self.euro_ATRD_total = round(self.euro_ATRD_fixe + self.euro_ATRD_variable, 2)



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
    """Calcul détaillé de la part transport (ATRT) pour le gaz naturel."""

    def __init__(self, contrat, facture):
        self.contrat = contrat
        self.facture = facture
        self.coeff, self.zi = find_atrt_coeff(contrat, facture)
        print("self.zi", self.zi)
        # Valeurs des coefficients A
        self.coef_A_GRTgaz = self.coeff.get("coef_A_GRTgaz", 1.0)
        self.coef_A_Terega = self.coeff.get("coef_A_Terega", 1.0)
        print("self.coef_A_GRTgaz", self.coef_A_GRTgaz)
        print("self.coef_A_Terega", self.coef_A_Terega)
        self.coef_A=None
        self.nb_jour = (self.facture.end - self.facture.start).days + 1

        # valeur à calculer
        
        self.CJN = 0.0 # Capacité Journalière Normalisée (CJN) en MWh
        self.modulation_hivernale= 0.0  # Modulation hivernale (en MWh) 
        self.euro_TCS=0.0 #Acheminement réseau principal
        self.euro_TCR=0.0 # Acheminement sur le réseau 
        self.euro_TCL=0.0 #ouscription de capacité journalière de livraison à un point de livraison
        self.NTR=0.0 # Niveau de tarif régional compris entre 0 et 10.
       
        # Résultats
        self.euro_fixe_transport = 0.0
        self.euro_variable_transport = 0.0
        self.euro_compensation_stockage = 0.0
        self.euro_total_ATRT = 0.0

    def calculate(self):
        if self.contrat.reseau_transport == "GRTgaz":
            # Coefficient A pour GRTgaz
            self.coef_A = self.coef_A_GRTgaz
            self.euro_TCR = self.coeff.get("TCR_GRTgaz", 0.0)  # TCR pour GRTgaz
            self.euro_TCL = self.coeff.get("TCL_GRTgaz", 0.0)  # TCL pour GRTgaz
        elif self.contrat.reseau_transport == "Terega":
            # Coefficient A pour Terega
            self.coef_A = self.coef_A_Terega
            self.euro_TCR= self.coeff.get("TCR_Terega", 0.0)  # TCR pour Terega
            self.euro_TCL = self.coeff.get("TCL_Terega", 0.0)
        else:
            self.coef_A = 1
        print("self.coef_A", self.coef_A)


        # calcul de la Capacité Journalière Normalisée = CAR * Coefficient Zi *Coefficient A
        if self.contrat.CAR_MWh is not None and self.contrat.CAR_MWh > 0:
            # lire les coefficients depuis le fichier JSON avec self.coeff["coefficient_Zi"] 
            self.CJN = self.contrat.CAR_MWh * self.zi * self.coef_A
        else:
            self.CJN = 0.0

        #Modulation Hivernale = Capacité de transport – (CAR/365)
        self.modulation_hivernale = self.CJN - (self.contrat.CAR_MWh / 365.0) if self.contrat.CAR_MWh else 0.0
        self.euro_TCS=self.coeff["TCS"] 
        self.NTR = self.contrat.niv_tarif_region  # Niveau tarif régional

        #TS : produit du terme tarifaire de stockage et de la modulation Hivernale
        coef_stockage = self.coeff.get("coef_compensation_stockage", 0)
        print("coef_stockage", coef_stockage)
        self.euro_compensation_stockage = round(self.modulation_hivernale * coef_stockage, 2) if self.modulation_hivernale else 0.0
        self.euro_total_ATRT=self.CJN*(self.euro_TCS+self.euro_TCR*self.NTR+self.euro_TCL)+self.euro_compensation_stockage
        print("self.euro_total_ATRT=", self.CJN, "*(", self.euro_TCS, "+", self.euro_TCR, "*", self.NTR, "+", self.euro_TCL, ")+", self.euro_compensation_stockage    )



      
       
 

        

    def resume(self):
        return pd.DataFrame([
            ("Capacité Journalière Normalisée (CJN) (MWh)", self.CJN),
            ("Modulation hivernale (MWh)", self.modulation_hivernale),
            ("Acheminement sur le réseau principal (€)", self.euro_TCS),
            ("Acheminement sur le réseau régional TCR(€)", self.euro_TCR),
            ("Souscription de capacité journalière de livraison à un point de livraison TCL (€)", self.euro_TCL),
            ("Coefficient A", self.coef_A),
            ("Coefficient Zi", self.zi),
        
            ("Compensation stockage (€)", self.euro_compensation_stockage),
            ("Total ATRT (€)", self.euro_total_ATRT)
        ], columns=["Composante", "Montant (€)"])
