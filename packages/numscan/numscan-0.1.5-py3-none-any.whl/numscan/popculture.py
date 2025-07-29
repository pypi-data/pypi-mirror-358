from .base import NumberCounter

class PopCultureCounter(NumberCounter):
    _pop_culture_data: dict[int, str] = {
        3: "Trinity in many religions, e.g. Christianity (Father, Son, Holy Spirit)",
        7: "Often considered a lucky number; Seven Wonders of the World",
        11: "Stranger Things – Eleven is the name of a main character with powers",
        13: "Unlucky number in many cultures",
        23: "Conspiracy number (e.g., 23 enigma)",
        42: "The answer to life, the universe and everything (The Hitchhiker’s Guide to the Galaxy)",
        66: "Order 66 in Star Wars (Jedi purge)",
        69: "Known for sexual innuendo, popular internet meme",
        88: "Back to the Future – Delorean time travel speed (88 mph)",
        99: "Agent 99 in *Get Smart*",
        101: "101 Dalmatians (Disney)",
        108: "Sacred number in Hinduism and Buddhism",
        616: "Marvel Comics multiverse – Earth-616 is the primary continuity",
        666: "Number of the Beast (Biblical, Book of Revelation)",
        1337: "Leetspeak for 'leet' (elite) in hacker culture",
        1408: "Stephen King horror short story and movie",
        3000: "Marvel – 'I love you 3000' (Tony Stark’s daughter in Avengers: Endgame)",
        4400: "*The 4400* – sci-fi series about abducted people with powers",
        4711: "Classic German perfume brand; used synonymously with 'something old-fashioned'",
        6174: "Kaprekar’s constant – a special number in mathematics"
    }

    def _generate_numbers(self) -> list[int]:
        return list(self._pop_culture_data.keys())

    def get_description(self, number: int) -> str:
        return self._pop_culture_data.get(number, "No known pop culture reference.")