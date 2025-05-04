# CoinMarketCap Data Scraper

A desktop application that extracts cryptocurrency data from CoinMarketCap including the top 10 cryptocurrencies. It features a search functionality for historical data of specific coins and exports results to CSV files.

## Features

- Display top 10 cryptocurrencies from CoinMarketCap
- Search for historical data of specific cryptocurrencies
- Export data to CSV files
- Clean/reset functionality

## Prerequisites

Before running this application, you need to have the following installed:

- Python 3.6 or higher
- Chrome browser (for Selenium WebDriver)
- ChromeDriver compatible with your Chrome version

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/coinmarketcap-scraper.git
cd coinmarketcap-scraper
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

Or install them individually:
```
pip install beautifulsoup4 selenium PyQt5
```

## Usage

1. Run the application:
```
python coinMarketcap.py
```

2. The main interface will display:
   - The current top 10 cryptocurrencies from CoinMarketCap
   - A search bar to look up historical data for specific coins
   - Export button to save data as CSV
   - Clean button to reset the view

3. To search for a specific cryptocurrency:
   - Enter the coin name or symbol in the search bar
   - Select search parameters if applicable
   - Click the search button

4. To export data:
   - After retrieving data, click the export button
   - Choose a location to save the CSV file

## Troubleshooting

- **WebDriver Issues**: Make sure your ChromeDriver version matches your Chrome browser version
- **Data Not Loading**: Check your internet connection or if CoinMarketCap website structure has changed
- **UI Not Displaying Properly**: Ensure you have the correct PyQt5 version installed

## Dependencies

- sys
- csv
- time
- datetime
- BeautifulSoup4
- Selenium
- PyQt5

