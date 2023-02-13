import os
import requests
from bs4 import BeautifulSoup
import yaml
from yaml.loader import SafeLoader


DOWNLOADS_URL = "https://api.pepy.tech/api/v2/projects/gym"
COLABTORATORS_URLS = "https://api.github.com/repos/Farama-Foundation/{repo}/contributors"
REPOS_USE_URL = "https://github.com/Farama-Foundation/Gymnasium/network/dependents"


def scrape_downloads():
    val = None
    try:
        res = requests.get(DOWNLOADS_URL)
        val = res.json()["total_downloads"]
    except Exception as e:
        print(f"Error while requesting data from: {DOWNLOADS_URL}. This might mean \
                that something changed in the API or the API is not public anymore.")
        print("Error message:")
        print(e)
    return val


def scrape_colaborators():
    MAX_PER_PAGE = 100
    val = None
    usernames = []

    projects = []
    projects_yaml = os.path.join(os.path.dirname(__file__), "..", "_data", "projects.yml")
    with open(projects_yaml) as fp:
        projects = yaml.load(fp, SafeLoader)
        projects = list(map(lambda x: x["github"].split("/")[-1].rstrip("/"), projects))

    for project in projects:
        lastPage = False
        page = 1
        while not lastPage:
            res = requests.get(COLABTORATORS_URLS.format(repo=project) + f"?per_page={MAX_PER_PAGE}&page={page}")
            contributers = res.json()

            if len(contributers) < MAX_PER_PAGE:
                lastPage = True

            for contributer in contributers:
                if contributer["login"] not in usernames:
                    usernames.append(contributer["login"])
            page += 1

    return len(usernames)


def scrape_repos_use():
    try:
        res = requests.get(REPOS_USE_URL)
        soup = BeautifulSoup(res.content, 'html.parser')
        val = soup.select('#dependents > div.Box > div.Box-header.clearfix > div > div.table-list-header-toggle.states.flex-auto.pl-0 > a.btn-link.selected')[0].text.strip().rstrip("Repositories\n")
        val = int(val)
    except Exception as e:
        print(f"Unable to retrieve the number of dependent repositories at {REPOS_USE_URL}. \
               This might mean that something has changed in the page we are trying to scrape. \
               Make sure you update the query accordingly.")
        print("Error message:")
        print(e)
    return val


def scrape_stats():
    stats = {}
    stats_yaml = os.path.join(os.path.dirname(__file__), "..", "_data", "stats.yml")
    with open(stats_yaml) as fp:
        stats = yaml.load(fp, SafeLoader)

    for key, val in stats.items():
        if key == "downloads":
            scraped_val = scrape_downloads()
            stats[key] = scraped_val or val
        elif key == "colaborators":
            scraped_val = scrape_colaborators()
            stats[key] = scraped_val or val
        elif key == "repos_use":
            scraped_val = scrape_repos_use()
            stats[key] = scraped_val or val
        else:
            print("Invalid stat key")

    with open(stats_yaml, "w") as fp:
        yaml.dump(stats, fp)


if __name__ == "__main__":
    scrape_stats()