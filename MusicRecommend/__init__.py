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
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import requests
from lxml import html
import bs4

__author__ = 'jarbas'

logger = getLogger(__name__)


class MetalSkill(MycroftSkill):

    def __init__(self):
        super(MetalSkill, self).__init__(name="MetalSkill")
        self.Name = ""
        self.Style = "Metal"
        self.Theme = ""
        self.Label = ""
        self.Country = ""
        self.Location = ""
        self.Status = ""
        self.Date = ""
        self.Years = ""
        self.link = "http://www.metal-archives.com/band/random"

    def initialize(self):

        suggest_intent = IntentBuilder("SuggestMetalIntent") \
            .require("MetalRecomendKeyword").build()
        self.register_intent(suggest_intent,
                             self.handle_suggest_intent)

    def handle_suggest_intent(self, message):

        self.get_band()
        #"Tell name"
        self.speak_dialog("metal_recommend", {"band":self.Name})
        self.speak_dialog("origin", {"country":self.Country})
        #tell style
        self.speak_dialog("styledialog", {"style":self.Style})
        #tell band status
        if self.Status != "active":
            self.speak_dialog("splitup")
        else:
            #how long been playing
            self.speak_dialog("active", {"date":self.Date})

        self.add_result("Band_Name",self.Name)
        self.add_result("Band_Style",self.Style)
        self.add_result("Band_Theme", self.Theme)
        self.add_result("Band_Label", self.Label)
        self.add_result("Band_Country", self.Country)
        self.add_result("Band_Location", self.Location)
        self.add_result("Band_Status", self.Status)
        self.add_result("Band_Formation_Date", self.Date)
        self.add_result("Band_Active_Years", self.Years)
        self.emit_results()

    def get_band(self):
        sucess = False
        while not sucess:
            try:
                response = requests.get('http://www.metal-archives.com/band/random')
                tree = html.fromstring(response.content)
                soup = bs4.BeautifulSoup(response.text, "lxml")

                self.Name = soup.select('h1 a[href^=http://www.metal-archives.com]')[0].get_text()
                self.link = soup.select('h1 a[href^=http://www.metal-archives.com]')[0].attrs.get('href')
                self.Style = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[1]/text()")[0]
                self.Theme = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[2]/text()")[0]
                self.Label = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[3]/text()")[0]
                self.Country = tree.xpath(".//*[@id='band_stats']/dl[1]/dd[1]/a/text()")[0]
                self.Location = tree.xpath(".//*[@id='band_stats']/dl[1]/dd[2]/text()")[0]
                self.Status = tree.xpath(".//*[@id='band_stats']/dl[1]/dd[3]/text()")[0]
                self.Date = tree.xpath(".//*[@id='band_stats']/dl[1]/dd[4]/text()")[0]
                years_active = tree.xpath(".//*[@id='band_stats']/dl[3]/dd/text()")[0]
                self.Years = years_active.strip()
                sucess = True
            except:
                pass

    def stop(self):
        pass


def create_skill():
    return MetalSkill()
