# encoding: utf-8
from pathlib import Path

from selenium.webdriver import Chrome
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import csv
from selenium.webdriver.chrome.service import Service

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


if __name__ == "__main__":
    user_operators_path = '../files/user_operators.csv'
    json_path = '../arknights/resources/operator'

    with open(user_operators_path, mode="r", encoding="utf-8") as f:
        operators = [dict(operator) for operator in csv.DictReader(f, delimiter=';')]
        f.close()

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    with Chrome(service=Service("chromedriver95.exe"), options=options) as driver:
        for iteration, operator in enumerate(operators[202:], start=1):
            print(f"Progress: {iteration}/{len(operators)}.")
            name = 'Роса' if operator["name"].strip().lower() == 'rosa' else operator["name"]
            print(f"Scraping operator {name}")
            stars = int(operator['stars'])

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

                name = 'Rosa' if name.strip().lower() == 'pоса' else name
                operator_data = {
                    "name": name,
                    "stars": stars,
                    "skills": skills,
                    "elite": elite
                }

                op_path = f'{json_path}/{stars}stars/{name}.json'
                Path(op_path).parent.mkdir(parents=True, exist_ok=True)
                with open(op_path, 'w+', encoding='utf-8') as f:
                    json.dump(operator_data, f, indent=4)
                print("Done.")
                print("============================\n")
            except TimeoutException:
                print("Loading took too much time!")
