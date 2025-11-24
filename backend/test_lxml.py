try:
    import lxml
    print(f"lxml version: {lxml.__version__}")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup("<html><body><p>test</p></body></html>", "lxml")
    print("BeautifulSoup with lxml works!")
except Exception as e:
    print(f"Error: {e}")
