
import time

import pygame
from pygame.locals import *

from ErrorsHandler import *

import Database

#---------------------------------------------------------------------------------
class Event:
    """this is a superclass for any events that might be generated by an
        object and sent to the EventManager"""
    def __init__(self):
        self.name = "Generic Event"

#---------------------------------------------------------------------------------
class TickEvent(Event):
    def __init__(self):
        self.name = "CPU Tick Event"
        time.sleep(0.01)

#---------------------------------------------------------------------------------
class QuitEvent(Event):
    def __init__(self):
        self.name = "Program Quit Event"
        sys.exit(0)

#---------------------------------------------------------------------------------
class MapBuiltEvent(Event):
	def __init__(self, map):
		self.name = "Map Finished Building Event"
		self.map = map

#---------------------------------------------------------------------------------
class GameStartedEvent(Event):
    def __init__(self, game):
        self.name = "Game Started Event"
        self.game = game

#---------------------------------------------------------------------------------
class CharactorMoveRequest(Event):
    def __init__(self, action):
        self.name = "Charactor Move Request"
        self.action = action

#---------------------------------------------------------------------------------
class CharactorPlaceEvent(Event):
    """this event occurs when a Charactor is *placed* in a sector, 
        ie it doesn't move there from an adjacent sector."""
    def __init__(self, charactor):
        self.name = "Charactor Placement Event"
        self.charactor = charactor

#---------------------------------------------------------------------------------
class CharactorMoveEvent(Event):
    def __init__(self, charactor):
        self.name = "Charactor Move Event"
        self.charactor = charactor

#---------------------------------------------------------------------------------
class CharactorFormEnd(Event):
    def __init__(self, charactor):
        self.name = "Charactor Form End"
        self.charactor = charactor

#---------------------------------------------------------------------------------
class KeyboardController:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener( 'kbd', self )

    def Notify(self, event):
        if isinstance( event, TickEvent ):
            sprites = self.evManager.listeners

            #Handle Input Events
            for event in pygame.event.get():
                ##logger.info( str(event) )

                action = None
                current = self.evManager.GetFocused()
                ev = None

                if event.type == QUIT:
                    ev = QuitEvent()

                if event.type == 123:
                    sprites[current].sprite.goDown()
                    sprites[current].sprite.stopMoving()
                    try: sprites[current].sprite.BrowseForward()
                    except Exception, e:
                        if str(e) == "PLAY TRACK":
                            action = 'PLAY'

                if event.type == KEYDOWN or event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                    if sprites['burner'].sprite.Finished:
                        logger.info("Finished burning.. we quit now!")
                        ev = QuitEvent()
                        #sys.exit(0)

                    #######################################################################
                    # joypad events
                    #######################################################################
                    if event.type == pygame.JOYAXISMOTION:
                        sprite = self.evManager.listeners[self.evManager.current].sprite
                        if event.axis == 0:
                            if event.value < 0: sprite.BrowseBack()
                            if event.value > 0:
                                try: sprite.BrowseForward()
                                except Exception, e:
                                    if str(e) == "PLAY TRACK": action = 'PLAY'
                        if event.axis == 1:
                            if event.value < 0: sprite.goUp()
                            if event.value > 0: sprite.goDown()
                            if event.value == 0: sprite.stopMoving()
                    elif event.type == pygame.JOYBUTTONDOWN:
                        logger.info( "Joy: %i Button: %i DOWN" % (event.joy,event.button) )

                        from JoyConf import joyMap, joyType

                        action = self.getAction(event.button, joyMap, joyType, sprites)

                    #######################################################################
                    # keyboard events
                    #######################################################################
                    elif event.type == KEYDOWN:
                        #logger.info("GOT KEYPRESS: %s" % event.key)


                        #--------------------------------------------------------------------
                        if sprites['login'].sprite.visible:
                            login = sprites['login'].sprite
                            if event.key == K_ESCAPE:
                                login.SetUnVisible()
                                sprites['musicbrowser'].sprite.SetVisible()
                            if not login.finished:
                                login.key = event.key
                            else:
                                user = login.fields[0].result
                                password = login.fields[1].result
                                logger.debug( "LOGIN user: " + user )
                                logger.debug( "LOGIN password: " + password )

                                # DB auth
                                if Database.Auth(user, password):
                                    sprites['musicbrowser'].sprite.SetType('path')
                                    sprites['musicbrowser'].sprite.SetVisible()
                                    sprites['playlist'].sprite.SetType('fs_playlist')
                                    self.evManager.SetFocus('musicbrowser')
                                    self.evManager.SetUnFocus('login')
                                    login.SetUnVisible()

                                    login.user = user
                                else:
                                    # TODO allow user to retry login
                                    login.FormError("Incorrect user or password")
                                    login.Restart()
                                    print login.finished

                        #--------------------------------------------------------------------
                        elif sprites['register'].sprite.visible:
                            register = sprites['register'].sprite
                            if event.key == K_ESCAPE:
                                register.SetUnVisible()
                                sprites['musicbrowser'].sprite.SetVisible()
                            if not register.finished:
                                register.key = event.key
                            else:
                                user     = register.fields[0].result
                                email    = register.fields[1].result
                                password = register.fields[2].result
                                logger.debug( "REGISTER user: " + user )
                                logger.debug( "REGISTER email: " + email )
                                logger.debug( "REGISTER password: " + password )

                                # DB auth
                                if Database.Register(user, email, password):
                                    sprites['musicbrowser'].sprite.SetType('path')
                                    sprites['musicbrowser'].sprite.SetVisible()
                                    sprites['playlist'].sprite.SetType('fs_playlist')
                                    sprites['login'].sprite.user = user
                                    self.evManager.SetFocus('musicbrowser')
                                    self.evManager.SetUnFocus('register')
                                    register.SetUnVisible()
                                else:
                                    # user already exists
                                    register.FormError("User registration failed!")

                        #--------------------------------------------------------------------
                        elif sprites['publish'].sprite.visible:
                            publish = sprites['publish'].sprite
                            # Get at least the LABEL and LICENSE to publish
                            if event.key == K_ESCAPE:
                                publish.SetUnVisible()
                                sprites['musicbrowser'].sprite.SetVisible()
                            if not publish.finished:
                                publish.key = event.key
                            else:
                                label     = publish.fields[0].result
                                logger.debug( "PUBLISH into LABEL: " + label )

                                sprites['playlist'].sprite.Publish(sprites['login'].sprite.user, label)
                                self.evManager.SetFocus('musicbrowser')
                                sprites['musicbrowser'].sprite.SetType('path')
                                sprites['musicbrowser'].sprite.SetVisible()
                                sprites['playlist'].sprite.SetType('fs_playlist')
                                publish.Restart()
                                self.evManager.SetUnFocus('publish')
                                publish.SetUnVisible()

                        #--------------------------------------------------------------------
                        elif event.key == K_ESCAPE: # ESC = quit
                           ev = QuitEvent()
                        elif event.key == 108: # l = login
                           action = 'LOGIN'
                        elif event.key == 114: # r = register
                           action = 'REGISTER'
                        elif event.key == 112: # p = publish
                           # make sure the user is logged in before allowing to publish
                           if sprites['login'].sprite.user is not None:
                               action = 'PUBLISH'
                        elif event.key == 116: # t = switch MusicBrowser type
                            sprites['musicbrowser'].sprite.SetType('path')
                            sprites['playlist'].sprite.SetType('fs_playlist')
                        elif event.key == 9: # TAB = switch between playlist and music browser
                            if current == 'musicbrowser':
                                self.evManager.SetUnFocus('musicbrowser')
                                self.evManager.SetFocus('playlist')
                            elif current == 'playlist':
                               self.evManager.SetUnFocus('playlist')
                               self.evManager.SetFocus('musicbrowser')
                        elif event.key == 57: # 0 = volume down
                           action = 'VOL_DOWN'
                        elif event.key == 48: # 9 = volume up
                           action = 'VOL_UP'
                        elif event.key == 98: # b = burn
                           action = 'BURN'
                        elif event.key == 49: # 1 = burn audio
                            if sprites['burner'].sprite.visible:
                                logger.info("Starting to burn AUDIO CD")
                                action = 'BURN_AUDIO'
                        elif event.key == 50: # 2 = burn data
                            if sprites['burner'].sprite.visible:
                                logger.info("Starting to burn DATA CD")
                                action = 'BURN_DATA'
                        elif event.key == 51: # 3 = copy to USB
                            if sprites['burner'].sprite.visible:
                                logger.info("Starting to burn DATA to USB")
                                action = 'BURN_USB'
                        elif event.key == 120: # x = stop playback
                            action = 'STOP'
                        elif event.key == 99: # c = playback seek forward
                            action = 'SEEK_FWD'
   
                        elif current == 'musicbrowser' or current == 'playlist':
                            if event.key == 118: # add to playlist
                                sprites[current].sprite.AddToRemoveFromPlaylist(sprites['playlist'].sprite.playlistID)
                                sprites['playlist'].sprite.Refresh()
                            else:
                                try: sprites[current].sprite.action[event.key]()
                                except Exception, e:
                                    if str(e) == "PLAY TRACK": action = 'PLAY'
    
                if event.type == KEYUP or event.type == pygame.JOYBUTTONUP:
                    try: sprites['musicbrowser'].sprite.stopMoving()
                    except Exception, e: logger.error("ActionsManager EXCEPTION: %s" % str(e))
                    try: sprites['musicplayer'].sprite.stopMoving()
                    except Exception, e: logger.error("ActionsManager EXCEPTION: %s" % str(e))

                #######################################################################
                # Actions to take upon
                #######################################################################
                if action is not None:
                    #logger.debug( "ACTION: %s" % str(action) )
                    #if action == 'PLAY'    : sprites['musicplayer'].sprite.Play("file://" + sprites[current].sprite.list[sprites[current].sprite.selected]['location'])
                    if action == 'VOL_DOWN': sprites['musicplayer'].sprite.VolumeDown()
                    if action == 'VOL_UP'  : sprites['musicplayer'].sprite.VolumeUp()
                    if action == 'STOP'    : sprites['musicplayer'].sprite.Stop()
                    if action == 'SEEK_FWD': sprites['musicplayer'].sprite.Seek('fwd')
                    if action == 'PLAYLIST_ADD':
                        sprites[current].sprite.AddToRemoveFromPlaylist(sprites['playlist'].sprite.playlistID)
                        sprites['playlist'].sprite.Refresh()
                    if action == 'BROWSER_SWITCH':
                        if current == 'musicbrowser':
                            self.evManager.SetUnFocus('musicbrowser')
                            self.evManager.SetFocus('playlist')
                        elif current == 'playlist':
                            self.evManager.SetUnFocus('playlist')
                            self.evManager.SetFocus('musicbrowser')
                    if action == 'BURN':
                        sprites['burner'].sprite.ToggleVisible()
                        sprites['musicplayer'].sprite.ToggleBurnControls()
                    if action == 'BURN_AUDIO':
                        tracks = ""
                        list = sprites['playlist'].sprite.browser.list
                        for i in range(len(list)):
                            tracks += list[i]['location']+":"
                        sprites['burner'].sprite.BurnCD(tracks, action)
                    if action == 'BURN_DATA':
                        tracks = ""
                        list = sprites['playlist'].sprite.browser.list
                        for i in range(len(list)):
                            tracks += list[i]['location']+":"
                        sprites['burner'].sprite.BurnCD(tracks, action)
                    if action == 'BURN_USB':
                        tracks = ""
                        list = sprites['playlist'].sprite.browser.list
                        for i in range(len(list)):
                            tracks += list[i]['location']+":"
                        sprites['burner'].sprite.BurnCD(tracks, action)
                    if action == 'LOGIN':
                        sprites['login'].sprite.ToggleVisible()
                        sprites['musicbrowser'].sprite.SetUnVisible()
                    if action == 'REGISTER':
                        sprites['register'].sprite.ToggleVisible()
                        sprites['musicbrowser'].sprite.SetUnVisible()
                    if action == 'PUBLISH':
                        sprites['publish'].sprite.ToggleVisible()
                        sprites['musicbrowser'].sprite.SetUnVisible()

                if action is not None: ev = CharactorMoveRequest(action)
                if ev: self.evManager.Post( ev )

    def getAction(self, button, joyMap, joyType, sprites):
    
        action = None
    
        #---------------------------
        if joyType == 'DragonRise':
            # Pinnacle e-design joypad
    
            if button == joyMap[joyType]['PLAYLIST_ADD']:
                if sprites['burner'].sprite.visible: action = 'BURN_DATA'
                else: action = 'PLAYLIST_ADD'
            if button == joyMap[joyType]['BURN_AUDIO']:
                if sprites['burner'].sprite.visible: action = 'BURN_AUDIO'
            if button == joyMap[joyType]['SEEK_FWD']:
                if sprites['burner'].sprite.visible: action = 'BURN_USB'
                else: action = 'SEEK_FWD'
            if button == joyMap[joyType]['BURN']:
                action = 'BURN'
            if button == joyMap[joyType]['BROWSER_SWITCH']:
                action = 'BROWSER_SWITCH'
            if button == joyMap[joyType]['VOL_UP']:
                action = 'VOL_UP'
            if button == joyMap[joyType]['VOL_DOWN']:
                action = 'VOL_DOWN'
            if button == joyMap[joyType]['STOP']: # click left hat = stop
                if sprites['burner'].sprite.visible: action = 'BURN_AUDIO'
                else: action = 'STOP'
            if button == joyMap[joyType]['BROWSE_FORWARD']: 
                sprite = self.evManager.listeners[self.evManager.current].sprite
                try:
                    sprite.BrowseForward()
                except Exception, e:
                    if str(e) == "PLAY TRACK": action = 'PLAY'
        #---------------------------
        elif joyType == 'precision':
            # Logitech precision joypad
    
            if button == joyMap[joyType]['STOP']:
                action = 'STOP'
            if button == joyMap[joyType]['PLAYLIST_ADD']:
                action = 'PLAYLIST_ADD'
            if button == joyMap[joyType]['SEEK_FWD']:
                action = 'SEEK_FWD'
            if button == joyMap[joyType]['BURN']:
                action = 'BURN'
            if button == joyMap[joyType]['BROWSER_SWITCH']:
                action = 'BROWSER_SWITCH'
            if button == joyMap[joyType]['BROWSER_SWITCH2']:
                action = 'BROWSER_SWITCH'
            if button == joyMap[joyType]['VOL_UP']:
                action = 'VOL_UP'
            if button == joyMap[joyType]['VOL_DOWN']:
                action = 'VOL_DOWN'
            if button == joyMap[joyType]['BURN_AUDIO']:
                if sprites['burner'].sprite.visible: action = 'BURN_AUDIO'
            if button == joyMap[joyType]['BURN_DATA']:
                if sprites['burner'].sprite.visible: action = 'BURN_DATA'
    
        return action
