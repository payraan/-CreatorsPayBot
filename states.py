from aiogram.fsm.state import State, StatesGroup

class DonationFlow(StatesGroup):
    selecting_amount = State()
    custom_amount = State()
    selecting_network = State()
    waiting_for_txid = State()
