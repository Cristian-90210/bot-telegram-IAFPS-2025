
import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import numpy as np

# --- 1. Definirea Stărilor Conversației ---
MENU, MARCA, MODELUL, ALIMENTARE, TIP_COMBUSTIBIL, TRANSMISIE, ANOTIMP, TEMPERATURA, AN, VITEZA, SARCINA, FINAL = range(12)

# --- 2. Datele de Referință (Listă Extinsă de Mărci și Modele) ---
MODELE = {
    "Dacia": ["Logan", "Sandero", "Duster", "Spring", "Jogger", "Lodgy", "Dokker", "Bigster", "1310", "Pick-Up"],
    "Volkswagen": ["Golf", "Passat", "Tiguan", "Polo", "T-Roc", "Touareg", "Arteon", "ID.4", "Caddy", "Sharan"],
    "Skoda": ["Octavia", "Fabia", "Superb", "Kamiq", "Kodiaq", "Scala", "Enyaq", "Karoq", "Citigo", "Rapid"],
    "Renault": ["Clio", "Megane", "Captur", "Talisman", "Koleos", "Arkana", "Zoe", "Kangoo", "Twizy", "Espace"],
    "Opel": ["Astra", "Corsa", "Insignia", "Mokka", "Grandland", "Crossland", "Adam", "Zafira", "Karl", "Vivaro"],
    "Ford": ["Focus", "Fiesta", "Kuga", "Mondeo", "Puma", "Explorer", "Mustang Mach-E", "Ranger", "Edge", "Transit"],
    "Toyota": ["Corolla", "Yaris", "RAV4", "Camry", "C-HR", "Land Cruiser", "Prius", "Aygo", "Hilux", "Supra"],
    "Hyundai": ["i30", "Tucson", "Kona", "Elantra", "Bayon", "Santa Fe", "Ioniq 5", "Veloster", "H1", "i10"],
    "Kia": ["Ceed", "Sportage", "Stonic", "Rio", "Sorento", "Picanto", "EV6", "ProCeed", "Carnival", "Venga"],
    "Nissan": ["Qashqai", "Juke", "X-Trail", "Micra", "Leaf", "Navara", "Patrol", "GT-R", "Ariya", "Almera"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "A-Class", "S-Class", "GLE", "G-Class", "CLA", "EQS", "Vito"],
    "BMW": ["Seria 3", "Seria 5", "X5", "Seria 1", "X3", "X7", "Seria 7", "iX", "X1", "Z4"],
    "Audi": ["A4", "Q5", "A6", "A3", "Q7", "TT", "A1", "Q8", "E-tron", "R8"],
    "Peugeot": ["208", "308", "3008", "508", "2008", "Rifter", "108", "5008", "Traveller", "RCZ"],
    "Fiat": ["Panda", "500", "Tipo", "Punto", "Doblo", "Ducato", "Croma", "Linea", "Bravo", "Fiorino"],
}

# --- BAZĂ DE DATE CU MASA, CAPACITATEA ȘI CONSUM_BAZA ---
DATE_AUTO = {
    # Dacia
    "Logan": {"masa": 1100, "capacitate": 999, "consum_baza": 7.0},
    "Sandero": {"masa": 1150, "capacitate": 999, "consum_baza": 6.5},
    "Duster": {"masa": 1350, "capacitate": 1461, "consum_baza": 6.4},
    "Spring": {"masa": 1000, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Jogger": {"masa": 1250, "capacitate": 999, "consum_baza": 7.0},
    "Lodgy": {"masa": 1200, "capacitate": 1461, "consum_baza": 6.8},
    "Dokker": {"masa": 1300, "capacitate": 1461, "consum_baza": 6.9},
    "Bigster": {"masa": 1450, "capacitate": 1332, "consum_baza": 7.2},
    "1310": {"masa": 950, "capacitate": 1397, "consum_baza": 8.0},
    "Pick-Up": {"masa": 1250, "capacitate": 1598, "consum_baza": 8.5},
    # Volkswagen
    "Golf": {"masa": 1300, "capacitate": 1498, "consum_baza": 6.0},
    "Passat": {"masa": 1500, "capacitate": 1968, "consum_baza": 6.5},
    "Tiguan": {"masa": 1600, "capacitate": 1984, "consum_baza": 7.5},
    "Polo": {"masa": 1100, "capacitate": 999, "consum_baza": 5.5},
    "T-Roc": {"masa": 1450, "capacitate": 1498, "consum_baza": 6.5},
    "Touareg": {"masa": 2100, "capacitate": 2967, "consum_baza": 9.0},
    "Arteon": {"masa": 1600, "capacitate": 1984, "consum_baza": 7.0},
    "ID.4": {"masa": 2000, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Caddy": {"masa": 1500, "capacitate": 1968, "consum_baza": 7.5},
    "Sharan": {"masa": 1800, "capacitate": 1968, "consum_baza": 7.8},
    # Skoda
    "Octavia": {"masa": 1350, "capacitate": 1498, "consum_baza": 5.5},
    "Fabia": {"masa": 1100, "capacitate": 999, "consum_baza": 5.0},
    "Superb": {"masa": 1600, "capacitate": 1968, "consum_baza": 6.5},
    "Kamiq": {"masa": 1250, "capacitate": 999, "consum_baza": 5.5},
    "Kodiaq": {"masa": 1700, "capacitate": 1968, "consum_baza": 7.0},
    "Scala": {"masa": 1200, "capacitate": 999, "consum_baza": 5.2},
    "Enyaq": {"masa": 1800, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Karoq": {"masa": 1500, "capacitate": 1498, "consum_baza": 6.5},
    "Citigo": {"masa": 950, "capacitate": 999, "consum_baza": 5.0},
    "Rapid": {"masa": 1200, "capacitate": 1197, "consum_baza": 5.8},
    # Renault
    "Clio": {"masa": 1100, "capacitate": 999, "consum_baza": 5.5},
    "Megane": {"masa": 1350, "capacitate": 1332, "consum_baza": 7.0},
    "Captur": {"masa": 1300, "capacitate": 1332, "consum_baza": 6.5},
    "Talisman": {"masa": 1500, "capacitate": 1749, "consum_baza": 7.5},
    "Koleos": {"masa": 1700, "capacitate": 1749, "consum_baza": 7.8},
    "Arkana": {"masa": 1450, "capacitate": 1332, "consum_baza": 6.8},
    "Zoe": {"masa": 1500, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Kangoo": {"masa": 1400, "capacitate": 1461, "consum_baza": 7.0},
    "Twizy": {"masa": 475, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Espace": {"masa": 1750, "capacitate": 1997, "consum_baza": 8.0},
    # Opel
    "Astra": {"masa": 1400, "capacitate": 1498, "consum_baza": 6.0},
    "Corsa": {"masa": 1100, "capacitate": 1199, "consum_baza": 5.8},
    "Insignia": {"masa": 1650, "capacitate": 1998, "consum_baza": 7.5},
    "Mokka": {"masa": 1300, "capacitate": 1199, "consum_baza": 6.2},
    "Grandland": {"masa": 1500, "capacitate": 1499, "consum_baza": 6.8},
    "Crossland": {"masa": 1250, "capacitate": 1199, "consum_baza": 6.0},
    "Adam": {"masa": 1100, "capacitate": 998, "consum_baza": 5.5},
    "Zafira": {"masa": 1600, "capacitate": 1499, "consum_baza": 7.2},
    "Karl": {"masa": 950, "capacitate": 999, "consum_baza": 5.2},
    "Vivaro": {"masa": 1800, "capacitate": 1997, "consum_baza": 8.5},
    # Ford
    "Focus": {"masa": 1350, "capacitate": 998, "consum_baza": 6.5},
    "Fiesta": {"masa": 1100, "capacitate": 998, "consum_baza": 5.5},
    "Kuga": {"masa": 1600, "capacitate": 1498, "consum_baza": 7.0},
    "Mondeo": {"masa": 1650, "capacitate": 1998, "consum_baza": 7.2},
    "Puma": {"masa": 1250, "capacitate": 998, "consum_baza": 6.0},
    "Explorer": {"masa": 2200, "capacitate": 2999, "consum_baza": 10.0},
    "Mustang Mach-E": {"masa": 2000, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Ranger": {"masa": 2100, "capacitate": 1996, "consum_baza": 9.0},
    "Edge": {"masa": 1850, "capacitate": 1999, "consum_baza": 8.5},
    "Transit": {"masa": 1900, "capacitate": 1995, "consum_baza": 9.5},
    # Toyota
    "Corolla": {"masa": 1350, "capacitate": 1798, "consum_baza": 6.0},
    "Yaris": {"masa": 1100, "capacitate": 1490, "consum_baza": 5.0},
    "RAV4": {"masa": 1650, "capacitate": 2487, "consum_baza": 7.5},
    "Camry": {"masa": 1600, "capacitate": 2487, "consum_baza": 7.0},
    "C-HR": {"masa": 1400, "capacitate": 1798, "consum_baza": 6.2},
    "Land Cruiser": {"masa": 2400, "capacitate": 2755, "consum_baza": 11.0},
    "Prius": {"masa": 1450, "capacitate": 1798, "consum_baza": 4.5},
    "Aygo": {"masa": 900, "capacitate": 998, "consum_baza": 4.8},
    "Hilux": {"masa": 2000, "capacitate": 2393, "consum_baza": 9.0},
    "Supra": {"masa": 1500, "capacitate": 2998, "consum_baza": 8.5},
    # Hyundai
    "i30": {"masa": 1300, "capacitate": 1482, "consum_baza": 6.0},
    "Tucson": {"masa": 1600, "capacitate": 1598, "consum_baza": 6.3},
    "Kona": {"masa": 1350, "capacitate": 998, "consum_baza": 6.0},
    "Elantra": {"masa": 1350, "capacitate": 1493, "consum_baza": 6.2},
    "Bayon": {"masa": 1150, "capacitate": 998, "consum_baza": 5.5},
    "Santa Fe": {"masa": 1850, "capacitate": 2151, "consum_baza": 8.0},
    "Ioniq 5": {"masa": 2000, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Veloster": {"masa": 1350, "capacitate": 1591, "consum_baza": 7.0},
    "H1": {"masa": 1900, "capacitate": 2497, "consum_baza": 9.5},
    "i10": {"masa": 1000, "capacitate": 998, "consum_baza": 5.2},
    # Kia
    "Ceed": {"masa": 1300, "capacitate": 1482, "consum_baza": 5.7},
    "Sportage": {"masa": 1650, "capacitate": 1598, "consum_baza": 7.0},
    "Stonic": {"masa": 1150, "capacitate": 998, "consum_baza": 5.8},
    "Rio": {"masa": 1100, "capacitate": 1197, "consum_baza": 5.5},
    "Sorento": {"masa": 1950, "capacitate": 2151, "consum_baza": 8.5},
    "Picanto": {"masa": 900, "capacitate": 998, "consum_baza": 5.0},
    "EV6": {"masa": 2000, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "ProCeed": {"masa": 1400, "capacitate": 1482, "consum_baza": 6.0},
    "Carnival": {"masa": 2100, "capacitate": 2199, "consum_baza": 9.0},
    "Venga": {"masa": 1300, "capacitate": 1396, "consum_baza": 6.5},
    # Nissan
    "Qashqai": {"masa": 1450, "capacitate": 1332, "consum_baza": 6.0},
    "Juke": {"masa": 1250, "capacitate": 999, "consum_baza": 6.2},
    "X-Trail": {"masa": 1700, "capacitate": 1497, "consum_baza": 7.5},
    "Micra": {"masa": 1050, "capacitate": 999, "consum_baza": 5.3},
    "Leaf": {"masa": 1550, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Navara": {"masa": 1900, "capacitate": 2299, "consum_baza": 9.0},
    "Patrol": {"masa": 2600, "capacitate": 5552, "consum_baza": 12.0},
    "GT-R": {"masa": 1750, "capacitate": 3799, "consum_baza": 12.0},
    "Ariya": {"masa": 1900, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Almera": {"masa": 1150, "capacitate": 1498, "consum_baza": 6.0},
    # Mercedes-Benz
    "C-Class": {"masa": 1650, "capacitate": 1999, "consum_baza": 6.5},
    "E-Class": {"masa": 1800, "capacitate": 1993, "consum_baza": 7.0},
    "GLC": {"masa": 1900, "capacitate": 1993, "consum_baza": 7.5},
    "A-Class": {"masa": 1400, "capacitate": 1332, "consum_baza": 5.8},
    "S-Class": {"masa": 2000, "capacitate": 2989, "consum_baza": 8.5},
    "GLE": {"masa": 2200, "capacitate": 2989, "consum_baza": 9.5},
    "G-Class": {"masa": 2500, "capacitate": 3982, "consum_baza": 13.0},
    "CLA": {"masa": 1500, "capacitate": 1991, "consum_baza": 6.5},
    "EQS": {"masa": 2400, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "Vito": {"masa": 2000, "capacitate": 1950, "consum_baza": 8.5},
    # BMW
    "Seria 3": {"masa": 1550, "capacitate": 1998, "consum_baza": 6.0},
    "Seria 5": {"masa": 1750, "capacitate": 1998, "consum_baza": 6.8},
    "X5": {"masa": 2150, "capacitate": 2998, "consum_baza": 8.5},
    "Seria 1": {"masa": 1400, "capacitate": 1499, "consum_baza": 6.0},
    "X3": {"masa": 1850, "capacitate": 1998, "consum_baza": 7.5},
    "X7": {"masa": 2400, "capacitate": 2998, "consum_baza": 9.5},
    "Seria 7": {"masa": 2000, "capacitate": 2998, "consum_baza": 8.0},
    "iX": {"masa": 2500, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "X1": {"masa": 1600, "capacitate": 1995, "consum_baza": 6.5},
    "Z4": {"masa": 1450, "capacitate": 1998, "consum_baza": 7.5},
    # Audi
    "A4": {"masa": 1500, "capacitate": 1968, "consum_baza": 6.0},
    "Q5": {"masa": 1850, "capacitate": 1984, "consum_baza": 7.0},
    "A6": {"masa": 1700, "capacitate": 1968, "consum_baza": 6.8},
    "A3": {"masa": 1400, "capacitate": 1498, "consum_baza": 5.8},
    "Q7": {"masa": 2200, "capacitate": 2995, "consum_baza": 8.5},
    "TT": {"masa": 1350, "capacitate": 1984, "consum_baza": 7.0},
    "A1": {"masa": 1150, "capacitate": 999, "consum_baza": 5.5},
    "Q8": {"masa": 2150, "capacitate": 2995, "consum_baza": 8.8},
    "E-tron": {"masa": 2500, "capacitate": 0, "consum_baza": 0.0}, # Electric
    "R8": {"masa": 1650, "capacitate": 5204, "consum_baza": 14.0},
    # Peugeot
    "208": {"masa": 1050, "capacitate": 1199, "consum_baza": 5.6},
    "308": {"masa": 1300, "capacitate": 1199, "consum_baza": 5.5},
    "3008": {"masa": 1500, "capacitate": 1499, "consum_baza": 6.5},
    "508": {"masa": 1550, "capacitate": 1499, "consum_baza": 6.8},
    "2008": {"masa": 1350, "capacitate": 1199, "consum_baza": 6.0},
    "Rifter": {"masa": 1500, "capacitate": 1499, "consum_baza": 6.5},
    "108": {"masa": 900, "capacitate": 998, "consum_baza": 4.8},
    "5008": {"masa": 1600, "capacitate": 1499, "consum_baza": 7.0},
    "Traveller": {"masa": 1750, "capacitate": 1997, "consum_baza": 7.5},
    "RCZ": {"masa": 1400, "capacitate": 1598, "consum_baza": 7.2},
    # Fiat
    "Panda": {"masa": 950, "capacitate": 999, "consum_baza": 6.0},
    "500": {"masa": 1000, "capacitate": 999, "consum_baza": 6.5},
    "Tipo": {"masa": 1300, "capacitate": 1499, "consum_baza": 6.5},
    "Punto": {"masa": 1050, "capacitate": 1242, "consum_baza": 6.2},
    "Doblo": {"masa": 1300, "capacitate": 1598, "consum_baza": 7.0},
    "Ducato": {"masa": 1900, "capacitate": 2200, "consum_baza": 9.0},
    "Croma": {"masa": 1450, "capacitate": 1910, "consum_baza": 8.0},
    "Linea": {"masa": 1200, "capacitate": 1368, "consum_baza": 7.0},
    "Bravo": {"masa": 1300, "capacitate": 1368, "consum_baza": 7.2},
    "Fiorino": {"masa": 1200, "capacitate": 1248, "consum_baza": 7.5},
}

# ============ 3. Regresie liniară pe DATE_AUTO (ML integrat în cod) ============

def _train_linear_regression_from_date_auto():
    """Antrenează un model de regresie liniară simplă pe (masa, capacitate) -> consum_baza."""
    X_list = []
    y_list = []
    for info in DATE_AUTO.values():
        masa = info["masa"]
        capacitate = info["capacitate"]
        consum = info["consum_baza"]
        # Ignorăm modelele electrice (capacitate == 0, consum_baza 0)
        if capacitate > 0 and consum > 0:
            X_list.append([masa, capacitate])
            y_list.append(consum)
    X = np.array(X_list, dtype=float)
    y = np.array(y_list, dtype=float)
    # Adăugăm coloană de 1 pentru intercept
    ones = np.ones((X.shape[0], 1), dtype=float)
    X_aug = np.hstack([ones, X])  # [1, masa, capacitate]
    # Rezolvăm prin least squares: beta = (X^T X)^(-1) X^T y
    beta, *_ = np.linalg.lstsq(X_aug, y, rcond=None)
    # beta[0] = intercept, beta[1] = coef_masa, beta[2] = coef_capacitate
    return beta

# Antrenăm la încărcarea modulului (o singură dată)
LR_BETA = _train_linear_regression_from_date_auto()

def predict_consum_linear(masa: float, capacitate: float) -> float:
    """Predicție AI (regresie liniară) pentru consum_baza, pe baza masei și capacității motorului."""
    intercept, coef_masa, coef_cap = LR_BETA
    return float(intercept + coef_masa * masa + coef_cap * capacitate)

# --- 4. Funcția de Calcul a Consumului ---
def calculeaza_consum(an, masa, capacitate, viteza, sarcina, alimentare, tip_combustibil=None, model=None, transmisie=None, anotimp=None, temperatura=None):
    """Calculează consumul bazat pe consum_baza predefinit pentru model, ajustat cu factori realiști, inclusiv transmisie, anotimp și temperatură."""
    if an <= 2009:
        return "ERROR_AN", 0.0, 0.0

    if capacitate == 0 or alimentare == "Electric":
        return "ELECTRIC", 0.0, 0.0

    # Preia consum_baza predefinit din baza de date pentru model
    consum_baza = DATE_AUTO.get(model, {"consum_baza": 6.5})["consum_baza"]

    # Factori pentru tipul de combustibil (influențează eficiența: valori <1 = mai eficient)
    combustibil_factors = {
        "Benzină": {"95": 1.00, "98": 0.98, "100": 0.95},
        "Diesel": {"Standard": 1.02, "Premium": 0.97},
        "Hibrid": {"Conventional": 0.85, "Plug-in": 0.75},
    }
    factor_comb = combustibil_factors.get(alimentare, {}).get(tip_combustibil, 1.0)

    # Factori realiști de ajustare
    vechime = 2025 - an
    factor_eficienta = 0.95 if vechime < 5 else 1.0 if vechime < 10 else 1.05  # Modele noi mai eficiente

    # Influențe ajustate pentru realism (bazate pe consum_baza predefinit)
    factor_viteza = 1.0 + max(0, (viteza - 90) / 90 * 0.15)   # Crește cu 15% per 90km/h peste 90
    factor_masa = 1.0 + max(0, (masa - 1200) / 1200 * 0.10)   # +10% per 20% masă extra
    factor_sarcina = 1.0 + sarcina * 0.20                     # +20% la sarcină full

    # Factori pentru transmisie
    factor_transmisie = {
        "Manuală": 1.00,
        "Automată": 1.05,
        "CVT": 1.08,
        "Dublu ambreiaj": 1.03
    }.get(transmisie, 1.00)

    # Factori pentru anotimp
    factor_anotimp = {
        "Iarnă": 1.10,
        "Primăvară": 1.02,
        "Vară": 0.98,
        "Toamnă": 1.01
    }.get(anotimp, 1.00)

    # Factor pentru temperatură (doar dacă <10°C, crește consumul)
    factor_temperatura = 1.00
    if temperatura is not None and temperatura < 10:
        factor_temperatura = 1 + (10 - temperatura) / 40.0  # la 0°C +0.25, la -10°C +0.5

    consum_optim = consum_baza * factor_eficienta * factor_masa
    consum_real = consum_optim * factor_viteza * factor_sarcina * factor_comb * factor_transmisie * factor_anotimp * factor_temperatura

    return "OK", consum_real, consum_optim

# --- 5. Funcția de Recomandare Personalizată ---
def generate_recommendation(model, masa, consum_real, alimentare, tip_combustibil=None, transmisie=None, anotimp=None, temperatura=None):
    """Generează o recomandare personalizată bazată pe model, masă, consumul real, alimentare, tip combustibil, transmisie, anotimp și temperatură."""
    if alimentare == "Electric":
        return (
            "⚡️ **Sfaturi pentru Vehicule Electrice:** Eficiența depinde mult de temperatură și de stilul de "
            "conducere regenerativă. Încearcă să pre-condiționezi habitaclul când mașina este încă conectată la "
            "încărcător. Folosește modul 'Brake' (regenerare maximă) în oraș pentru a recupera energie."
        )

    combustibil_tip = f" ({tip_combustibil})" if tip_combustibil else ""
    if consum_real < 6.0:
        advice = f"Felicitări! Mașina ta {alimentare.lower()}{combustibil_tip} este extrem de eficientă, iar stilul tău de condus este excelent. "
        if alimentare == "Benzină" and tip_combustibil == "100":
            advice += "Benzina 100 octani reduce detonarea și îmbunătățește performanța la turații înalte."
        elif alimentare == "Diesel" and tip_combustibil == "Premium":
            advice += "Dieselul premium reduce emisiile și îmbunătățește lubrifierea motorului."
        else:
            advice += "Verifică regulat presiunea în anvelope – o presiune optimă poate salva încă 0.1-0.2 L/100km."
    elif 6.0 <= consum_real <= 8.0:
        advice = f"Consumul estimat pentru {alimentare.lower()}{combustibil_tip} este moderat. "
        if alimentare == "Hibrid" and tip_combustibil == "Plug-in":
            advice += "Încărcarea regulată a bateriei maximizează modul electric, reducând consumul de combustibil cu până la 50%."
        else:
            advice += "Încearcă să folosești frâna de motor și să anticipezi traficul pentru a evita frânările și accelerările bruște. Utilizarea Cruise Control pe distanțe lungi ajută la menținerea eficienței."
    else:
        advice = f"Consumul pentru {alimentare.lower()}{combustibil_tip} este ridicat. "
        if alimentare == "Benzină" and tip_combustibil == "95":
            advice += "Treci la o benzină cu octan mai mare (98 sau 100) pentru a reduce consumul cu 2-5%."
        else:
            advice += "Verifică dacă filtrele de aer și ulei sunt schimbate la timp. De asemenea, evită să transporți obiecte grele inutile, deoarece fiecare kilogram contează la accelerare."

    if transmisie == "Automată":
        advice += "\n\n**Sfat pentru transmisie automată:** Schimbă manual în modul 'Eco' pe autostradă pentru a economisi până la 0.5 L/100km."
    elif transmisie == "CVT":
        advice += "\n\n**Sfat pentru CVT:** Evită accelerările bruște; menține viteza constantă pentru eficiență maximă."

    if anotimp == "Iarnă":
        advice += "\n\n**Sfat pentru iarnă:** Folosește uleiuri speciale pentru frig și verifică bateria – iarna crește consumul cu 10%."
    elif anotimp == "Vară":
        advice += "\n\n**Sfat pentru vară:** Aerul condiționat adaugă 0.5-1 L/100km; folosește recircularea aerului."

    if temperatura is not None and temperatura < 10:
        advice += f"\n\n**Sfat pentru temperatură scăzută ({temperatura}°C):** Încălzirea habitaclului crește consumul; preîncălzește motorul 2-3 minute înainte de pornire."

    if masa > 1750:
        advice += (
            "\n\n**Sfaturi pentru vehicule mari/SUV (Masa > 1750 kg):** Datorită aerodinamicii și masei considerabile, "
            "reducerea vitezei cu doar 10 km/h la drum lung poate aduce economii substanțiale. Evită să porți cutii "
            "portbagaj pe plafon dacă nu sunt necesare."
        )
    elif masa < 1300:
        advice += (
            "\n\n**Sfaturi pentru vehicule compacte/mici (Masa < 1300 kg):** Deși mașina este ușoară, "
            "menținerea turațiilor motorului în zona de cuplu maxim (de obicei 2000-3000 rpm) este cheia. Nu subtura "
            "și nu supratura motorul."
        )
    return advice

# --- Meniu Principal ---
def get_menu_keyboard():
    menu_buttons = [
        ["Estimare Consum"],
        ["Propuneri", "Date de Contact"],
        ["Despre Bot"],
        ["Raportare Problemă"]
    ]
    return ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True, one_time_keyboard=False)

def get_final_keyboard():
    final_buttons = [
        ["Începe o nouă estimare", "Înapoi la Meniu"]
    ]
    return ReplyKeyboardMarkup(final_buttons, resize_keyboard=True, one_time_keyboard=True)

def add_back_button(buttons):
    buttons_with_back = buttons + [["Înapoi"]]
    return ReplyKeyboardMarkup(buttons_with_back, resize_keyboard=True, one_time_keyboard=True)

# --- Handler pentru blocarea textului acolo unde nu este permis ---
async def block_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Te rog folosește butoanele."
    )

# --- Funcții pentru Meniul Principal ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['data'] = {}
    await update.message.reply_text(
        " **Meniu Principal**\n\n"
        "Alege o opțiune din butoanele de mai jos:",
        reply_markup=get_menu_keyboard(),
        parse_mode='Markdown'
    )
    return MENU

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Despre Bot":
        await update.message.reply_text(
            "📖 **Despre Bot**\n\n"
            "Acest bot reprezintă un estimator inteligent de consum auto, conceput pentru a oferi utilizatorilor o evaluare cât mai realistă a consumului de combustibil al vehiculului propriu, în condiții de utilizare reale. Spre deosebire de valorile standard declarate de producători, care sunt obținute în medii controlate de testare, acest sistem ia în considerare o gamă largă de factori dinamici ce influențează direct consumul efectiv.\n\n"
            "Estimarea consumului se realizează pe baza unor parametri precum marca și modelul autoturismului, anul fabricației, tipul transmisiei, viteza medie de deplasare, gradul de încărcare al vehiculului, anotimpul și temperatura ambientală, factori care au un impact semnificativ asupra eficienței energetice. Toate aceste date sunt procesate prin intermediul unui model de inteligență artificială bazat pe regresie liniară, antrenat să identifice relațiile dintre variabile și să genereze o estimare coerentă și adaptată contextului specific de utilizare.\n\n"
	    "Baza de date a aplicației este extinsă și include peste 150 de modele auto populare, aparținând unor mărci larg răspândite precum Dacia, Volkswagen, Toyota și altele, ceea ce asigură o acoperire relevantă pentru majoritatea utilizatorilor.\n\n"
	    "Prin această abordare, botul devine un instrument util atât pentru șoferii care doresc să își optimizeze consumul de combustibil, cât și pentru scopuri educaționale sau analitice, oferind o perspectivă practică asupra modului în care diferiți factori influențează consumul real al unui autoturism.\n\n"
            "Mulțumim că îl folosești! ",
            reply_markup=get_menu_keyboard(),
            parse_mode='Markdown'
        )
        return MENU
    elif text == "Date de Contact":
        await update.message.reply_text(
            "📞 **Date de Contact**\n\n"
            "Dezvoltator: 𝕮𝖗𝖎𝖘𝖙𝖎𝖆𝖓\n"
            "Email: postcrist@gmail.com\n\n"
            "Ne poți contacta pentru întrebări sau feedback!",
            reply_markup=get_menu_keyboard(),
            parse_mode='Markdown'
        )
        return MENU
    elif text == "Propuneri":
        await update.message.reply_text(
            "💡 **Propuneri**\n\n"
            "Ai idei pentru îmbunătățiri? Sugestii pentru noi funcții sau modele auto?\n\n"
            "Trimite-mi un mesaj direct cu propunerea ta sau folosește butonul de mai jos pentru a contacta dezvoltatorul.\n\n"
            "Mulțumim pentru contribuție! ",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Contactează Dezvoltatorul", url="https://t.me/pcrist_7")]]),
            parse_mode='Markdown'
        )
        return MENU
    elif text == "Raportare Problemă":
        await update.message.reply_text(
            "🐛 **Raportare Problemă**\n\n"
            "Ai întâlnit o eroare sau un bug? Descrie problema în detaliu (inclusiv modelul auto, pașii reprodusi).\n\n"
            "Vom analiza și rezolva cât mai curând posibil!\n\n"
            "Trimite raportul la: postcrist@gmail.com",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Raportează pe Telegram", url="https://t.me/pcrist_7")]]),
            parse_mode='Markdown'
        )
        return MENU
    elif text == "Estimare Consum":
        context.user_data['data'] = {}
        marci_list = list(MODELE.keys())
        marci_buttons = [marci_list[i:i + 2] for i in range(0, len(marci_list), 2)]
        reply_keyboard = add_back_button(marci_buttons)
        await update.message.reply_text(
            "👋 Bun venit la Estimatorul de Consum Auto! Vom trece prin câțiva pași.\n\n"
            "Pasul 1: Alege Marca automobilului:",
            reply_markup=reply_keyboard
        )
        return MARCA
    else:
        await update.message.reply_text(
            "❌ Opțiune invalidă. Te rog alege din meniu.",
            reply_markup=get_menu_keyboard()
        )
        return MENU

# --- 5. Funcțiile de Gestionare a Conversației ---
async def get_marca(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Înapoi":
        await update.message.reply_text(
            "🍽️ **Meniu Principal**\n\nAlege o opțiune din butoanele de mai jos:",
            reply_markup=get_menu_keyboard(),
            parse_mode='Markdown'
        )
        return MENU
    marca = text
    if marca not in MODELE:
        marci_list = list(MODELE.keys())
        marci_buttons = [marci_list[i:i + 2] for i in range(0, len(marci_list), 2)]
        reply_keyboard = add_back_button(marci_buttons)
        await update.message.reply_text(
            f"❌ '{marca}' nu este o opțiune validă. Te rog alege din butoanele de mai jos:",
            reply_markup=reply_keyboard
        )
        return MARCA
    context.user_data['data']['marca'] = marca
    modele_list = MODELE[marca]
    modele_buttons = [modele_list[i:i + 2] for i in range(0, len(modele_list), 2)]
    reply_keyboard = add_back_button(modele_buttons)
    await update.message.reply_text(
        f"Pasul 2: Ai ales {marca}. Acum alege Modelul:",
        reply_markup=reply_keyboard
    )
    return MODELUL

async def get_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Preia modelul, extrage Masa, Capacitatea și consum_baza din baza de date,
    calculează și afișează și predicția AI (regresie liniară),
    apoi cere Tipul de Alimentare.
    """
    text = update.message.text.strip()
    if text == "Înapoi":
        marci_list = list(MODELE.keys())
        marci_buttons = [marci_list[i:i + 2] for i in range(0, len(marci_list), 2)]
        reply_keyboard = add_back_button(marci_buttons)
        await update.message.reply_text(
            "Pasul 1: Alege Marca automobilului:",
            reply_markup=reply_keyboard
        )
        return MARCA

    model = text
    marca = context.user_data['data']['marca']

    if model not in MODELE[marca]:
        modele_list = MODELE[marca]
        modele_buttons = [modele_list[i:i + 2] for i in range(0, len(modele_list), 2)]
        reply_keyboard = add_back_button(modele_buttons)
        await update.message.reply_text(
            f"❌ '{model}' nu este un model valid pentru {marca}. Te rog alege din butoane:",
            reply_markup=reply_keyboard
        )
        return MODELUL

    context.user_data['data']['model'] = model
    date_tehnice = DATE_AUTO.get(model, {"masa": 1400, "capacitate": 1600, "consum_baza": 6.5})
    context.user_data['data']['masa'] = date_tehnice['masa']
    context.user_data['data']['capacitate'] = date_tehnice['capacitate']
    context.user_data['data']['consum_baza'] = date_tehnice['consum_baza']

    # Predicție AI: regresie liniară antrenată pe toată baza DATE_AUTO
    if date_tehnice["capacitate"] > 0:
        consum_ai = predict_consum_linear(date_tehnice["masa"], date_tehnice["capacitate"])
        ai_text = f"\nPredicție AI (Regresie Liniară, doar după masă + motor): **{consum_ai:.2f} L/100km**"
    else:
        ai_text = "\nPredicție AI: N/A pentru modele electrice."

    await update.message.reply_text(
        f"⚙️ Specificații predefinite pentru **{model}**:\n\n"
        f"Masa la gol (medie): **{date_tehnice['masa']} kg**\n"
        f"Capacitate cilindrică: **{date_tehnice['capacitate']} cm³**\n"
        f"Consum mediu de referință: **{date_tehnice['consum_baza']:.1f} L/100km**"
        f"{ai_text}",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )

    alimentare_buttons = [
        ["Benzină", "Diesel"],
        ["Hibrid", "Electric"]
    ]
    reply_keyboard = add_back_button(alimentare_buttons)
    await update.message.reply_text(
        "Pasul 3: Alege Tipul de Alimentare:",
        reply_markup=reply_keyboard
    )
    return ALIMENTARE

async def get_alimentare(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Înapoi":
        modele_list = MODELE[context.user_data['data']['marca']]
        modele_buttons = [modele_list[i:i + 2] for i in range(0, len(modele_list), 2)]
        reply_keyboard = add_back_button(modele_buttons)
        await update.message.reply_text(
            f"Pasul 2: Ai ales {context.user_data['data']['marca']}. Acum alege Modelul:",
            reply_markup=reply_keyboard
        )
        return MODELUL

    alimentare = text
    valid_alimentare = ["Benzină", "Diesel", "Hibrid", "Electric"]
    if alimentare not in valid_alimentare:
        alimentare_buttons = [["Benzină", "Diesel"], ["Hibrid", "Electric"]]
        reply_keyboard = add_back_button(alimentare_buttons)
        await update.message.reply_text(
            "❌ Opțiune invalidă. Te rog alege Tipul de Alimentare din butoane:",
            reply_markup=reply_keyboard
        )
        return ALIMENTARE

    context.user_data['data']['alimentare'] = alimentare
    if alimentare == "Electric":
        transmisie_buttons = [["Manuală"], ["Automată"], ["CVT"], ["Dublu ambreiaj"]]
        reply_keyboard = add_back_button(transmisie_buttons)
        await update.message.reply_text(
            "Pasul 4: Alege Tipul de Transmisie:",
            reply_markup=reply_keyboard
        )
        return TRANSMISIE
    else:
        if alimentare == "Benzină":
            tip_buttons = [["95", "98"], ["100"]]
        elif alimentare == "Diesel":
            tip_buttons = [["Standard", "Premium"]]
        elif alimentare == "Hibrid":
            tip_buttons = [["Conventional", "Plug-in"]]
        reply_keyboard = add_back_button(tip_buttons)
        await update.message.reply_text(
            f"Pasul 4: Alege tipul specific de {alimentare.lower()}:",
            reply_markup=reply_keyboard
        )
        return TIP_COMBUSTIBIL

async def get_tip_combustibil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Înapoi":
        alimentare_buttons = [["Benzină", "Diesel"], ["Hibrid", "Electric"]]
        reply_keyboard = add_back_button(alimentare_buttons)
        await update.message.reply_text(
            "Pasul 3: Alege Tipul de Alimentare:",
            reply_markup=reply_keyboard
        )
        return ALIMENTARE

    tip = text
    alimentare = context.user_data['data']['alimentare']
    valid_tips = {
        "Benzină": ["95", "98", "100"],
        "Diesel": ["Standard", "Premium"],
        "Hibrid": ["Conventional", "Plug-in"]
    }
    if tip not in valid_tips.get(alimentare, []):
        if alimentare == "Benzină":
            tip_buttons = [["95", "98"], ["100"]]
        elif alimentare == "Diesel":
            tip_buttons = [["Standard", "Premium"]]
        elif alimentare == "Hibrid":
            tip_buttons = [["Conventional", "Plug-in"]]
        reply_keyboard = add_back_button(tip_buttons)
        await update.message.reply_text(
            f"❌ Opțiune invalidă pentru {alimentare}. Te rog alege din butoane:",
            reply_markup=reply_keyboard
        )
        return TIP_COMBUSTIBIL

    context.user_data['data']['tip_combustibil'] = tip
    transmisie_buttons = [["Manuală"], ["Automată"], ["CVT"], ["Dublu ambreiaj"]]
    reply_keyboard = add_back_button(transmisie_buttons)
    await update.message.reply_text(
        "Pasul 5: Alege Tipul de Transmisie:",
        reply_markup=reply_keyboard
    )
    return TRANSMISIE

async def get_transmisie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Înapoi":
        if context.user_data['data'].get('tip_combustibil'):
            alimentare = context.user_data['data']['alimentare']
            if alimentare == "Benzină":
                tip_buttons = [["95", "98"], ["100"]]
            elif alimentare == "Diesel":
                tip_buttons = [["Standard", "Premium"]]
            elif alimentare == "Hibrid":
                tip_buttons = [["Conventional", "Plug-in"]]
            reply_keyboard = add_back_button(tip_buttons)
            await update.message.reply_text(
                f"Pasul 4: Alege tipul specific de {alimentare.lower()}:",
                reply_markup=reply_keyboard
            )
            return TIP_COMBUSTIBIL
        else:
            alimentare_buttons = [["Benzină", "Diesel"], ["Hibrid", "Electric"]]
            reply_keyboard = add_back_button(alimentare_buttons)
            await update.message.reply_text(
                "Pasul 3: Alege Tipul de Alimentare:",
                reply_markup=reply_keyboard
            )
            return ALIMENTARE

    transmisie = text
    valid_transmisie = ["Manuală", "Automată", "CVT", "Dublu ambreiaj"]
    if transmisie not in valid_transmisie:
        transmisie_buttons = [["Manuală"], ["Automată"], ["CVT"], ["Dublu ambreiaj"]]
        reply_keyboard = add_back_button(transmisie_buttons)
        await update.message.reply_text(
            "❌ Opțiune invalidă. Te rog alege Tipul de Transmisie din butoane:",
            reply_markup=reply_keyboard
        )
        return TRANSMISIE

    context.user_data['data']['transmisie'] = transmisie
    anotimp_buttons = [["Iarnă", "Primăvară"], ["Vară", "Toamnă"]]
    reply_keyboard = add_back_button(anotimp_buttons)
    await update.message.reply_text(
        "Pasul 6: Alege Anotimpul:",
        reply_markup=reply_keyboard
    )
    return ANOTIMP

async def get_anotimp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Înapoi":
        transmisie_buttons = [["Manuală"], ["Automată"], ["CVT"], ["Dublu ambreiaj"]]
        reply_keyboard = add_back_button(transmisie_buttons)
        await update.message.reply_text(
            "Pasul 5: Alege Tipul de Transmisie:",
            reply_markup=reply_keyboard
        )
        return TRANSMISIE

    anotimp = text
    valid_anotimp = ["Iarnă", "Primăvară", "Vară", "Toamnă"]
    if anotimp not in valid_anotimp:
        anotimp_buttons = [["Iarnă", "Primăvară"], ["Vară", "Toamnă"]]
        reply_keyboard = add_back_button(anotimp_buttons)
        await update.message.reply_text(
            "❌ Opțiune invalidă. Te rog alege Anotimpul din butoane:",
            reply_markup=reply_keyboard
        )
        return ANOTIMP

    context.user_data['data']['anotimp'] = anotimp
    temp_buttons = [["-10°C", "0°C"], ["10°C", "15°C"], ["20°C", "25°C"]]
    reply_keyboard = add_back_button(temp_buttons)
    await update.message.reply_text(
        "Pasul 7: Alege Temperatura de afară (în °C):",
        reply_markup=reply_keyboard
    )
    return TEMPERATURA

async def get_temperatura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Înapoi":
        anotimp_buttons = [["Iarnă", "Primăvară"], ["Vară", "Toamnă"]]
        reply_keyboard = add_back_button(anotimp_buttons)
        await update.message.reply_text(
            "Pasul 6: Alege Anotimpul:",
            reply_markup=reply_keyboard
        )
        return ANOTIMP

    temp_map = {"-10°C": -10, "0°C": 0, "10°C": 10, "20°C": 20, "30°C": 30, "40°C": 40}
    if text not in temp_map:
        temp_buttons = [["-10°C", "0°C"], ["10°C", "20°C"], ["30°C", "40°C"]]
        reply_keyboard = add_back_button(temp_buttons)
        await update.message.reply_text(
            "❌ Opțiune invalidă. Te rog alege Temperatura din butoane:",
            reply_markup=reply_keyboard
        )
        return TEMPERATURA

    temperatura = temp_map[text]
    context.user_data['data']['temperatura'] = temperatura

    all_years = [str(y) for y in range(2010, 2026)]
    year_buttons = [all_years[i:i + 4] for i in range(0, len(all_years), 4)]
    reply_keyboard = add_back_button(year_buttons)
    await update.message.reply_text(
        "Pasul 8: Alege Anul fabricației:",
        reply_markup=reply_keyboard
    )
    return AN

async def get_an(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Înapoi":
        temp_buttons = [["-10°C", "0°C"], ["10°C", "20°C"], ["30°C", "40°C"]]
        reply_keyboard = add_back_button(temp_buttons)
        await update.message.reply_text(
            "Pasul 7: Alege Temperatura de afară (în °C):",
            reply_markup=reply_keyboard
        )
        return TEMPERATURA
    try:
        an = int(text)
        if an < 2010 or an > 2025:
            await update.message.reply_text("❌ Anul trebuie să fie un an valid din butoane (2010-2025).")
            return AN

        context.user_data['data']['an'] = an
        viteza_keyboard = [["Înapoi"]]
        reply_keyboard = ReplyKeyboardMarkup(viteza_keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text(
            "Pasul 9: Introdu Viteza medie de deplasare în km/h (doar numere, ex: 60):",
            reply_markup=reply_keyboard
        )
        return VITEZA
    except ValueError:
        all_years = [str(y) for y in range(2010, 2026)]
        year_buttons = [all_years[i:i + 4] for i in range(0, len(all_years), 4)]
        reply_keyboard = add_back_button(year_buttons)
        await update.message.reply_text("❌ Te rog alege un an din butoanele afișate.", reply_markup=reply_keyboard)
        return AN

async def get_viteza(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Înapoi":
        temp_buttons = [["-10°C", "0°C"], ["10°C", "20°C"], ["30°C", "40°C"]]
        reply_keyboard = add_back_button(temp_buttons)
        await update.message.reply_text(
            "Pasul 7: Alege Temperatura de afară (în °C):",
            reply_markup=reply_keyboard
        )
        return TEMPERATURA
    try:
        viteza = float(text)
        if viteza < 0 or viteza > 200:
            viteza_keyboard = [["Înapoi"]]
            reply_keyboard = ReplyKeyboardMarkup(viteza_keyboard, resize_keyboard=True, one_time_keyboard=False)
            await update.message.reply_text("❌ Viteza trebuie să fie o valoare rezonabilă (ex: 10-200 km/h).", reply_markup=reply_keyboard)
            return VITEZA

        context.user_data['data']['viteza'] = viteza
        sarcina_buttons = [["0% - Mașina goală"], ["50% - Parțial încărcată"], ["100% - Complet încărcată"]]
        reply_keyboard = add_back_button(sarcina_buttons)
        await update.message.reply_text(
            "Pasul 10: Alege Procentul de sarcină:",
            reply_markup=reply_keyboard
        )
        return SARCINA
    except ValueError:
        viteza_keyboard = [["Înapoi"]]
        reply_keyboard = ReplyKeyboardMarkup(viteza_keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("❌ Te rog introdu o valoare numerică validă pentru viteză.", reply_markup=reply_keyboard)
        return VITEZA

async def get_sarcina(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()
    if text == "înapoi":
        sarcina_buttons = [["0% - Mașina goală"], ["50% - Parțial încărcată"], ["100% - Complet încărcată"]]
        reply_keyboard = add_back_button(sarcina_buttons)
        await update.message.reply_text(
            "Pasul 10: Alege Procentul de sarcină:",
            reply_markup=reply_keyboard
        )
        return SARCINA

    sarcina_map = {
        "0% - mașina goală": 0.0,
        "50% - parțial încărcată": 0.5,
        "100% - complet încărcată": 1.0
    }
    sarcina = sarcina_map.get(text)
    if sarcina is None:
        sarcina_buttons = [["0% - Mașina goală"], ["50% - Parțial încărcată"], ["100% - Complet încărcată"]]
        reply_keyboard = add_back_button(sarcina_buttons)
        await update.message.reply_text(
            "❌ Opțiune de sarcină invalidă. Te rog alege din butoane:",
            reply_markup=reply_keyboard
        )
        return SARCINA

    data = context.user_data['data']
    data['sarcina'] = sarcina
    model = data['model']

    status, consum_real, consum_optim = calculeaza_consum(
        data['an'], data['masa'], data['capacitate'], data['viteza'], data['sarcina'],
        data['alimentare'], data.get('tip_combustibil'), model,
        data.get('transmisie'), data.get('anotimp'), data.get('temperatura')
    )

    marca_model = f"**{data.get('marca', 'N/A')} {data.get('model', 'N/A')}**"
    alimentare_tip = data.get('alimentare', 'N/A')
    tip_combustibil = data.get('tip_combustibil', 'N/A')
    transmisie_tip = data.get('transmisie', 'N/A')
    anotimp_tip = data.get('anotimp', 'N/A')
    temperatura_tip = data.get('temperatura', 'N/A')

    if status == "ERROR_AN":
        await update.message.reply_text(
            "⚠️ Nu se calculează, deoarece mașinile fabricate înainte de 2010 au un consum extrem de mare. Ne cerem scuze.\n\n"
            "Folosește butonul de mai jos pentru a începe o nouă estimare.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Dorești să estimezi consumul pentru o altă mașină?",
            reply_markup=get_final_keyboard()
        )
        return FINAL
    elif status == "ELECTRIC":
        recomandare_electrica = generate_recommendation(data['model'], data['masa'], consum_real, alimentare_tip, None, transmisie_tip, anotimp_tip, temperatura_tip)
        await update.message.reply_text(
            "Procesăm rezultatele...",
            reply_markup=ReplyKeyboardRemove()
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=(
                "⚡️ **Estimarea Consumului Finalizată!**\n\n"
                "--- **Rezultate Consum Estimativ** ---\n"
                "❌ Modelul Electric nu poate fi calculat în L/100km.\n"
                "Consumul este estimat în **kWh/100km** (uzual între 15-25 kWh/100km).\n\n"
                "--- **Detalii Vehicul și Condiții de Drum** ---\n"
                f"Marca/Model: {marca_model} (**{alimentare_tip}**)\n"
                f"Transmisie: {transmisie_tip}\n"
                f"Anotimp: {anotimp_tip}\n"
                f"Temperatură: {temperatura_tip}°C\n"
                f"An fabricație: {data['an']}\n"
                f"Masa de referință: {data['masa']} kg\n"
                f"Viteza medie: {data['viteza']:.1f} km/h\n"
                f"Sarcină aplicată: {int(data['sarcina'] * 100)}%\n\n"
                "--- **Recomandarea Ta Personalizată** ---\n"
                f"{recomandare_electrica}"
            ),
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="--- **Următorul Pas** ---\nCe vrei să faci în continuare?",
            reply_markup=get_final_keyboard(),
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
    else:
        recomandare = generate_recommendation(data['model'], data['masa'], consum_real, alimentare_tip, tip_combustibil, transmisie_tip, anotimp_tip, temperatura_tip)
        sarcina_procent = int(data['sarcina'] * 100)

        message_parts = [
            "✅ **Estimarea Consumului Finalizată!**",
            "\n\n--- **Rezultate Consum Estimativ** ---",
            f"📉 Consum optim (Bază): {consum_optim:.2f} L/100km",
            f"⛽ **Consum REAL estimat:** **{consum_real:.2f} L/100km**",
            "\n\n--- **Detalii Vehicul și Condiții de Drum** ---",
            f"Marca/Model: {marca_model}",
            f"Alimentare: **{alimentare_tip}**",
            f"Tip combustibil: **{tip_combustibil}**",
            f"Transmisie: **{transmisie_tip}**",
            f"Anotimp: **{anotimp_tip}**",
            f"Temperatură: **{temperatura_tip}°C**",
            f"An fabricație: {data['an']}",
            f"Masa de referință: {data['masa']} kg",
            f"Capacitate cilindrică: {data['capacitate']} cm³",
            f"Consum mediu de referință: {data['consum_baza']:.1f} L/100km",
            f"Viteza medie: {data['viteza']:.1f} km/h",
            f"Sarcină aplicată: {sarcina_procent}%",
            "\n\n--- **Recomandarea Ta Personalizată** ---\n"
            f"{recomandare}"
        ]

        await update.message.reply_text(
            "Procesăm rezultatele...",
            reply_markup=ReplyKeyboardRemove()
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="\n".join(message_parts),
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="--- **Următorul Pas** ---\nCe vrei să faci în continuare?",
            reply_markup=get_final_keyboard(),
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
    return FINAL

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Conversație anulată. Scrie /start pentru a reveni la meniu.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def handle_final_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == "Începe o nouă estimare":
        context.user_data['data'] = {}
        marci_list = list(MODELE.keys())
        marci_buttons = [marci_list[i:i + 2] for i in range(0, len(marci_list), 2)]
        reply_keyboard = add_back_button(marci_buttons)
        await update.message.reply_text(
            "👋 Bun venit din nou! Pasul 1: Alege Marca automobilului:",
            reply_markup=reply_keyboard
        )
        return MARCA
    elif text == "Înapoi la Meniu":
        await update.message.reply_text(
            "🍽️ **Meniu Principal**\n\nAlege o opțiune din butoanele de mai jos:",
            reply_markup=get_menu_keyboard(),
            parse_mode='Markdown'
        )
        return MENU
    else:
        await update.message.reply_text(
            "❌ Opțiune invalidă. Te rog alege din butoane.",
            reply_markup=get_final_keyboard()
        )
        return FINAL

# --- 6. Funcția Principală de Rulare a Botului ---
def main() -> None:
    TOKEN = "8422879122:AAFE-gMbHtiwVt6P7-vm_qbkqDDxURssD9E"
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                MessageHandler(filters.Regex("^(Estimare Consum|Propuneri|Date de Contact|Despre Bot|Raportare Problemă)$"), handle_menu),
                MessageHandler(filters.ALL, block_text_input)
            ],
            MARCA: [
                MessageHandler(filters.Regex("^(" + "|".join(MODELE.keys()) + ")$"), get_marca),
                MessageHandler(filters.Regex("^Înapoi$"), get_marca),
                MessageHandler(filters.ALL, block_text_input)
            ],
            MODELUL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_model),
                MessageHandler(filters.ALL, block_text_input)
            ],
            ALIMENTARE: [
                MessageHandler(filters.Regex("^(Benzină|Diesel|Hibrid|Electric)$"), get_alimentare),
                MessageHandler(filters.Regex("^Înapoi$"), get_alimentare),
                MessageHandler(filters.ALL, block_text_input)
            ],
            TIP_COMBUSTIBIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_tip_combustibil),
                MessageHandler(filters.Regex("^Înapoi$"), get_tip_combustibil),
                MessageHandler(filters.ALL, block_text_input)
            ],
            TRANSMISIE: [
                MessageHandler(filters.Regex("^(Manuală|Automată|CVT|Dublu ambreiaj)$"), get_transmisie),
                MessageHandler(filters.Regex("^Înapoi$"), get_transmisie),
                MessageHandler(filters.ALL, block_text_input)
            ],
            ANOTIMP: [
                MessageHandler(filters.Regex("^(Iarnă|Primăvară|Vară|Toamnă)$"), get_anotimp),
                MessageHandler(filters.Regex("^Înapoi$"), get_anotimp),
                MessageHandler(filters.ALL, block_text_input)
            ],
            TEMPERATURA: [
                MessageHandler(filters.Regex("^(-10°C|0°C|10°C|20°C|30°C|40°C)$"), get_temperatura),
                MessageHandler(filters.Regex("^Înapoi$"), get_temperatura),
                MessageHandler(filters.ALL, block_text_input)
            ],
            AN: [
                MessageHandler(filters.Regex("^(201[0-9]|202[0-5])$"), get_an),
                MessageHandler(filters.Regex("^Înapoi$"), get_an),
                MessageHandler(filters.ALL, block_text_input)
            ],
            VITEZA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_viteza)
            ],
            SARCINA: [
                MessageHandler(filters.Regex("^(0% - Mașina goală|50% - Parțial încărcată|100% - Complet încărcată|înapoi)$"), get_sarcina),
                MessageHandler(filters.ALL, block_text_input)
            ],
            FINAL: [
                MessageHandler(filters.Regex("^(Începe o nouă estimare|Înapoi la Meniu)$"), handle_final_options),
                MessageHandler(filters.ALL, block_text_input)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    print("Botul rulează!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
