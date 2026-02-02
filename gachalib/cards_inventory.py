"""
things to deal with users and their cards
"""
import db_lib

import gachalib,gachalib.types

def sort_userlist_cards(a:list[gachalib.types.CardsInventory]) -> list[gachalib.types.CardsInventory]:
    return sorted(a, key=lambda b: b.card_id)

def get_users_cards(user_id:int) -> tuple[bool, list[gachalib.types.CardsInventory]]:
    try:
        a = db_lib.read_data(f"SELECT id,card_id FROM gacha_cards WHERE (user_id) = (?)", (user_id,))
        b = []

        for c in a:
            b.append( gachalib.types.CardsInventory(inv_id=c[0],card_id=c[1],user_id=user_id) )

        return (True,b)
    except IndexError:
        return (False,) # pyright: ignore[reportReturnType]
    
def get_users_cards_by_id_range(user_id:int, id_start:int,id_end:int) -> tuple:
    try:
        success, cards = get_users_cards(user_id)
        if success:
            return(True, cards[id_start-1:id_end])
        else:
            return (False,)
    except IndexError:
        return (False,)

def get_users_cards_by_card_id(user_id:int, card_id:int) -> tuple[bool, list[gachalib.types.CardsInventory]]:
    try:
        a = db_lib.read_data(f"SELECT id,card_id FROM gacha_cards WHERE (user_id, card_id) = (?,?)", (user_id, card_id))
        b = []

        for c in a:
            b.append( gachalib.types.CardsInventory(inv_id=c[0],card_id=c[1],user_id=user_id) )
        
        return (True, b)
    except IndexError:
        return (False,) # pyright: ignore[reportReturnType]
    
def give_user_card(user_id:int,card_id:int) -> gachalib.types.CardsInventory:
    a = db_lib.read_data(f"SELECT id FROM gacha_cards;", ())
    if len(a) == 0:
        inv_id = 1
    else:
        inv_id = a[len(a)-1][0] + 1

    db_lib.write_data("INSERT INTO gacha_cards (id,card_id,user_id) VALUES (?,?,?)", (inv_id,card_id,user_id))
    return gachalib.types.CardsInventory(inv_id=inv_id,card_id=card_id,user_id=user_id)

def change_card_owner(user_id:int,inv_id:int) -> bool: # ?
    try:
        db_lib.write_data("UPDATE gacha_cards SET user_id = ? WHERE id = ?", (user_id, inv_id))
        return True
    except IndexError:
        return False
    

def ownsCard(id:int,uid:int) -> bool:
    a = db_lib.read_data(f"SELECT id FROM gacha_cards WHERE (user_id,card_id) = (?,?);", (uid,id))
    if len(a) == 0:
        return False
    else:
        return True