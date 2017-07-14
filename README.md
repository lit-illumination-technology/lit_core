# L.I.T.
***Lit Ilumination Technology***
## Synopisis
This is an improved version of the <a href="http://github.com/nickpesce/neopixels">Neopixels</a> project</br>
This python script is intended for <a href="https://www.adafruit.com/products/1138">Adafruit Neopixels</a></br>
Lights can  be controlled from the command line, web interface, or any other programs that use the RESTful API such as this <a href="http://github.com/nickpesce/NeopixelAndroidApp">Android app</a>.</br>
## Installation
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
<li>Clone this repository to your Raspberry Pi<br/>
<code>$ git clone https://github.com/nickpesce/L.I.T..git</code><br/><code>$ cd L.I.T.</code></li>
<li><code>$ cp -r defaultconfiguration configuration</code></li>
<li>Modify username and password in config.ini<br/><code>$ nano configuration/config.ini</code></li>
<li>Run web_server.py<br/><code>$ sudo python web_server.py</code></li>
<li>Check that the controls at <code>localhost:5000</code> work</li>
</ol>

## Customization
The configuration directory contains four files that can be changed to reflect your personal setup.
<ul>
<li>config.ini:
  <ul>
  <li>
  General
    <ul>
    <li>leds: The number of leds connected to your pi</li>
    <li>pin: The pwm pin that your data line is connected to</li>
    <li>port: The port that the web server should run on</li>
    <li>username: The username to log into the website</li>
    <li>password: The password to log into the website</li>
    </ul>
   </li>
   <li>
   API: Optional
      <ul>
      <li>apiai: Api.Ai client access token</li>
      </ul>
   </li>
   <li>
   Link: If link effect is installed (it is by default)
     <ul>
     <li>port: The port that the effect listens on</li>
     <li>username: The username for link</li>
     <li>password: The password for link</li>
     </ul>
   </li>
   </ul>
</li>

<li>ranges.json: Contains information about light groupings.
  <ul>
  <li>sections: Contiguous sections of leds defined by a name mapped to a start and end index.</li>
  <li>zones: Groups of sections that can all be controlled at once. Defined by a name mapped to a list of sections.</li>
  <li>default: The section or zone that should be used if none are explictly chosen.
  </ul>
</li>

<li>colors.json: A list of all preset color values defined by an object containing a name and color. The color field is defined as an array contining a red, green, and blue value.
</li>

<li>speeds.json: Preset speed values. An object containing a mapping between names and speeds. 0 is the slowest possible, and 50 is the default.
</li>
</ul>

## Updating
<ol>
<li>cd into the L.I.T. directory</li>
<li><code>git pull</code></li>
<li>If defaultconfiguration/changes.txt changed, your configuration files must be updated
  <ol>
  <li>less defaultconfiguration/changes.txt</li>
  <li>Read the most recent changes</li>
  <li>update the relevant files in you configuration directory</li>
  </ol>
</li>
</ol>

## Api.Ai Integration
<a href="https://api.ai/Api.Ai">Api.Ai</a> is a free and easy artificial intelligence API. It can easily be integrated into L.I.T. to enable natural language commands!
<ol>
<li>Run generate.py and get the files from the api-ai directory<br/>
<code>$ sudo python generate.py</code></li>
<li>Install apiai and it's dependencies<br/>
<code>$ apt-get install python-pyaudio python-numpy</code><br/>
<code>$ pip install apiai</code></li>
<li>Make an account at <a href="https://console.api.ai/api-client/#/signup">Api.Ai</a> and watch the tutorials</li>
<li>Create a new agent</li>
<li>Go to Entities and click on the menu icon next to "Create Entity"</li>
<li>Click "Upload Entity"</li>
<li>Upload each of the json files from the api-ai directory (Ad-Blockers may have to be turned off)</li>
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

### Custom Api.Ai Fulfillment
Define custom actions for your api.ai agent. Allows you to override all of the Smalltalk responses.
<ol>
<li>In the L.I.T. directory, create a new file called fulfillment.py</li>
<li>Create a 'process' function <br><code>def process(json)</code></li>
<li>The json parameter contains the Api.Ai request (If the action was not lights)</li>
<li>In the process function, either return the response text, or <code>None</code> if the action should not be handled</li>
</ol>

## Adding New Effects
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
<li>If you want to share your creation, feel free to create a pull request!</li>
<li>That's it!</li>
</ol>
