"""
things to deal with the actual cards
"""
import gachalib
import db_lib
from random import randint
import os

import gachalib.cards
import gachalib.types

def evilify(card):
    return ("EVIL " + card[0], card[1], card[2] + " evil", card[3], card[4], card[5], card[6] * -1)

# Getting cards
######################################
def get_cards() -> tuple[bool, list[gachalib.types.Card]]:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha", ())
        b = []

        for c in a:
            b.append(gachalib.types.Card(name=c[0],description=c[1],rarity=c[2],filename=c[3],maker_id=c[4],accepted=c[5],card_id=c[6]))

        return (True, b)
    except IndexError:
        return (False, None) # pyright: ignore[reportReturnType]

def get_approved_cards() -> tuple[bool, list[gachalib.types.Card]]:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha WHERE accepted = True", ())
        b = []

        for c in a:
            b.append(gachalib.types.Card(name=c[0],description=c[1],rarity=c[2],filename=c[3],maker_id=c[4],accepted=c[5],card_id=c[6]))

        return (True, b)
    except IndexError:
        return (False, None) # pyright: ignore[reportReturnType]
    
def get_card_by_id(card_id:int) -> tuple[bool, gachalib.types.Card]:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha WHERE (id) = (?)", (abs(int(card_id)),))[0]
        a = evilify(a) if int(card_id) < 0 else a
        return (True, gachalib.types.Card(name=a[0],description=a[1],rarity=a[2],filename=a[3],maker_id=a[4],accepted=a[5],card_id=a[6]))
    except IndexError:
        return (False, None) # pyright: ignore[reportReturnType]


def get_card_by_id_range(id_start:int, id_end:int) -> tuple[bool, list[gachalib.types.Card]]:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha;", ())[id_start-1:id_end]
        b = []

        for c in a:
            b.append(
                gachalib.types.Card(name=c[0],description=c[1],rarity=c[2],filename=c[3],maker_id=c[4],accepted=c[5],card_id=c[6])
            )

        return (True, b)
    except IndexError:
        return (False,None) # pyright: ignore[reportReturnType]
    
def get_unapproved_cards() -> tuple[bool, list[gachalib.types.Card]]:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha WHERE (accepted) = (?);", (False,))
        b = []

        for c in a:
            b.append(
                gachalib.types.Card(name=c[0],description=c[1],rarity=c[2],filename=c[3],maker_id=c[4],accepted=c[5],card_id=c[6])
            )

        return (True, b)
    except IndexError:
        return (False,None) # pyright: ignore[reportReturnType]



# other
######################################

def random_card_by_rarity(rarity:str) -> tuple[bool, gachalib.types.Card]:
    try:
        a = db_lib.read_data(f"SELECT id FROM gacha WHERE (rarity,accepted) = (?,?)", (rarity,True))
        card_id = a[randint(0,len(a)-1)][0]
        card_id = card_id * -1 if randint(1, 25) == 1 else card_id
        success, card = get_card_by_id(card_id)
        if success:
            return(True, card)
        else:
            return (False,None) # pyright: ignore[reportReturnType]
    except IndexError:
        return (False,None) # pyright: ignore[reportReturnType]
    

def group_like_cards(a:list[gachalib.types.Card]) -> list[tuple[gachalib.types.Card, int]]:
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
    db_lib.write_data("INSERT INTO gacha \
(maker_id, request_message_id, id, accepted, \
name, description, rarity, filename) \
VALUES (?,?,?,?,?,?,?,?)", (userid,messageid,id,False,name,description,rarity,filename))
    
def update_card(id:int, update, value) -> None:
    db_lib.write_data(f"UPDATE gacha SET {update}=? WHERE id=?;", (value,id))
    
def delete_card(card_id:int) -> bool:
    success, card = get_card_by_id(card_id)
    if success:
        try:
            os.remove("images/" + card.filename)
        except FileNotFoundError:
            pass
        db_lib.write_data(f"DELETE FROM gacha WHERE id=(?);", (card_id,))
        return True
    else:
        return False