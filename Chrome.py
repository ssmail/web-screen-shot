# -*- coding: utf-8 -*-
# !/usr/bin/env python


# coding=utf-8
import glob
import os
from time import sleep
from selenium import webdriver
from ImageDiff import *


class UrlCompatibility:
    script_scroll_height = "return document.body.scrollHeight"
    script_current_height = "return document.body.scrollTop"

    driver = webdriver.Chrome()

    def __init__(self, url, max_scroll=10):
        self.max_scroll = max_scroll
        self.url = url

    def over_url(self):
        # init chromedriver
        dis_distance = []

        self.driver.get(self.url)
        self.driver.maximize_window()

        window_height = self.driver.execute_script(self.script_scroll_height)

        print self.driver.title, window_height

        for i in range(1, self.max_scroll):

            current_height = self.driver.execute_script(self.script_current_height)

            image_name = str(i) + ".png"
            last_image_name = str(i - 1) + ".png"

            self.screen_shot(image_name)

            height = self.get_image_size(image_name)

            if i > 2:
                dis_distance.append(current_height)

                image_diff = image_similarity_histogram_via_pil(image_name, last_image_name)
                if image_diff < 10:
                    self.re_last_img(image_name, dis_distance[-2] - dis_distance[-3])
                    os.remove(str(i - 1) + ".png")
                    break

            scroll_distance = height[1] * i
            scroll_script = "window.scrollTo(0, {distance});".format(distance=scroll_distance)

            self.driver.execute_script(scroll_script)
            sleep(1)
        else:
            print 'page too long'

        self.combine_images()

    def screen_shot(self, image_name):
        self.driver.save_screenshot(image_name)

    def page_has_loaded(self):
        page_state = self.driver.execute_script('return document.readyState;')
        return page_state == 'complete'

    @staticmethod
    def get_image_size(filepath):
        from PIL import Image
        im = Image.open(filepath)
        return im.size  # (width,height) tuple

    @staticmethod
    def re_last_img(fp, height):
        print "resize fp", fp, height
        from PIL import Image
        img = Image.open(fp)
        area = (0, img.size[1] - height, img.size[0], img.size[1])
        cropped_img = img.crop(area)
        cropped_img.save(fp)

    @staticmethod
    def combine_images():
        os.system("convert -append *.png webpage.png")
        l = glob.glob("*.png")
        for i in l:
            if i != "webpage.png":
                os.remove(i)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


with UrlCompatibility("https://vmspub.weidian.com/gaia/5828/f3a5fd2e.html?p=iphone&wfr=wxShare", 15) as a:
    a.over_url()
