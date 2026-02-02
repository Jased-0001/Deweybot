import discord
from dataclasses import dataclass, field

class Card:
    def __init__(self,
                 maker_id:int=-1,request_message_id:int=-1,card_id:int=-1,accepted:bool=False,
                 name:str="", description:str="",rarity:str="",filename:str="") -> None:
        self.maker_id           = maker_id
        self.request_message_id = request_message_id
        self.card_id            = card_id
        self.accepted           = accepted
        self.name               = name
        self.description        = description
        self.rarity             = rarity
        self.filename           = filename
    
    def __repr__(self):
        return f'{self.__class__.__name__} (name = {self.name} - cardid= {self.card_id})'
    def __eq__(self, other):
        return self.card_id == other.card_id
    

class CardsInventory:
    def __init__(self,inv_id:int=-1,card_id:int=-1,user_id:int=-1) -> None:
        self.inv_id   = inv_id
        self.card_id  = card_id
        self.user_id  = user_id

    def __repr__(self):
        return f'{self.__class__.__name__} (invid = {self.inv_id} - cardid = {self.card_id})'
    def __eq__(self, other):
        return self.inv_id == other.inv_id
    

class GachaUser:
    def __init__(self,user_id:int=-1,last_use:int=-1) -> None:
        self.user_id   = user_id
        self.last_use  = last_use

    def __repr__(self):
        return f'{self.__class__.__name__} (uid = {self.user_id} - lastuse = {self.last_use})'
    
@dataclass
class Trade:
    message: discord.Message | None = None
    user1: discord.Member | None = None
    user2: discord.Member | None = None
    user1_cards: list[CardsInventory] = field(default_factory=list)
    user2_cards: list[CardsInventory] = field(default_factory=list)
    accept_message: discord.Message | None = None
    accepted_user: discord.Member | None = None

    def __repr__(self):
        return f'{self.__class__.__name__} (user1id = {self.user1.id} - user2id = {self.user2.id} - user1cards = {self.user2_cards} - user2cards = {self.user2_cards})' # pyright: ignore[reportOptionalMemberAccess]