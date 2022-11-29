# README for nfl-pp-scrapers

This is a repository for scraping data from the website https://www.playerprofiler.com. You can retreive data from players based on their offensive positions [QB, RB, WR, TE]. Running a web scraping script will automatically download and store data in .csv files. Below are the instructions to install and run this project.

For now, data is being scraped from the following parts of the website:

![Playerprofiler](/images/highlight_image.jpg)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
    - Scraping
    - Preprocessing
    - Training
- [Support](#support)
- [Contributing](#contributing)

## Installation

Download this repository using the following code:

```
git clone https://github.com/jsawalha/nfl-pp-scraper.git
```

Download the requisite libraries for this repo:
```
pip install .
```

OR

```
pip install -r requirements.txt
```

## Usage

### Scraping

To run the web scraping script, the command line in the terminal is:

```
python scraping/scrape.py
```

Customizing your web scraping script is done using the `scraping/utils/config.yaml`. Here, you can do the following:
- Set the football position that you want to scrape (`running-back`, `quarterback`, `tight-end`, `wide-reciever`)
- *You can enter in your header user agent* (Might be mandatory for web scraping. Follow instructions inside the `config.yaml` file)
- Control whether you want to scrape ALL players at a given position, OR just the most popular ones (using `pop_index`)

Once you have set your configuartion, you can run `scrape.py`, and the saved data will be stored in `scraping/scraped_data/`
## Support

Please [open an issue](https://github.com/fraction/readme-boilerplate/issues/new) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/fraction/readme-boilerplate/compare/).
