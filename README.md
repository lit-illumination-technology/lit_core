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
  <li><code>$ sudo apt-get update</code></li>
  <li><code>$ sudo apt-get install scons swig python-dev build-essential git</code></li>
  <li><code>$ cd ~</code></li>
  <li><code>$ git clone https://github.com/jgarff/rpi_ws281x.git</code></li>
  <li><code>$ cd rpi_ws281x</code></li>
  <li><code>$ scons</code></li>
  <li><code>$ cd python</code></li>
  <li><code>$ sudo python setup.py install</code></li>
  <li><code>$ cd ~</code></li>
  <li><code>$ sudo rm -rf rpi_ws281x</code></li>
  </ol>
</li>
<li>Clone this repository to your computer<br/>
<code>$git clone https://github.com/nickpesce/Neopixels-2.0.git</code><br/><code>$ cd Neopixels-2.0</code></li>
<li>Modify username and password in config.ini<br/><code>$ nano config.ini</code></li>
<li>Run web_server.py<br/><code>$ sudo python web_server.py</code></li>
<li>Check that the controls at <code>localhost:5000</code> work</li>
</ol>

</hr>
##Api.Ai Integration
<a href="https://api.ai/Api.Ai">Api.Ai</a> is a free and easy artificial intelligence API. It can easily be integrated into Neopixels to enable natural language commands!
<ol>
<li>Run generate.py and get the files from the api-ai directory<br/>
<code>$sudo python generate.py</code></li>
<li>Install apiai and it's dependencies<br/>
<code>$ apt-get install python-pyaudio python-numpy</code><br/>
<code>$ pip install apiai</code></li>
<li>Make an account at <a href="https://console.api.ai/api-client/#/signup">Api.Ai</a> and watch the tutorials</li>
<li>Create a new agent</li>
<li>Go to Entities and click on the benu icon next to "Create Entity"</li>
<li>Click "Upload Entity"</li>
<li>Upload each of the json files from the api-ai directory</li>
<li>Go to Fulfillment
  <ol>
  <li>Enable webhook.</li>
  <li>For URL, enter your server hostname followed by <code>/ai_action</code></li>
  <li>Under "Basic Auth", enter your username and password as defined in the config.ini</li>
  </ol>
</li>
<li>Click the gear next to the agent selector</li>
<li>Take note of the "Client access token"</li>
<li>Back on the raspberry pi, <code>$ nano config.ini</code>.
  <ol>
  <li>Add a new section <code>[Api]</code></li>
  <li>Add a new entry <code>apiai: YOUR_CLIENT_ACCESS_TOKEN</code>.
  </ol>
<li>Create whatever intents you want</li>
<li>For each intent you create, be sure to check "enable webhook" at the bottom</li>
<li>Restart the server and there should be a new text entry at the top of the website</li>
</ol>

</hr>
##Adding new effects
Easily add new and personalized effects. Basic python knowlege is required.
<ol>
<li>Navigate to the <code>effects</code> directory</li>
<li>Make a copy of the template<br/>
<code>$ cp template.py YOUR_EFFECT_NAME.py</code></li>
<li>Edit the new effect<br/>
<code>$ nano YOUR_EFFECT_NAME.py</code></li>
<li>Change each field according to the comments</li>
<li>Code your effect in the <code>start</code> function</li>
<li>Restart the server</li>
<li>That's it!</li>
</ol>
