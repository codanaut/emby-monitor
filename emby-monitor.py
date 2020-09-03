#!/usr/bin/python3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
from PyQt5 import QtWebEngineWidgets
from embyui import Ui_MainWindow
import requests
import json
import datetime
import configparser
import sys
if sys.platform.startswith( 'linux' ) :
    from OpenGL import GL

# Get Emby URL & Key
try:
    config = configparser.ConfigParser()
    config.read('settings.ini')
    url = config['Connection']['url']
    key = config['Connection']['apiKey']
except:
    print("No settings.ini found")
    

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        #old stuff examples
        #self.pushButton.clicked.connect(self.on_click)
        #self.label_server_name.setText("This is a test")

        # On first load
        on_load(self)
        QTimer.singleShot(1,self.nowPlaying)
        self.groupBox_about.setAutoFillBackground(True)

        timer = QTimer(self)
        timer.setInterval(60000)
        timer.timeout.connect(self.nowPlaying)
        timer.timeout.connect(self.updateStats)
        timer.start()
        
        

    @pyqtSlot()
    def on_click(self):
        textboxValue = self.lineEdit.text()
        response = requests.request("GET", textboxValue)
        data = response.json()
        self.textBrowser.setText(str(data))

    def updateStats(self):
        on_load(self)
    
    @pyqtSlot()
    def nowPlaying(self):
        try:
            getDevicecount = requests.request("GET", "%s/emby/Sessions?api_key=%s" % (url,key),timeout=3)
            activeCount = getDevicecount.json()
            streamCount = 0
            for device in activeCount:
                try:
                    vType = device['NowPlayingItem']['Type']
                    streamCount += 1
                    
                except KeyError:
                    pass
            
            # Set Now Playing Count
            self.label_NowPlaying.setText(f'Now Playing: {streamCount}')

            # delete everythig in scroll area and rebuild section on refresh
            self.scrollAreaWidgetContents_2.deleteLater()
            self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
            self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 764, 306))
            self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
            self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
            self.verticalLayout.setObjectName("verticalLayout")
            self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
            self.gridLayout_2.addWidget(self.scrollArea, 4, 0, 1, 1)

            # check each active device and print out info if playing media, skip if not playing anything
            for user in activeCount:
                try:
                    client = user['UserName']
                    
                    vType = user['NowPlayingItem']['Type']

                    # check if playing or paused
                    if user['PlayState']['IsPaused'] == True:
                        playState = "Paused"
                    
                    elif user['PlayState']['IsPaused'] == False:
                        playState = "Playing"

                    # get play position
                    runtimeTicks = user['NowPlayingItem']['RunTimeTicks']
                    currentPosistionTicks = user['PlayState']['PositionTicks']

                    # convert runtime ticks
                    runTimeSeconds = runtimeTicks / 10000000 / 60
                    runTime = str(datetime.timedelta(seconds=runTimeSeconds)).split('.', 2)[0].split(':',3)
                    runTime = runTime[1]+ ":" +runTime[2]
                    
                    # convert current posistion ticks
                    currentTimeSeconds = currentPosistionTicks / 10000000 / 60
                    currentTime = str(datetime.timedelta(seconds=currentTimeSeconds)).split('.', 2)[0].split(':',3)
                    currentTime = currentTime[1] + ":" + currentTime[2]
                    
                    
                    # If Movie
                    if vType == "Movie":
                        movie = user['NowPlayingItem']['Name']
                        streamMethod = user['PlayState']['PlayMethod']

                        # Create nowplaying groupbox
                        self.groupBox_nowplaying = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_2)
                        self.groupBox_nowplaying.setObjectName("groupBox_nowplaying")
                        self.gridLayout_NowPlaying = QtWidgets.QGridLayout(self.groupBox_nowplaying)
                        self.gridLayout_NowPlaying.setObjectName("gridLayout_NowPlaying")

                        # Set Label for Current User
                        self.label_User = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_User.setObjectName("label_User")
                        self.gridLayout_NowPlaying.addWidget(self.label_User, 0, 0, 1, 1)
                        self.label_User.setText(f'User: {client}')

                        # Set Label for Playing Media
                        self.label_Media_Name = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_Media_Name.setObjectName("label_Media_Name")
                        self.gridLayout_NowPlaying.addWidget(self.label_Media_Name, 1, 0, 1, 1)
                        self.label_Media_Name.setText(f'Movie: {movie}')

                        # Set Label for Play Status
                        self.label_Play_Status = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_Play_Status.setObjectName("label_Play_Status")
                        self.gridLayout_NowPlaying.addWidget(self.label_Play_Status, 2, 0, 1, 1)
                        self.label_Play_Status.setText(f'Status: {playState} {currentTime}/{runTime}')

                        # Set Label for Play Method
                        self.label_Play_Method = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_Play_Method.setObjectName("label_Play_Method")
                        self.gridLayout_NowPlaying.addWidget(self.label_Play_Method, 3, 0, 1, 1)
                        self.label_Play_Method.setText(f'Stream Method: {streamMethod}')

                        #self.label_Test = QtWidgets.QLabel(self.groupBox_nowplaying)
                        #self.label_Test.setObjectName("label_Test")
                        #self.gridLayout_NowPlaying.addWidget(self.label_Test, 0, 1, 3, 2)
                        #self.label_Test.setText(f'Fucking Fuck')

                        # Set movie Banner
                        parrentID = user['NowPlayingItem']['Id']
                        logoThumb = f'{url}/emby/items/{parrentID}/Images/Thumb?api_key={key}'
                        logoBanner = f'{url}/emby/items/{parrentID}/Images/Banner?api_key={key}'
                        try:
                            response = requests.get(logoBanner,timeout=3)

                            if response.status_code == 200:
                                #print(response.status_code)
                                logoURL = logoBanner
                            else:
                                #print(response.status_code)
                                logoURL = logoThumb
                        except:
                            pass
                        

                        self.webEngineView = QtWebEngineWidgets.QWebEngineView(self.groupBox_nowplaying)
                        self.webEngineView.setGeometry(QtCore.QRect(50, 50, 50, 50))
                        self.webEngineView.setUrl(QtCore.QUrl(logoURL))
                        self.webEngineView.setObjectName("webEngineView")
                        self.gridLayout_NowPlaying.addWidget(self.webEngineView, 0, 2, 4, 2)

                        # add group to layout
                        self.verticalLayout.addWidget(self.groupBox_nowplaying)
                        
                    # If Tv Show
                    elif vType == "Episode":
                        show = user['NowPlayingItem']['SeriesName']
                        episode = user['NowPlayingItem']['Name']
                        seasonNumber = str(user['NowPlayingItem']['ParentIndexNumber'])
                        episodeNumber = str(user['NowPlayingItem']['IndexNumber'])
                        streamMethod = user['PlayState']['PlayMethod']
                        
                        #print(logoURL)

                        # Create nowplaying group
                        self.groupBox_nowplaying = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_2)
                        self.groupBox_nowplaying.setObjectName("groupBox_nowplaying")
                        self.gridLayout_NowPlaying = QtWidgets.QGridLayout(self.groupBox_nowplaying)
                        self.gridLayout_NowPlaying.setObjectName("gridLayout_NowPlaying")

                        # Set Label for Current User
                        self.label_User = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_User.setObjectName("label_User")
                        self.gridLayout_NowPlaying.addWidget(self.label_User, 0, 0, 1, 1)
                        self.label_User.setText(f'User: {client}')
                        
                        # Set Label for Playing Media
                        self.label_Media_Name = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_Media_Name.setObjectName("label_Media_Name")
                        self.gridLayout_NowPlaying.addWidget(self.label_Media_Name, 1, 0, 1, 1)
                        self.label_Media_Name.setText(f'Show: {show}')

                        # Set Label for Episode Name
                        self.label_Episode_Name = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_Episode_Name.setObjectName("label_Episode_Name")
                        self.gridLayout_NowPlaying.addWidget(self.label_Episode_Name, 2,0,1,1)
                        self.label_Episode_Name.setText(f'Episode: {episode}')

                        # Set Label for Season and Episode Number
                        self.label_Season_Episode = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_Season_Episode.setObjectName("label_Season_Episode")
                        self.gridLayout_NowPlaying.addWidget(self.label_Season_Episode, 3,0,1,1)
                        self.label_Season_Episode.setText(f'Season: {seasonNumber} Episode: {episodeNumber}')

                        # Set Label for Play Status
                        self.label_Play_Status = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_Play_Status.setObjectName("label_Play_Status")
                        self.gridLayout_NowPlaying.addWidget(self.label_Play_Status, 4, 0, 1, 1)
                        self.label_Play_Status.setText(f'Status: {playState} {currentTime}/{runTime}')

                        # Set Label for Play Method
                        self.label_Play_Method = QtWidgets.QLabel(self.groupBox_nowplaying)
                        self.label_Play_Method.setObjectName("label_Play_Method")
                        self.gridLayout_NowPlaying.addWidget(self.label_Play_Method, 5, 0, 1, 1)
                        self.label_Play_Method.setText(f'Stream Method: {streamMethod}')

                        # Set TV Banner
                        parrentID = user['NowPlayingItem']['ParentLogoItemId']
                        #logoURL = f'{url}/emby/items/{parrentID}/Images/Banner?api_key={key}'
                        if streamCount == 1:
                            logoURL = f'{url}/emby/items/{parrentID}/Images/Thumb?api_key={key}'
                        else:
                            logoURL = f'{url}/emby/items/{parrentID}/Images/Banner?api_key={key}'
                        self.webEngineView = QtWebEngineWidgets.QWebEngineView(self.groupBox_nowplaying)
                        self.webEngineView.setGeometry(QtCore.QRect(50, 50, 50, 50))
                        self.webEngineView.setUrl(QtCore.QUrl(logoURL))
                        self.webEngineView.setObjectName("webEngineView")
                        self.gridLayout_NowPlaying.addWidget(self.webEngineView, 0, 2, 6, 2)

                        self.verticalLayout.addWidget(self.groupBox_nowplaying)
                        
                        

                # if error or not tv show or movie then pass and keep going
                except KeyError:
                    pass
        except:
            pass


# custom functions that arnt connected slots    
def on_load(self):
    try:
        sysInfo = systemInfo()
        embyVersion = sysInfo['Version']
        self.label_server_name.setText(sysInfo['ServerName'])
        self.label_version.setText(f'Version: {embyVersion}')

        # Users and Acitve devices
        users = allUsers()
        totalUsers = len(users)
        toatDevices = deviceCount()
        self.label_users.setText(f'Users: {totalUsers}')
        self.label_active_devices.setText(f'Active Devices: {toatDevices}')

        # Get media count
        totalMedia = mediaCount()
        totalMovies = str(totalMedia['MovieCount'])
        totalShows = str(totalMedia['SeriesCount'])
        self.label_total_tv.setText(f'Tv Shows: {totalShows}')
        self.label_total_movies.setText(f'Movies: {totalMovies}')

        ###
        # Users Tab
        ###
        self.users_tab_label.setText(f'Users: {totalUsers}')

        self.scrollAreaWidgetContents_users.deleteLater()
        self.scrollAreaWidgetContents_users = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_users.setGeometry(QtCore.QRect(0, 0, 764, 456))
        self.scrollAreaWidgetContents_users.setObjectName("scrollAreaWidgetContents_users")
        self.verticalLayout_UsersScroll = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_users)
        self.verticalLayout_UsersScroll.setObjectName("verticalLayout_UsersScroll")
        self.scrollArea_Users.setWidget(self.scrollAreaWidgetContents_users)
        self.verticalLayout_UserTab.addWidget(self.scrollArea_Users)

        for user in users:
            #print(user)
            userName = user['Name']
            hasPasswordSet = user['HasConfiguredPassword']

            # Last Activity Date
            lastActivity = user.get('LastActivityDate')
            try:
                lastActivityDate = lastActivity[:-14]
                formatLastActivityDate = datetime.datetime.strptime(lastActivityDate,"%Y-%m-%dT%H:%M:%S")
                newFormat = "%m-%d-%Y"
                useLastActivityDate = formatLastActivityDate.strftime(newFormat)
            except:
                useLastActivityDate = "No Activity Yet"
            

            

            # Create Users groupbox
            self.groupBox_UsersTab = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_users)
            self.groupBox_UsersTab.setObjectName("groupBox_UsersTab")
            self.gridLayout_Users = QtWidgets.QGridLayout(self.groupBox_UsersTab)
            self.gridLayout_Users.setObjectName("gridLayout_Users")

            # Set Label for each User
            self.label_User = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_User.setObjectName("label_User")
            self.gridLayout_Users.addWidget(self.label_User, 0, 0, 1, 2)
            self.label_User.setAlignment(QtCore.Qt.AlignCenter)
            self.label_User.setText(f'{userName}')
            font = QtGui.QFont()
            font.setPointSize(20)
            self.label_User.setFont(font)

            # Set Label for last activity
            self.label_Last_Activity = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_Last_Activity.setObjectName("label_Last_Activity")
            self.gridLayout_Users.addWidget(self.label_Last_Activity, 1, 0, 1, 2)
            self.label_Last_Activity.setAlignment(QtCore.Qt.AlignCenter)
            self.label_Last_Activity.setText(f'Last Activity: {useLastActivityDate}')

            # Set Label for Config section
            self.label_userConfig = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_userConfig.setObjectName("label_userConfig")
            self.gridLayout_Users.addWidget(self.label_userConfig, 3, 1, 1, 1)
            self.label_userConfig.setAlignment(QtCore.Qt.AlignCenter)
            self.label_userConfig.setText(f'Configuration')
            font = QtGui.QFont()
            font.setPointSize(13)
            self.label_userConfig.setFont(font)

            # Set Label for Has Password
            self.label_HasPassword = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_HasPassword.setObjectName("label_HasPassword")
            self.gridLayout_Users.addWidget(self.label_HasPassword, 4, 1, 1, 1)
            self.label_HasPassword.setAlignment(QtCore.Qt.AlignCenter)
            self.label_HasPassword.setText(f'Pasword Set: {hasPasswordSet}')

            # Set Label for PlayDefaultAudioTrack
            playDefaultAudioTrack = user['Configuration']['PlayDefaultAudioTrack']
            self.label_PlayDefaultAudioTrack = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_PlayDefaultAudioTrack.setObjectName("label_PlayDefaultAudioTrack")
            self.gridLayout_Users.addWidget(self.label_PlayDefaultAudioTrack, 5, 1, 1, 1)
            self.label_PlayDefaultAudioTrack.setAlignment(QtCore.Qt.AlignCenter)
            self.label_PlayDefaultAudioTrack.setText(f'Play Default Audio Track: {playDefaultAudioTrack}')

            # Set Label for AudioLanguagePreference
            try:
                audioLanguagePreference = user['Configuration']['AudioLanguagePreference']
            except:
                audioLanguagePreference = "Not Set"
            self.label_AudioLanguagePreference = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_AudioLanguagePreference.setObjectName("label_AudioLanguagePreference")
            self.gridLayout_Users.addWidget(self.label_AudioLanguagePreference, 6, 1, 1, 1)
            self.label_AudioLanguagePreference.setAlignment(QtCore.Qt.AlignCenter)
            self.label_AudioLanguagePreference.setText(f'Audio Language Preference: {audioLanguagePreference}')

            #######################
            
            # Set Label for Policy
            self.label_Policy = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_Policy.setObjectName("label_Policy")
            self.gridLayout_Users.addWidget(self.label_Policy, 3, 0, 1, 1)
            self.label_Policy.setAlignment(QtCore.Qt.AlignCenter)
            self.label_Policy.setText(f'Policy')
            font = QtGui.QFont()
            font.setPointSize(13)
            self.label_Policy.setFont(font)

            # Set Label for isAdministrator
            isAdministrator = user['Policy']['IsAdministrator']
            self.label_IsAdministrator = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_IsAdministrator.setObjectName("label_IsAdministrator")
            self.gridLayout_Users.addWidget(self.label_IsAdministrator, 4, 0, 1, 1)
            self.label_IsAdministrator.setAlignment(QtCore.Qt.AlignCenter)
            self.label_IsAdministrator.setText(f'Administrator: {isAdministrator}')

            # Set Label for IsDisabled
            isDisabled = user['Policy']['IsDisabled']
            self.label_IsDisabled = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_IsDisabled.setObjectName("label_IsDisabled")
            self.gridLayout_Users.addWidget(self.label_IsDisabled, 5, 0, 1, 1)
            self.label_IsDisabled.setAlignment(QtCore.Qt.AlignCenter)
            self.label_IsDisabled.setText(f'Disabled: {isDisabled}')

            # Set Label for SimultaneousStreamLimit
            SimultaneousStreamLimit = user['Policy']['SimultaneousStreamLimit']
            if SimultaneousStreamLimit == 0:
                StreamLimit = "Unlimited"
            else:
                StreamLimit = SimultaneousStreamLimit
            self.label_SimultaneousStreamLimit = QtWidgets.QLabel(self.groupBox_UsersTab)
            self.label_SimultaneousStreamLimit.setObjectName("label_SimultaneousStreamLimit")
            self.gridLayout_Users.addWidget(self.label_SimultaneousStreamLimit, 6, 0, 1, 1)
            self.label_SimultaneousStreamLimit.setAlignment(QtCore.Qt.AlignCenter)
            self.label_SimultaneousStreamLimit.setText(f'Simultaneous Stream Limit: {StreamLimit}')

            self.verticalLayout_UsersScroll.addWidget(self.groupBox_UsersTab)


        ###
        # Devices Tab
        ###

        devices = allDevices()
        totalDevices = devices['TotalRecordCount']
        deviceList = devices['Items']

        self.devices_tab_label.setText(f'Total Devices: {totalDevices}')

        self.scrollAreaWidgetContents_Devices.deleteLater()
        self.scrollAreaWidgetContents_Devices = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_Devices.setGeometry(QtCore.QRect(0, 0, 764, 456))
        self.scrollAreaWidgetContents_Devices.setObjectName("scrollAreaWidgetContents_Devices")
        self.verticalLayout_Devices = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_Devices)
        self.verticalLayout_Devices.setObjectName("verticalLayout_Devices")
        self.scrollArea_Devices.setWidget(self.scrollAreaWidgetContents_Devices)
        self.verticalLayout_DeviceTab.addWidget(self.scrollArea_Devices)

        for device in deviceList:
            
            deviceName = device['Name']
            lastUser = device['LastUserName']
            appName = device['AppName']

            lastUsed = device['DateLastActivity']
            strippedLastUsed = lastUsed.strip('.0000000Z')
            fixDeviceDate = datetime.datetime.strptime(strippedLastUsed,"%Y-%m-%dT%H:%M:%S")
            newFormat = "%m-%d-%Y"
            lastUsedDate = fixDeviceDate.strftime(newFormat)



            # Create device groupbox
            self.groupBox_DeviceTab = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_users)
            self.groupBox_DeviceTab.setObjectName("groupBox_DeviceTab")
            self.gridLayout_Users = QtWidgets.QGridLayout(self.groupBox_DeviceTab)
            self.gridLayout_Users.setObjectName("gridLayout_Users")

            # Set Label for Device Name
            self.label_DeviceName = QtWidgets.QLabel(self.groupBox_DeviceTab)
            self.label_DeviceName.setObjectName("label_DeviceName")
            self.gridLayout_Users.addWidget(self.label_DeviceName, 0, 0, 1, 1)
            self.label_DeviceName.setAlignment(QtCore.Qt.AlignCenter)
            self.label_DeviceName.setText(f'Device Name: {deviceName}')

            # Set Label for Device Last User
            self.label_DeviceLastUser = QtWidgets.QLabel(self.groupBox_DeviceTab)
            self.label_DeviceLastUser.setObjectName("label_DeviceLastUser")
            self.gridLayout_Users.addWidget(self.label_DeviceLastUser, 0, 1, 1, 1)
            self.label_DeviceLastUser.setAlignment(QtCore.Qt.AlignCenter)
            self.label_DeviceLastUser.setText(f'Last User: {lastUser}')

            # Set Label for Device App Name
            self.label_DeviceAppName = QtWidgets.QLabel(self.groupBox_DeviceTab)
            self.label_DeviceAppName.setObjectName("label_DeviceAppName")
            self.gridLayout_Users.addWidget(self.label_DeviceAppName, 1, 0, 1, 1)
            self.label_DeviceAppName.setAlignment(QtCore.Qt.AlignCenter)
            self.label_DeviceAppName.setText(f'App Name: {appName}')

            # Set Label for Device Last Used
            self.label_DeviceLastUsed = QtWidgets.QLabel(self.groupBox_DeviceTab)
            self.label_DeviceLastUsed.setObjectName("label_DeviceLastUsed")
            self.gridLayout_Users.addWidget(self.label_DeviceLastUsed, 1, 1, 1, 1)
            self.label_DeviceLastUsed.setAlignment(QtCore.Qt.AlignCenter)
            self.label_DeviceLastUsed.setText(f'Last Used: {lastUsedDate}')

            self.verticalLayout_Devices.addWidget(self.groupBox_DeviceTab)


        ####
        # System INFO TAB
        ####
        # Servername
        self.groupBox_SystemInfo.setTitle(sysInfo['ServerName'])
        # Version and update
        self.label_ServerVersion.setText(f'{embyVersion}')
        self.label_HasUpdate.setText(f"Update Available: {sysInfo['HasUpdateAvailable']}")
        self.label_PendinRestart.setText(f"Pending Restart: {sysInfo['HasPendingRestart']}")
        # Connection info
        self.label_Wan.setText(f"Wan Address: {sysInfo['WanAddress']}")
        self.label_Lan.setText(f"Lan Address: {sysInfo['LocalAddress']}")
        # Server Info Section
        self.label_OperatingSystem.setText(f"Operating System: {sysInfo['OperatingSystem']}")
        self.label_ProgramDataPath.setText(f"Program Path: {sysInfo['ProgramDataPath']}")
        self.label_LogPath.setText(f"Log Path: {sysInfo['LogPath']}")
        self.label_CachePath.setText(f"Cache Path: {sysInfo['CachePath']}")
    except KeyError as ex:
        self.label_server_name.setText(f'Unable To Connect')
        self.label_version.setText(f'Please Check Settings')
        print(ex)
    

    



#
# Custom non self functions
#
# Get mediacount to use later
def mediaCount():
    response = requests.request("GET", "%s/emby/Items/Counts?api_key=%s" % (url,key), timeout=3)
    mediaCount = response.json()
    return (mediaCount)

# Get user count
def allUsers():
    try:
        usersresponse = requests.request("GET", "%s/emby/Users?api_key=%s" % (url,key), timeout=3)
        users = usersresponse.json()
        return users
    except:
        print("it broke in allUsers")
        pass

def deviceCount():
    try:
        getDevicecount = requests.request("GET", "%s/emby/Sessions?api_key=%s" % (url,key), timeout=3)
        activeCount = getDevicecount.json()
        devicecount = len(activeCount)
        return devicecount
    except:
        print("it broke in deviceCount")
        pass

def allDevices():
    try:
        deviceresponse = requests.request("GET", "%s/emby/Devices?api_key=%s" % (url,key), timeout=3)
        devices = deviceresponse.json()
        return devices
    except:
        print("it broke in allDevice")
        pass


def systemInfo():
    try:
        getSystemInfo = requests.request("GET", "%s/emby/System/Info?api_key=%s" % (url,key), timeout=3)
        systemInfo = getSystemInfo.json()
        return systemInfo
    except:
        print("it broke in systemInfo")
        pass
        



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    # 'Breeze', 'Oxygen', 'QtCurve', 'Windows', 'Fusion'
    app.setStyle('Fusion')
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())