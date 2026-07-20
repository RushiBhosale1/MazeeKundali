import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Mock context for the biodata PDF
ctx = {
    "personal_info": {
        "full_name": "रुषी जाधव",
        "dob": "15 जुलै 1995",
        "birth_time": "सकाळी 10:30",
        "birth_place": "पुणे",
        "height": "5 फूट 8 इंच",
        "blood_group": "O+",
        "complexion": "गव्हाळ",
        "caste": "९६ कुळी मराठा"
    },
    "family_info": {
        "father_name": "प्रकाश जाधव",
        "father_occupation": "शेतकरी",
        "mother_name": "सुनीता जाधव",
        "brothers": "1 (विवाहित)",
        "sisters": "नाही",
        "mama_surname": "देशमुख",
        "contact_number": "9876543210"
    },
    "education_info": {
        "education": "B.E. Computer",
        "occupation": "सॉफ्टवेअर इंजिनिअर",
        "employer": "Tech Solutions Pune",
        "annual_income": "12 लाख/वर्ष"
    },
    "horoscope_info": {
        "rashi_mr": "मेष",
        "nakshatra_mr": "अश्विनी",
        "devak": "पंचपल्लव",
        "mangal_dosha": "नाही"
    },
    "photo_url": "https://via.placeholder.com/150",
    "expectations": "सुशिक्षित आणि समजूतदार."
}

def generate():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed.")
        return

    tpl_dir = Path(__file__).parent / "static" / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    tpl = env.get_template("biodata_pdf.html")

    out_dir = Path(__file__).parent.parent / "frontend" / "public" / "themes"
    out_dir.mkdir(parents=True, exist_ok=True)

    themes = ["royal_gold", "marathi_classic", "traditional", "shahi", "ruby", "modern", "peacock", "floral"]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        # Use a smaller viewport to generate a cropped "thumbnail" feeling or full A4.
        page = browser.new_page(device_scale_factor=1)
        page.set_viewport_size({"width": 794, "height": 1123})

        for theme in themes:
            ctx["template_id"] = theme
            html = tpl.render(**ctx)
            page.set_content(html, wait_until="networkidle")
            
            out_path = out_dir / f"{theme}.jpg"
            # Take full screenshot
            page.screenshot(path=str(out_path), type="jpeg", quality=60, full_page=True)
            print(f"Generated {out_path}")

        browser.close()

if __name__ == "__main__":
    generate()
