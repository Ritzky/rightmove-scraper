import re
import json
import requests
from bs4 import BeautifulSoup
import csv

class RightmoveScraper:
    results = []

    def fetch(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print('HTTP GET request to URL: %s' % url, end='')

        response = requests.get(url, headers=headers)
        print(' | Status code: %s' % response.status_code)

        if response.status_code == 200:
            return response
        else:
            return None

    def parse_location_id(self, html):
        data = re.search(r"__PRELOADED_STATE__ = ({.*?})<", html)
        if data:
            json_data = json.loads(data.group(1))
            location_id = json_data.get("searchLocation", {}).get("locationId")
            return location_id
        return None

    def parse_properties(self, html, pp):
        content = BeautifulSoup(html, 'html.parser')

        titles = [title.text.strip() for title in content.findAll('h2', {'class': 'propertyCard-title'})]
        addresses = [address['content'] for address in content.findAll('meta', {'itemprop': 'streetAddress'})]
        descriptions = [description.text for description in content.findAll('span', {'data-test': 'property-description'})]
        prices = []
        for price in content.findAll('div', {'class': 'propertyCard-priceValue'}):
            clean_price = price.text.strip().replace('£', '').replace(',', '').replace('�', '')
            prices.append(clean_price)
        dates = [date.text for date in content.findAll('span', {'class': 'propertyCard-branchSummary-addedOrReduced'})]

        for index in range(len(titles)):
            self.results.append({
                'postcode': pp,
                'title': titles[index],
                'address': addresses[index],
                'description': descriptions[index],
                'price': prices[index],
                'date': dates[index] if index < len(dates) else 'N/A'
            })
            for index in range(len(titles)):
                self.results.append({
                    'postcode': pp,
                    'title': titles[index],
                    'address': addresses[index],
                    'description': descriptions[index],
                    'price': prices[index],
                    'date': dates[index] if index < len(dates) else 'N/A'
                })

    def to_csv(self):
        with open('output.csv', 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.results[0].keys())
            writer.writeheader()
            for row in self.results:
                writer.writerow(row)

        print('Stored results to "output.csv"')

    def run(self, postcode_areas):
        for postcode in postcode_areas:
            print(f"Processing postcode area: {postcode}")
            # Step 1: Get the location identifier based on postcode
            url = f"https://www.rightmove.co.uk/house-prices/{postcode}.html"
            response = self.fetch(url)
            if response:
                location_id = self.parse_location_id(response.text)
                if location_id:
                    # Step 2: Generate the correct property search link with the location identifier
                    final_link = (
                        f"https://www.rightmove.co.uk/property-for-sale/find.html?"
                        f"locationIdentifier=REGION%5E{location_id}&propertyTypes=&"
                        f"includeSSTC=true&mustHave=&dontShow=retirement%2CsharedOwnership&"
                        f"furnishTypes=&keywords="
                    )
                    print("Generated Rightmove URL:", final_link)

                    # Step 3: Fetch properties within the last 14 days
                    response = self.fetch(final_link)
                    if response:
                        self.parse_properties(response.text, postcode)
                    else:
                        print("Failed to fetch property data.")
                else:
                    print("Failed to retrieve the location identifier.")
            else:
                print("Failed to fetch the initial postcode data.")

        self.to_csv()

if __name__ == '__main__':
    postcode_areas = [
        'AB', 'AL', 'B', 'BA', 'BB', 'BD', 'BH', 'BL', 'BN', 'BR', 'BS', 'BT', 'CA',
        'CB', 'CF', 'CH', 'CM', 'CO', 'CR', 'CT', 'CV', 'CW', 'DA', 'DD', 'DE',
        'DG', 'DH', 'DL', 'DN', 'DT', 'DY', 'E', 'EC', 'EH', 'EN', 'EX', 'FK',
        'FY', 'G', 'GL', 'GU', 'GY', 'HA', 'HD', 'HG', 'HP', 'HR', 'HS', 'HU',
        'HX', 'IG', 'IM', 'IP', 'IV', 'JE', 'KA', 'KT', 'KW', 'KY', 'L', 'LA',
        'LD', 'LE', 'LL', 'LN', 'LS', 'LU', 'M', 'ME', 'MK', 'ML', 'N', 'NE',
        'NG', 'NN', 'NP', 'NR', 'NW', 'OL', 'OX', 'PA', 'PE', 'PH', 'PL', 'PO',
        'PR', 'QC', 'RG', 'RH', 'RM', 'S', 'SA', 'SE', 'SG', 'SK', 'SL', 'SM',
        'SN', 'SO', 'SP', 'SR', 'SS', 'ST', 'SW', 'SY', 'TA', 'TD', 'TF', 'TN',
        'TQ', 'TR', 'TS', 'TW', 'UB', 'W', 'WA', 'WC', 'WD', 'WF', 'WN', 'WR',
        'WS', 'WV', 'YO', 'ZE'
    ]
    scraper = RightmoveScraper() 
    scraper.run(postcode_areas)
