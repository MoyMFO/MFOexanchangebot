import asyncio
from client import PricesStreaming

book_name1 = "btc_mxn"
prices_btc = PricesStreaming(book_name1)


if __name__ == "__main__":

    listed = asyncio.get_event_loop().run_until_complete((prices_btc.prices_listener()))


