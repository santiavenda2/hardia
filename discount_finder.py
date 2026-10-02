import argparse
import logging
import sys

from models import Article, ProductWithTargetPrice
from scrapers import HardgamersScraper, BestgamingScraper, Scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def find_discount_for_multiple_products(scraper: Scraper, product_identifiers_and_target_price: list[ProductWithTargetPrice]) -> dict[str, list[Article]]:
    products_with_target_price_by_product_identifier = {}
    for product_with_target_price in product_identifiers_and_target_price:
        articles_with_target_price, query = find_discount_for_product(scraper=scraper, product_with_target_price=product_with_target_price)
        if articles_with_target_price:
            products_with_target_price_by_product_identifier[query] = articles_with_target_price

    return products_with_target_price_by_product_identifier


def find_discount_for_product(scraper: Scraper, product_with_target_price: ProductWithTargetPrice) -> tuple[
    list[Article], str]:
    logger.info(f"Searching discount for {product_with_target_price.keywords} (target price: {product_with_target_price.target_price})")
    articles, url, query = scraper.search(product_with_target_price.keywords, max_price=int(product_with_target_price.target_price))

    articles_with_target_price = []

    for article in articles:
        if product_with_target_price.exact:
            all_keywords_in_title = True
            for keyword in product_with_target_price.keywords:
                if keyword.upper() not in article.title:
                    all_keywords_in_title = False
                    break
            if not all_keywords_in_title:
                continue

        # Esto no es necesario porque ya estoy filtrando por precio, pero lo dejo por si se cuela algun articulo extra
        if article.current_price <= product_with_target_price.target_price:
            articles_with_target_price.append(article)
        else:
            # Dado que los productos estan ordenados en orden creciente de precios, puedo cortar al primero
            # que supera el precio objetivo
            break
    return articles_with_target_price, query


def main():
    parser = argparse.ArgumentParser(description="Find discount for given scraper")
    parser.add_argument(
        "--scraper",
        type=str,
        default=HardgamersScraper.SOURCE_KEY,
        help="Scraper name (allowed values: hardgamers, bestgaming)",
    )
    args = parser.parse_args()
    logger.info(f"Args: {args}")

    if args.scraper == HardgamersScraper.SOURCE_KEY:
        scraper = HardgamersScraper()
    elif args.scraper == BestgamingScraper.SOURCE_KEY:
        scraper = BestgamingScraper()
    else:
        raise ValueError(f"Invalid scraper name: {args.scraper_name}")

    product_identifiers_and_target_price = [
        ProductWithTargetPrice(keywords=["274QPF"], target_price=510_000),
        ProductWithTargetPrice(keywords=["27GS85Q"], target_price=630_000),
        ProductWithTargetPrice(keywords=["32GS85Q"], target_price=700_000),
        ProductWithTargetPrice(keywords=["LOGITECH", "MX KEYS S"], target_price=150_000, exact=True),
        ProductWithTargetPrice(keywords=["LOGITECH", "MX MASTER 4"], target_price=140_000, exact=True),
        ProductWithTargetPrice(keywords=["LOGITECH", "MX MASTER 3S"], target_price=100_000, exact=True),
        ProductWithTargetPrice(keywords=["LOGITECH", "BRIO 100"], target_price=50_000),
        ProductWithTargetPrice(keywords=["CORSAIR", "5000D"], target_price=170_000),
    ]
    products_with_target_price_by_product_identifier = find_discount_for_multiple_products(
        scraper=scraper,
        product_identifiers_and_target_price=product_identifiers_and_target_price)
    for product_keyword, article_list in products_with_target_price_by_product_identifier.items():
        print(f"\nProducts with target price for {product_keyword}")
        for article in article_list:
            print(article)
    print("\n")


if __name__ == "__main__":
    main()
