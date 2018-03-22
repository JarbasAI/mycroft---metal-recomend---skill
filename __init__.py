# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
try:
    from pymetal import MetalArchives
except ImportError:
    import sys
    from os.path import dirname
    sys.path.append(dirname(__file__))
    from pymetal import MetalArchives

__author__ = 'jarbas'


class MetalSkill(MycroftSkill):

    def __init__(self):
        super(MetalSkill, self).__init__(name="MetalSkill")
        self.archives = MetalArchives()
        self.band_index = 0
        self.last_band = ""

    def speak_band_data(self, band):
        LOG.info(band)
        self.speak_dialog("origin", {"country": band["country"]})
        self.speak_dialog("styledialog", {"style": band["genre"]})
        if band["active"].lower() != "active":
            self.speak_dialog("splitup")
        else:
            self.speak_dialog("active", {"date": band["date"]})

    @intent_handler(IntentBuilder("RandomMetalBandIntent")
                    .one_of("MetalKeyword", "MetalGenreKeyword")
                    .require("RandomKeyword"))
    def handle_suggest_intent(self, message):
        genre = message.data.get("MetalGenreKeyword")
        band = self.archives.random_band(genre)
        if genre and not band:
            self.speak_dialog("not.found", {"band": genre})
        else:
            self.speak_dialog("metal_recommend", {"band": band["name"]})
            self.speak_band_data(band)

    @intent_handler(IntentBuilder("SearchMetalBandIntent")
                    .require("MetalArchives")
                    .require("search")
                    .optionally("MetalGenreKeyword")
                    .optionally("for"))
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

    @intent_handler(IntentBuilder("SearchNextMetalBandIntent")
                    .require("next")
                    .require("search_next_band")
                    .optionally("MetalGenreKeyword")
                    .optionally("search")
                    .optionally("for"))
    def handle_search_next_intent(self, message):
        message.data["index"] = self.band_index + 1
        message.data["MetalBandNameKeyword"] = self.last_band
        self.handle_search_intent(message)


def create_skill():
    return MetalSkill()
