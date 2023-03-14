from bots.translate_tiktoks import TranslateTikToksBot

translation_settings = {
    # language settings
    "src": "th",
    "dst": "en",
    # replacements applied before translating
    "glossary": {
        # "ง้อ": "reconcile",
        # "งอน": "sulk",
        "มุมุ": "mumu",
        "มามี้": "Mami",
        "ยัก": "รัก",  # yak
        "ปีโย๊": "Piyo",
        "ฟรีนกี้": "Freenky",
        "พี่ฟรีน": "P'Freen",
        "ฟรีน": "Freen",
        "คุณสาม": "คุณแซม",  # Khun Sam
        "นุคน": "หนู",  # Nu -> Sandra
        "นุ": "หนู",
        "หนู": "แซนดร้า",
        "น้องพุง": "Nong Belly",
        "น้อง": "Nong",
        "พี่": "Phi",
        "คุณ": "Khun",
        # "อะ": "",  # a
    },
    # replacements applied after translating
    "corrections": {
        "Sandra": "Nu",
        "sandra": "Nu",
        "Beck ": "Bec ",
        "I am": "",
        "I'm ": "",
        "I ": "",
        " me ": " me/you ",
        " me.": " me/you.",
        "boyfriend": "girlfriend",
        " him ": " her ",
        " him.": " her.",
        "his ": "her ",
    },
}

bot_settings = {
    "tiktok_handles": {
        "srchafreen": "freen",
        "angelssbecky": "becky",
    },
    "emojis": {
        "freen": "\ud83d\udc30",
        "becky": "\ud83e\udda6",
    },
}


def main():
    bot = TranslateTikToksBot(
        src=translation_settings["src"],
        dst=translation_settings["dst"],
        glossary=translation_settings["glossary"],
        corrections=translation_settings["corrections"],
        handles=bot_settings["tiktok_handles"],
        emojis=bot_settings["emojis"],
        )
    bot.start()

if __name__ == "__main__":
    main()