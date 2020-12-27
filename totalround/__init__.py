from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command
from .views import TotalTimeWidget, TotalList
import random
class TacConfig(AppConfig):
    #name = 'apps.totalround'
    game_dependencies = ['trackmania']
    app_dependencies = ['core.maniaplanet']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = TotalTimeWidget(self)


    async def on_start(self):
        await self.instance.command_manager.register(
            Command(command='tops', target=self.show_records_list),
        )
        await self.instance.command_manager.register(
            Command(command='reset_time', target=self.reset_times, admin=True),
            )
            
        
        self.context.signals.listen(mp_signals.map.map_end , self.map_start)
        self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
        self.context.signals.listen(tm_signals.finish, self.player_finish)
        self.context.signals.listen(mp_signals.flow.round_end, self.round_end)
        self.context.signals.listen(mp_signals.flow.round_start, self.round_start)
        self.context.signals.listen(tm_signals.warmup_start, self.widget.warm_start)
        self.context.signals.listen(tm_signals.warmup_status, self.widget.warm_test)
        
        
        for player in self.instance.player_manager.online:
                await self.widget.init_player(player.login, player.nickname)
                await self.widget.get_player(str(player)) 
                await self.widget.display(player=player)
        return
                  
    async def map_start(self, map, **kwargs):
        for player in self.instance.player_manager.online:
            await self.widget.get_player(str(player))
            await self.widget.display(player=player)

    async def waiting_map(self,player,data,**kwargs):
        await self.widget.waiting_map()
        return

    async def reset_times(self,player,data,**kwargs):
        await self.widget.delete_time()
        for player in self.instance.player_manager.online:
            await self.widget.get_player(str(player))
            await self.widget.display(player=player)
        return
        
    async def player_connect(self, player, is_spectator, source, signal):
        await self.widget.get_player(str(player))
        await self.widget.init_player(player.login, player.nickname)
        for current_player in self.instance.player_manager.online:
            await self.widget.get_player(str(current_player))
            await self.widget.display(player=current_player)
        return
            
    async def show_records_list(self, player, data = None, **kwargs):

        
        await TotalList(self).display(player=player.login)
        return

        
    async def get_differences(abc, player, data = None, **kwargs):

        await  DifferenceList(self, data['login']).display(player=player.login)
        return 
        
    async def player_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
        
        await self.widget.Send_Record(player.login, race_time)
        return
        
    async def round_end(self, count, time):
        await  TotalTimeWidget.round_end(self)
        for current_player in self.instance.player_manager.online:
            await self.widget.get_player(str(current_player))
            await self.widget.display(player=current_player)
        
    async def round_start(self, count, time):
        await TotalTimeWidget.round_start(self)
        for current_player in self.instance.player_manager.online:
            await self.widget.get_player(str(current_player))
            await self.widget.display(player=current_player)
        return