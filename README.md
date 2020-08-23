# emby-monitor
## A Basic Monitor For Emby

This is a continuation of [emby-cli-monitor](https://github.com/codanaut/emby-cli-monitor).

I find it handy having a way to check playback statuses or basic info quickly without having to log into the dashboard.


![alt text](https://i.imgur.com/S9UhBVA.png)
 
[full album here](https://imgur.com/a/UZ4haSq)

This project is still very much a beta and has very little testing outside of one environment. 

## Usage
Edit the url and key with your info. You can get an emby api key by going to your *Dashboard>API Keys* and then you can generate a key. 


Install the requirements\
`pip3 install –upgrade -r requirements.txt`

Open [settings.ini](settings.ini) and enter your server ip or url and api key like so\
[Connection]\
url = http://0.0.0.0:8096\
apiKey = yourReallyLongrandomKey

Run the program\
`python3 emby-monitor.py`



Planned Future Features
- library tab
- user statistics
- replace settings.ini with gui settings tab

##### Disclaimer
###### I have no relation to Emby, i just use it and wanted my own monitor. 
###### I’m still learning python so this will probably be refined and tweaked a lot, but I have been running it for a few months now without issue as is. 