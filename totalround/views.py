import math

from pyplanet.utils.style import style_strip
from pyplanet.utils.times import format_time
from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.views.generics.list import ManualListView
from pyplanet.utils import times
from pyplanet.conf import settings

global player_index
player_index = ''

global map_attente
map_attente = ""
global player_scoreboard
player_scoreboard = {}
global first_time
global isRound
first_time = 0
isRound = False

class TotalTimeWidget(TimesWidgetView):
    widget_x = -160
    widget_y = 70.5
    size_x = 38
    size_y = 55.5
    top_entries = 5
    title = 'Total Time'

    def __init__(self, app):
        super().__init__(app.context.ui)
        self.app = app
        self.id = 'pyplanet__widgets_tacount'
        self.instance = app.instance
        self.action = self.action_recordlist
        
    async def waiting_map(self):
        map_name = self.instance.map_manager.current_map.name
        message = '{} has been set as waiting maps (not counted in total times)'.format(
            map_name
        )
        
        global map_attente
        map_attente = map_name
        return
        
    async def delete_time(self):
        global player_scoreboard
        player_scoreboard = {}
        for player in self.instance.player_manager.online:
            player_scoreboard[player.login] = [0, False,player.nickname]
        await self.instance.chat("All Times Has been set to 0")
        return
         
    async def warm_start(self):
        global isRound
        isRound = False
        return
        
    async def warm_test(self, responseid, available, active):
        global isRound
        isRound = active
        return
        
    async def get_player_nickname(self, player_login):
        player = await self.instance.player_manager.get_player(login=player_login)
        return player.nickname
        
    async def init_player(self, player_login, player_nickname, **kwargs):
        try: 
            player_scoreboard[player_login]
        except:
            if(player_scoreboard):
                datas = []
                for player in player_scoreboard:
                    datas.append((player_scoreboard[player][0], player,player_scoreboard[player][2])) 
                datas.sort()
                time = int(datas[0][0]) * 2
                player_scoreboard[player_login] = [time, False, player_nickname]  
            else:
                player_scoreboard[player_login] = [0, False, player_nickname]
        return

    async def get_player(self, player_args):
        global player_index
        player_index = player_args
        return

    async def Send_Record(self, player, race_time):
        global map_attente 
        global first_time
        global isRound
        
        if(isRound and self.instance.map_manager.current_map.name != map_attente):
            if(first_time == 0):
                first_time = race_time
            
            player_scoreboard[player][0] += race_time;
            player_scoreboard[player][1] = True;
        return
        
    async def round_end(self):
        global first_time
        global isRound
        if(isRound):
            for i in player_scoreboard:
                if( not player_scoreboard[i][1]):
                    player_scoreboard[i][0] += first_time * 2
                player_scoreboard[i][1] = False;
            first_time = 0
        isRound = False
        return
        
    async def round_start(self):
        global isRound
        await self.instance.chat(str("LIVE ROUND START !"))
        isRound = True
        return
        
    async def get_context_data(self):

        context = await super().get_context_data()
        index_range = 10
        data_length = 0
        datas_length = 0
        player_spot = 0
        toprange = 0
        global player_index		
        pindex_length = len(player_scoreboard)
        datas = []
        
        for player in player_scoreboard:
            datas.append((player_scoreboard[player][0], player, player_scoreboard[player][2]))
            
        datas.sort()
        
        try:
            pindex = [x[1] for x in datas].index(player_index)
        except:
            pindex = 0
        
        index = 1
        list_records = []
        min_index = 0
        max_index = 0
        
        if datas: #replace data with our own list
            for total, login, nickname in datas[:5]:
                list_record = dict()
                list_record['index'] = index	
                list_record['color'] = '$ff0'				
                if login == player_index:
                    list_record['color'] = '$0f3'
                list_record['nickname'] = nickname
                list_record['score'] = format_time(int(total))
                list_records.append(list_record)
                index += 1
            if pindex_length > 5:
                if pindex > 15 :
                    min_index = pindex - 5
                    max_index = pindex + 5
                    index = pindex - 4
                else:
                    min_index = 5
                    max_index = 15
                    
            for total, login, nickname in datas[min_index:max_index]:
                list_record = dict()
                list_record['index'] = index
                list_record['color'] = '$fff'
                if login == player_index:
                    list_record['color'] = '$0f3'
                list_record['nickname'] = nickname
                list_record['score'] = format_time(int(total))
                list_records.append(list_record)
                index += 1

        context.update({
                'times': list_records
        })	
        
        return context
        
    async def action_recordlist(self, player, **kwargs):
        await self.app.show_records_list(player)
        return
        
class TotalList(ManualListView):
    title = 'Total Time'
    icon_style = 'Icons128x128_1'
    icon_substyle = 'Total Time'

    fields = [
        {
            'name': '#',
            'index': 'index',
            'sorting': True,
            'searching': False,
            'width': 10,
            'type': 'label'
        },
        {
            'name': 'Player',
            'index': 'player_nickname',
            'sorting': False,
            'searching': True,
            'width': 70
        },
        {
            'name': 'Times',
            'index': 'score',
            'sorting': True,
            'searching': False,
            'width': 30,
            'type': 'label'
        },
        {
            'name': 'Difference',
            'index': 'difference',
            'sorting': True,
            'searching': False,
            'width': 50,
            'type': 'label'
        }
    ]

    def __init__(self, app, *args, **kwargs):
        super().__init__(self,*args, **kwargs)
        self.app = app
        self.manager = app.context.ui
        self.instance = app.instance
        
    async def get_player_nickname(self, player_login):
        player = await self.instance.player_manager.get_player(login=player_login)
        return player.nickname
    
    async def get_data(self): #to fix
        index = 1
        items = []
        difference = ''
        datas = []
        
        for player in player_scoreboard:
            datas.append((player_scoreboard[player][0], player,player_scoreboard[player][2]))
            
        datas.sort()
        
        for total, login, nickname in datas: # a revoir
            if total is None:
                break
                
            if index > 1:
                int_diff = total - datas[0][0]
                difference = '$f00 + ' + str(format_time(int_diff))
            items.append({
                'index': index, 'player_nickname': nickname,
                'score': format_time(int(total)),
                'difference': difference,
                'login': login,
            })
            index += 1
        return items

        