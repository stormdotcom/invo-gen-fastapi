from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from docx import Document
from docx2pdf import convert
from num2words import num2words
import tempfile, math, os

# ✅ Always load template.docx from project root (absolute path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "template.docx")

app = FastAPI(title="Invo GEN API")

# ---------- Data Models ----------

class Item(BaseModel):
    description: str
    hsn: str
    qty: float
    rate: float
    unit: str = "Nos"

class InvoiceData(BaseModel):
    customer_name: str
    invoice_no: str
    invoice_date: str
    items: List[Item]


# ---------- Generate Invoice ----------

@app.post("/generate_invoice")
async def generate_invoice(data: InvoiceData):
    try:
        # === 1️⃣ Totals ===
        subtotal = sum(item.qty * item.rate for item in data.items)
        sgst = subtotal * 0.09
        cgst = subtotal * 0.09
        total_tax = sgst + cgst
        grand_total = subtotal + total_tax
        round_off = math.ceil(grand_total)
        amount_in_words = num2words(round_off, to="cardinal").title() + " Rupees Only"

        # === 2️⃣ Load Template ===
        if not os.path.exists(file_path):
            return JSONResponse({"error": f"Template not found at {file_path}"}, status_code=404)

        print(f"📄 Using template: {file_path}")
        doc = Document(file_path)

        # === 3️⃣ Fill static placeholders ===
        mapping = {
            "customer_name": data.customer_name,
            "invoice_no": data.invoice_no,
            "invoice_date": data.invoice_date,
            "subtotal": f"{subtotal:.2f}",
            "sgst": f"{sgst:.2f}",
            "cgst": f"{cgst:.2f}",
            "total_tax": f"{total_tax:.2f}",
            "grand_total": f"{grand_total:.2f}",
            "round_off": f"{round_off:.2f}",
            "amount_in_words": amount_in_words,
        }

        for p in doc.paragraphs:
            for key, val in mapping.items():
                if f"{{{{{key}}}}}" in p.text:
                    p.text = p.text.replace(f"{{{{{key}}}}}", str(val))

        # === 4️⃣ Populate item table ===
        table = doc.tables[0]

        # Clear any existing rows (keep only header)
        while len(table.rows) > 1:
            table._element.remove(table.rows[1]._element)

        # Add rows dynamically
        for idx, item in enumerate(data.items, start=1):
            row = table.add_row().cells
            row[0].text = str(idx)
            row[1].text = item.description
            row[2].text = item.hsn
            row[3].text = f"{item.qty:.2f}"
            row[4].text = f"{item.rate:.2f}"
            row[5].text = item.unit
            row[6].text = f"{item.qty * item.rate:.2f}"

        # === 5️⃣ Save and convert ===
        tmp_dir = tempfile.mkdtemp()
        docx_path = os.path.join(tmp_dir, f"invoice_{data.invoice_no}.docx")
        pdf_path = docx_path.replace(".docx", ".pdf")

        doc.save(docx_path)
        convert(docx_path, pdf_path)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"invoice_{data.invoice_no}.pdf",
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ---------- View Template ----------

@app.get("/view_template")
def view_template():
    """Download the existing template.docx"""
    if not os.path.exists(file_path):
        return JSONResponse(content={"error": "Template not found"}, status_code=404)
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="template.docx",
    )


# ---------- Template Info ----------

@app.get("/template_info")
def template_info():
    """Return metadata for the Word template"""
    if not os.path.exists(file_path):
        return JSONResponse(content={"error": "Template not found"}, status_code=404)

    doc = Document(file_path)
    return {
        "template_path": file_path,
        "paragraphs": len(doc.paragraphs),
        "tables": len(doc.tables),
        "sections": len(doc.sections),
    }


# ---------- Optional: Upload Template ----------

@app.post("/upload_template")
async def upload_template(file: UploadFile = File(...)):
    """Replace current template.docx via API upload"""
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        return {"message": f"Template updated successfully at {file_path}"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ---------- Root ----------

@app.get("/")
def index():
    return {"message": f"Invo Gen API running, using template: {file_path}"}
