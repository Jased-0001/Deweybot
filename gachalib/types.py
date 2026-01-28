import discord

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
    

class Cards_User:
    def __init__(self,inv_id:int=-1,card_id:int=-1,user_id:int=-1) -> None:
        self.inv_id   = inv_id
        self.card_id  = card_id
        self.user_id  = user_id

    def __repr__(self):
        return f'{self.__class__.__name__} (invid = {self.inv_id} - cardid = {self.card_id})'
    def __eq__(self, other):
        return self.inv_id == other.inv_id
    

class Cards_Timeout:
    def __init__(self,user_id:int=-1,last_use:int=-1) -> None:
        self.user_id   = user_id
        self.last_use  = last_use

    def __repr__(self):
        return f'{self.__class__.__name__} (uid = {self.user_id} - lastuse = {self.last_use})'
    
class Trade:
    def __init__(self,message:discord.Message=[],user1:discord.Member=[],user2:discord.Member=[],user1_cards:list=[],user2_cards=[]) -> None:
        self.message  = message
        self.user1       = user1
        self.user1_cards = user1_cards
        self.user2       = user2
        self.user2_cards = user2_cards

    def __repr__(self):
        return f'{self.__class__.__name__} (message = {self.message} - user1id = {self.user1.id} - user2id = {self.user2.id} - user1cards = {self.user2_cards} - user2cards = {self.user2_cards})'