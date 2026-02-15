class Statistics:
    def __init__(self,highestbalance:int=0,transactions:int=0,spent:int=0,totalearned:int=0) -> None:
        self.highestbalance:int  = highestbalance
        self.transactions:int    = transactions
        self.spent:int           = spent
        self.totalearned:int     = totalearned

    def __repr__(self):
        return f"(Statistics highestbalance = '{self.highestbalance}', transactions = {self.transactions}\
, spent = {self.spent}, totalearned = {self.totalearned})"
    def __eq__(self, other):
        return self.highestbalance == other.higherbalance and self.transactions == other.transactions and \
            self.spent == other.spent and self.totalearned == other.totalearned


class User:
    def __init__(self, uid: int = 0, balance: int = 0, statistics: Statistics = Statistics()) -> None:
        self.uid: int                 = uid
        self.balance: int             = balance
        self.statistics: Statistics   = statistics
    
    def __repr__(self):
        return f'(User uid = {self.uid}, balance = {self.balance}, statistics = {self.statistics})'
    def __eq__(self, other):
        return self.uid == other.uid
    