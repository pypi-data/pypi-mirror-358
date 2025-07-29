# Fichier de schémas Pydantic
# Ce fichier contient les modèles de données utilisés pour représenter
# les objets retournés par l'API e-commerce.
# Pydantic est utilisé ici pour garantir la validation et la cohérence
# des données reçues depuis l'API.

# L'API étant en lecture seule, seuls les modèles de sortie
# (réponses) sont définis. Aucune validation d'entrée n'est requise côté SDK.

# Importation des modules nécessaires
from pydantic import BaseModel
from typing import List, Optional 

# --- Modèles de sortie pour les ventes ---
class VenteFaitBase(BaseModel):
    id_commande: int
    id_client: int
    id_produit: int
    quantite_totale: int
    vente_totale: float

    class Config:
        from_attributes  = True  # Permet à Pydantic de lire les données des objets ORM

# --- Modèle de sortie pour les clients ---
class ClientDimBase(BaseModel):
    id_client: int
    nom: str
    prenom: str
    gender: str
    email: str
    telephone: str
    adresse: str

    class Config:
        from_attributes  = True # Permet à Pydantic de lire les données des objets ORM

# --- Modèle de sortie pour les produits ---
class ProduitDimBase(BaseModel):
    id_produit: int
    nom: str
    categorie: str

    class Config:
        from_attributes  = True  # Permet à Pydantic de lire les données des objets ORM

# --- Modèle de sortie pour les commandes ---
class CommandeDimBase(BaseModel):
    id_commande: int
    date_commande: str  # Utiliser str pour la date, Pydantic gère la conversion
    statut: str

    class Config:
        from_attributes  = True  # Permet à Pydantic de lire les données des objets ORM 

class Analytics(BaseModel):
    ventes_count: int
    clients_count: int
    produits_count: int
    commandes_count: int

    class Config:
        from_attributes  = True

