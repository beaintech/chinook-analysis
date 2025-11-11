# 🎵 Chinook Data Analysis Project

This project performs a complete **Exploratory Data Analysis (EDA)** on the classic **Chinook music store** database using **Python**, **SQLAlchemy**, and **pandas**.  
The goal is to uncover business insights such as top-selling genres, artists, customers, and sales performance of employees.

---

## 📊 Project Overview

The Chinook database simulates a digital music shop that stores information about:
- Customers, invoices, and sales transactions  
- Albums, artists, and tracks  
- Employees (sales representatives)

This analysis answers key business questions, including:

1. **Umsatz / Revenue**
   - What is the total and average sales amount?
   - In which months were sales particularly high?

2. **Kundenverhalten / Customer Behavior**
   - Who are the top customers by total revenue?
   - Which three countries generated the highest sales?

3. **Artists & Genres Performance**
   - What is the best-selling genre?
   - Which artist and which album sold the most tracks?

4. **Sales Performance**
   - Which sales representatives achieved the highest total sales?

All results are supported by **visualizations** (bar charts and line plots) and summarized in a final report.

---

## 🧱 Project Structure

Download the Chinook database

You can download the SQLite file from the official repo:
👉 https://github.com/lerocha/chinook-database

Use the file:
ChinookDatabase/DataSources/Chinook_Sqlite.sqlite
and save it in your local folder:
data/Chinook.sqlite

pip freeze > requirements.txt

python main.py# chinook-analysis
