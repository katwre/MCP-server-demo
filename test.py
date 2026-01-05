from main import scrape_web_raw

def main():
    url = "https://github.com/alexeygrigorev/minsearch"
    content = scrape_web_raw(url)

    print("URL:", url)
    print("Characters:", len(content))
    print("\n--- HEAD (first 500 chars) ---\n")
    print(content[:500])

if __name__ == "__main__":
    main()
