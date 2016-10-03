# Neopixels-2.0
##Synopisis
This is an improved version of the <a href="http://github.com/nickpesce/neopixels">Neopixels</a> project</br>
This python script is intended for <a href="https://www.adafruit.com/products/1138">Adafruit Neopixels</a></br>
Lights can  be controlled from the command line, web interface, or any other programs that use the RESTful API such as this <a href="http://github.com/nickpesce/NeopixelAndroidApp">Android app</a>.</br>
</hr>
##Installation
<ol>
<li>Install the <a href="https://github.com/jgarff/rpi_ws281x">rpi_ws281x</a> module
  <ol>
  <li><code>sudo apt-get update</code></li>
  <li><code>sudo apt-get install scons swig python-dev build-essentials git</code></li>
  <li><code>cd ~</code></li>
  <li><code>git clone https://github.com/jgarff/rpi_ws281x.git</code></li>
  <li><code>cd rpi_ws281x</code></li>
  <li><code>scons</code></li>
  <li><code>cd python</code></li>
  <li><code>sudo python setup.py install</code></li>
  <li><code>cd ~</code></li>
  <li><code>sudo rm -rf rpi_ws281x</code></li>
  </ol>
</li>
<li>Clone this repository to your computer<br/>
<code>git clone https://github.com/nickpesce/Neopixels-2.0.git</code><br/><code>cd Neopixels-2.0</code></li>
<li>Modify username and password in config.ini<br/><code>nano config.ini</code></li>
<li>Run web_server.py<br/><code>sudo python web_server.py</code></li>
<li>Check that the controls at <code>localhost:5000</code> work</li>
</ol>
