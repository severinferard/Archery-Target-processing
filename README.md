# Archery-Target-processing
Image processing of an archery target using a Raspberry Pi, HTML5-CSS-Javascript and Python for server side.
The app uses computer computer vision to identify the point of impact of each arrow, which is send onto a web server allowing the archer to see the point of impact of is arrows in real time.

![](388c0t.gif)

## Hardware
The project uses:
- a Raspberry Pi B with a camera module
- a HC-SR04 ultrasonic distance sensor
- several diodes and resistances
- a computer
- (a tripod)

## Operation of the app
The Raspberry Pi has 3 roles: it take and sends the pictures through a socket pipe to the main computer which host the server, it process the distance sensor data and trigger the calibration process through the socket pipe if necessary, and it operate some LEDs to show the user what is going on.

The computer recieve the images and callibration orders via the RPI. It then uses a Python script to process each images. The informations found are send to a web server which allow the user to see the information on a local website. 

### Raspberry Pi
When boot up, the RPi start the script. If the socket server is running on the computer, it will connect to it and start sending data. if it's not, the RPi will try to connect continuously.
When connected to the server, if the distance sensor detects a distance inferior to a certain threshold, (meaning the archer is at the target to take out his arrows), the RPi will start a loop. While there is movement near the sensor, the loop waits. Then if there is no movement in for 10 seconds, the RPi sends a callibration order to the computer, which will operate the designated function.

