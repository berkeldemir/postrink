import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime

# PDF için DejaVu fontu
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

DB_NAME = "database.db"
PDF_NAME = "gunluk_rapor.pdf"

def sales_report_pdf(db_name=DB_NAME, pdf_name=PDF_NAME):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            s.sale_id,
            s.customer_name,
            s.total_amount,
            s.payment_method,
            s.payment_info,
            ci.item_count,
            i.item_name,
            i.item_price,
            ci.item_total
        FROM sales AS s
        JOIN cart_items AS ci ON s.sale_id = ci.sale_id
        JOIN items AS i ON ci.item_id = i.item_id
        WHERE DATE(s.sale_date) = '2025-09-03'
        ORDER BY s.sale_date, s.sale_id;
    """)

    rows = cursor.fetchall()

    # organize by sale_id
    sales_dict = {}
    for row in rows:
        sale_id, cname, total, pay_method, pay_info, count, item_name, item_price, item_total = row
        if sale_id not in sales_dict:
            sales_dict[sale_id] = {
                "customer_name": cname,
                "total": total,
                "payment_method": pay_method,
                "payment_info": pay_info,
                "items": []
            }
        sales_dict[sale_id]["items"].append((count, item_name, item_price, item_total))

    # PDF oluştur
    c = canvas.Canvas(pdf_name, pagesize=A4)
    width, height = A4
    c.setFont("DejaVu", 14)
    c.drawString(20*mm, height-20*mm, f"Günlük Satış Raporu - {datetime.now().strftime('%d %B %Y')}")

    y = height - 30*mm
    c.setFont("DejaVu", 10)

    # Sütun başlıkları
    col_widths = [35*mm, 15*mm, 50*mm, 25*mm, 30*mm, 30*mm]
    headers = ["Müşteri Adı", "Adet", "Ürün", "Ürün Fiyatı", "Toplam Tutar", "Ödeme Biçimi"]
    x = 20*mm
    for i, header in enumerate(headers):
        c.setFillColor(colors.lightgrey)
        c.rect(x, y, col_widths[i], 8*mm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.drawString(x+2*mm, y+2*mm, header)
        x += col_widths[i]

    y -= 8*mm

    total_nakit = 0
    total_iban = 0
    total_all = 0

    # Satırları yaz
    for sale in sales_dict.values():
        cname = sale["customer_name"]
        total = sale["total"]
        method = sale["payment_method"]
        info = sale["payment_info"] or ""
        pay_text = f"{method} ({info})" if info else method

        first_row = True
        for count, item_name, price, item_total in sale["items"]:
            x = 20*mm
            row_height = 7*mm
            # Satır arka plan zebra
            if (int(y//row_height) %2)==0:
                c.setFillColorRGB(0.95,0.95,0.95)
                c.rect(x, y, sum(col_widths), row_height, fill=1, stroke=0)
            c.setFillColor(colors.black)

            row_values = [
                cname if first_row else "",
                str(count),
                item_name,
                f"{price:.2f} TL",
                f"{total:.2f} TL" if first_row else "",
                pay_text if first_row else ""
            ]
            for i, val in enumerate(row_values):
                c.drawString(x+2*mm, y+2*mm, val)
                x += col_widths[i]
            y -= row_height
            first_row = False

        total_all += total
        if method.lower() == "nakit":
            total_nakit += total
        elif method.lower() == "iban":
            total_iban += total

        # Sayfa altına gelirse yeni sayfa aç
        if y < 40*mm:
            c.showPage()
            c.setFont("DejaVu", 10)
            y = height - 20*mm

    # Özet alanı
    y -= 10*mm
    c.setFont("DejaVu", 12)
    c.drawString(20*mm, y, f"Toplam Nakit Gelir: {total_nakit:.2f} TL")
    y -= 7*mm
    c.drawString(20*mm, y, f"Toplam IBAN Gelir:  {total_iban:.2f} TL")
    y -= 7*mm
    c.drawString(20*mm, y, f"Toplam Gelir:       {total_all:.2f} TL")

    c.save()
    conn.close()
    print(f"{pdf_name} oluşturuldu.")

if __name__ == "__main__":
    sales_report_pdf()
