from Facture.ATR_Transport_Distribution import input_Contrat, input_Facture,input_Tarif, ATRD_calculation, ATRT_calculation

if __name__ == "__main__":
    contrat = input_Contrat(type_tarif_acheminement='T3',CJA_MWh_j=93,CAR_MWh=8920.959,profil="P019",station_meteo="NANTES-BOUGUENAIS",reseau_transport="GRTgaz",niv_tarif_region=1)
    facture = input_Facture(start="2024-01-01", end="2024-01-31", kWh_total=1358713)
    tarif = input_Tarif(prix_kWh=0.03171+0.00571)

   
  
    atrd = ATRD_calculation(contrat, facture,tarif)
    atrd.calculate()
    print("=== Distribution (ATRD) ===")
    print(atrd.resume())
    atrt = ATRT_calculation(contrat, facture)
    atrt.calculate()
    print("=== Transport (ATRT) ===")
    print(atrt.resume())