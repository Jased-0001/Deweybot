"""
things to deal with users and their cards
"""
import gachalib.cards
import gachalib,gachalib.types

# Not sure if these are being used, since the InventoryView should take care of all this
def sort_cards_by_id(a:list[gachalib.types.CardsInventory] | list[gachalib.types.Card]) -> list[gachalib.types.CardsInventory | gachalib.types.Card]:
    return sorted(a, key=lambda b: b.card_id)

def sort_cards_by_quantity(a:list[tuple[gachalib.types.Card, int]]) -> list[tuple[gachalib.types.Card, int]]:
    return sorted(a, key=lambda b: b[1])

def sort_cards_by_rarity(a:list[gachalib.types.CardsInventory] | list[gachalib.types.Card]) -> list[gachalib.types.CardsInventory | gachalib.types.Card]:
    if type(a) == gachalib.types.Card:
        return sorted(a, key=lambda b: gachalib.rarity_order[b.rarity]) # type: ignore
    else:
        #didn't test this
        return sorted(a, key=lambda b: gachalib.rarity_order[gachalib.cards.get_card_by_id(card_id=b.card_id)[1].rarity])

def get_users_cards(user_id:int,include_evil:bool=True) -> tuple[bool, list[gachalib.types.CardsInventory]]:
    try:
        a = gachalib.gacha_database.read_data(f"SELECT id,card_id FROM gacha_cards WHERE (user_id) = (?)", (user_id,))
        b = []

        for c in a:
            if c[1] < 0 and not include_evil: continue
            b.append( gachalib.types.CardsInventory(inv_id=c[0],card_id=c[1],user_id=user_id) )

        return (True,b)
    except IndexError:
        return (False, [])
    
def get_users_cards_by_id_range(user_id:int, id_start:int,id_end:int,include_evil:bool=True) -> tuple[bool, list[gachalib.types.CardsInventory]]:
    try:
        success, cards = get_users_cards(user_id=user_id,include_evil=include_evil)
        if success:
            return(True, cards[id_start-1:id_end])
        else:
            return (False, [])
    except IndexError:
        return (False, [])

def get_users_cards_by_card_id(user_id:int, card_id:int) -> tuple[bool, list[gachalib.types.CardsInventory]]:
    try:
        a = gachalib.gacha_database.read_data(f"SELECT id,card_id FROM gacha_cards WHERE (user_id, card_id) = (?,?)", (user_id, card_id))
        b = []

        for c in a:
            b.append( gachalib.types.CardsInventory(inv_id=c[0],card_id=c[1],user_id=user_id) )
        
        return (True, b)
    except IndexError:
        return (False, [])
    
def give_user_card(user_id:int,card_id:int) -> gachalib.types.CardsInventory:
    a = gachalib.gacha_database.read_data(f"SELECT id FROM gacha_cards;", ())
    if len(a) == 0:
        inv_id = 1
    else:
        inv_id = a[len(a)-1][0] + 1

    gachalib.gacha_database.write_data("INSERT INTO gacha_cards (id,card_id,user_id) VALUES (?,?,?)", (inv_id,card_id,user_id))
    return gachalib.types.CardsInventory(inv_id=inv_id,card_id=card_id,user_id=user_id)

def change_card_owner(user_id:int,inv_id:int) -> bool:
    try:
        gachalib.gacha_database.write_data("UPDATE gacha_cards SET user_id = ? WHERE id = ?", (user_id, inv_id))
        return True
    except IndexError:
        return False
    

def ownsCard(id:int,uid:int) -> tuple[bool, int]:
    a = gachalib.gacha_database.read_data(f"SELECT id FROM gacha_cards WHERE (user_id,card_id) = (?,?);", (uid,id))
    if len(a) == 0:
        return (False,len(a))
    else:
        return (True,len(a))
    
def get_all_issued() -> list[gachalib.types.CardsInventory]:
    try:
        a = gachalib.gacha_database.read_data(f"SELECT id,card_id,user_id FROM gacha_cards", parameters=())
        b = []

        for c in a:
            b.append( gachalib.types.CardsInventory(inv_id=c[0],card_id=c[1],user_id=c[2]) )
        
        return b
    except IndexError:
        return []