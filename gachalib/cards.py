"""
things to deal with the actual cards
"""
import gachalib
import db_lib
import os

import gachalib.types


# Getting cards
######################################

def get_card_by_id(card_id:int) -> tuple[bool, gachalib.types.Card]:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted FROM gacha WHERE (id) = (?)", (card_id,))[0]
        return (True, gachalib.types.Card(name=a[0],description=a[1],rarity=a[2],filename=a[3],maker_id=a[4],accepted=a[5],card_id=card_id))
    except IndexError:
        return (False, None) # pyright: ignore[reportReturnType]


def get_card_by_id_range(id_start:int, id_end:int) -> tuple[bool, list[gachalib.types.Card]]:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha WHERE (id) BETWEEN (?) AND (?);", (id_start,id_end))
        b = []

        for c in a:
            b.append(
                gachalib.types.Card(name=c[0],description=c[1],rarity=c[2],filename=c[3],maker_id=c[4],accepted=c[5],card_id=c[6])
            )

        return (True, b)
    except IndexError:
        return (False,None) # pyright: ignore[reportReturnType]
    

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