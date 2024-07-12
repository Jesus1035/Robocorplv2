from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def process_robot_orders():
    """
    Orchestrates the process of ordering robots from RobotSpareBin Industries Inc.,
    saving receipts and screenshots, embedding screenshots into receipts, 
    and creating a ZIP archive of the receipts and images.
    """
    setup_browser()
    access_order_website()
    fetch_orders_csv()
    handle_orders_from_csv()
    create_zip_archive()
    cleanup_output_folders()

def setup_browser():
    """Configure the browser settings."""
    browser.configure(slowmo=200)

def access_order_website():
    """Navigate to the robot order page and handle pop-up."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    browser.page().click('text=OK')

def fetch_orders_csv():
    """Download the orders CSV file."""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def place_new_order():
    """Initiate the process for placing a new order."""
    browser.page().click("#order-another")

def confirm_order_popup():
    """Handle the confirmation pop-up after placing an order."""
    browser.page().click('text=OK')

def fill_order_form(order):
    """Populate the robot order form and submit the order."""
    page = browser.page()
    head_options = {
        "1": "Roll-a-thor head",
        "2": "Peanut crusher head",
        "3": "D.A.V.E head",
        "4": "Andy Roid head",
        "5": "Spanner mate head",
        "6": "Drillbit 2000 head"
    }
    page.select_option("#head", head_options[order["Head"]])
    page.click(f'//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{order["Body"]}]/label')
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    while True:
        page.click("#order")
        if browser.page().query_selector("#order-another"):
            pdf_path = save_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = take_robot_screenshot(int(order["Order number"]))
            add_screenshot_to_receipt(screenshot_path, pdf_path)
            place_new_order()
            confirm_order_popup()
            break

def save_receipt_as_pdf(order_number):
    """Save the order receipt as a PDF file."""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def handle_orders_from_csv():
    """Read orders from the CSV file and process each order."""
    csv_reader = Tables()
    orders = csv_reader.read_table_from_csv("orders.csv")
    for order in orders:
        fill_order_form(order)

def take_robot_screenshot(order_number):
    """Capture a screenshot of the ordered robot."""
    page = browser.page()
    screenshot_path = f"output/screenshots/{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def add_screenshot_to_receipt(screenshot_path, pdf_path):
    """Embed the robot screenshot into the PDF receipt."""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, source_path=pdf_path, output_path=pdf_path)

def create_zip_archive():
    """Archive all receipt PDFs into a ZIP file."""
    archiver = Archive()
    archiver.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

def cleanup_output_folders():
    """Remove the folders containing receipts and screenshots."""
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")

if __name__ == "__main__":
    process_robot_orders()
