# Your Bot token (get it from BotFather)
token = 'TOKEN'

# Message send when user 'start' the bot
start_msg = "Benvenuto su @AFHSearchBot\n"\
            "questo bot ti aiuterà a trovare file/dispositivi/sviluppatori che ti interessano.\n"\
            "Per cercare un file scrivere /find.\n\n"\
            "⚠️Attenzione⚠️\n"\
            "Il bot è stato creato in modo non ufficiale."

# File with 'started' clients
client_file = "clients_id.txt"

# keypad
keypad = [
    ["1", "2", "3", "4"],
    ["5", "6", "7", "8"],
    ["9", "10", "11", "12"],
    ["13", "14", "15"]
]

# typepad
typepad = [
    ["files"],
    ["devices"],
    ["developers"]
]

# type
type_ = {
    "files": "file",
    "devices": "dispositivi",
    "developers": "sviluppatori"
}