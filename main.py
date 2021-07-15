import asyncio
import os

import discord
from discord.ext import commands

import frases
import imagens

import config



from league_of_legends_async import Perfil as LOL_Perfil, Mastery as LOL_Mastery

# -------------------------------------------------------------------------------------- #
# Set bot triggers
prefixes = config.bot_prefixes

# Bot
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=commands.when_mentioned_or(*prefixes), case_insensitive=True, intents=intents,
                   description='Bot feito por um entusiasta em Python (e main singed =D)\n'
                               f'Digite **{config.bot_prefixes[0]} help** para ver os comandos')
bot.remove_command("help")


# Token
bot_token = config.bot_token
if bot_token is None:
    raise Exception("BOT TOKEN NÃO FOI ENCONTRADO NAS VARIAVEIS DE SISTEMA")


# -------------------------------------------------------------------------------------- #


class Help(commands.Cog):
    """Show all commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', description='Show the available commands', aliases=['info', 'commands'])
    async def _help_command(self, ctx, *commands: str):
        """Show the help message"""
        bot = ctx.bot
        embed = discord.Embed(color=discord.Colour.green())
        embed.set_author(name="SingedBot Commands",
                         icon_url="https://media.discordapp.net/attachments/697506479112192024/697640187764932779/singed.png")

        def generate_usage(command_name):
            """Show the command usage"""
            temp = f'{config.bot_prefixes[0]}'
            command = bot.get_command(command_name)
            temp += command.name

            # Parameters
            params = f' '
            for param in command.clean_params:
                params += f'<{command.clean_params[param]}> '
            temp += f'{params}'
            return temp

        def generate_command_list(cog):
            """Create a list of all commands"""
            # Determine longest word
            max = 0
            for command in bot.get_cog(cog).get_commands():
                if not command.hidden:
                    if len(f'{command}') > max:
                        max = len(f'{command}')
            # Build list
            temp = ""
            for command in bot.get_cog(cog).get_commands():
                if command.hidden:
                    temp += ''
                elif command.help is None:
                    temp += f'{config.bot_prefixes[0]}{command}\n'
                else:
                    temp += f'`{config.bot_prefixes[0]}{command}`'
                    for i in range(0, max - len(f'{command}') + 1):
                        temp += '   '
                    temp += f'{command.help}\n'
            return temp

        # Help by itself just lists our own commands.
        if len(commands) == 0:
            for cog in bot.cogs:
                temp = generate_command_list(cog)
                if temp != "":
                    embed.add_field(name=f'**[{str(cog).upper()}]:**', value=temp, inline=False)
        elif len(commands) == 1:
            # Verifica se é o nome de um "cog"
            name = commands[0].capitalize()
            command = None

            if name in bot.cogs:
                cog = bot.get_cog(name)
                msg = generate_command_list(name)
                embed.add_field(name=name, value=msg + ": ", inline=False)
                msg = f'{cog.description}\n'
                embed.set_footer(text=msg)

            # Então só pode ser um comando:
            else:
                command = bot.get_command(name)
                if command is not None:
                    help = f''
                    if command.help is not None:
                        help = command.help
                    embed.add_field(name=f'**{command}**',
                                    value=f'{command.description}```{generate_usage(name)}```\n{help}',
                                    inline=False)
                else:
                    msg = ' '.join(commands)
                    embed.add_field(name="Não encontrado", value=f'Comando/categoria `{msg}` não encontrado.')
        else:
            msg = ' '.join(commands)
            embed.add_field(name="Não encontrado", value=f'Comando/categoria `{msg}` não encontrado.')

        await ctx.send(f'{ctx.author.mention}', embed=embed)
        return

# -------------------------------------------------------------------------------------- #


@bot.event
async def on_message(message):
    """For each received message"""
    print(f"recebi uma mensagem em {message.guild.name} | Enviada por {message.author}: {str(message.content)}")

    if message.author.id == bot.user.id:
        return

    if "singed morreu" in message.content.lower():
        await message.channel.send("Ninguém aqui morreu não, panaca!")

    if "emo" in message.content.lower() and "morreu" in message.content.lower():
        await message.channel.send("PJL emo sapopemba :sob:")

    if message.content.startswith("_juniao"):
        await message.channel.send(
            '''PC: Rocketz Raptor;\nProcessador: Intel Core i3-8100;\nPlaca de vídeo: GTX 1050 2GB GDDR5 128-bit;\nPlaca mãe: H310;\nRAM: 8GB DDR4 2400MHz;\nHDD: HDD1TB;\nFonte: 400W 80 PLUS;''')

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    guild = member.guild
    try:
        print(f"Membro novo em {guild.name}")

        if guild.system_channel is not None:
            mensagem = f"Bem vindo {member.mention} ao {guild.name}!!!"
            await asyncio.sleep(1)
            await guild.system_channel.send(mensagem)

    except Exception as E:
        print("Exceção 01 em on_member_join: " + str(E))

# -------------------------------------------------------------------------------------- #


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tft')
    async def _tft(self, ctx):
        """Send a meme print"""
        await imagens.tft_imagem(ctx)

    @commands.command(name="imagem")
    async def _imagem(self, ctx):
        """Send a singed picture :P"""
        await imagens.singed_imagem(ctx)

    @commands.command(name="frase")
    async def _frase(self, ctx):
        """Send a singed random phrase"""
        await ctx.channel.send(frases.RandomMessage(ctx.message.author).randomoption())

    @commands.command(pass_context=True, name="activity", description="Set the bot activity to playing|listening|streaming|watching", aliases=["set_activity", "atividade", "set_atividade"])
    @commands.is_owner()
    async def _set_activity(self, ctx, activity_type_input, *activity_input):
        """Set the bot custom status."""
        try:
            if str(activity_type_input).lower() == "play" or str(activity_type_input).lower() == "playing" or str(activity_type_input).lower() == "game" or str(activity_type_input).lower() == "jogando":
                activity_type = discord.ActivityType.playing

            elif str(activity_type_input).lower() == "listen" or str(activity_type_input).lower() == "listening" or str(activity_type_input).lower() == "music" or str(activity_type_input).lower() == "ouvindo":
                activity_type = discord.ActivityType.listening

            elif str(activity_type_input).lower() == "stream" or str(activity_type_input).lower() == "streaming" or str(activity_type_input).lower() == "streamando":
                activity_type = discord.ActivityType.streaming

            elif str(activity_type_input).lower() == "watch" or str(activity_type_input).lower() == "watching" or str(activity_type_input).lower() == "assistir" or str(activity_type_input).lower() == "assistindo":
                activity_type = discord.ActivityType.watching

            else:
                activity_type = discord.ActivityType.unknown

            # Tenta chamar o método activity_text da classe Texts
            try:
                await ctx.channel.send(frases.Texts(activity_type, activity_input).set_text(), delete_after=10)

            except Exception as E:
                print(E)

            if activity_type == discord.ActivityType.streaming:
                activity_texts = frases.Texts(activity_type, activity_input)
                activity = discord.Streaming(name=activity_texts.get_title(), url=activity_texts.get_url())
                await self.bot.change_presence(status=discord.Status.online, activity=activity)

            elif activity_type != discord.ActivityType.unknown and activity_input is not None:
                activity = discord.Activity(name=" ".join(activity_input), type=activity_type)
                await self.bot.change_presence(activity=activity)
            else:
                await self.bot.change_presence()



        except discord.InvalidArgument as e:
            await ctx.channel.send(e, delete_after=15)
            raise commands.CommandError(e)

        except Exception as E:
            print("Erro aconteceu: " + str(E))
            await ctx.send("Erro aconteceu: " + str(E), delete_after=15)

        finally:
            # Delete the user message
            await asyncio.sleep(10)
            await ctx.message.delete()

    @_set_activity.error
    async def _set_activity_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("Apenas o <@323310217779478533> pode mexer nisso.\nMorra"
                           "{0.message.author.mention}:middle_finger:!!!".format(ctx), delete_after=15)

        else:
            print("erro: ", type(error), error)


    @commands.guild_only()
    @commands.command(name='clear', description="Delete the X latest chat messages.", aliases=['purge', 'apagar', 'delete'])
    @commands.has_permissions(manage_messages=True)
    async def _clear(self, ctx, quantidade=1):
        """Clears the lastest chat messages. It is possible especify how many messages to delete"""
        try:
            quantidade = int(quantidade)

        except ValueError:
            await ctx.channel.send("Por favor digite um número válido.")

        quantidade_mais_1 = int(quantidade) + 1
        await ctx.channel.purge(limit=quantidade_mais_1)

        # Após apagar mensagem
        mensagem = f"{quantidade} mensagem foi apagada" if quantidade == 1 else f"{quantidade} mensagens foram apagadas"
        output = await ctx.channel.send(mensagem + f" por {ctx.message.author.mention}.")
        await output.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == '❌'

        try:
            await bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await output.remove_reaction("❌", bot.user)
        else:
            await output.delete()

    @_clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.channel.send(f"Desculpa {ctx.message.author.mention}, você não tem permissão para isso!")

        else:
            print("erro ao dar clear: ", type(error), error)


    @commands.has_permissions(manage_roles=True)
    @commands.command(name='kick')
    async def _kick(self, ctx, member: discord.Member, *, reason_input=''):
        """Kicks a user from the guild. Ex: singed kick @user"""

        if reason_input != '':
            reason = f" | Motivo: {reason_input} | Por: {ctx.author}"
        else:
            reason = f" | Por: {ctx.author}"

        if member.top_role >= ctx.author.top_role:
            await ctx.send("Você só pode kickar alguém de nível abaixo de você.")
            return

        if str(member.id) == "258664711099383808":
            await ctx.channel.send("Mais um mono singed sofrendo preconceito :sob:")

        try:
            await member.send(f"Você foi kickado de {ctx.guild.name}" + str(reason))

        except Exception as E:
            print(E)

        finally:
            try:
                await member.kick(reason=reason)
                await ctx.channel.send(f"{member.display_name} foi kickado de {ctx.guild.name} {reason}")
            except Exception as E:
                print(E)


    @_kick.error
    async def _kick_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.channel.send(f"Desculpa {ctx.message.author.mention}, você não tem permissão para isso!")

        else:
            print("erro ao kickar: ", type(error), error)

    @commands.has_permissions(ban_members=True)
    @commands.command(name='ban')
    async def _ban(self, ctx, member: discord.Member, *, reason_input=''):
        """Ban a user from the guild. Ex: singed ban @user"""

        print("Comando ban foi invocado!")
        print("member: ", member)
        print("memberId:", member.id, type(member.id))
        print('reason: ', reason_input)
        print('by: ', ctx.message.author)

        reason = ''
        if reason_input != '':
            reason = f" | Motivo: {reason_input} | Por: {ctx.author}"

        else:
            reason = f" | Por: {ctx.author}"

        if member.top_role >= ctx.author.top_role:
            print("top role True")
            await ctx.send("Você só pode banir alguém de nível abaixo de você.")
            return

        else:
            print("top role False")

        if not member.bot:
            await member.send(f"Você foi banido de {ctx.guild.name}" + str(reason) + " | Por:" + str())
            await member.ban(reason=reason)
            await ctx.channel.send(f"{member.display_name} foi banido de {ctx.guild.name} {reason}")

        else:
            await member.ban(reason=reason)
            await ctx.channel.send(f"O bot {member.display_name} foi banido de {ctx.guild.name} {reason}")


    @_ban.error
    async def _ban_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.channel.send(f"VAI TOMAR NO CU {ctx.message.author.mention} :middle_finger:, QUEM TU PENSA QUE É PRA TENTAR FAZER ISSO??? :angry: ")

        else:
            print("erro ao banir: ", type(error), error)

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name='unban')
    async def unban_(self, ctx, id: int):
        """Unban a user from the guild by ID. Ex: singed unban 1234567"""
        user = await bot.fetch_user(id)
        await ctx.guild.unban(user)
        await ctx.send(f"{user.name}#{user.discriminator} foi desbanido do servidor por {ctx.message.author.mention}")
        print(f"{str(user.name)} foi desbanido do servidor {ctx.guild.name} por {ctx.message.author.name}")


    @unban_.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.channel.send(f"Desculpa {ctx.message.author.mention}, você não tem permissão para isso!")

        else:
            print("erro ao desbanir: ", type(error), error)



@bot.event
async def on_ready():
    """When the bot is ready..."""
    print("===============================================")
    print('Entrei como', bot.user)
    print(f"Nome: {bot.user.name} | ID: {bot.user.id}")
    print("===============================================")


if __name__ == "__main__":
    bot.add_cog(Help(bot=bot))
    bot.add_cog(Utilities(bot=bot))
    bot.add_cog(LOL_Perfil(bot=bot))
    bot.add_cog(LOL_Mastery(bot=bot))
    bot.run(bot_token)
