"""
nfl-web-scraping.utils
~~~~~~~~~~~~~~
This module provides utility functions that are used within scrape.py to collect data from www.playerprofiler.com.
"""
from utils.att_list_headings import *

from bs4 import BeautifulSoup
import requests
import re

import numpy as np
import pandas as pd
from itertools import chain
import os
import logging
import pandas as pd
from tqdm import tqdm
import time


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class web_crawler:
    """
    web_crawler is a class that serves as a blueprint for an instance.

    This crawler will scrape data from https://www.playerprofiler.com, using inputs
    to determine which position to scrape. All players scraped for a specific position
    will be saved separately in a csv file inside the directory ../scraped_data/. Please
    refer to the README.md file to initialize and use this web crawler.

    Parameters
    ----------

    url (str): the url of the website (default = https://www.playerprofiler.com/position/POSITION})
    headers (str): The headers that are used for your web browser. If you do not know your headers,
                   please visit https://www.whatismybrowser.com/detect/what-is-my-user-agent/ ,
                   and copy and paste your user agent in the /profile_config.yaml file under headers.
    cookies (str): These are cookies that are saved on your web browser. default = None

    Returns
    --------
    getPagebs4: Returns html parsed content based on the given url
    getNameLinks: Returns a list of player profile links for a given position.
                  Option to save list as a .csv file.
    scrapePage: Returns a csv file of different football statistics and attributes for all players
                that were provided by the getNameLinks function. This function saves a .csv file in
                ../scraped_data/, which can later be used to for analysis

    Notes
    -----
    Use the profile_config.yaml to customize your web scraping parameters. For example, you can specify
    which position you want to scrape data for (running back, quarterback etc...)
    """

    def __init__(self, url, headers, cookies):
        self.url = url
        self.headers = headers
        self.cookies = cookies

        self.LINKS_OUTPATH = "scraped_data/"
        self.pos_str = self.url.split("/")[-1]
        self.link_path = self.LINKS_OUTPATH + self.pos_str + ".csv"

    def __repr__(self):
        """
        Returns the string representation of the value passed to eval function by default.
        """
        return f"web_crawler({self.url}, {self.headers}, {self.cookies}, {self.scrape_flag})"

    def pos_assert_check(self):
        """
        Asserts that the position parameter from profile_config.yaml is set to one of the 4 position options
        """
        pos_array = ["running-back", "quarterback", "wide-receiver", "tight-end"]

        if self.pos_str not in pos_array:
            raise ValueError(
                f'The "pos" parameter in profile_config.yaml is not set to one of {pos_array}'
            )

    def getPagebs4(self, url):
        """
        This gets the page html code for a given page on www.playerprofiler.com

        Parameters
        ----------
        url (str): the url of the website (default = https://www.playerprofiler.com/position/POSITION})

        Returns
        --------
        soup (bs4 instance): Returns html parsed content based on the given url
        """
        req = requests.get(url=url, headers=self.headers, cookies=self.cookies)
        if req.status_code != 200:
            logging.error("Reqeust code is not [200]. Could not access page")
            return None
        soup = BeautifulSoup(req.text, "html.parser")
        return soup

    def getNameLinks(self, pop_index=True, save=True, scrape_links=True):
        """
        Retreives the links for all players at a given position. Will save all links in a .csv
        file that will be later called for scraping.

        Parameters
        ----------
        pop_index (bool): Determines whether to scrape players without a popularity index, a measure of how
                          often a player profile is viewed on the website
        save (bool): save .csv file of player links, overwriting the last version
        scrape_links (bool): A boolean function to determine whether you should run this function or not

        Returns
        --------
        name_links (list): A list of http links for all players at a given position

        Notes
        -----
        If you have already ran and saved the .csv file, you can set scrape_links to 'False' in
        'profile_config.yaml', and it will bypass this

        """
        # Check if the position parameter is properly set
        self.pos_assert_check()

        if scrape_links:
            soup = self.getPagebs4(url=self.url)
            names = soup.find_all(
                "a",
                {
                    "class": "flex items-center justify-between space-x-3 px-4 md:px-8 pt-2"
                },
                href=True,
            )

            if pop_index is True:
                name_links = []
                for name in names:
                    if name.find("span").get_text() == "-":
                        pass
                    else:
                        name_links.append(name["href"])
            else:
                name_links = [name["href"] for name in names]

            logging.info(f"retrieved {len(name_links)} players from {self.pos_str}")
            logging.info(f"User wanted population_index scraping set to: {pop_index}")

            if save:
                df = pd.DataFrame()
                df["saved_links"] = name_links
                self.check_path_exist(self.LINKS_OUTPATH)
                df.to_csv(self.link_path, index=False)
                logging.info(f"Saving page links in {self.LINKS_OUTPATH}")

            return name_links

        else:
            # load previous position link csv file, convert to numpy file
            try:
                name_links = pd.read_csv(self.link_path).to_numpy().ravel()
            except:
                logging.warn("Links for position csv do not exist, scraping now.")
                name_links = self.getNameLinks(
                    pop_index=pop_index, save=True, scrape_links=True
                )
            return name_links

    def scrapePage(self, page_list=None, save=True):
        """
        Scrapes all information on a given player profiler page, saves all data to a final .csv file

        Parameters
        ----------
        page_list (list): A list of player links retrieved from 'getNameLinks'
        save (bool): Determines whether to save .csv file

        Returns
        --------
        df_stats (DataFrame): A dataframe of all player data for a given position
        """
        # Retrieves an array of data headings based on the position
        att_list = pos_dict(self.pos_str)
        # Makes empty dictionary from att_list
        att_dict = {item: None for item in list(chain.from_iterable(att_list))}
        # Setting empty array to append all scraped data
        stats = []

        # Iterate through each page_list
        for page in tqdm(page_list):
            # Retrieve soup instance
            soup = self.getPagebs4(url=page)

            # Title card (top part of the card): Name, position, team.
            card = soup.find(
                "div",
                {
                    "class": "flex flex-col justify-between h-full px-4 pt-4 overflow-hidden"
                },
            )
            soup_cmd = [
                get_text_exist(card, "h1"),
                get_text_exist(
                    card, "div", "leading-none text-xl md:text-2xl -mb-px md:mb-0"
                ),
                get_text_exist(card, "a", "text-blue-light hover:underline").replace(
                    "\n", ""
                ),
            ]
            # Write to dictionary
            card_to_dict(att_list[0], soup_cmd, att_dict)

            # Player card (top left hand side): Height, weight, draft, college, age
            player_card = get_card(
                soup,
                tag="span",
                tag_class="class",
                html_str="leading-none whitespace-nowrap",
            )

            soup_cmd = [
                convert_inch_to_cm(player_card[0]),
                convert_to_num(player_card[1], remove_chars=True),
                player_card[3],
                player_card[4],
                convert_to_num(player_card[5]),
            ]
            # Write to dictionary
            card_to_dict(att_list[1], soup_cmd, att_dict)

            # Metrics card: 40, speed, burst, agility, bench
            metrics_card = get_card(
                soup,
                tag="span",
                tag_class="class",
                html_str="block font-light text-xs sm:text-sm leading-none",
            )
            soup_cmd = [convert_to_num(metrics_card[k]) for k in range(0, 5)]
            # Write to dictionary
            card_to_dict(att_list[2], soup_cmd, att_dict)

            # College stats card: col-dom, col-ypc/ypr, col-tar/sparq, col-sparq
            key_soup = soup.find_all("div", {"class": "flex items-start space-x-1"})
            key_card = get_card(key_soup, tag="span")
            key_card = [x for x in key_card if "(" not in x]
            soup_cmd = [convert_to_num(key_card[k]) for k in range(0, 4)]
            # Write to dictionary
            card_to_dict(att_list[3], soup_cmd, att_dict)

            # Season stats card: 'games-played', 'rush-attempts',
            #                    'rush-yards', 'ypc-nfl', 'rec',
            #                    'rec-yards', 'tds', 'fantasy-ppg'
            # TODO: Only retrieves latest year, get all years later
            szn_soup = soup.find(
                "tr", {"class": "border-t border-solid border-gray-700"}
            )
            try:
                # If there is no 2022 stats, fill szn_card with nan
                szn_card = get_card(
                    szn_soup,
                    tag="span",
                    tag_class="class",
                    html_str="text-xxs md:text-base",
                )
            except:
                szn_card = ["NaN"] * 9
            soup_cmd = [convert_to_num(szn_card[k]) for k in range(1, 9)]
            card_to_dict(att_list[4], soup_cmd, att_dict)

            # appends all values in the dictionary to an array
            stats.append(np.array(tuple(att_dict.values())))

        # Writes the appended array of stats to a pandas dataframe
        df_stats = pd.DataFrame(stats, columns=list(chain.from_iterable(att_list)))
        # Saving df file
        if save:
            # Setting the output path for writing .csv
            todays_date = time.strftime("%d-%m-%Y")
            OUTPUT = (
                self.LINKS_OUTPATH
                + "nfl_stats-"
                + self.pos_str
                + "-"
                + todays_date
                + ".csv"
            )
            logging.info(f"Saving csv... in {OUTPUT}")
            df_stats.to_csv(OUTPUT, index=False)

        return df_stats

    @classmethod
    def check_path_exist(self, path=None):
        """
        Check if path exists, if not, creates one.
        """
        if os.path.isdir(path):
            pass
        else:
            print("Path does not exist. Creating path now.")
            os.mkdir(path)


##### FUNCTIONS ######


def pos_dict(pos_str):
    """
    Returns a list of attributes based on the position.
    Each position has different set/order of attributes

    Parameters
    ----------
    pos_str (str): The position being scraped

    Returns
    --------
    att_list (list): A list of positional headings from website player profile.

    """
    if pos_str == "quarterback":
        return att_list_qb
    elif pos_str == "running-back":
        return att_list_rb
    elif pos_str == "wide-receiver":
        return att_list_wr
    elif pos_str == "tight-end":
        return att_list_te
    else:
        raise ValueError("This must be one of 4 offensive football positions")


def get_text_exist(soup, tag, tag_class=None, return_text=True):
    """
    Beautifulsoup function that retrieves the text from a search function in bs4.

    Parameters
    ----------
    soup (bs4 instance): A parsed html code from a given player profile link
    tag (str): Search tag for soup.find_all()
    tag_class (str): Search class for soup.find_all()
    return_text (bool): Boolean function to return text or not from beautifulsoup search

    Returns
    --------
    The text portion of the beautifulsoup search.

    """
    if tag_class:
        item = soup.find(tag, {"class": tag_class})
    else:
        item = soup.find(tag)

    if item and return_text:
        return item.get_text()
    else:
        return "NaN"


def get_card(soup, tag, tag_class=None, html_str=None, return_text=True):
    """
    Retireves segments of scraped data from the website. Uses the soup parser to identify
    the different types of cards (college, metrics, player profile cards etc...). This function
    formats the cards in an easy-to-scrape format.

    Parameters
    ----------
    soup (bs4 instance): A parsed html code from a given player profile link
    tag (str): Search tag for soup.find_all()
    tag_class (str): Search class for soup.find_all()
    html_str (str): The text within the tag_class to search for
    return_text (bool): Boolean function to return text or not from beautifulsoup search

    Returns
    --------
    The beautifulsoup parsed data from a given card.

    """

    if tag_class:
        item = soup.find_all(tag, {tag_class: html_str})
    else:
        try:
            item = soup.find_all(tag)
        except:
            item_list = []
            for s in soup:
                item_list.append(s.find(tag).get_text())
            return item_list

    if item and return_text:
        item_list = [k.get_text() for k in item]
        return item_list
    else:
        return item


def convert_to_num(item, remove_chars=True):
    """
    A function to convert string entries to integers from the player profiler website
    """

    if remove_chars:
        item = re.sub("[^\d.]+", "", item)

    if item.isdigit():
        return int(item)
    elif item.count(".") == 1:
        return float(item)
    else:
        return np.nan


def convert_inch_to_cm(item):
    """
    A function to convert inches to centimeters for height on the website
    """

    item = re.sub("\D", "", item)
    try:
        feet, inches = float(item[0]), float(item[1])
    except:
        return np.nan

    inches += feet * 12

    cm = round(inches * 2.54, 1)

    return cm


def card_to_dict(att_list, soup_cmd, att_dict):
    """
    A function to write the soup parsed data to the attribute dictionary. This dictionary will then be
    written to a pandas dataframe.

    Parameters
    ----------
    att_list (list): A list of statistical headers on the website.
                     E.G: yards per carry, receptions, touchdowns etc...

    soup_cmd (list): A list of beautiful soup commands to parse data from a given card

    att_dict (dict): the dictionary that is storing all scraped data from a give player
    """

    assert len(att_list) == len(
        soup_cmd
    ), "The attribute dictionary list does not match the number of attributes"

    zip_list = list(zip(att_list, soup_cmd))

    for att in zip_list:
        att_dict[att[0]] = att[1]
