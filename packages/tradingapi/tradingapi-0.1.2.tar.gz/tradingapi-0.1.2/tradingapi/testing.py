from tradingapi.fivepaisa import FivePaisa
from tradingapi.shoonya import Shoonya
from tradingapi.utils import delete_broker_order_id, place_combo_order, get_pnl_table

fp = FivePaisa()
fp.connect(redis_db=4)
brok = fp
# sh = Shoonya()
# sh.connect(redis_db=7)
# brok = sh
brok.redis_o.keys("TEST_*")
paper = False
for key in brok.redis_o.keys("TEST_*"):
    print(f"deleting key {key}")
    delete_broker_order_id(brok, key)
order_symbol = "SENSEX_OPT_20250603_CALL_81000"
exchange = "BSE"
size = brok.get_min_lot_size(order_symbol, exchange="BSE")
print(size)
quote = brok.get_quote(order_symbol, exchange="BSE")
print(quote)
print(quote.bid / 2)
order = place_combo_order(
    brok,
    "TEST",
    [order_symbol],
    quantities=[size],
    entry=True,
    price_types=[int(quote.bid / 2)],
    exchanges=exchange,
    paper=paper,
)
symbol, internal_order_id = order.popitem()
broker_order_id = brok.redis_o.hget(internal_order_id, "entry_keys")
print(f"Symbol: {symbol},Internal Order ID: {internal_order_id},Broker Order ID: {broker_order_id}")
order_info = brok.get_order_info(broker_order_id=broker_order_id)
print(order_info)
order = brok.modify_order(broker_order_id=broker_order_id, new_price=int(quote.bid / 2) - 1, new_quantity=size)
broker_order_id = order.broker_order_id  # broker_order_id  changes in fp on modification.
order_info = brok.get_order_info(broker_order_id=broker_order_id)
print(order_info)
pnl = get_pnl_table(brok, "TEST", refresh_status=True)
print(pnl)
order = brok.cancel_order(broker_order_id=order.broker_order_id)
order_info = brok.get_order_info(broker_order_id=broker_order_id)
print(order_info)
pnl = get_pnl_table(brok, "TEST", refresh_status=True)
print(pnl)
