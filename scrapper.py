# encoding: utf-8
from selenium.webdriver import Chrome
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import json


def get_stars(element):
    soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
    return len(soup.findAll(class_='fa fa-star', recursive=True))


def get_materials(soup):
    items = map(lambda x: x.contents[0], soup.findAll(class_="item-name", recursive=True))
    quantity = map(lambda x: int(x.contents[0].replace("x", "").replace(".", "")),
                   soup.findAll(class_="item-amount", recursive=True))
    return dict(zip(items, quantity))


def get_elite_resources():
    def parse(element):
        soup = BeautifulSoup(element.get_attribute("innerHTML"), 'html.parser')
        return get_materials(soup)

    element = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="elite1Stats"]/div[2]/div[2]')))
    elite1_resources = parse(element)

    element = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="elite2Stats"]/div[2]/div[2]')))
    elite2_resources = parse(element)

    return {"elite": [{"level": 1, "resources": elite1_resources}, {"level": 2, "resources": elite2_resources}]}


def get_upgrade_json(iteration, materials):
    resources = []
    for name, quantity in materials.items():
        resources.append({"name": name, "quantity": quantity})
    return {"level": iteration, "resources": resources}


def get_skills_resources():
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
    sleep(4)
    element = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="op-rarity"]')))
    stars = get_stars(element)

    # Get Upgrades
    element = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="skill0StatsCollapsible"]')))
    upgrade = parse_upgrade(element)

    # Get Mastery1
    element = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="skill0StatsCollapsible"]')))
    mastery.append(parse_mastery(element, 1))

    # Get Mastery2
    element = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="skill1StatsCollapsible"]')))
    mastery.append(parse_mastery(element, 2))

    # Get Mastery3
    if stars == 6:
        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="skill2StatsCollapsible"]')))
        mastery.append(parse_mastery(element, 3))

    return {**upgrade, "mastery": mastery}


with Chrome(executable_path='./chromedriver94.exe') as driver:
    driver.get("https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname=Ptilopsis")
    delay = 10
    try:
        print("Scraping elite resources.")
        elite = get_elite_resources()
        print("Elite resources ready.")

        print("Scraping skills resources.")
        skills = get_skills_resources()
        print("Skills ready.")

        print(elite, skills)
        print("Done.")
    except TimeoutException:
        print("Loading took too much time!")
    sleep(20)

#
# html = """
# <tbody><tr>
# <td colspan="4">
# <div class="ak-btn-non btn-sm ak-shadow-small ak-btn ak-btn-bg btn-char spType-1" data-original-title="" data-placement="top" data-toggle="tooltip" id="" style="text-align:left;min-width:80px;" title="">
# <a class="ak-subtitle2" style="font-size:11px;margin-left:-9px;margin-bottom:-15px">SP Charge Type</a>Per second</div>
# <div class="ak-btn-non btn-sm ak-shadow-small ak-btn ak-btn-bg btn-char" data-original-title="" data-placement="top" data-toggle="tooltip" id="" style="text-align:left;min-width:80px;" title="">
# <a class="ak-subtitle2" style="font-size:11px;margin-left:-9px;margin-bottom:-15px">Skill Activation</a>Manual Trigger</div>
# <div class="ak-btn-non btn-sm ak-shadow-small ak-btn ak-btn-bg btn-char" data-original-title="" data-placement="top" data-toggle="tooltip" id="" style="text-align:left;min-width:80px;" title="">
# <a class="ak-subtitle2" style="font-size:11px;margin-left:-9px;margin-bottom:-15px">Duration</a>30 Seconds</div>
# </td>
# </tr>
# <tr style="height:10px"></tr>
# <tr>
# <td class="skilldesc" colspan="2">ATK <span class="" style="color:#0098DC">+<div class="stat-important">45%</div></span></td>
# </tr>
# <tr style="height:10px"></tr>
# <tr>
# <td>
# <div class="ak-btn-non btn-sm ak-shadow-small ak-btn ak-btn-bg btn-char" data-original-title="" data-placement="top" data-toggle="tooltip" id="" style="text-align:left;min-width:80px;" title="">
# <a class="ak-subtitle2" style="font-size:11px;margin-left:-9px;margin-bottom:-15px">SP Cost</a>40</div>
# <div class="ak-btn-non btn-sm ak-shadow-small ak-btn ak-btn-bg btn-char" data-original-title="" data-placement="top" data-toggle="tooltip" id="" style="text-align:left;min-width:80px;" title="">
# <a class="ak-subtitle2" style="font-size:11px;margin-left:-9px;margin-bottom:-15px">Initial SP</a>20</div>
# </td>
# </tr>
# <tr><td colspan="4"><button class="btn btn-sm btn-block ak-btn" id="skilldetailtitle" onclick='SlideToggler("skilldetailcontent")' style="color:#fff;text-align:center;background:#222;padding:2px">Skill Details <i class="fas fa-caret-down"></i></button>
# <div class="ak-shadow skilldetailcontent" id="skilldetailcontent" style="display:none;margin-bottom:8px;padding-top:10px;padding:2px;background:#666">
# <div style="background:#444;margin:4px;padding:2px;padding-top:8px;background:#444;border-radius:2px;color: #999999">
# <div style="padding-top:0px;display:inline-block">
# <div class="" data-original-title="" data-placement="top" data-toggle="tooltip" id="" style="color:#222;font-size:13px;background:#999;display:inline-block;padding:2px;border-radius:2px;" title="">
# <a class="ak-subtitle" style="color:#999;background:#222;display:inline-block;border-radius:0px;padding:0px 3px;margin-left:-4px;margin-top:-12px"> atk </a> Attack</div>
# </div>  0.45
#                             </div>
# </div>
# </td></tr>
# <tr>
# <td colspan="4">
# <div style="text-align:center;background:#222">Rank Up Requirements</div>
# <div style="margin-top:15px">
# <div class="ak-btn-non btn-sm ak-shadow-small ak-btn ak-btn-bg btn-char" data-original-title="" data-placement="top" data-toggle="tooltip" id="" style="text-align:left;min-width:80px;" title="">
# <a class="ak-subtitle2" style="font-size:11px;margin-left:-9px;margin-bottom:-15px">Level Required</a>Level 1</div>
# </div>
# <div class="akmat-container" style="position:relative">
# <div class="item-name" title="技巧概要·卷1">Skill Summary - 1</div>
# <div class="item-image">
# <img id="item-image" src="img/items/MTL_SKILL1.png"/>
# </div>
# <img class="item-rarity" src="img/material/bg/item-2.png"/>
# <div class="item-amount">4x</div>
# </div> </td>
# </tr>
# </tbody>
# """
#
# soup = BeautifulSoup(html, 'html.parser')
# print(soup)
# items = soup.findAll(class_="item-name", recursive=True)
# print(items)
# # items = map(lambda x: x.contents[0], )
# # quantity = map(lambda x: int(x.contents[0].replace("x", "").replace(".", "")),
# #                soup.findAll(class_="item-amount", recursive=True))
# # skills_resources = dict(zip(items, quantity))
