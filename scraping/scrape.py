from utils.scrape_utils import web_crawler
import yaml

## Call items from carsearch_config.yaml
with open("utils/profile_config.yaml", "r") as f:
    try:
        config = yaml.load(f, Loader=yaml.FullLoader)
    except:
        raise ValueError("Configuration file is not here")


# Setting config parameters
pos = config["profile_options"]["pos"]

headers = config["urlParams"]["headers"]
cookies = config["urlParams"]["cookies"]

# Scrape links again?
# If true, it will crawl all car links based on the search
# If false, it will skip and use the most recently saved file
scrape_link_bool = config["scrape_links"]


URL = f"https://www.playerprofiler.com/position/{pos}"


def main():
    
    # Initialize instance for web crawler
    auto_web = web_crawler(url=URL, headers=headers, cookies=None)

    # Determine the links for all players on playerprofiler.com
    page_links = auto_web.getNameLinks(
        pop_index=True, save=True, scrape_links=scrape_link_bool
    )

    # Retreive all the car links on a given page
    df = auto_web.scrapePage(page_list=page_links)

    print("Finished")


if __name__ == "__main__":
    main()
