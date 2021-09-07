from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
import requests
import os
import time

media_explicit_wait_time = 30
wall_explicit_wait_time = 2
button_hold_time = 8

class music_scraper:
    def __init__(self, driver_path, out_image_folder, instrument_type = None):
        self.start_t = time.time()
        self.chrome = webdriver.Chrome(executable_path = driver_path)
        if instrument_type is not None:
            self.out_f = out_image_folder + instrument_type
            out_log = os.path.join("%s/log_%s" % (self.out_f, instrument_type))
        self.log_f = open(out_log, "w")
        self.item_counter = 1
        self.variant_counter = 0
        self.guitar_counter = 0
        self.page_counter = 0
        self.block_passes = 0
    def log_progress(self, message):
        print(message)
        self.log_f.write("%s\n" % message)
    def pass_block_wall(self):
        try:
            WebDriverWait(self.chrome, wall_explicit_wait_time).until(EC.presence_of_element_located((By.ID, "px-captcha")))
            block_button = self.chrome.find_element_by_id("px-captcha")
            self.log_progress("\n\n\nBlock button found, attemping to press it")
        except:
            try:
                self.wait_for_store_item()
                return
            except:
                self.log_progress("Store item not found, refreshing page\n")
                self.chrome.refresh()
                self.pass_block_wall()
        self.log_progress('initialize action object')
        action = AC(self.chrome)
        self.log_progress("moving cursor to block_button")
        action.move_to_element_with_offset(block_button, 50, 50)
        self.log_progress("initialize click and hold")
        action.click_and_hold()
        self.log_progress("perform click and hold")
        action.perform()
        self.log_progress("holding for a few seconds")
        time.sleep(button_hold_time)
        self.log_progress("Pressed button")
        action.release().perform()
        self.log_progress("Released button, waiting for product confirmation")
        try:
            self.wait_for_store_item()
            self.log_progress("Found store item, parsing should proceed as normal\n\n\n")
            self.block_passes += 1
            return
        except:
            self.log_progress("Store item not found, restarting")
            self.chrome.refresh()
            self.pass_block_wall()
    def wait_for_store_item(self):
        WebDriverWait(self.chrome, media_explicit_wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/store/detail/']")))
    def find_store_item(self, element):
        self.wait_for_store_item()
        return element.find_element_by_css_selector("a[href*='/store/detail/']").get_attribute("href")
    def go_to_link(self, url):
        self.chrome.get(url)
    def return_to_prev_window(self, prev_window):
        self.chrome.close()
        self.chrome.switch_to.window(prev_window)
    def save_image(self, img_link, prod_name):
        page = requests.get(img_link)
        out_file = os.path.join(self.out_f + "/pic_%s.wbep" % prod_name)
        with open(out_file, "wb") as f:
            f.write(page.content)
    def get_media_link(self):
        WebDriverWait(self.chrome, media_explicit_wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='media']")))
        return self.chrome.find_element_by_css_selector("a[href*='media']").get_attribute("href")
    def get_product_name(self):
        raw_text = self.chrome.find_element_by_class_name("product__name").text
        bad_chars = [" ", "\n", "/", "\\"]
        for char in bad_chars:
            raw_text = raw_text.replace(char, "_")
        prod_name = raw_text.replace("___", "_").replace("_-_", "_")
        self.log_progress("%d    %s" % (self.item_counter, prod_name))
        self.item_counter += 1
        return prod_name
    def get_second_image_media_link(self):
        WebDriverWait(self.chrome, media_explicit_wait_time).until(EC.presence_of_element_located((By.XPATH, '//*[@id="store-detail"]/div[1]/section[1]/div/nav/div/div[2]')))
        next_img_button = self.chrome.find_element_by_xpath('//*[@id="store-detail"]/div[1]/section[1]/div/nav/div/div[2]')
        next_img_button.click()
        self.pass_block_wall()
        return self.get_media_link()
    def go_to_product_page(self, link):
        self.chrome.execute_script("window.open('%s', 'new window')" % link)
        new_window = self.chrome.window_handles[1]
        self.chrome.switch_to.window(new_window)
        self.pass_block_wall()
        img_link = self.get_media_link()
        if "angle" in img_link:
            img_link = self.get_second_image_media_link()
        prod_name = self.get_product_name()
        self.save_image(img_link, prod_name)
        self.guitar_counter += 1
    def parse_products_on_page(self):
        elements = self.chrome.find_elements_by_class_name("product-card__name")
        for element in elements:
            link = self.find_store_item(element)
            self.go_to_product_page(link)
            self.return_to_prev_window(self.main_window)
    def scrape(self, url):
        self.go_to_link(url)
        self.main_window = self.chrome.window_handles[0]
        self.pass_block_wall()
        while True:
            WebDriverWait(self.chrome, media_explicit_wait_time).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card__name")))
            self.parse_products_on_page()
            try:
                WebDriverWait(self.chrome, media_explicit_wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "next")))
                next_button = self.chrome.find_element_by_class_name("next")
                next_button.click()
            except:
                self.log_progress("Next button not found, ending process")
                break
            self.pass_block_wall()
            self.page_counter += 1
        self.log_progress("Finished parsing\nDisplaying output information:")
        self.log_progress("    Pictures saved: %d" % self.item_counter)
        self.log_progress("    Variants found: %d" % self.variant_counter)
        self.log_progress("    Guitars found: %d" % self.guitar_counter)
        self.log_progress("    Pages passed: %d\n" % self.page_counter)
        self.log_progress("    Block walls passed: %d" % self.block_passes)
        self.log_progress("    Total time to complete scrape: %f" % (time.time() - self.start_t))
        self.log_f.close()
        self.chrome.close()