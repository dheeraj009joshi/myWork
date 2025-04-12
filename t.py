from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https:/youtube.com')
    print('✅ Title:', page.title())


# # Example usage
# country = input("Enter a country name: ")
# cities = get_cities_by_country(country)

# if cities:
#     for city in cities:
#         print(f"City: {city['city']}, Latitude: {city['latitude']}, Longitude: {city['longitude']}")
# else:
#     print("No cities found or incorrect country name.")
