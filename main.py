# main.py
# ===============================================
# Chinook 数据集分析 - 从第 1 题到第 6 题（脚本版本）
# 运行方式：
#   python main.py
# 要求：
#   - data/Chinook.sqlite 存在
#   - 已安装 pandas, sqlalchemy, matplotlib
# ===============================================

import os
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt


def setup_engine():
    """创建数据库连接引擎"""
    db_path = "data/Chinook.sqlite"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"未找到数据库文件：{db_path}")
    engine = create_engine(f"sqlite:///{db_path}")
    return engine


def ensure_reports_folder():
    """确保 reports 文件夹存在"""
    os.makedirs("reports", exist_ok=True)


def analyze_revenue(engine):
    """
    1. 销售额分析：
       - 总销售额
       - 平均订单金额
       - 每月销售额走势
    """
    print("\n=== 1. Umsatzanalyse / 销售额分析 ===")

    invoices = pd.read_sql('SELECT * FROM "Invoice";', engine)
    invoices["InvoiceDate"] = pd.to_datetime(invoices["InvoiceDate"])

    gesamtumsatz = invoices["Total"].sum()
    mittlerer_wert = invoices["Total"].mean()

    print(f"Gesamtumsatz / 总销售额: {gesamtumsatz:.2f}")
    print(f"Mittlerer Einkaufswert / 平均订单金额: {mittlerer_wert:.2f}")

    # 每月销售额
    invoices["YearMonth"] = invoices["InvoiceDate"].dt.to_period("M").astype(str)
    umsatz_monat = (
        invoices
        .groupby("YearMonth")["Total"]
        .sum()
        .reset_index()
        .sort_values("YearMonth")
    )

    # 线图：每月销售额
    plt.figure(figsize=(10, 4))
    plt.plot(umsatz_monat["YearMonth"], umsatz_monat["Total"])
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Monat / 月份")
    plt.ylabel("Umsatz / 销售额")
    plt.title("Monatlicher Umsatz / 每月销售额")
    plt.tight_layout()
    plt.savefig("reports/01_monthly_revenue.png", bbox_inches="tight", dpi=150)
    plt.close()

    return invoices


def analyze_customers(engine, invoices):
    """
    2. 客户行为：
       - Top 客户
       - 销售额最高的 3 个国家 / 地区
    """
    print("\n=== 2. Kundenverhalten / 客户行为 ===")

    customers = pd.read_sql('SELECT * FROM "Customer";', engine)

    # Top Kunden nach Umsatz
    umsatz_kunde = (
        invoices
        .groupby("CustomerId")["Total"]
        .sum()
        .reset_index()
        .merge(customers, on="CustomerId", how="left")
    )

    top_kunden = umsatz_kunde.sort_values("Total", ascending=False).head(10)

    print("\nTop 10 Kunden nach Umsatz / 按销售额排名前 10 的客户：")
    print(top_kunden[["FirstName", "LastName", "Total"]])

    # 柱状图：Top 10 客户
    plt.figure(figsize=(10, 4))
    labels = top_kunden["FirstName"] + " " + top_kunden["LastName"]
    plt.bar(labels, top_kunden["Total"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Umsatz / 销售额")
    plt.title("Top 10 Kunden nach Umsatz")
    plt.tight_layout()
    plt.savefig("reports/02_top_customers.png", bbox_inches="tight", dpi=150)
    plt.close()

    # 按国家 / 地区销售额
    umsatz_land = (
        invoices
        .groupby("BillingCountry")["Total"]
        .sum()
        .reset_index()
        .sort_values("Total", ascending=False)
    )

    top3 = umsatz_land.head(3)
    print("\nTop 3 Länder nach Umsatz / 销售额最高的 3 个国家：")
    print(top3)

    plt.figure(figsize=(6, 4))
    plt.bar(top3["BillingCountry"], top3["Total"])
    plt.ylabel("Umsatz / 销售额")
    plt.title("Top 3 Länder nach Umsatz")
    plt.tight_layout()
    plt.savefig("reports/03_top_countries.png", bbox_inches="tight", dpi=150)
    plt.close()


def analyze_artists_and_genres(engine):
    """
    3. 流派 + 艺术家 + 专辑表现：
       - 最畅销流派
       - 销量最高的 Artist
       - 销量最高的 Album
    """
    print("\n=== 3. Artists & Genres Performance / 艺术家与流派表现 ===")

    # 5.1 Meistverkauftes Genre / 最畅销流派
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

    print("\nTop Genres / 最畅销流派：")
    print(genre_agg.head())

    plt.figure(figsize=(10, 4))
    plt.bar(genre_agg["GenreName"].head(10), genre_agg["Quantity"].head(10))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Verkaufte Stückzahl / 销量")
    plt.title("Top Genres nach verkauften Tracks")
    plt.tight_layout()
    plt.savefig("reports/04_top_genres.png", bbox_inches="tight", dpi=150)
    plt.close()

    # 5.2 Band mit den meisten verkauften Tracks / 销量最高的乐队（艺术家）
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

    print("\nTop Artists / 销量最高的艺术家：")
    print(artist_agg.head(10))

    plt.figure(figsize=(10, 4))
    plt.bar(artist_agg["ArtistName"].head(10), artist_agg["Quantity"].head(10))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Verkaufte Stückzahl / 销量")
    plt.title("Top 10 Artists nach verkauften Tracks")
    plt.tight_layout()
    plt.savefig("reports/05_top_artists.png", bbox_inches="tight", dpi=150)
    plt.close()

    # 5.3 Album mit den meisten Verkäufen / 最畅销专辑
    album_agg = (
        artist_sales
        .groupby("AlbumTitle")["Quantity"]
        .sum()
        .reset_index()
        .sort_values("Quantity", ascending=False)
    )

    print("\nTop Alben / 最畅销专辑：")
    print(album_agg.head(10))

    plt.figure(figsize=(10, 4))
    plt.bar(album_agg["AlbumTitle"].head(10), album_agg["Quantity"].head(10))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Verkaufte Stückzahl / 销量")
    plt.title("Top 10 Alben nach verkauften Tracks")
    plt.tight_layout()
    plt.savefig("reports/06_top_albums.png", bbox_inches="tight", dpi=150)
    plt.close()


def analyze_salespersons(engine, invoices):
    """
    4. Sales Performance / 销售员表现：
       - 每个销售员对应的总销售额
    """
    print("\n=== 4. Sales Performance / 销售员表现 ===")

    # Customer 里有 SupportRepId
    customers = pd.read_sql(
        'SELECT CustomerId, SupportRepId FROM "Customer";',
        engine
    )
    employees = pd.read_sql(
        'SELECT EmployeeId, FirstName, LastName FROM "Employee";',
        engine
    )

    # Invoice + Customer → 得到每张发票的 SupportRepId
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

    print("\nSales Performance (nach Umsatz) / 按销售额排名的销售员：")
    print(sales_by_rep[["FirstName", "LastName", "Total"]])

    plt.figure(figsize=(8, 4))
    labels = sales_by_rep["FirstName"] + " " + sales_by_rep["LastName"]
    plt.bar(labels, sales_by_rep["Total"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Umsatz / 销售额")
    plt.title("Umsatz nach Salesperson")
    plt.tight_layout()
    plt.savefig("reports/07_sales_by_rep.png", bbox_inches="tight", dpi=150)
    plt.close()


def main():
    print("🚀 Starte Chinook Analyse (main.py) ...")
    ensure_reports_folder()
    engine = setup_engine()

    # 1. 销售额分析
    invoices = analyze_revenue(engine)

    # 2. 客户行为
    analyze_customers(engine, invoices)

    # 3. 流派 & 艺术家 & 专辑表现
    analyze_artists_and_genres(engine)

    # 4. 销售员表现
    analyze_salespersons(engine, invoices)

    print("\n✅ 分析完成！所有图表已保存到 reports/ 文件夹。")


if __name__ == "__main__":
    main()
