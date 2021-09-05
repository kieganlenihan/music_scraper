## Music Scraper
Here is a class implementation of a web scraper which parses through sweetwater.com and downloads images of musical instruments. These images are useful for training machine learning models for things like image generation via Generative Adversarial Networks (GANs). The code is stable and can pass by sweetwater human verification captcha test automatically. One instance of the code successfully downloaded 3,049 electric guitar images over the course of of 2 hours.
  
This code was written and executed in Python 3.6, with the following packages:
Selenium
Requests
os
time
  
To run music scraper, simply initialize the class object with the path to your browser driver (I use chrome and have not tested other drivers), for the variable driver_path. Then select the url which you want to scrape. This should be a page with lists of products, such as https://www.sweetwater.com/c590--Solidbody_Guitars. For selenium to run a browser instance of chrome, the url must contain https://www. Pass the folder you would like to save the images and the output log to the variable out_image_folder, just make sure that the out_image_folder string ends with a "/". Finally, if you would like to break your output image folder into several subfolders, this can be done automatically with the instrument_type variable. Just make sure that the folder for the output path already exists before running.


