# coding=utf-8
# Волшебный комментарий, что работаем с кодировкой utf-8
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def testing():
    # Создание объекта драйвера
    pytest.driver = webdriver.Chrome('chromedriver.exe')
    # Переходим на страницу авторизации
    pytest.driver.get('http://petfriends1.herokuapp.com/login')

    yield

    pytest.driver.quit()


def test_my_pets():
    x_fail = 0
    # Вводим email
    pytest.driver.find_element_by_id('email').send_keys('vasya@mail.com')
    # Вводим пароль
    pytest.driver.find_element_by_id('pass').send_keys('12345')
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element_by_css_selector('button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert pytest.driver.find_element_by_tag_name('h1').text == "PetFriends"
    # Неявное ожидание
    pytest.driver.implicitly_wait(2)
    # Переход на страницу питомцев пользователя
    pytest.driver.get('http://petfriends1.herokuapp.com/my_pets')
    # Получение кол-ва питомцев пользователя с явным ожиданием элемента
    pet_count = WebDriverWait(pytest.driver, 2).until(EC.presence_of_element_located((By.XPATH, '//div[@class '
                                                                                                '=".col-sm-4 left"]')))
    pet_count = int(pet_count.text.split()[2])
    # Получаем данные о изображениях питомцев
    images = pytest.driver.find_elements_by_xpath('//tr/th/img')
    # Получаем данные об имени, виде и возрасте всех питомцев. Значения в виде текста складываем в список
    pet_names_list = pytest.driver.find_elements_by_xpath('//tbody/tr/td[not(contains(@class, "smart_cell"))][1]')
    pet_names = [i.text for i in pet_names_list]
    pet_type_list = pytest.driver.find_elements_by_xpath('//tbody/tr/td[not(contains(@class, "smart_cell"))][2]')
    pet_type = [i.text for i in pet_type_list]
    pet_age_list = pytest.driver.find_elements_by_xpath('//tbody/tr/td[not(contains(@class, "smart_cell"))][3]')
    pet_age = [i.text for i in pet_age_list]
    # Тесты, что данные питомцев соответствут требованиями. Поскольку нужно проверить все данные, то проверки
    # выполняются в блоках try except с подсчетом числа падений тестов
    try:
        assert len(pet_names) == pet_count
    except Exception:
        print("[FAIL] Кол-во питомцев на странице не равно числу питомцев пользователя! ")
        x_fail += 1
    try:
        assert sum(1 for i in images if images[i].get_attribute('src') != '') >= pet_count // 2
    except Exception:
        print("[FAIL] Меньше чем у половины питомцев есть изображение!")
        x_fail += 1
    try:
        assert sum(1 for i in range(len(pet_names)) if pet_names[i] == '' or pet_type[i] == '' or pet_age[i] == '') == 0
    except Exception:
        print("[FAIL] Есть питомцы с пустым именем или породой или возрастом!")
        x_fail += 1
    try:
        assert sum(1 for i in pet_names if pet_names.count(i) > 1) == 0
    except Exception:
        print("[FAIL] Есть питомцы с повторяющимися именами")
        x_fail += 1
    # Для подсчета числа одинаковых питомцев создаем список из кортежей и считаем количество одинаковых элементов
    pets = [(pet_names[i], pet_type[i], pet_age[i]) for i in range(len(pet_names))]
    try:
        assert sum(1 for i in pets if pets.count(i) > 1) == 0
    except Exception:
        print("[FAIL] Есть одинаковые питомцы")
        x_fail += 1
    # Если тесты падали, то выводим общее число падений и поднимаем исключение
    if x_fail > 0:
        print(f'Тесты упали, раз: {x_fail}')
        raise Exception


# Вызов теста питомцев
def main():
    test_my_pets()


# Проверка, что код не импортирован
if __name__ == '__main__':
    main()
