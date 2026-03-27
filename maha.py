from playwright.async_api import async_playwright
import asyncio
import pandas as pd
from datetime import datetime
import os

keywords = ["Pune", "pune", "PMC/BHAVAN", "PCMC", "Yerawada", "yerawada", "Pune Camp", "pune camp", "Kothrud", "kothrud", "Bavdhan", "bavdhan", "baner", "Baner", "Aundh", "aundh", "Warje", "warje", "Karvenagar", "karvenagar", "Ganeshkind", "ganeshkind", "Balewadi", "balewadi", "Pashan", "pashan", "Kharadi", "kharadi", "Vadgaon Sheri", "vadgaon sheri", "Vidyanagar", "vidyanagar", "Vishrantwadi", "vishrantwadi", "Hadapsar", "hadapsar", "Magarpatta", "magarpatta", "Sinhagad Road", "sinhagad road", "Mundhwa", "mundhwa", "Anandnagar", "anandnagar", "Khadakwasla", "khadakwasla", "Dhayari", "dhayari", "Bibwewadi", "bibwewadi", "Vadgaon Budruk", "vadgaon budruk", "Market Yard", "market yard", "salisbury park", "Salisbury Park", "Dhankawadi", "dhankawadi", "Katraj", "katraj", "kondhwa", "Kondhwa", "Ambegaon", "ambegaon", "NIBM", "Hinjewadi", "hinjewadi", "Marunji", "marunji", "Chinchwad", "chinchwad", "Akurdi", "akurdi", "Chichwadgaon", "chichwadgaon", "Thergaon", "thergaon", "Punawale", "punawale", "Sangvi", "sangvi", "Pimple Nilakh", "pimple nilakh", "Bhosari", "bhosari", "Talwade", "talwade", "Shivajinagar", "shivajinagar", "Laxmi Road", "laxmi road", "Kasba Peth", "kasba peth", "Rasta Peth", "rasta peth", "Mangalwar Peth", "mangalwar peth", "Sadashiv Peth", "sadashiv peth", "Shaniwar Peth", "shaniwar peth", "Narayan Peth", "narayan peth"]
tenders = []
given_date = datetime.strptime("01-Mar-2026", "%d-%b-%Y")

async def fetch_data(page, n, context):
    if n == 1:
        selector = "//a[@id='DirectLink']"
    else:
        selector = f"//a[@id='DirectLink_{n}']"
    async with context.expect_page() as event_info:
        await page.locator(selector).click()
    active_page = await event_info.value
    print(active_page.url)
    date = (await active_page.locator("//td[text()='Contract Date : ']/following-sibling::td/b").inner_text()).strip()
    organisation = (await active_page.locator("//td[text()='Organisation Chain']/following-sibling::td").inner_text()).strip()
    id = (await active_page.locator("//td[text()='Tender ID : ']/following-sibling::td").inner_text()).strip()
    title = (await active_page.locator("//td[text()='Tender Title : ']/following-sibling::td").inner_text()).strip()
    period = (await active_page.locator("//td[text()='Work Completion Period (in days) : ']/following-sibling::td/b").inner_text()).strip()
    name = (await active_page.locator("//tr[@id='informal']/td[3]").inner_text()).strip()
    amount = (await active_page.locator("//tr[@id='informal']/td[5]").inner_text()).strip()
    await active_page.close()
    return date, organisation, id, title, period, name, amount

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"height": 800, "width": 1280})
        page = await context.new_page()
        await page.set_extra_http_headers({
            "Accept-language": "en=US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        })

        await page.goto("https://mahatenders.gov.in/nicgep/app", timeout=30000)
        await page.wait_for_load_state("networkidle")

        await page.locator("//a[text()='Results of Tenders']").click()

        for keyword in keywords:
            await page.locator("//input[@name='Keyword']").type(keyword)
            command = await asyncio.to_thread(input, "Enter command: ")

            if command == "fetch":
                num_of_tender = 1
                while True:
                    date, organisation, id, title, period, name, amount = await fetch_data(page, num_of_tender, context)
                    tender_date = datetime.strptime(date, "%d-%b-%Y")

                    if tender_date >= given_date:
                        print(num_of_tender)
                        num_of_tender += 1
                        tenders.append({
                            "TENDER ID": id,
                            "TENDER TITLE": title,
                            "CONTRACT DATE": date,
                            "CONTRACT VALUE(INR)": amount,
                            "WORK PERIOD(IN DAYS)": period,
                            "ORGANISATION": organisation,
                            "BIDDER NAME": name,
                        })

                    else:
                        await page.locator("//a[@id='clear']").click()
                        break

            elif command == "next":
                await page.locator("//a[@id='clear']").click()

            else: 
                break

        await context.close()
        await browser.close()

asyncio.run(main())

filename = "tenders01.xlsx"
new_df = pd.DataFrame(tenders)
if os.path.exists(filename):
    existing_df = pd.read_excel(filename)
    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    updated_df.drop_duplicates(subset=["TENDER ID"], inplace=True)
    updated_df.to_excel(filename, index=False)
    print("Data appended successfully!")
else:
    new_df.to_excel(filename, index=False)
    print("File created and saved successfully!")