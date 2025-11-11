# main.py
# ===============================================
# Chinook Data Analysis Project
# Complete workflow from Revenue → Customers → Genres → Artists → Albums → Salespersons
# Comments: English + German (no Chinese)
# ===============================================

import os
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt


def setup_engine():
    """Create database engine / Datenbankverbindung erstellen"""
    db_path = "data/Chinook.sqlite"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")
    engine = create_engine(f"sqlite:///{db_path}")
    return engine


def ensure_reports_folder():
    """Ensure reports folder exists / Sicherstellen, dass der reports-Ordner existiert"""
    os.makedirs("reports", exist_ok=True)


def analyze_revenue(engine):
    """
    1. Revenue Analysis / Umsatzanalyse
       - Total revenue
       - Average invoice value
       - Monthly revenue trend
    """
    print("\n=== 1. Revenue Analysis / Umsatzanalyse ===")

    invoices = pd.read_sql('SELECT * FROM "Invoice";', engine)
    invoices["InvoiceDate"] = pd.to_datetime(invoices["InvoiceDate"])

    total_revenue = invoices["Total"].sum()
    avg_invoice = invoices["Total"].mean()

    print(f"Total Revenue / Gesamtumsatz: {total_revenue:.2f}")
    print(f"Average Invoice Value / Durchschnittlicher Einkaufswert: {avg_invoice:.2f}")

    # Monthly revenue trend
    invoices["YearMonth"] = invoices["InvoiceDate"].dt.to_period("M").astype(str)
    monthly_revenue = (
        invoices
        .groupby("YearMonth")["Total"]
        .sum()
        .reset_index()
        .sort_values("YearMonth")
    )

    plt.figure(figsize=(10, 4))
    plt.plot(monthly_revenue["YearMonth"], monthly_revenue["Total"])
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Month / Monat")
    plt.ylabel("Revenue / Umsatz")
    plt.title("Monthly Revenue / Monatlicher Umsatz")
    plt.tight_layout()
    plt.savefig("reports/01_monthly_revenue.png", bbox_inches="tight", dpi=150)
    plt.close()

    return invoices


def analyze_customers(engine, invoices):
    """
    2. Customer Behavior / Kundenverhalten
       - Top customers by revenue
       - Top 3 countries by revenue
    """
    print("\n=== 2. Customer Behavior / Kundenverhalten ===")

    customers = pd.read_sql('SELECT * FROM "Customer";', engine)

    # Top customers
    revenue_by_customer = (
        invoices
        .groupby("CustomerId")["Total"]
        .sum()
        .reset_index()
        .merge(customers, on="CustomerId", how="left")
    )

    top_customers = revenue_by_customer.sort_values("Total", ascending=False).head(10)
    print("\nTop 10 Customers / Top 10 Kunden:")
    print(top_customers[["FirstName", "LastName", "Total"]])

    plt.figure(figsize=(10, 4))
    labels = top_customers["FirstName"] + " " + top_customers["LastName"]
    plt.bar(labels, top_customers["Total"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Revenue / Umsatz")
    plt.title("Top 10 Customers by Revenue / Top 10 Kunden nach Umsatz")
    plt.tight_layout()
    plt.savefig("reports/02_top_customers.png", bbox_inches="tight", dpi=150)
    plt.close()

    # Revenue by country
    revenue_by_country = (
        invoices
        .groupby("BillingCountry")["Total"]
        .sum()
        .reset_index()
        .sort_values("Total", ascending=False)
    )

    top3 = revenue_by_country.head(3)
    print("\nTop 3 Countries by Revenue / Top 3 Länder nach Umsatz:")
    print(top3)

    plt.figure(figsize=(6, 4))
    plt.bar(top3["BillingCountry"], top3["Total"])
    plt.ylabel("Revenue / Umsatz")
    plt.title("Top 3 Countries by Revenue / Top 3 Länder nach Umsatz")
    plt.tight_layout()
    plt.savefig("reports/03_top_countries.png", bbox_inches="tight", dpi=150)
    plt.close()


def analyze_artists_and_genres(engine):
    """
    3. Artists & Genres Performance / Künstler- und Genre-Performance
       - Best-selling genres
       - Top-selling artists
       - Top-selling albums
    """
    print("\n=== 3. Artists & Genres Performance / Künstler- und Genre-Performance ===")

    # 3.1 Best-selling Genres
    invoice_items = pd.read_sql(
        'SELECT InvoiceLineId, TrackId, Quantity FROM "InvoiceLine";',
        engine
    )
    tracks_genre = pd.read_sql(
        'SELECT TrackId, GenreId FROM "Track";',
        engine
    )
    genres = pd.read_sql(
        'SELECT GenreId, Name AS GenreName FROM "Genre";',
        engine
    )

    genre_sales = (
        invoice_items
        .merge(tracks_genre, on="TrackId", how="left")
        .merge(genres, on="GenreId", how="left")
    )

    genre_agg = (
        genre_sales
        .groupby("GenreName")["Quantity"]
        .sum()
        .reset_index()
        .sort_values("Quantity", ascending=False)
    )

    print("\nTop Genres / Meistverkaufte Genres:")
    print(genre_agg.head())

    plt.figure(figsize=(10, 4))
    plt.bar(genre_agg["GenreName"].head(10), genre_agg["Quantity"].head(10))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Units Sold / Verkaufte Stückzahl")
    plt.title("Top Genres by Sold Tracks / Top Genres nach verkauften Tracks")
    plt.tight_layout()
    plt.savefig("reports/04_top_genres.png", bbox_inches="tight", dpi=150)
    plt.close()

    # 3.2 Top Artists
    tracks_album = pd.read_sql(
        'SELECT TrackId, AlbumId FROM "Track";',
        engine
    )
    albums = pd.read_sql(
        'SELECT AlbumId, Title AS AlbumTitle, ArtistId FROM "Album";',
        engine
    )
    artists = pd.read_sql(
        'SELECT ArtistId, Name AS ArtistName FROM "Artist";',
        engine
    )

    artist_sales = (
        invoice_items
        .merge(tracks_album, on="TrackId", how="left")
        .merge(albums, on="AlbumId", how="left")
        .merge(artists, on="ArtistId", how="left")
    )

    artist_agg = (
        artist_sales
        .groupby("ArtistName")["Quantity"]
        .sum()
        .reset_index()
        .sort_values("Quantity", ascending=False)
    )

    print("\nTop Artists / Erfolgreichste Künstler:")
    print(artist_agg.head(10))

    plt.figure(figsize=(10, 4))
    plt.bar(artist_agg["ArtistName"].head(10), artist_agg["Quantity"].head(10))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Units Sold / Verkaufte Stückzahl")
    plt.title("Top 10 Artists by Sold Tracks / Top 10 Künstler nach verkauften Tracks")
    plt.tight_layout()
    plt.savefig("reports/05_top_artists.png", bbox_inches="tight", dpi=150)
    plt.close()

    # 3.3 Top Albums
    album_agg = (
        artist_sales
        .groupby("AlbumTitle")["Quantity"]
        .sum()
        .reset_index()
        .sort_values("Quantity", ascending=False)
    )

    print("\nTop Albums / Meistverkaufte Alben:")
    print(album_agg.head(10))

    plt.figure(figsize=(10, 4))
    plt.bar(album_agg["AlbumTitle"].head(10), album_agg["Quantity"].head(10))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Units Sold / Verkaufte Stückzahl")
    plt.title("Top 10 Albums by Sold Tracks / Top 10 Alben nach verkauften Tracks")
    plt.tight_layout()
    plt.savefig("reports/06_top_albums.png", bbox_inches="tight", dpi=150)
    plt.close()


def analyze_salespersons(engine, invoices):
    """
    4. Sales Performance / Verkaufsleistung
       - Total revenue per salesperson
    """
    print("\n=== 4. Sales Performance / Verkaufsleistung ===")

    customers = pd.read_sql(
        'SELECT CustomerId, SupportRepId FROM "Customer";',
        engine
    )
    employees = pd.read_sql(
        'SELECT EmployeeId, FirstName, LastName FROM "Employee";',
        engine
    )

    invoice_with_rep = (
        invoices
        .merge(customers, on="CustomerId", how="left")
    )

    sales_by_rep = (
        invoice_with_rep
        .groupby("SupportRepId")["Total"]
        .sum()
        .reset_index()
        .merge(
            employees,
            left_on="SupportRepId",
            right_on="EmployeeId",
            how="left"
        )
    )

    sales_by_rep = sales_by_rep.sort_values("Total", ascending=False)

    print("\nSales by Salesperson / Umsatz nach Verkaufsmitarbeiter:")
    print(sales_by_rep[["FirstName", "LastName", "Total"]])

    plt.figure(figsize=(8, 4))
    labels = sales_by_rep["FirstName"] + " " + sales_by_rep["LastName"]
    plt.bar(labels, sales_by_rep["Total"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Revenue / Umsatz")
    plt.title("Revenue by Salesperson / Umsatz nach Salesperson")
    plt.tight_layout()
    plt.savefig("reports/07_sales_by_rep.png", bbox_inches="tight", dpi=150)
    plt.close()


def main():
    print("🚀 Starting Chinook Analysis ... / Analyse wird gestartet ...")
    ensure_reports_folder()
    engine = setup_engine()

    # 1. Revenue
    invoices = analyze_revenue(engine)

    # 2. Customers
    analyze_customers(engine, invoices)

    # 3. Genres, Artists, Albums
    analyze_artists_and_genres(engine)

    # 4. Salespersons
    analyze_salespersons(engine, invoices)

    print("\n✅ Analysis complete! / Analyse abgeschlossen!")
    print("All charts have been saved to the reports/ folder. / Alle Diagramme wurden im Ordner reports/ gespeichert.")


if __name__ == "__main__":
    main()
