=

# ⚡  Gen  — Invoice Generator API

A lightweight **FastAPI** backend that generates **PDF invoices from a Word template (`template.docx`)** for **A S Electricals**.
It calculates GST automatically and can be deployed easily to **Render** or any virtual machine.

---

## 🧩 Features

* Accepts JSON invoice data (customer name, invoice no, qty, rate, etc.)
* Calculates **SGST 9 %**, **CGST 9 %**, totals, round-off, and amount-in-words
* Fills placeholders in `template.docx`
* Converts it to a **PDF invoice** and returns it as a download
* Built with `FastAPI`, `python-docx`, `docx2pdf`, and `num2words`
* Uses **uv** for dependency and environment management

---

## 🗂️ Project structure

```
invo-gen/
│
├── main.py                # FastAPI app
├── template.docx          # Word invoice template with {{placeholders}}
├── requirements.txt       # Python dependencies
└── README.md
```

---

## ⚙️ Local setup (using uv)

> **uv** is a modern Python tool that replaces pip + venv.
> Install it once:
>
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

### 1️⃣ Create the virtual environment

```bash
uv venv
```

### 2️⃣ Install dependencies

```bash
uv pip install -r requirements.txt
```

or manually:

```bash
uv pip install fastapi uvicorn python-docx docx2pdf num2words pydantic
```

### 3️⃣ Run locally

```bash
uv run python -m uvicorn main:app --reload
```

Then open your browser at
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

Use the Swagger UI to send test data and download your generated invoice.

---

## 🧾 Example request (JSON)

```json
{
  "customer_name": "ACME Industries",
  "invoice_no": "INV-1024",
  "invoice_date": "2025-11-07",
  "description": "Electrical Wiring Kit",
  "hsn": "8544",
  "qty": 10,
  "rate": 275.50
}
```

---

## 🧰 Template format (`template.docx`)

Insert placeholders in your Word file exactly as shown below:

```
Customer: {{customer_name}}
Invoice No: {{invoice_no}}
Date: {{invoice_date}}

Description: {{description}}
HSN: {{hsn}}
Qty: {{qty}}
Rate: {{rate}}

Subtotal: {{subtotal}}
SGST (9%): {{sgst}}
CGST (9%): {{cgst}}
Total Tax: {{total_tax}}
Grand Total: {{grand_total}}
Round Off: {{round_off}}
Amount in Words: {{amount_in_words}}
```

---

## ☁️ Deploying to Render

1. **Push your project to GitHub.**

2. In Render, click **New → Web Service**.

3. Connect your repo and configure:

   | Setting       | Value                                                           |
   | ------------- | --------------------------------------------------------------- |
   | Runtime       | Python 3.11 +                                                   |
   | Build command | `uv pip install -r requirements.txt`                            |
   | Start command | `uv run python -m uvicorn main:app --host 0.0.0.0 --port 10000` |
   | Environment   | Production                                                      |

4. Deploy.
   Render will provide a live URL, for example:

   ```
   https://invo-gen.onrender.com/generate_invoice
   ```

5. Visit:

   ```
   https://invo-gen.onrender.com/docs
   ```

   to test invoice generation.

---

## 💻 Deploying to a VM (Ubuntu / EC2 / DigitalOcean)

```bash
sudo apt update && sudo apt install -y curl python3
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/<your-user>/invo-gen.git
cd invo-gen

uv venv
uv pip install -r requirements.txt

uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Access it from

```
http://<your-server-ip>:8000/docs
```

To keep it running in background:

```bash
nohup uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

---

## ✅ Quick checklist

* [ ] `template.docx` exists in the root folder
* [ ] Port 8000 (local) or 10000 (Render) is open
* [ ] `docx2pdf` works (Word or LibreOffice installed)
* [ ] Test `/generate_invoice` in Swagger UI

---

## 🧠 Notes

* Linux servers without Word need **LibreOffice** or **pdfkit** for DOCX → PDF conversion.
* To persist generated files, create a `/generated` folder and write PDFs there.
* Logs show full file paths for debugging.

---

## 🪶 License

MIT © 2025 A S Electricals

=