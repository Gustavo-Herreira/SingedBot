import aiohttp
from datetime import datetime
from discord.ext import commands

from textwrap import dedent
import config

# Constantes:
api_key = config.riot_api_key
if api_key is None:
    raise Exception("RIOT_API_KEY NÃO FOI ENCONTRADO NAS VARIAVEIS DE SISTEMA")


# Returns summoner's info
async def get_summoner(in_game_name):
    async with aiohttp.ClientSession() as client:
        response = await client.get(
            f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{in_game_name}?api_key={api_key}")

        data = await response.json()

        if "status" in data:
            status_json = {
                'status_code': data['status']['status_code'],
                'message': data['status']['message']
            }
            await client.close()
            return status_json


        else:
            player_json = {
                'name': data['name'],
                'account_level': data['summonerLevel'],
                'summonerid': data['id'],
                'summonerpuuid': data['puuid'],
                'profileIconId': data['profileIconId']
            }
            await client.close()
    return player_json


# Returns all champion's info
async def get_champions():
    async with aiohttp.ClientSession() as client:
        response = await client.get("http://ddragon.leagueoflegends.com/cdn/10.8.1/data/en_US/champion.json")

        content = await response.json()
        champions_data = content['data']

        champions = []
        for champion in champions_data:
            champions.append(
                {
                    'id': champions_data[champion]['id'],
                    'name': champions_data[champion]['name'],
                    'key': champions_data[champion]['key'],
                    'info': champions_data[champion]['info'],
                    'tags': champions_data[champion]['tags']
                }
            )
        await client.close()
    return champions


# Returns all info about champions of a specific summoner
async def get_mastery(encrypted_summoner_id):
    async with aiohttp.ClientSession() as client:
        response = await client.get(
            f"https://br1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}?api_key={api_key}")

        all_champions_mastery = await response.json()

        _champions_masterys = []
        for champion in all_champions_mastery:
            _champions_masterys.append(
                {
                    'championId': champion['championId'],
                    'masteryLevel': champion['championLevel'],
                    'masteryPoints': champion['championPoints'],
                    'chestGranted': champion['chestGranted'],
                    'lastPlayTime': champion['lastPlayTime'],
                    'tokensEarned': champion['tokensEarned']
                }
            )
        await client.close()
    return _champions_masterys


# Returns all info about a specific champion of a specific summoner
async def get_mastery_by_champion_name(encrypted_summoner_id, champion_id):
    async with aiohttp.ClientSession() as client:
        response = await client.get(
            f"https://br1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}/by-champion/{champion_id}?api_key={api_key}")

        champion_mastery = await response.json()

        champions_mastery = {
            'championId': champion_mastery['championId'],
            'championLevel': champion_mastery['championLevel'],
            'championPoints': champion_mastery['championPoints'],
            'chestGranted': champion_mastery['chestGranted'],
            'lastPlayTime': datetime.utcfromtimestamp(champion_mastery['lastPlayTime'] / 1000).strftime('%d/%m/%Y %H:%M:%S'),
            'championPointsSinceLastLevel': champion_mastery['championPointsSinceLastLevel'],
            'championPointsUntilNextLevel': champion_mastery['championPointsUntilNextLevel'],
            'tokensEarned': champion_mastery['tokensEarned']
        }

        await client.close()
    return champions_mastery


# Returns summoner's characters and their respective mastery (ordered in order of mastery points)
def my_mastery_champions(champions, masteries):
    new_champion_mastery = []

    for summoner_mastery in masteries:
        for champion in champions:
            if str(summoner_mastery['championId']) == str(champion['key']):
                new_champion_mastery.append(
                    {
                        'nome': champion['name'],
                        'id': champion['id'],
                        'key': champion['key'],
                        'info': {'attack': champion['info']['attack'], 'defense': champion['info']['defense'],
                                 'magic': champion['info']['magic'], 'difficulty': champion['info']['difficulty']},
                        'tags': champion['tags'],
                        'mastery_points': summoner_mastery['masteryPoints'],
                        'mastery_level': summoner_mastery['masteryLevel'],
                        'chestGranted': summoner_mastery['chestGranted'],
                        'tokensEarned': summoner_mastery['tokensEarned'],
                        'lastPlayTime': datetime.utcfromtimestamp(summoner_mastery['lastPlayTime'] / 1000).strftime('%d/%m/%Y %H:%M:%S')
                    }
                )
                # a = {
                #     'info': {'difficulty': champion['info']['difficulty']},
                # }
    return new_champion_mastery


# Returns summoner's statistics
async def get_entries(encrypted_summoner_id):
    async with aiohttp.ClientSession() as client:
        response = await client.get(
            f"https://br1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}?api_key={api_key}")

    entries_response = await response.json()

    entries = []

    for entry in entries_response:
        entries.append({
            'entry_type': entry['queueType'],
            'tier': entry['tier'],
            'rank': entry['rank'],
            'lp': entry['leaguePoints'],
            'wins': entry['wins'],
            'losses': entry['losses'],
            'veteran': entry['veteran'],
            'inactive': entry['inactive'],
            'freshBlood': entry['freshBlood'],
            'hotStreak': entry['freshBlood']
        })

    return entries


class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='perfil', aliases=['main', 'mains'])
    async def _mains(self, ctx, *nick):
        """Retorna os campeões com maior maestria
        :parameter
        ------------
        Nick: Nome in-game do usuário que deseja ver as maestrias [obrigatório]
        """

        self.player_name = ''.join(nick).replace(" ", "_")

        summoner_response = await get_summoner(self.player_name)

        # if everything is fine:
        if "status_code" not in summoner_response:
            all_champions = await get_champions()
            my_masteries = await get_mastery(summoner_response['summonerid'])

            my_champions_masteries = my_mastery_champions(all_champions, my_masteries)

            # OUTPUT:
            mensagem = f'''```ini\n{summoner_response['name']} [lv. {summoner_response['account_level']}]:\n'''

            # ELO / ENTRIES:
            entries = await get_entries(summoner_response['summonerid'])
            for entry in entries:
                if entry['entry_type'] == "RANKED_SOLO_5x5":
                    ranked_type = "RANQUEADA SOLO/DUO"
                elif entry['entry_type'] == "RANKED_FLEX_SR":
                    ranked_type = "RANQUEADA FLEXÍVEL"
                else:
                    ranked_type = entry['entry_type']
                tier = entry['tier']
                rank = entry['rank']
                pontos = entry['lp']
                wins = entry['wins']
                losses = entry['losses']
                hot_streak = entry['hotStreak']

                mensagem += f'''
{ranked_type}: [{tier} {rank}] | Pontos: [{pontos}] | WinRate: [{(wins / (wins + losses)) * 100:.2f}%] | Wins/Loses: [W: {wins} / L: {losses}] | WinStreak: [{hot_streak}]
                            '''

            # MAESTRIAS:
            max_num_champions = 5 if len(my_champions_masteries) >= 5 else len(my_champions_masteries) - 1
            champions = 0

            for i in my_champions_masteries:
                if champions <= max_num_champions:
                    mensagem += f'\n' + \
                                f'\nCampeão: [{i["nome"]}]' + \
                                f'\nPontos Maestria: [{i["mastery_points"]}]' + \
                                f'\nNivel Maestria: [{i["mastery_level"]}]' + \
                                f'\nEmblemas de maestria: [{i["tokensEarned"]}]' + \
                                f'\nUltima partida em: [{i["lastPlayTime"]}]'


                    # Tags Campeão: [{i['tags'][0]}, {i['tags'][1]}]
                    # Stats Campeão: [Ataque: {i['info']['attack']}, Defesa: {i['info']['defense']}, Magia: {i['info']['magic']}, Dificuldade: {i['info']['difficulty']}]

                    champions += 1
            mensagem += f"\n```"

            print(mensagem)
            await ctx.channel.send(mensagem)

        # if error:
        else:
            if "summoner not found" in summoner_response['message']:
                output_message_error = \
                    f'''
                    - Algo deu errado 😭
                    - Nick de invocador não encontrado!'''
                output_message_formatacao = \
                    f'''
                    [Formatação da função]
                    {config.bot_prefixes[0]}perfil [nick]
                    [Exemplo]
                    {config.bot_prefixes[0]}perfil Tico Makonha'''

                await ctx.channel.send(f"```diff\n{dedent(output_message_error)}``````ini{dedent(output_message_formatacao)}```")

            else:
                print(f"status code: {summoner_response['status_code']}, message: {summoner_response['message']}")

            await ctx.channel.send(
                f'''```ini\nTente usar [{config.bot_prefixes[0]}help perfil]```''')


class Mastery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="maestria", aliases=['maestrias'])
    async def _maestria_by_champion(self, ctx, champion_name, *nick):
        """Retorna a pontuação de maestria do campeão especificado
        :parameter
        ------------
        Nick: Nome in-game do usuário que deseja ver a maestria [obrigatório]
        ------------
        Champion_name: Nome do campeão que deseja ver as maestrias [obrigatório]
            O nome deve ser escrito em uma única palavra (sem acentos), ex: 'Aurelion Sol' escreve-se 'AurelionSol'
        """
        self.player_name = ''.join(nick).replace(" ", "_")

        summoner_response = await get_summoner(self.player_name)

        # if everything is fine:
        champion_mastery_by_name = None
        if "status_code" not in summoner_response:
            all_champions = await get_champions()
            for champion in all_champions:
                if str(champion_name) == str(champion['id']).lower():
                    champion_name = champion['name']
                    champion_mastery_by_name = await get_mastery_by_champion_name(summoner_response['summonerid'], champion['key'])

            if champion_mastery_by_name is None:
                await ctx.channel.send("O nome do personagem que você digitou não existe, tente escrever o nome em uma palavra só | Ex: 'Lee Sin' escreve-se 'LeeSin'")
                return


            # OUTPUT:
            mensagem = f'''```ini\n{summoner_response['name']} [lv. {summoner_response['account_level']}]:\n'''

            mensagem += f'\n' + \
                        f'\nCampeão: [{champion_name}]' + \
                        f'\nPontos Maestria: [{champion_mastery_by_name["championPoints"]}]' + \
                        f'\nNivel Maestria: [{champion_mastery_by_name["championLevel"]}]' + \
                        f'\nEmblemas de maestria com o campeão: [{champion_mastery_by_name["tokensEarned"]}]' + \
                        f'\nUltima partida em: [{champion_mastery_by_name["lastPlayTime"]}]' + \
                        f'\nPontos desde o nível [{champion_mastery_by_name["championLevel"]}]: [{champion_mastery_by_name["championPointsSinceLastLevel"]}]' + \
                        f'\nPontos necessários para o próximo nível: [{champion_mastery_by_name["championPointsUntilNextLevel"]}]'


            mensagem += "\n```"
            await ctx.channel.send(mensagem)

        # if error:
        else:
            await ctx.channel.send(
                f'''```css\n[Algo deu errado 😭]```''')

            if "summoner not found" in summoner_response['message']:
                output_message_error = \
                    f'''
                    - Algo deu errado 😭
                    - Nick de invocador não encontrado!
                    '''
                output_message_formatacao = \
                    f'''
                    [Formatação da função]
                    {config.bot_prefixes[0]}maestria [campeão] [nick]
                    [Exemplo]
                    {config.bot_prefixes[0]}maestria singed Tico Makonha
                    '''

                await ctx.channel.send(f"```diff\n{dedent(output_message_error)}```\n```ini{dedent(output_message_formatacao)}```")

            else:
                print(f"status code: {summoner_response['status_code']}, message: {summoner_response['message']}")

            await ctx.channel.send(
                f'''```ini\nTente usar [{config.bot_prefixes[0]}help maestria]```''')
