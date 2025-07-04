from fastapi import FastAPI, HTTPException
from playwright.sync_api import sync_playwright
from fastapi.middleware.cors import CORSMiddleware;

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "running"}



@app.get("/contributions/{username}")
def get_contributions(username: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            channel="chrome",  
            args=["--no-sandbox"]  
        )
        page = browser.new_page()
        page.goto(f"https://github.com/{username}")
        page.wait_for_selector("td.ContributionCalendar-day")

        contribution_cells = page.query_selector_all("td.ContributionCalendar-day")
        contributions = [
            {
                "date": cell.get_attribute("data-date"),
                "level": int(cell.get_attribute("data-level"))
            }
            for cell in contribution_cells if cell.get_attribute("data-date")
        ]

        browser.close()

        if not contributions:
            raise HTTPException(status_code=503, detail="No contributions found")

        return contributions