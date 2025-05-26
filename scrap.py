import requests
from bs4 import BeautifulSoup

# URL de la page à scraper (à adapter selon le site réel)
url = 'URL_DE_LA_PAGE_DE_TRAINS_MASSY'

# Envoyer la requête HTTP
response = requests.get(url)
response.raise_for_status()

# Parser le contenu HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Exemple de sélection des éléments (à adapter selon la structure réelle)
# Supposons que les départs soient dans des divs avec classe 'departure'
departures = soup.find_all('div', class_='departure')

# Extraire et afficher les prochains départs
for departure in departures:
    train_time = departure.find('span', class_='time').text
    train_dest = departure.find('span', class_='destination').text
    print(f"Prochain train à {train_time} vers {train_dest}")
