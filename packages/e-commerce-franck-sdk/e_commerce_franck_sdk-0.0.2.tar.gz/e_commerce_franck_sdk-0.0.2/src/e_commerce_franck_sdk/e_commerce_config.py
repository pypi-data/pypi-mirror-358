import os
from dotenv import load_dotenv

load_dotenv()

class E_commerceConfig:
    """Classe de configuration contenant des arguments pour le client SDK.

    Contient la configuration de l'URL de base et du backoff progressif.
    """

    e_commerce_base_url: str
    e_commerce_base_backoff: bool
    e_commerce_base_backoff_max_time: int

    def __init__(
        self,
        e_commerce_base_url: str = None,
        backoff: bool = True,
        backoff_max_time: int = 30,
    ):
        """Constructeur pour la classe de configuration.

        Contient des valeurs d'initialisation pour écraser les valeurs par défaut.

        Args:
        e_commerce_base_base_url (optional):
            L'URL de base à utiliser pour tous les appels d'API. Transmettez-la ou définissez-la dans une variable d'environnement.
        e_commerce_base_backoff:
            Un booléen qui détermine si le SDK doit réessayer l'appel en utilisant un backoff (réessais automatiquement en cas d’échec) lorsque des erreurs se produisent.
        e_commerce_base_backoff_max_time:
            Le nombre maximal de secondes pendant lesquelles le SDK doit continuer à essayer un appel API avant de s'arrêter.
        """

        self.e_commerce_base_url = e_commerce_base_url or os.getenv("e_commerce_API_BASE_URL")
        print(f"Initialisation de e_commerceConfig : URL de base = {self.e_commerce_base_url}")  

        if not self.e_commerce_base_url:
            raise ValueError("L'URL de base n'a pas été fournie. Veuillez définir la variable d'environnement e_commerce_API_BASE_URL.")

        self.e_commerce_backoff = backoff
        self.e_commerce_backoff_max_time = backoff_max_time

    def __str__(self):
        """Retourne une représentation lisible de la configuration e-commerce (utile pour les logs)."""
        return f"{self.e_commerce_base_url} {self.e_commerce_backoff} {self.e_commerce_backoff_max_time}"