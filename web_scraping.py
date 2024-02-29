import requests
from bs4 import BeautifulSoup

base_url = "https://www.cotesdarmor.com/a-voir-a-faire/gastronomie-bretonne/restaurants/"
page_param = "id1[currentPage]"
total_pages = 7 # ajustez le nombre de pages que vous souhaitez parcourir


def get_content() -> str:
    content = ""
    for page_num in range(1, total_pages + 1):
        url = f"{base_url}?{page_param}={page_num}"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            for link in links:
                href = link.get('href')
                if href and href.startswith('/fr/'):
                    absolute_url = f"https://www.cotesdarmor.com{href}"
                    response_link = requests.get(absolute_url)

                    if response_link.status_code == 200:
                        soup_link = BeautifulSoup(response_link.text, 'html.parser')
                        description_div = soup_link.find('div', class_='lcol-8_md-12 main-content-col')
                        title_div = soup_link.find('div', class_='lgrid-noGutter-noWrap-spaceBetween-middle')
                        address_icon_span = soup_link.find('div', class_='coordonnees pt-40 pb-40 pr-40 pl-20')
                        if title_div:
                                title = title_div.find('h1').get_text(strip=True)
                                content += f"Titre: {title}\n"
                        
                        if address_icon_span:
                            address_span = address_icon_span.find_next('span', class_='lcol')
                            if address_span:
                                address_text = ' '.join(address_span.stripped_strings)
                                content += f"Adresse: {address_text}\n"

                        if description_div:
                            
                            div_text = ' '.join(description_div.stripped_strings)
                            content += f"Description: {div_text}\n\n"
                    else:
                        print(f"Échec de la récupération de la page {absolute_url}. Statut {response_link.status_code}")

        else:
            print(f"Échec de la récupération de la page {url}. Statut {response.status_code}")
    return content

