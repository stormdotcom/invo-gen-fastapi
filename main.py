from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from docx import Document
from docx2pdf import convert
from num2words import num2words
import tempfile, math, os

app = FastAPI(title="A S Electricals Invoice Generator")

class InvoiceData(BaseModel):
    customer_name: str
    invoice_no: str
    invoice_date: str
    description: str
    hsn: str
    qty: float
    rate: float

@app.post("/generate_invoice")
async def generate_invoice(data: InvoiceData):
    try:
        subtotal = data.qty * data.rate
        sgst = subtotal * 0.09
        cgst = subtotal * 0.09
        total_tax = sgst + cgst
        grand_total = subtotal + total_tax
        round_off = math.ceil(grand_total)
        amount_in_words = num2words(round_off, to='cardinal').title() + " Only"

        doc = Document("template.docx")
        mapping = {
            "customer_name": data.customer_name,
            "invoice_no": data.invoice_no,
            "invoice_date": data.invoice_date,
            "description": data.description,
            "hsn": data.hsn,
            "qty": f"{data.qty:.2f}",
            "rate": f"{data.rate:.2f}",
            "subtotal": f"{subtotal:.2f}",
            "sgst": f"{sgst:.2f}",
            "cgst": f"{cgst:.2f}",
            "total_tax": f"{total_tax:.2f}",
            "grand_total": f"{grand_total:.2f}",
            "round_off": f"{round_off:.2f}",
            "amount_in_words": amount_in_words
        }

        for p in doc.paragraphs:
            for key, val in mapping.items():
                if f"{{{{{key}}}}}" in p.text:
                    p.text = p.text.replace(f"{{{{{key}}}}}", str(val))

        tmp_dir = tempfile.mkdtemp()
        docx_path = os.path.join(tmp_dir, f"invoice_{data.invoice_no}.docx")
        pdf_path = docx_path.replace(".docx", ".pdf")

        doc.save(docx_path)
        convert(docx_path, pdf_path)

        return FileResponse(pdf_path, media_type="application/pdf", filename=f"invoice_{data.invoice_no}.pdf")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
def index():
    return {"message": "A S Electricals Invoice API running with uv"}
