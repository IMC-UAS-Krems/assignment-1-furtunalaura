from datetime import date

class User:
    def __init__(self, user_id:str, name:str, age:int):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions: list["ListeningSession"] = []
    def add_session(self, session:"ListeningSession") ->None:
        #add a listening session
        self.sessions.append(session)
    def total_listening_seconds(self) ->int:
        # sum all session durations
        return sum(session.duration_listened_seconds for session in self.sessions)
    def total_listening_minutes(self) -> float:
        #convert seconds to minutes
        return self.total_listening_seconds() / 60
    def unique_tracks_listened(self) -> set[str]:
        #return a set of track IDs
        return {session.track.track_id for session in self.sessions}

class FreeUser(User):
    MAX_SKIPS_PER_HOUR: int = 6  # class-level constant
    def __init__(self, user_id:str, name:str, age:int):
        super().__init__(user_id, name, age)

class PremiumUser(User):
    def __init__(self, user_id:str, name:str, age:int, subscription_start:date):
        super().__init__(user_id, name, age)
        self.subscription_start = subscription_start

class FamilyAccountUser(User):
    def __init__(self, user_id:str, name:str, age:int):
        super().__init__(user_id, name, age)
        #list of family members
        self.sub_users: list["FamilyMember"] = []
        #add family member to the account
    def add_sub_user(self, sub_user:"FamilyMember") -> None:
        self.sub_users.append(sub_user)
        #return a list of all users in the family account
    def all_members(self) ->list[User]:
        return [self] +self.sub_users

class FamilyMember(User):
    def __init__(self, user_id:str, name:str, age:int, parent: "FamilyAccountUser"):
        super().__init__(user_id, name, age)
        self.parent: FamilyAccountUser = parent