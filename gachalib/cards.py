"""
things to deal with the actual cards
"""
import gachalib
from random import randint
import os

import gachalib.cards
import gachalib.types

def evilify(card):
    return ("EVIL " + card[0], card[1], card[2] + " evil", "E" + card[3], card[4], card[5], card[6] * -1)

# Getting cards (multiple)
######################################
def db_get_cards(statement: str, parameters: tuple = ()) -> tuple[bool, list[gachalib.types.Card]]:
    try:
        a = gachalib.gacha_database.read_data(statement=statement, parameters=parameters)
        b = []

        for c in a:
            b.append(gachalib.types.Card(name=c[0],description=c[1],rarity=c[2],filename=c[3],maker_id=c[4],accepted=c[5],card_id=c[6]))

        return (True, b)
    except IndexError:
        return (False, [])
    
# | None
def get_cards() -> tuple[bool, list[gachalib.types.Card]]:
    return db_get_cards(statement=f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha")

def get_approved_cards() -> tuple[bool, list[gachalib.types.Card]]:
    return db_get_cards(statement=f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha WHERE accepted = True")


def get_card_by_id_range(id_start:int, id_end:int) -> tuple[bool, list[gachalib.types.Card]]:
    a,b = db_get_cards(statement="SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha;")
    if a:
        return a, b[id_start-1:id_end]
    else:
        return (False, [])

    
def get_unapproved_cards() -> tuple[bool, list[gachalib.types.Card]]:
    return db_get_cards(statement=f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha WHERE (accepted) = (?);", parameters=(False,))




# Getting cards (singular)
######################################

def get_card_by_id(card_id:int) -> tuple[bool, gachalib.types.Card]:
    try:
        a = gachalib.gacha_database.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha WHERE (id) = (?)", (abs(int(card_id)),))[0]
        a = evilify(a) if int(card_id) < 0 else a
        return (True, gachalib.types.Card(name=a[0],description=a[1],rarity=a[2],filename=a[3],maker_id=a[4],accepted=a[5],card_id=a[6]))
    except IndexError:
        return (False, gachalib.types.Card())
    

# other
######################################

def random_card_by_rarity(rarity:str, evil_chance: int=25) -> tuple[bool, gachalib.types.Card]:
    try:
        a = gachalib.gacha_database.read_data(f"SELECT id FROM gacha WHERE (rarity,accepted) = (?,?)", (rarity,True))
        card_id = a[randint(0,len(a)-1)][0]
        card_id = card_id * -1 if randint(1, evil_chance) == 1 else card_id
        success, card = get_card_by_id(card_id)
        if success:
            return(True, card)
        else:
            return (False,gachalib.types.Card())
    except IndexError:
        return (False,gachalib.types.Card())
    

def group_like_cards(a:list[gachalib.types.CardsInventory] | list[gachalib.types.Card] | list[gachalib.types.CardsInventory | gachalib.types.Card]) -> list[tuple[gachalib.types.Card, int]]:
    b = {}

    for i in a:
        if str(i.card_id) in b:
            b[str(i.card_id)] += 1
        else:
            b[str(i.card_id)] = 1

    c = []

    for card_id,count in b.items():
        success, card = gachalib.cards.get_card_by_id(card_id)
        if success:
            c.append((card, count))

    return c


async def approve_card(approve:bool, card:gachalib.types.Card) -> tuple[bool, str]: # success, note
    if not card.accepted:
        if approve:
            if card.rarity == "None":
                return (False, "Please set a rarity first! /z-gacha-admin-setrarity")
            
            gachalib.cards.update_card(card.card_id, "accepted", "1")
            
            userchannel = await gachalib.get_card_maker_channel(card.maker_id)
            await userchannel.send(f"Your card \"{card.name}\" ({card.card_id}) has been ACCEPTED!!! GOOD JOB!!!")

            return (True, f"Approved card ID {card.card_id}!")
        else:

            gachalib.cards.delete_card(card.card_id)

            userchannel = await gachalib.get_card_maker_channel(card.maker_id)
            await userchannel.send(f"Your card \"{card.name}\" ({card.card_id}) has been denied. Sorry for your loss.")
            
            return (True, f"Denied and deleted card ID {card.card_id}")
    else:
        return (False, "Card was already accepted, use /z-gacha-admin-deletecard")


# Making, deleting, editing cards
######################################

def register_new_card(userid:int, messageid:int, id:int, name:str, description:str, rarity:str, filename:str) -> None:
    gachalib.gacha_database.write_data("INSERT INTO gacha \
(maker_id, request_message_id, id, accepted, \
name, description, rarity, filename) \
VALUES (?,?,?,?,?,?,?,?)", (userid,messageid,id,False,name,description,rarity,filename))
    
def update_card(id:int, update, value) -> None:
    gachalib.gacha_database.write_data(f"UPDATE gacha SET {update}=? WHERE id=?;", (value,id))
    
def delete_card(card_id:int) -> bool:
    success, card = get_card_by_id(card_id)
    if success:
        try:
            os.remove("images/" + card.filename)
        except FileNotFoundError:
            pass
        gachalib.gacha_database.write_data(f"DELETE FROM gacha WHERE id=(?);", (card_id,))
        return True
    else:
        return False