import os

TOKEN = os.getenv("TOKEN_OFFICIAL")

DATA = {
    "principal": {
        "guild": 419529681885331456,
        "suggestion": 1011704888679477369,
        "suggest_result": 1011705768002727987,
        "bda_waiting": 1046381499143950356
    },
    "logs": {
        "guild": 1025129313546285056,
        "messages": {
            "new": 1025130771456983080,
            "edit": 1025703859689103392,
            "delete": 1025703875061219358
        },
        "moderation": {
            "clear": 1025703890513035284,
            "timeout": 1025705989745422377,
            "ban": 1025706023333408878,
            "nuke": 1025705944266588160
        },
        "ticket": {
            "create": 1030764531720392734,
            "close": 1030764601295519845
        },
        "global": {
            "join": 1039280742993240125,
            "leave": 1039280760403787829
        }
    },
    "roles": {
        "Staff": 1018602650566139984,
        "Moderator": 419532481319010314,
        "Admin": 419532345134284810,
        "Owner": 419532166888816640
    }
}
