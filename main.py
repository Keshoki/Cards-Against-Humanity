#/bin/python3
import discord
from discord.ext import commands
from discord.utils import get
import asyncio
from random import choices
from random import choice

bot = commands.Bot(command_prefix=">")
bot.remove_command('help') # own help menu near to the end

@bot.event
async def on_ready():
    print("I'm ready!")

## import cards
blacks = [x.replace("\n","") for x in  open("./black.txt").readlines()]
whites = [x.replace("\n","") for x in  open("./white.txt").readlines()]

userlist = []
card_numer = 5
reactions = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣"] # if you wanna play with more cards, add the emojies
icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Cards_Against_Humanity_logo.png/220px-Cards_Against_Humanity_logo.png"

class User:
    score = 0
    current_card= None
    def __init__(self,cards,name,user):
        self.cards = cards
        self.name = name
        self.user = user
        for x in self.cards:
            whites.remove(x)
            
#ping command
@bot.command(aliases = ["p"])
async def ping(ctx):
    ping_ = bot.latency
    ping =  round(ping_ * 1000)
    embed = discord.Embed(title="Ping", value=f"{ping}", color=discord.Color.gold())
    embed.add_field(name=f"{ping}", value="ms")
    embed.set_footer(text="CAH", icon_url=icon)
    await ctx.send(embed=embed)

#join to the game
@bot.command(aliases = ["j"])
async def join(ctx):
    author=ctx.author

    # check if user already joined
    if all([x.user != author for x in userlist]):
        # create new user
        userlist.append(User(choices(whites,k=card_numer),author.name,author))

        # get the new user's cards
        cards = "\n".join(userlist[-1].cards) 

        # send join message and cards
        embed = discord.Embed(title="Wellcome to the game", color=discord.Color.gold())
        embed.add_field(name = 'Your cards:', value=cards, inline=True)
        embed.set_footer(text="CAH", icon_url=icon)
        await author.send(embed=embed)

    #error if user already joined
    else:await author.send(embed=discord.Embed(title="You've already joined to the game", color=discord.Color.red()))

#list your cards
@bot.command(aliases = ["card", "c"])
async def cards(ctx):
    # get the user
    for user in userlist:
        if ctx.author.name == user.name:
            break
    # get the user's cards and send
    cards = "\n".join(user.cards)
    embed = discord.Embed(title="Cards Against Humanity", color=discord.Color.gold())
    embed.add_field(name = 'Your cards:', value=cards, inline=True)
    embed.set_footer(text="CAH", icon_url=icon)
    await ctx.author.send(embed=embed)

# list all users in the game
@bot.command(aliases = ["user", "u"])
async def users(ctx):
    userl="\n".join(x.name for x in userlist)
    embed = discord.Embed(title="Cards Against Humanity", color=discord.Color.gold())
    embed.add_field(name = 'Users in game:', value=userl, inline=True)
    embed.set_footer(text="CAH", icon_url=icon)
    await ctx.author.send(embed=embed)

#help menu
@bot.command(aliases = ["h"])
async def help(ctx):
    embed = discord.Embed(title="Help", color=discord.Color.gold())
    embed.add_field(name=">start", value="Start the game", inline=False)
    embed.add_field(name=">help", value="Give this help list", inline=False)
    embed.add_field(name=">join", value="Join to the game", inline=False)
    embed.add_field(name=">cards", value="Your current cards", inline=False)
    embed.add_field(name=">users", value="Users in game", inline=False)
    embed.add_field(name=">ping", value="Checks the ping", inline=False)
    embed.set_footer(text="CAH", icon_url=icon) 
    await ctx.author.send(embed=embed)

#start the game
@bot.command(aliases = ["s"])
async def start(ctx):
    def check(reaction, user):
        print(str(reaction.emoji)+reactions[0],user)
        return str(reaction.emoji) == reactions[0]

    #draw a black card
    black_card = choice(blacks)
    blacks.remove(black_card)
    author=ctx.author
    #check if user joined
    if any([x.user == author for x in userlist]):
        messages=[]
        #enumerate users and send the personal vote
        for user in userlist:

            embed = discord.Embed(title=black_card,color=discord.Color.gold())
            #enumerate user's cards
            for n,card in enumerate(user.cards):            
                embed.add_field(name=f"[{n+1}]",value=card, inline=False)

            #send black cards and user's cards
            embed.set_footer(text="CAH", icon_url=icon)
            msg = await user.user.send(embed=embed)
        
            #add emojies
            for emoji in reactions:
                await msg.add_reaction(emoji)
            #get reaction
            messages.append(msg)
        
        #wait for users
        await asyncio.sleep(5)
        
        #check user personal vote
        for n,msg in enumerate(messages):
            msg = await msg.channel.fetch_message(msg.id)
            msg_reactions = {emoji.emoji:emoji.count for emoji in msg.reactions}
            msgreact = max(msg_reactions,key=msg_reactions.get)
            user= userlist[n]
            replaced=black_card.replace("____",user.cards[list(msg_reactions).index(msgreact)])
            user.current_card= f"{replaced}"

        #generate the embed what shows the vote ansvers
        for user in userlist:
            embed = discord.Embed(title="Cards Against Humanity", color=discord.Color.gold())
            for n in range(len(userlist)):
                embed.add_field(name = f'{userlist[n].name}', value=f"{userlist[n].current_card}", inline=True)
            embed.set_footer(text="CAH", icon_url=icon)
            await user.user.send(embed=embed)

    else:await author.send(embed=discord.Embed(title="You aren't joined. Type: **>join**", color=discord.Color.red()))  

@bot.command()
async def scoreboard(ctx):
    pass 
#todo later

TOKEN = open("token.txt",'r').read().replace("\n","")
bot.run(TOKEN)