from Facture.ATR_Transport_Distribution import input_Contrat, input_Facture,input_Tarif, ATRD_calculation, ATRT_calculation

if __name__ == "__main__":
    contrat = input_Contrat(type_tarif_acheminement='T3',CJA=130)
    facture = input_Facture(start="2022-12-26", end="2023-01-25", kWh_total=71475)
    tarif = input_Tarif(prix_kWh=0.15855)

   
  
    atrd = ATRD_calculation(contrat, facture,tarif)
    atrd.calculate()
    print("=== Distribution (ATRD) ===")
    print(atrd.resume())
    atrt = ATRT_calculation(contrat, facture)
    atrt.calculate()
    print("=== Transport (ATRT) ===")
    print(atrt.resume())