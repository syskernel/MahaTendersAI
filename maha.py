from playwright.async_api import async_playwright
import asyncio
import pandas as pd
from datetime import datetime
#page.wait_for_timeout(5000)

keywords = ["Pune", "pune", "PMC/BHAVAN", "PCMC", "Yerawada"]
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
    await active_page.close()
    return date

#Launch the browser
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"height": 800, "width": 1280})
        page = await context.new_page()
        await page.set_extra_http_headers({
            "Accept-language": "en=US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        })
#go to the site
        await page.goto("https://mahatenders.gov.in/nicgep/app", timeout=30000)
        await page.wait_for_load_state("networkidle")
#click at result of tenders
        await page.locator("//a[text()='Results of Tenders']").click()
#enter the keywords in the loop
        for keyword in keywords:
            await page.locator("//input[@name='Keyword']").type(keyword)
#Ask for command input and wait for my command until i enter the captcha and press enter
            command = await asyncio.to_thread(input, "Enter command: ")
#if command=fetch
            if command == "fetch":
                num_of_tender = 1
                while True:
    #click on all the links of tenders and fetch desired reults
                    date = await fetch_data(page, num_of_tender, context)
                    tender_date = datetime.strptime(date, "%d-%b-%Y")
        #if contract date > present date: append fetched details to list
                    if tender_date >= given_date:
                        print(num_of_tender)
                        num_of_tender += 1
                        tenders.append({
                            "CONTRACT DATE": date
                        })
        #else: click on clear and break out of loop
                    else:
                        await page.locator("//a[@id='clear']").click()
                        break
    #if command=next: click clear
            elif command == "next":
                await page.locator("//a[@id='clear']").click()
    #else break
            else: 
                break

        await context.close()
        await browser.close()

asyncio.run(main())
#append the list into dataframe
df = pd.DataFrame(tenders)
#save the excel file as tenders01.xlsx
df.to_excel("tenders01.xlsx", index=False)