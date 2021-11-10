# pylint: disable=C0111,R0903

"""Draws a widget with configurable text content.

Parameters:
    * spacer.text: Widget contents (defaults to empty string)
"""

import core.module
import core.widget
import core.decorators
import requests

class Module(core.module.Module):
    @core.decorators.every(minutes=60)
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.text))
        self.__text = self.parameter("text", "WAITING")
        self.__streams = dict()
        self.__msg_queue = list()
        self.__request_timer = 60
        self.__msg_timer = 0
        self.__new_stream_timer = 15
        self.__stream_timer = 5
        self.__oauth = "75m708dso63uhrpvawtmhjjilys6h8"
        
    def text(self, _):
        return self.__text

    def __get_msg(self):
        
        if not len(self.__msg_queue):
            message = "NO STREAMS"
        elif "LIVE" not in self.__msg_queue[0][1] and\
             self.__msg_timer >= self.__stream_timer:
            msg = self.__msg_queue.pop(0)
            self.__msg_queue.append(msg)
            message = self.__msg_queue[0][1]
            self.__msg_timer = 0
        elif "LIVE" in self.__msg_queue[0][1] and\
             self.__msg_timer >= self.__new_stream_timer:
            msg = self.__msg_queue.pop(0)
            self.__msg_queue.append(msg)
            message = self.__msg_queue[0][1]
            self.__msg_timer = 0
        else:
            message = self.__msg_queue[0][1]
            self.__msg_timer += 5
        
        self.__text = self.parameter("text", f"{message}")
    
    def update(self):
        self.__request_timer += 5
        if self.__request_timer <= 60:
            self.__get_msg()
            return
        self.__request_timer = 0
        streams = self.__get_streams()
        for s in dict(streams).keys():
            if s not in self.__streams:
                self.__add_newstream_msg(s, **streams[s])
            else:
                self.__add_oldstream_msg(s, **streams[s])
        for s in self.__streams:
            if s not in streams:
                self.__remove_msg(s)
        self.__streams = streams
        self.__get_msg()

    def __add_newstream_msg(self, stream, game = "", viewers = ""):
        for m in self.__msg_queue:
            if m[0] == stream:
                m[1] = f"NOW LIVE | {stream} | {game}"
                return
        self.__msg_queue.append([stream, f"NOW LIVE | {stream} | {game}"])
    
    def __add_oldstream_msg(self,stream, game = "", viewers = ""):
        for m in self.__msg_queue:
            if m[0] == stream:
                m[1] = f"{stream} | {game} | {viewers}"
                return
            
    def __remove_msg(self, stream):
        self.__msg_queue = list(filter(lambda e : e[0] != stream,
                                       self.__msg_queue))
        
    def __get_streams(self):
        try:
            url = 'https://api.twitch.tv/kraken/streams/followed'
            headers = {'Accept' : 'application/vnd.twitchtv.v5+json',
                       'Authorization' : f'OAuth {self.__oauth}'}
            res = (requests.get(url, headers=headers).json())
            streams = dict()
            for i in res['streams']:
                streams[str(i['channel']['display_name'])] = {
                    'game'    : str(i['game']),
                    'viewers' : str(i['viewers'])}
            return streams
        except Exception as e:
            return { "ERROR": { 'game' : "Connection Error",
                                "viewers": ""} }

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
