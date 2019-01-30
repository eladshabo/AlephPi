# AlephPi
AlephPi is a game for children in the preschool stage, allowing them to learn the alphabetical letters using **RaspberryPi** and **Google Cloud Services**


# Content
* [Operation](https://github.com/eladshabo/AlephPi#operation)
* [BOM](https://github.com/eladshabo/AlephPi#bom)
* [Hardware](https://github.com/eladshabo/AlephPi#Hardware)
* [Software](https://github.com/eladshabo/AlephPi#Software)
* [Demo](https://github.com/eladshabo/AlephPi#Demo)
* [Preparation](https://github.com/eladshabo/AlephPi#Preparation)



# Operation
AlephPi workflow is described in the graph below:

![alt text](https://raw.githubusercontent.com/eladshabo/AlephPi/master/images/diagram.png)



# BOM


|Material|Link to purchase  |
|--|--|
| RaspberryPi 3 | [Amazon](https://www.amazon.com/gp/product/B01C6EQNNK/ref=ppx_yo_dt_b_asin_title_o07__o00_s00?ie=UTF8&psc=1) |
| 3.3V LEDs | [Aliexpress](https://www.aliexpress.com/item/100Pcs-lot-5-Colors-F3-3MM-Round-LED-Assortment-Kit-Ultra-Bright-Diffused-Green-Yellow-Blue/32896935877.html?spm=2114.search0104.3.52.1b1d387037EGtt&ws_ab_test=searchweb0_0,searchweb201602_1_10065_10068_319_10059_10884_317_10887_10696_100031_321_322_10084_453_10083_454_10103_433_10618_431_10307_537_536_10902,searchweb201603_45,ppcSwitch_0&algo_expid=1f1967cb-ee93-4170-9c76-82fdaf3bfcfa-7&algo_pvid=1f1967cb-ee93-4170-9c76-82fdaf3bfcfa) |
| 2N4401 Transistors | [Aliexpress](https://www.aliexpress.com/item/100pcs-2N4401-TO-92-NPN-General-Purpose-Transistor/32387641334.html?spm=a2g0s.9042311.0.0.27424c4dJI7cTk)
|36Ω  Resistors | [Aliexpress](https://www.aliexpress.com/item/20pcs-3W-Metal-film-resistor-1-1R-1M-1R-4-7R-10R-22R-33R-47R-1K/32845316445.html?spm=a2g0s.9042311.0.0.27424c4dJI7cTk)
|Push Button | [Sparkfun](https://www.sparkfun.com/products/9181)
|Seven Segment (Optional) | [Sparkfun](https://www.sparkfun.com/products/11441)
| USB Microphone | Any PnP microphone should fit
|Google Cloud Account | [Google Cloud](https://cloud.google.com/speech-to-text/)
|Wooden surface | Supermarket 🙂



# Hardware

## GPIOs
RaspberryPi has 40 GPIOs which can be used for different proposes. 

(credit to www.raspberrypi-spy.co.uk for this great image)
![enter image description here](https://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated-2700x900-1024x341.png)

**AlephPi** utilizes RPi's GPIOs in the following order:

|Porpose| GPIOs |
|--|--|
| Letters LED | [ 3 ,5, 7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36, 37 ] |
| Start Button | 38
| Recording LED | 40 |
| Lives Display (Serial) | [ 8, 10 ]

## Circuits

In order to protect RPi, each LED will be connected to RPi GPIO as described in circuit below:
![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/led_circuit.png?raw=true)




# Software


1. Download Raspbian from [here](https://www.raspberrypi.org/downloads/raspbian/) and flash it on microSD card
2. Open terminal and Install additional software:
`sudo apt-get update -y`
`sudo apt-get install -y python-pyaudio sox flac libportaudio-dev python-pip`
`pip python-pyaudio sox flac libportaudio-dev`
3. Use `raspi-config` to enable serial interface (without bash login)
`sudo raspi-config`
reboot when done.
 
 4. Test your microphone (refer to [snowboy](https://snowboy.kitt.ai/docs) in "Running on RaspberryPi" section)
 5. Download your json token from Google Cloud Services and save it somewhere on your RPi

 6. Clone `AlephPi`repository and change values in `Config.py` depending on your preferences.
 7. Run `python main.py`


# Demo
Click on the image to watch the demo in YouTube

[![Watch the video](https://img.youtube.com/vi/WuH887lcBRc/hqdefault.jpg)](https://youtu.be/WuH887lcBRc)



# Preparation
1. Soldering all the led circuit into one board and testing it with simple Python code that loops over the GPIOs. (I made GPIO-to-PIN adapter from an old IDE cable, but you can buy one [here](https://www.aliexpress.com/item/RPi-GPIO-Breakout-Expansion-Board-40pin-Flat-Ribbon-Cable-For-Raspberry-Pi-3-2-Model-B/32914708074.html?spm=a2g0s.9042311.0.0.7a5f4c4d0znMa7)) 

![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/prepare1.jpeg?raw=true)

2. Make sure everything actually works before assembling it on the wooden surface

![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/prepare2.JPG?raw=true)

3. Next, need to prepare the wooden surface and assemble all the LEDs on it.
![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/prepare3.jpeg?raw=true)

4. Now wire the LEDs thru the wooden surface
![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/prepare4.jpeg?raw=true)
 ![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/prepare5.jpeg?raw=true)

5. Assemble the RPi and circuit board on the wooden surface![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/prepare6.jpeg?raw=true)

6. Make sure we didn't break anything...
![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/prepare7.jpeg?raw=true)

7. Assemble it so some object (i picked an old chair)
![enter image description here](https://github.com/eladshabo/AlephPi/blob/master/images/prepare8.jpeg?raw=true)
