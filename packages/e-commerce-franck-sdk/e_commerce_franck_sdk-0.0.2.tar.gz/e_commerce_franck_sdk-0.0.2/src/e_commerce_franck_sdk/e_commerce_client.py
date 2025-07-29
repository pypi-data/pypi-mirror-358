import httpx 
from typing import Optional, Literal, Union, List
from .schemas import VenteFaitBase, ClientDimBase, ProduitDimBase, CommandeDimBase, Analytics
from .e_commerce_config import E_commerceConfig 

import pandas as pd

# Client SDK pour interagir avec l'API e-commerce.
# Fournit des méthodes pour accéder aux endpoints liés aux ventes, clients, produits, commandes et statistiques.
class E_commerceClient:
    # Initialise le client avec une configuration personnalisée ou par défaut.
    def __init__(self, config: Optional[E_commerceConfig] = None):
        self.config = config or E_commerceConfig()
        self.e_commerce_base_url = self.config.e_commerce_base_url
        
    # Formate les données selon le format de sortie désiré.
    def _format_output(self, data, model, output_format: Literal["pydantic", "dict", "pandas"]):
        """
        - 'pydantic' → liste d'objets typés
        - 'dict' → liste de dictionnaires
        - 'pandas' → DataFrame
        """
        if output_format == "pydantic":
            return [model(**item) for item in data]
        elif output_format == "dict":
            return data
        elif output_format == "pandas":
            import pandas as pd
            return pd.DataFrame(data)
        else:
            raise ValueError("Format de sortie invalide. Choisissez parmi : 'pydantic', 'dict' ou 'pandas'.")

    # Vérifie la santé de l'API.
    def health_check(self) -> dict:
        url = f"{self.e_commerce_base_url}/"
        response = httpx.get(url)
        response.raise_for_status()
        return response.json()

    # Récupère une vente spécifique à partir d’un triple ID.
    def get_vente(self, id_commande: int, id_client: int, id_produit: int) -> VenteFaitBase:
        url = f"{self.e_commerce_base_url}/vente/{id_commande}/{id_client}/{id_produit}"
        response = httpx.get(url)
        response.raise_for_status()
        return VenteFaitBase(**response.json())

    # Liste les ventes avec pagination et filtres.
    def list_ventes(
        self,
        skip: int = 0,
        limit: int = 100,
        id_commande: Optional[int] = None,
        id_client: Optional[int] = None,
        id_produit: Optional[int] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[VenteFaitBase], List[dict], "pd.DataFrame"]:
        url = f"{self.e_commerce_base_url}/ventes"
        params = {"skip": skip, "limit": limit}
        if id_commande:
            params["id_commande"] = id_commande
        if id_client:
            params["id_client"] = id_client
        if id_produit:
            params["id_produit"] = id_produit
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), VenteFaitBase, output_format)

    # Récupère un client par son ID.
    def get_client(self, id_client: int) -> ClientDimBase:
        url = f"{self.e_commerce_base_url}/client/{id_client}"
        response = httpx.get(url)
        response.raise_for_status()
        return ClientDimBase(**response.json())

    # Liste les clients avec pagination et possibilité de filtrer par nom et prénom.
    def list_clients(
        self,
        skip: int = 0,
        limit: int = 100,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[ClientDimBase], List[dict], "pd.DataFrame"]:
        url = f"{self.e_commerce_base_url}/clients"
        params = {"skip": skip, "limit": limit}
        if nom:
            params["nom"] = nom
        if prenom:
            params["prenom"] = prenom
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), ClientDimBase, output_format)

    # Récupère un produit par son ID.
    def get_produit(self, id_produit: int) -> ProduitDimBase:
        url = f"{self.e_commerce_base_url}/produit/{id_produit}"
        response = httpx.get(url)
        response.raise_for_status()
        return ProduitDimBase(**response.json())

    # Liste les produits avec pagination et filtres (nom, catégorie).
    def list_produits(
        self,
        skip: int = 0,
        limit: int = 100,
        nom: Optional[str] = None,
        categorie: Optional[str] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[ProduitDimBase], List[dict], "pd.DataFrame"]:
        url = f"{self.e_commerce_base_url}/produits"
        params = {"skip": skip, "limit": limit}
        if nom:
            params["nom"] = nom
        if categorie:
            params["categorie"] = categorie
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), ProduitDimBase, output_format)

    # Récupère une commande par son ID.
    def get_commande(self, id_commande: int) -> CommandeDimBase:
        url = f"{self.e_commerce_base_url}/commande/{id_commande}"
        response = httpx.get(url)
        response.raise_for_status()
        return CommandeDimBase(**response.json())

    # Liste les commandes avec pagination et filtres (date, statut).
    def list_commandes(
        self,
        skip: int = 0,
        limit: int = 100,
        date_commande: Optional[str] = None,
        statut: Optional[str] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[CommandeDimBase], List[dict], "pd.DataFrame"]:
        url = f"{self.e_commerce_base_url}/commandes"
        params = {"skip": skip, "limit": limit}
        if date_commande:
            params["date_commande"] = date_commande
        if statut:
            params["statut"] = statut
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), CommandeDimBase, output_format)

    # Récupère les statistiques globales (total clients, ventes, etc.).
    def get_analytics(self) -> Analytics:
        url = f"{self.e_commerce_base_url}/analytics"
        response = httpx.get(url)
        response.raise_for_status()
        return Analytics(**response.json())

