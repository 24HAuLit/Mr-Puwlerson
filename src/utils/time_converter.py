import sqlite3


def readable_to_time(time, time_type):
    """This function convert time from readable format to seconds.
    :param time: Time to convert
    :param time_type: Type of time to convert"""

    # Convert time
    if time_type == "s":
        time = int(time)
    elif time_type == "m":
        time = int(time) * 60
    elif time_type == "h":
        time = int(time) * 3600
    elif time_type == "d":
        time = int(time) * 86400
    elif time_type == "w":
        time = int(time) * 604800
    elif time_type == "mo":
        time = int(time) * 2592000
    elif time_type == "y":
        time = int(time) * 31536000

    # Return time
    return time


def time_to_readable(guild_id, time):
    """This function convert time from seconds to readable format.
    :param guild_id: ID of the guild
    :param time: Time to convert (getting seconds)"""

    conn = sqlite3.connect(f"./Database/{guild_id}.db")
    c = conn.cursor()

    locale = c.execute("SELECT locale from locale").fetchone()[0]
    conn.close()

    if locale == "fr":
        if time < 60:
            duration = f"{time} secondes"
        elif time < 3600:
            if time % 60 == 0:
                duration = f"{time // 60} minutes"
            else:
                duration = f"{time // 60} minutes et {time % 60} secondes"
        elif time < 86400:
            if time % 3600 == 0:
                duration = f"{time // 3600} heures"
            else:
                if time % 60 == 0:
                    duration = f"{time // 3600} heures et {time % 3600 // 60} minutes"
                else:
                    duration = f"{time // 3600} heures, {time % 3600 // 60} minutes et {time % 60} secondes"
        elif time < 604800:
            if time % 86400 == 0:
                duration = f"{time // 86400} jours"
            else:
                if time % 3600 == 0:
                    duration = f"{time // 86400} jours et {time % 86400 // 3600} heures"
                else:
                    if time % 60 == 0:
                        duration = f"{time // 86400} jours, {time % 86400 // 3600} heures et {time % 3600 // 60} minutes"
                    else:
                        duration = f"{time // 86400} jours, {time % 86400 // 3600} heures, {time % 3600 // 60} minutes et {time % 60} secondes"
        elif time < 2592000:
            if time % 604800 == 0:
                duration = f"{time // 604800} semaines"
            else:
                if time % 86400 == 0:
                    duration = f"{time // 604800} semaines et {time % 604800 // 86400} jours"
                else:
                    if time % 3600 == 0:
                        duration = f"{time // 604800} semaines, {time % 604800 // 86400} jours et {time % 86400 // 3600} heures"
                    else:
                        if time % 60 == 0:
                            duration = f"{time // 604800} semaines, {time % 604800 // 86400} jours, {time % 86400 // 3600} heures et {time % 3600 // 60} minutes"
                        else:
                            duration = f"{time // 604800} semaines, {time % 604800 // 86400} jours, {time % 86400 // 3600} heures, {time % 3600 // 60} minutes et {time % 60} secondes"

    elif locale == 'en':
        if time < 60:
            duration = f"{time} seconds"
        elif time < 3600:
            if time % 60 == 0:
                duration = f"{time // 60} minutes"
            else:
                duration = f"{time // 60} minutes and {time % 60} seconds"
        elif time < 86400:
            if time % 3600 == 0:
                duration = f"{time // 3600} hours"
            else:
                if time % 60 == 0:
                    duration = f"{time // 3600} hours and {time % 3600 // 60} minutes"
                else:
                    duration = f"{time // 3600} hours, {time % 3600 // 60} minutes and {time % 60} seconds"
        elif time < 604800:
            if time % 86400 == 0:
                duration = f"{time // 86400} days"
            else:
                if time % 3600 == 0:
                    duration = f"{time // 86400} days and {time % 86400 // 3600} hours"
                else:
                    if time % 60 == 0:
                        duration = f"{time // 86400} days, {time % 86400 // 3600} hours and {time % 3600 // 60} minutes"
                    else:
                        duration = f"{time // 86400} days, {time % 86400 // 3600} hours, {time % 3600 // 60} minutes and {time % 60} seconds"
        elif time < 2592000:
            if time % 604800 == 0:
                duration = f"{time // 604800} weeks"
            else:
                if time % 86400 == 0:
                    duration = f"{time // 604800} weeks and {time % 604800 // 86400} days"
                else:
                    if time % 3600 == 0:
                        duration = f"{time // 604800} weeks, {time % 604800 // 86400} days and {time % 86400 // 3600} hours"
                    else:
                        if time % 60 == 0:
                            duration = f"{time // 604800} weeks, {time % 604800 // 86400} days, {time % 86400 // 3600} hours and {time % 3600 // 60} minutes"
                        else:
                            duration = f"{time // 604800} weeks, {time % 604800 // 86400} days, {time % 86400 // 3600} hours, {time % 3600 // 60} minutes and {time % 60} seconds"

    return duration
