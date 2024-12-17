import os.path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from apps.models import SiteSettings, Order
from root.settings import MEDIA_ROOT


def make_pdf(order: Order):
    data = order.order_items.values_list(
        'product__title',
        'quantity',
        'product__price_percentage',
        'product__price',
        'product__shopping_cost')

    # Create a canvas object
    pdf_file_folder = 'order/pdf'
    if not os.path.exists(f"{MEDIA_ROOT}/{pdf_file_folder}"):
        os.makedirs(f"{MEDIA_ROOT}/{pdf_file_folder}")

    pdf_file_name = f"{pdf_file_folder}/order_{order.pk}.pdf"
    c = canvas.Canvas(f"{MEDIA_ROOT}/{pdf_file_name}", pagesize=letter)
    width, height = letter

    # Insert bold text in the middle of the top
    title = f"Order Detail #{order.pk}"
    c.setFont("Helvetica-Bold", 18)
    title_width = c.stringWidth(title, 'Helvetica-Bold', 18)
    c.drawString((width - title_width) / 2, height - 40, title)

    c.setFont("Helvetica", 14)
    # Define the starting position of the table
    x_offset = 50
    y_offset = height - 100
    line_height = 25
    col_widths = [50, 200, 100, 100, 100]  # Define column widths

    # Draw table headers with background color and borders
    headers = ['ID', 'Product title', 'Quantity', 'Price', 'Amount']
    c.setFillColor(colors.lightblue)
    c.rect(x_offset, y_offset, sum(col_widths), line_height, fill=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)

    x = x_offset
    for i, header in enumerate(headers):
        c.drawString(x + 5, y_offset + 5, header)
        c.rect(x, y_offset, col_widths[i], line_height, fill=0)
        x += col_widths[i]

    total_price = 0
    total_shipping_cost = 0
    c.setFont("Helvetica", 12)
    y_offset -= line_height

    # Draw table rows with alternating colors and borders
    for index, row in enumerate(data, 1):
        row = list(row)
        discount = row.pop(2)
        row_color = colors.whitesmoke if index % 2 == 0 else colors.lightgrey
        c.setFillColor(row_color)
        c.rect(x_offset, y_offset, sum(col_widths), line_height, fill=1)
        c.setFillColor(colors.black)

        product_name, quantity, price, shipping_cost = row
        price = price * (100 - discount) // 100
        subtotal = quantity * price
        total_price += subtotal
        total_shipping_cost += shipping_cost

        row_data = [index, product_name, quantity, f"{price} $", f"{subtotal} $"]
        x = x_offset
        for i, item in enumerate(row_data):
            c.drawString(x + 5, y_offset + 5, str(item))
            c.rect(x, y_offset, col_widths[i], line_height, fill=0)
            x += col_widths[i]

        y_offset -= line_height

    y_offset -= line_height
    text = f'Subtotal: {total_price} $'
    c.drawString(x_offset, y_offset, text)

    site = SiteSettings.objects.first()
    if site:
        total_price += total_shipping_cost
        y_offset -= line_height
        tax_amount = total_price * site.tax // 100
        text = f'Tax {site.tax}%: {tax_amount} $'
        c.drawString(x_offset, y_offset, text)
        total_price += tax_amount

    y_offset -= line_height
    text = f'Shipping Cost: {total_shipping_cost} $'
    c.drawString(x_offset, y_offset, text)

    y_offset -= 10
    c.setLineWidth(1)
    c.setStrokeColor(colors.grey)
    c.line(x_offset, y_offset, x_offset + 120, y_offset)

    y_offset -= 18
    text = f'Total price: {total_price} $'
    c.drawString(x_offset, y_offset, text)

    # Save the PDF
    c.save()
    order.pdf_file = pdf_file_name
    order.save()
