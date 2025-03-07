import sys
import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal


class Worker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, driver, currency_details, table):
        super().__init__()
        self.driver = driver
        self.currency_details = currency_details
        self.table = table

    def run(self):
        self.progress.emit("Fetching data...")
        self.extract_data()

        self.progress.emit("Loading may be take 5 to 10 minutes")
        self.press_load_more()

        self.progress.emit("Data fetch complete.")
        self.finished.emit()

    def extract_data(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        table = soup.find("table")
        if table:
            tbody = table.find('tbody')
            rows = tbody.find_all('tr')

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 7:  
                    cols = [ele.text.strip() for ele in cols]
                    self.currency_details.append({
                        "Date": cols[0],
                        "Open($)": cols[1],
                        "High($)": cols[2],
                        "Low($)": cols[3],
                        "Close($)": cols[4],
                        "Volume($)": cols[5],
                        "Market Cap($)": cols[6]
                    })

    def press_load_more(self):
        while True:
            try:
                load_more = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More')]"))
                )
                load_more.click()
                time.sleep(2)  
                self.extract_data()  
            except Exception as e:
                print("No more 'Load More' button found or an error occurred. Stopping loop.")
                print(e)
                break


class CoinMarketApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.top_10_coins()
        self.display_top_10_coins()

    def initUI(self):
        self.setWindowTitle("Coin Market")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.label = QLabel("Enter Coin Name in lowercase:")
        self.layout.addWidget(self.label)

        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.on_search_bar_enter) 
        self.layout.addWidget(self.search_bar)

        self.coin_dropdown = QComboBox()
        self.coin_dropdown.addItem("None") 
        self.layout.addWidget(self.coin_dropdown)

        self.refresh_top_10_btn = QPushButton("Refresh Top 10")
        self.refresh_top_10_btn.clicked.connect(self.refresh_top_10)
        self.layout.addWidget(self.refresh_top_10_btn)
        
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.get_data_btn = QPushButton("Get Data")
        self.get_data_btn.clicked.connect(self.get_data)
        self.layout.addWidget(self.get_data_btn)

        self.save_csv_btn = QPushButton("Save as CSV")
        self.save_csv_btn.clicked.connect(self.save_csv)
        self.layout.addWidget(self.save_csv_btn)

        self.clean_data_btn = QPushButton("Clean Data CSV")
        self.clean_data_btn.clicked.connect(self.clean_data)
        self.layout.addWidget(self.clean_data_btn)

        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)

        self.dev_label = QLabel("Developed by Mahmoud")
        self.layout.addWidget(self.dev_label)

        self.setLayout(self.layout)
    def on_search_bar_enter(self):
        """Handle Enter key press in the search bar."""
        self.name_of_coin = self.search_bar.text().strip().lower()
        if self.name_of_coin:
            self.status_label.setText(f"Selected coin: {self.name_of_coin}")
            self.coin_dropdown.setCurrentText("None")
        else:
            self.status_label.setText("Please enter a valid coin name.")
        
    def refresh_top_10(self):
        """Refresh the top 10 coins data and update the display."""
        self.status_label.setText("Refreshing top 10 coins...")
        self.top_10_coins()  
        self.display_top_10_coins()  
        self.status_label.setText("Top 10 coins refreshed.")

    def top_10_coins(self):
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        url = "https://coinmarketcap.com/"
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        soup = BeautifulSoup(driver.page_source, 'lxml')
        table_topCoin = soup.find("table")
        if table_topCoin:
            tbody = table_topCoin.find('tbody')
            rows = tbody.find_all('tr')

            self.coin_names = []
            top_10_data = []
            for row in rows[:10]:
                cols = row.find_all('td')
                cols[2] = cols[2].find('p')
                name = cols[2].text.strip().lower()
                self.coin_names.append(name)
                self.coin_dropdown.addItem(name)

                # Extract other details for CSV
                price = cols[3].text.strip()
                change_1h = cols[4].text.strip()
                change_24h = cols[5].text.strip()
                change_7d = cols[6].text.strip()
                market_cap = cols[7].text.strip()
                volume_24h = cols[8].text.strip()
                circulating_supply = cols[9].text.strip()

                top_10_data.append([name, price, change_1h, change_24h, change_7d, market_cap, volume_24h, circulating_supply])

        # Save top 10 coins data to CSV
        csv_filename = "top_10_coins.csv"
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Price", "1h %", "24h %", "7d %", "Market Cap", "Volume(24h)", "Circulating Supply"])
            writer.writerows(top_10_data)

        print(f"Top 10 coins data saved to {csv_filename}")
        driver.quit()

    def display_top_10_coins(self):
        csv_filename = "top_10_coins.csv"
        with open(csv_filename, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)
            data = list(reader)

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(item))

    def get_data(self):
        if self.coin_dropdown.currentText() == "None":
            if not hasattr(self, 'name_of_coin') or not self.name_of_coin:
                self.status_label.setText("Please select a coin or enter a coin name.")
                return
        else:
            self.name_of_coin = self.coin_dropdown.currentText().strip().lower()

        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        url = f"https://coinmarketcap.com/currencies/{self.name_of_coin}/historical-data/"
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        self.currency_details = []

        # Start worker thread
        self.worker = Worker(self.driver, self.currency_details, self.table)
        self.worker.finished.connect(self.on_finished)
        self.worker.progress.connect(self.update_status)
        self.worker.start()

    def on_finished(self):
        self.display_historical_data()
        self.driver.quit()

    def update_status(self, message):
        self.status_label.setText(message)

    def display_historical_data(self):
        if not hasattr(self, 'currency_details') or not self.currency_details:
            return

        headers = ["Date", "Open($)", "High($)", "Low($)", "Close($)", "Volume($)", "Market Cap($)"]
        self.table.setRowCount(len(self.currency_details))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(self.currency_details):
            for j, key in enumerate(headers):
                self.table.setItem(i, j, QTableWidgetItem(row[key]))

    def save_csv(self):
        if not hasattr(self, 'currency_details') or not self.currency_details:
            return

        # Ask the user if they want to save the CSV
        reply = QMessageBox.question(
            self, "Save CSV", "Do you want to save the historical data as CSV?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            csv_filename = f"{self.name_of_coin}_historical_data.csv"
            keys = ["Date", "Open($)", "High($)", "Low($)", "Close($)", "Volume($)", "Market Cap($)"]

            with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.currency_details)

            QMessageBox.information(self, "Success", f"Data saved to {csv_filename}")

    def clean_data(self):
        if not hasattr(self, 'currency_details') or not self.currency_details:
            return

        cleaned_data = []
        headers = ["Date", "Open($)", "High($)", "Low($)", "Close($)", "Volume($)", "Market Cap($)"]
        cleaned_data.append(headers)

        for row in self.currency_details:
            cleaned_row = [
                datetime.strptime(row["Date"], "%b %d, %Y").strftime("%Y-%m-%d"),
                float(row["Open($)"].replace("$", "").replace(",", "")),
                float(row["High($)"].replace("$", "").replace(",", "")),
                float(row["Low($)"].replace("$", "").replace(",", "")),
                float(row["Close($)"].replace("$", "").replace(",", "")),
                float(row["Volume($)"].replace("$", "").replace(",", "")),
                float(row["Market Cap($)"].replace("$", "").replace(",", ""))
            ]
            cleaned_data.append(cleaned_row)

        output_filename = f"{self.name_of_coin}_historical_data_cleaned.csv"
        with open(output_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(cleaned_data)

        QMessageBox.information(self, "Success", f"Cleaned data saved to {output_filename}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = CoinMarketApp()
    ex.show()
    sys.exit(app.exec_())