from ovos_utils.log import LOG
from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill

try:
    from pymetal import MetalArchives
except ImportError:
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__))
    from pymetal import MetalArchives

__author__ = 'jarbas'


class MetalSkill(OVOSSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archives = MetalArchives()
        self.band_index = 0
        self.last_band = ""

    def speak_band_data(self, band):
        LOG.info(band)
        self.speak_dialog("origin", {"country": band["country"]})
        self.speak_dialog("styledialog", {"style": band["genre"]})
        if band["status"].lower() != "active":
            self.speak_dialog("splitup")
        else:
            self.speak_dialog("active", {"date": band["date"]})

    @intent_handler(
        IntentBuilder("RandomMetalBandIntent").one_of(
            "MetalKeyword", "MetalGenreKeyword").require("RandomKeyword"))
    def handle_suggest_intent(self, message):
        genre = message.data.get("MetalGenreKeyword")
        band = self.archives.random_band(genre)
        if genre and not band:
            self.speak_dialog("not.found", {"band": genre})
        else:
            self.speak_dialog("metal_recommend", {"band": band["name"]})
            self.speak_band_data(band)

    @intent_handler(
        IntentBuilder("SearchMetalBandIntent").require("MetalArchives").
        require("search").optionally("MetalGenreKeyword").optionally("for"))
    def handle_search_intent(self, message):
        band_name = message.data.get("MetalBandNameKeyword",
                                     message.utterance_remainder())
        self.last_band = band_name
        band_genre = message.data.get("MetalGenreKeyword", "")
        self.band_index = int(message.data.get("index", 0))
        for band in self.archives.search_band(band_name=band_name,
                                              genre=band_genre,
                                              index=self.band_index):
            band = self.archives.get_band_data(band["url"])
            self.speak(band["name"])
            self.speak_band_data(band)
            self.set_context("search_next_band")
            self.set_context("MetalGenreKeyword", band_genre)
            return
        self.speak_dialog("not.found", {"band": band_name})

    @intent_handler(
        IntentBuilder("SearchNextMetalBandIntent").require("next").require(
            "search_next_band").optionally("MetalGenreKeyword").optionally(
            "search").optionally("for"))
    def handle_search_next_intent(self, message):
        message.data["index"] = self.band_index + 1
        message.data["MetalBandNameKeyword"] = self.last_band
        self.handle_search_intent(message)
