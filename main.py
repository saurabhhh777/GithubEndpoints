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
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://github.com/{username}")

        # Wait for the contribution calendar to load
        page.wait_for_selector("td.ContributionCalendar-day")

        # Extract contributions
        contribution_cells = page.query_selector_all("td.ContributionCalendar-day")

        contributions = []
        for cell in contribution_cells:
            date = cell.get_attribute("data-date")
            level = cell.get_attribute("data-level")
            if date and level is not None:
                contributions.append({"date": date, "level": int(level)})

        browser.close()

        if not contributions:
            raise HTTPException(status_code=503, detail="No contributions found")

        return contributions
