from pymongo import MongoClient

# from splash.api.config import ConfigStore
from splash.teams import NewTeam, Team
from splash.teams.teams_service import TeamsService

from splash.users import AuthenticatorModel,  NewUser, User
from splash.users.users_service import UsersService

def create():
  db = MongoClient()

  users_svc = UsersService(db, 'users')
  teams_svc = TeamsService(db, 'teams')

  user_dict = {
      "given_name": "User",
      "family_name": "McLastName",
      "authenticators": [
          {
              "issuer": "https://accounts.google.com",
              "subject": "x",
              "email": "user@example.com"
          }
      ]
  }
  user = NewUser(**user_dict)
  print(user)
  new_user_uid = users_svc.create("foo", user)

  new_team = {
    "name": "testr",
    "members": {
      new_user_uid: [
        "member"
      ]
    }
  }

  teams_svc.create("foo", NewTeam(**new_team))