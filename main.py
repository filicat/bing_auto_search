# 这是一个示例 Python 脚本。
import random
import time

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import string

from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import easygui
from datetime import datetime

fake = Faker('zh_CN')
STL_REWARD_FRAME = "#rewid-f > iframe"
STL_OFFER_NOT_COMPLETE = "#bingRewards > div > div.flyout_control_threeOffers > div[aria-label='Offer not Completed']"
STL_OTHER_NOT_COMPLETE = "#bingRewards > div > div.flyout_control_halfUnit > div[aria-label='Offer not Completed'] > a"
STL_POINT_TITLE = '#bingRewards > div > div.flyout_control_halfUnit > div.promo_cont > a.block > div:nth-child(2) > div.fc_dyn > div:nth-child(1) > div.fc_dyn > p.b_subtitle.promo-title'
STL_POINT_TITLE_NEW = '#bingRewards > div > div.search_earn_card > div > a > div > div.daily_search_row > span:nth-child(2)'
STL_POINT_TITLE_FINISH = '#bingRewards > div > div:nth-child(5) > div > a > div.fp_row.align-top.promo_card > div.fc_dyn > div:nth-child(1) > div > p'
is_pm = datetime.now().hour >= 12


# 定义一个自定义的等待条件，以确保输入框是可编辑的
def element_is_editable(locator):
    def _predicate(driver_p):
        try:
            element = driver_p.find_element(*locator)
            if element.is_displayed() and element.is_enabled():
                return element  # 返回WebElement对象而非布尔值
            else:
                return False
        except:
            return False
    return _predicate


def random_search_text(loop):
    match loop % 5:
        case 0:
            return fake.name()
        case 1:
            return fake.company()
        case 2:
            return fake.address()
        case 3:
            return fake.bank()
        case 4:
            return fake.job()


def offers_confirm():
    global ok_offer
    # 此时右边reward应该已经打开
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, STL_REWARD_FRAME)))
    offers = driver.find_elements(By.CSS_SELECTOR, STL_OFFER_NOT_COMPLETE)
    if len(offers) == 0:
        ok_offer = True
    elif is_pm:
        for offer in offers:
            driver.execute_script("arguments[0].scrollIntoView(true);", offer)
            driver.execute_script("arguments[0].click();", offer)
            time.sleep(1)
        ok_offer = True


def other_offers_confirm():
    global ok_other
    other_offers = driver.find_elements(By.CSS_SELECTOR, STL_OTHER_NOT_COMPLETE)
    if len(other_offers) == 0:
        ok_other = True
    else:
        for ot_offer in other_offers:
            print("ot_offer:"+ot_offer.get_attribute("href"))
            driver.execute_script("arguments[0].scrollIntoView(true);", ot_offer)
            driver.execute_script("arguments[0].click();", ot_offer)
            time.sleep(1)
        ok_other = True

def any_selector_visible(*locators):
    """ 自定义等待条件：任意一个定位器可见 """
    def _predicate(driver):
        for locator in locators:
            try:
                element = driver.find_element(*locator)
                if element.is_displayed():
                    return element
            except NoSuchElementException:
                continue
        raise TimeoutException(f"所有定位器均失败: {locators}")
    return _predicate



# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    # 添加保持登录的数据路径：安装目录一般在C:\Users\Administrator\AppData\Local\Google\Chrome\User Data
    options.add_argument(r"user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome\User Data")
    driver = webdriver.Chrome(options=options)

    search_list = set()
    ok_90: bool = False
    ok_offer: bool = False
    ok_other: bool = False
    wait = WebDriverWait(driver, 10)  # 最多等待10秒

    i = 0
    while True:
        # 切换回主文档
        driver.get('https://cn.bing.com/')
        time.sleep(2)  # 可选，等待时间可以根据实际情况调整
        driver.switch_to.default_content()

        # 使用自定义条件等待输入框变为可编辑
        search_box = wait.until(element_is_editable((By.ID, 'sb_form_q')))
        if search_box:
            # print("输入框可用")
            # 清空搜索框并输入新的搜索词
            search_term = ''
            while True:
                faker_data = random_search_text(i)
                if faker_data not in search_list:
                    search_term = faker_data
                    break
            driver.execute_script("arguments[0].value = arguments[1];", search_box, search_term)
            # 提交搜索
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", search_box)
            driver.execute_script("arguments[0].form.submit();", search_box)
            i = i + 1
            search_list.add(search_term)
        else:
            print("输入框不可用")

        time.sleep(5)
        # 等待 <div> 元素变得可点击
        reward_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'b_clickarea')))
        driver.execute_script("arguments[0].click();", reward_btn)

        # 这里执行完已经切换到内部iframe了, 无需再切换
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, STL_REWARD_FRAME)))
        point_card = wait.until(any_selector_visible(
            (By.CSS_SELECTOR, STL_POINT_TITLE_NEW),
            (By.CSS_SELECTOR, STL_POINT_TITLE_FINISH)
        ))
        print("90PointText:["+point_card.text+"]")
        if point_card.text == "你已获得 90 积分！":
            driver.switch_to.default_content()
            ok_90 = True
            print("停止90Point获取")
            break
        driver.switch_to.default_content()
        # 等待一段时间后再次搜索
        time.sleep(random.randint(30, 40))  # 这里设置为30秒，你可以根据需要调整

    offers_confirm()
    time.sleep(1)
    other_offers_confirm()

    easygui.msgbox(f"90积分: {ok_90}\n3项任务: {ok_offer}{' am' if not is_pm else '' }\n其他任务: {ok_other}", title="Bing自动积分获取")

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
