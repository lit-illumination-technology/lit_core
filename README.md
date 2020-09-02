# L.I.T.
***Lit Illumination Technology***
## Synopisis
Lit-core is a the foundation of the LIT ecosystem. it provides an interface that makes it very easy to control ws281x addressable leds using a raspberry pi.
## Installation
<code>sudo pip install lit-core</code>

### Startup Script
*If you are are using a config path that is not "/home/pi/.lit/litd", you must first edit the command in litd.service*
<ol>
<li>
  <code>sudo cp litd.service /etc/systemd/system</code>
</li>
<li>
  <code>sudo systemctl daemon-reload</code>
</li>
<li>
  <code>sudo systemctl start litd && sudo systemctl enable litd</code>
</li>
</ol>

## Customization
litd should be started with a --config PATH flag. The following files should all be in the PATH/config/ directory. Overriding the default configurations is optional, but making changes to ranges.json is almost definitely necessary. To copy the default configuration files, use <code>litd -g PATH</code>. For example, <code>litd -g /home/pi/.lit/litd</code>, then run it with <code>sudo litd -c /home/pi/.lit/litd</code>
<ul>
<li>ranges.json: Contains information about light groupings.
  <ul>
    <li>sections: Contiguous sections of leds.</li>
    <li>adapters: Devices that can be used to control leds.</li>
    <li>zones: Groups of sections that can all be controlled at once.</li>
    <li>default: The section or zone that should be used if none are explictly sepecified</li>
  </ul>
</li>

<li>presets.json: Named groups of effects that can be run together. Maps preset names to preset objects.
Preset objects contain:
  <ul>
  <li>start_message: Message that is returned when the preset starts</li>
  <li>commands: List of commands to run.</li>
  </ul>
</li>

<li>colors.json: Named color values that can be used by interfaces.</li>

<li>speeds.json: Named speed values that can be used by interfaces</li>
</ul>

## Adding New Effects
Easily add new and personalized effects. Basic python knowlege is required. To start, create a directory called 'effects' in your base directory (same level as the config directory). Create an empty file named '\_\_init\_\_.py' in the new directory. Finally, restart the daemon. Now any python files that are in this directory, or subdirectories of this directory, will try to be imported as effects when the daemon is started. Refer to effects/\_template.py for more information. 
