# encoding: utf-8
from selenium.webdriver import Chrome
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import json
import csv

def get_stars(element):
    soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
    return len(soup.findAll(class_='fa fa-star', recursive=True))


def get_materials(soup):
    items = map(lambda x: x.contents[0], soup.findAll(class_="item-name", recursive=True))
    quantity = map(lambda x: int(x.contents[0].replace("x", "").replace(".", "")),
                   soup.findAll(class_="item-amount", recursive=True))
    return dict(zip(items, quantity))


def get_elite_resources(stars):
    def parse(element):
        resources = []
        soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
        materials = get_materials(soup)
        for name, quantity in materials.items():
            resources.append({"name": name, "quantity": quantity})
        return resources

    elite1_resources = dict()
    elite2_resources = dict()
    if stars >= 3:
        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="elite1Stats"]/div[2]/div[2]')))
        elite1_resources = parse(element)

    if stars > 3:
        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="elite2Stats"]/div[2]/div[2]')))
        elite2_resources = parse(element)

    return [{"level": 1, "resources": elite1_resources}, {"level": 2, "resources": elite2_resources}]


def get_upgrade_json(iteration, materials):
    resources = []
    for name, quantity in materials.items():
        resources.append({"name": name, "quantity": quantity})
    return {"level": iteration, "resources": resources}


def get_skills_resources(stars):
    def parse_upgrade(element):
        result = []
        soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
        for iteration, skill in enumerate(soup.findAll(class_="skillstats", recursive=True), start=1):
            if iteration <= 7:
                result.append(get_upgrade_json(iteration, get_materials(skill)))
            else:
                continue
        return {"upgrade": result}

    def parse_mastery(element, skill_no):
        result = []
        soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
        for iteration, skill in enumerate(soup.findAll(class_="skillstats", recursive=True), start=1):
            if iteration > 7:
                result.append(get_upgrade_json((iteration % 7), get_materials(skill)))
            else:
                continue
        return {"skill": skill_no, "upgrade": result}

    mastery = []
    # sleep(4)
    # element = WebDriverWait(driver, delay).until(
    #     EC.presence_of_element_located((By.XPATH, '//*[@id="op-rarity"]')))
    # stars = get_stars(element)

    # Get Upgrades
    element = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="skill0StatsCollapsible"]')))
    upgrade = parse_upgrade(element)

    # Get Mastery1
    if stars >= 3:
        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="skill0StatsCollapsible"]')))
        mastery.append(parse_mastery(element, 1))

    # Get Mastery2
    if stars >= 4:
        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="skill1StatsCollapsible"]')))
        mastery.append(parse_mastery(element, 2))

    # Get Mastery3
    if stars == 6:
        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="skill2StatsCollapsible"]')))
        mastery.append(parse_mastery(element, 3))

    return {**upgrade, "mastery": mastery}


user_operators_path = 'files/user_operators.csv'
json_path = 'files/json/'

with open(user_operators_path, mode="r", encoding="utf-8") as f:
    operators = [dict(operator) for operator in csv.DictReader(f, delimiter=';')]
    f.close()

with Chrome(executable_path='./chromedriver94.exe') as driver:
    for iteration, operator in enumerate(operators, start=1):
        print(f"Progress: {iteration}/{len(operators)}.")
        stars = int(operator['stars'])
        name = operator["name"]

        driver.get(f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={name}")
        sleep(5)
        delay = 10
        try:
            print("Scraping elite resources.")
            elite = get_elite_resources(stars=stars)
            print("Elite resources ready.")

            print("Scraping skills resources.")
            skills = get_skills_resources(stars=stars)
            print("Skills ready.")

            operator_data = {
                "name": name,
                "stars": stars,
                "skills": skills,
                "elite": elite
            }
            with open(json_path + name + ".json", 'w+', encoding='utf8') as f:
                json.dump(operator_data, f)
            print("Done.")
        except TimeoutException:
            print("Loading took too much time!")
