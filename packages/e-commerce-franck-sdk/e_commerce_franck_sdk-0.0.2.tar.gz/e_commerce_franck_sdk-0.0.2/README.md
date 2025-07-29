# E-commerce SDK - `e-commerce-franck-sdk`

Un SDK Python simple pour interagir avec l’API REST E-commerce. Il est conçu pour les **Data Analysts** et **Data Scientists**, avec une prise en charge native de **Pydantic**, **dictionnaires** et **DataFrames Pandas**.

[![PyPI version](https://badge.fury.io/py/moviesdk.svg)](https://badge.fury.io/py/moviesdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## Installation

```bash
pip install e-commerce-franck-sdk
```

---

## Configuration

```python
from e-commerce-franck-sdk import E_commerceClient, E_commerceConfig

config = E_commerceConfig(e_commerce_base_url="https://projet-backend-e-commerce-1.onrender.com")
client = E_commerceClient(config=config)
```

---

## Tester le SDK

### 1. Health check

```python
client.health_check()
```

### 2. Récupérer une vente

```python
vente = client.get_vente(id_commande=9, id_client=9, id_produit=9)
print("Vente récupérée :", vente)
```

### 3. Récupère la Liste des ventes avec pagination et filtres.

```python
ventes = client.list_ventes(output_format="pandas")
print(ventes)
```

---

## Modes de sortie disponibles
Toutes les methodes de filtrage par id sont : (`get_vente`, `get_client`, `get_produit`, etc). 
Toutes les méthodes de liste (`list_ventes`, `list_clients`, `list_produits`, etc.) peuvent retourner :

- des objets **Pydantic** (défaut)
- des **dictionnaires**
- des **DataFrames Pandas**

Exemple :

```python
client.list_produits(limit=10, output_format="dict")
client.list_clients(limit=10, output_format="pandas")
```

---

## Tester en local

Vous pouvez aussi utiliser une API locale :
### Conteneur Kocker
```python
config = E_commerceConfig(e_commerce_base_url="http://localhost:80")
client = E_commerceClient(config=config)
```

---

## Public cible

- Data Analysts
- Data Scientists
- Étudiants et curieux en Data
- Développeurs Python

---

## Licence

MIT License

---

## Liens utiles

- API Render : [https://projet-backend-e-commerce-1.onrender.com](https://projet-backend-e-commerce-1.onrender.com)
- PyPI : [https://pypi.org/project/e-commerce-franck-sdk](https://pypi.org/project/e-commerce-franck-sdk)