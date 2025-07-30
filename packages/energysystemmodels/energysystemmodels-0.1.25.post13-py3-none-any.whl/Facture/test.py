from Facture.ATR_Transport_Distribution import input_Contrat, input_Facture,input_Tarif, ATRD_calculation, ATRT_calculation

if __name__ == "__main__":
    contrat = input_Contrat(type_tarif_acheminement='T4',CJA_MWh_j=130)
    facture = input_Facture(start="2025-01-01", end="2025-01-31", kWh_total=0)
    tarif = input_Tarif(prix_kWh=0.15855)

   
  
    atrd = ATRD_calculation(contrat, facture,tarif)
    atrd.calculate()
    print("=== Distribution (ATRD) ===")
    print(atrd.resume())
    atrt = ATRT_calculation(contrat, facture)
    atrt.calculate()
    print("=== Transport (ATRT) ===")
    print(atrt.resume())