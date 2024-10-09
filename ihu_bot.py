import discord
from discord.ext import commands
from discord.utils import get
from discord.ui import Button, View
import asyncio
from discordtoken import TOKEN
import json
import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(f"-help"))
    await bot.tree.sync(guild=discord.Object(id=898491436738174996))
    print("Bot is ready.")



# ------------------------ IHU INFO ------------------------ #

@bot.command()
async def teachers(ctx):

    await ctx.send(f"**Τα emails του Duth εδώ: <#{1265207476710805637}>**\n")

    with open("ihu_data/teachers.json", "rb") as f:
            teachers = json.load(f)
    e = discord.Embed(
        title=":bookmark_tabs: __Πληροφορίες Καθηγητών__ :bookmark_tabs:",
        colour=discord.Colour.red()
    )
    border = ""
    for i in range(1, len(teachers) + 1):
        border += str(i) + ". " + teachers[str(i)]["name"][2:-2] + "\n"
    e.add_field(name="Γράψε τον αριθμό του καθηγητή", value=border)
    await ctx.send(embed=e)

    check = lambda m: m.author == ctx.author
    msg = await bot.wait_for('message', check=check, timeout=30)

    try:
        teacher_index = int(msg.content)
        if str(teacher_index) in teachers:
            teacher_info = teachers[str(teacher_index)]
            response = (
                f"**Email:** {teacher_info['email']}\n"
                f"**Τηλέφωνο:** {teacher_info['phone']}\n"
                f"**Ώρες Διαθεσιμότητας:** {teacher_info['hours']}"
            )
            await ctx.send(embed=discord.Embed(
                title=teacher_info['name'],
                description=response,
                colour=discord.Colour.orange()
            ))
        else:
            await ctx.send("Δεν υπάρχει καθηγητής με αυτόν τον αριθμό.")
    except ValueError:
        await ctx.send("Δώσε έναν έγκυρο αριθμό.")




@bot.command()
async def services(ctx):

    services = pd.read_csv('ihu_data/services.csv')

    e = discord.Embed(
        title=":placard: __CS IHU Υπηρεσίες__ :placard:",
        colour=discord.Colour.orange()
    )
    for i in range(0, len(services)):
        e.add_field(name = services['service'].iloc[i], value = services['link'].iloc[i], inline = False)
    await ctx.send(embed=e)


@bot.command()
async def books(ctx):

    books = pd.read_csv('ihu_data/books.csv')

    pages = []
    TOTAL_PAGES = 6
    for i in range(0, TOTAL_PAGES):
        semester = i+1
        filtered_books = books[books['semester'] == semester]
        filtered_books = filtered_books[['subject','code']]
        page = discord.Embed (
            title = f"__{i+1}ο Εξάμηνο__",
            description="__Κωδικοί Συγγραμάτων__",
            colour = discord.Colour.orange()
        )
        for i in range(0, len(filtered_books)):
            page.add_field(name = filtered_books['subject'].iloc[i], value = filtered_books['code'].iloc[i], inline = False)
        page.set_footer(text = "Link για τις δηλώσεις: https://service.eudoxus.gr/student")
        pages.append(page)

    message = await ctx.send(embed = pages[0])

    reactions = ['⏮', '◀', '▶', '⏭']
    for reaction in reactions:
        await message.add_reaction(reaction)

    def check(reaction, user):
        return user == ctx.author

    reaction = None
    i = 0
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
            
            if str(reaction) == '⏮':
                i = 0
                await message.edit(embed = pages[i])
            elif str(reaction) == '◀':
                if i > 0:
                    i -= 1
                    await message.edit(embed = pages[i])
            elif str(reaction) == '▶':
                if i < 5:
                    i += 1
                    await message.edit(embed = pages[i])
            elif str(reaction) == '⏭':
                i = 5
                await message.edit(embed = pages[i])
        except asyncio.TimeoutError:
            break
        
    await message.clear_reactions()


@bot.command()
async def lessons(ctx):

    lessons = pd.read_csv('ihu_data/lessons.csv')

    pages = []
    TOTAL_PAGES = 8
    for i in range(0, TOTAL_PAGES):
        semester = i+1
        filtered_lessons = lessons[lessons['semester'] == semester]
        filtered_lessons = filtered_lessons[['subject','credits', 'teaching_hours', 'subject_type']]
        page = discord.Embed (
            title = f"__{i+1}ο Εξάμηνο__",
            colour = discord.Colour.orange()
        )
        for i in range(0, len(filtered_lessons)):
            page.add_field(name = "`" + filtered_lessons['subject'].iloc[i] + "`", 
                           value = "Διδακτικές Μονάδες: " + str(filtered_lessons['credits'].iloc[i]) +'\n'+
                                   "Ώρες Διδασκαλίας: " + str(filtered_lessons['teaching_hours'].iloc[i]) +'\n'+
                                   "Τύπος Μαθήματος: " + filtered_lessons['subject_type'].iloc[i], inline = True)
        pages.append(page)                                            

    message = await ctx.send(embed = pages[0])

    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
    
    for reaction in reactions:
        await message.add_reaction(reaction)
    
    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            await message.remove_reaction(reaction, user)
            if str(reaction) in reactions:
                i = reactions.index(str(reaction))
                await message.edit(embed=pages[i])
        except:
            break
    await message.clear_reactions()


@bot.command()
async def map(ctx):
    e = discord.Embed(
        color=discord.Colour.orange()
    )
    e.set_image(url="https://i.postimg.cc/pdr8kyFq/map.png")
    await ctx.send(embed=e)


@bot.command()
async def foodclub(ctx):
    e = discord.Embed(
        title=":fork_and_knife: __Ωράρια Λέσχης__ :fork_and_knife:",
        colour=discord.Colour.blue()
    )
    e.add_field(name="__Πρωί__", value="8:00-9:30", inline=True)
    e.add_field(name="__Μεσημέρι__", value="12:30-16:00", inline=True)
    e.add_field(name="__Βράδυ__", value="18:00-21:00", inline=True)
    await ctx.send(embed=e)


@bot.command(aliases=["secretariat", "contact"])
async def secreteriat(ctx):
    e = discord.Embed(
        title=":telephone: __Γραμματεία__ :telephone:",
        colour=discord.Colour.red()
    )
    e.add_field(name="__Ώρες Γραφείου__", value="11:00-13:00", inline=False)
    e.add_field(name="__Email__", value="info@cs.ihu.gr", inline=False)
    e.add_field(name="__Τηλέφωνα__", value="2510462147\n2510462341", inline=False)
    e.add_field(name="Website", value="http://www.cs.ihu.gr", inline=False)
    await ctx.send(embed=e)


@bot.command()
async def library(ctx):
    e = discord.Embed(
        title=":books: __Βιβλιοθήκη__ :books:",
        colour=discord.Colour.green()
    )
    e.add_field(name="__Ώρες Λειτουργίας__", value="8:00-14:30", inline=False)
    await ctx.send(embed=e)

# ----------------------------- KAVALA ----------------------------- #

@bot.command()
async def bmap(ctx, arg=None):
    error_line = f"Η γραμμή {arg} δεν λειτουργεί"
    busses = ['https://i.postimg.cc/y6SmmMxK/Capture.jpg', error_line, error_line, "https://i.postimg.cc/y6SmmMxK/Capture.jpg", "https://i.postimg.cc/G3ZZznjx/Capture.jpg", error_line, error_line,
                error_line, error_line, "https://i.postimg.cc/kMtH2hd6/Capture.jpg", "https://i.postimg.cc/dVnHbbGX/Capture.jpg"]
    if arg==None:
        await ctx.send("Γράψε την γράμμη μετά την εντολή `π.χ. -bmap 5`")
    else:
        try:
            if busses[int(arg)-1]!=error_line:
                e = discord.Embed(
                color=discord.Color.orange()
            )
                e.set_image(url=busses[int(arg)-1])
                await ctx.send(embed=e)
            else:
                await ctx.send(error_line)
        except:
            await ctx.send("Γράψε μια έγκυρη γραμμή")


@bot.command()
async def studyguide(ctx):
    e = discord.Embed(
        title=":books: __Οδηγός Σπουδών__ :books:",
        colour=discord.Colour.green()
    )
    e.add_field(name="__Link__", value="https://cs.ihu.gr/cs_hosting/attachments/webpages/el_study_guide.pdf", inline=False)
    await ctx.send(embed=e)

# ----------------------------- BOT ----------------------------- #

@bot.command()
async def ping(ctx):
    await ctx.send(f"{round(bot.latency * 800)}ms")

@bot.command()
async def code(ctx):
    e = discord.Embed(
        title=":robot: __Bot Code__ :robot:",
        colour=discord.Colour.blue()
    )
    e.add_field(name="Github", value="https://github.com/PhoenixDoom/ihu_bot", inline=False)
    await ctx.send(embed=e)


#----------------------------- HELP -----------------------------#

@bot.command(aliases=["commands", "cmds"])
async def help(ctx):
    #buttons
    style = discord.ButtonStyle.green
    uni = Button(label="CS IHU", style=style, emoji="🏫")
    town = Button(label="KAVALA", style=style, emoji="🏙️")
    bot = Button(label="BOT", style=style, emoji="🤖")

    view = View(timeout=30)
    view.add_item(uni)
    view.add_item(town)
    view.add_item(bot)

    page1 = discord.Embed(
        colour=discord.Colour.blue()
    )
    page1.set_author(name="Commands")
    page1.add_field(name="__CS IHU__", value="**-services** - Εμφανίζει όλες τις υπηρεσίες για το τμήμα.\n"
                                         "**-teachers** - Εμφανίζει πληροφορίες για τους καθηγητές του τμήματος.\n"
                                         "**-map** - Εμφανίζει τον χάρτη για κτήρια τμήματος.\n"
                                         "**-foodclub** - Εμφανίζει τα ωράρια της λέσχης.\n"
                                         "**-contact** - Εμφανίζει τα στοιχεία επικοινωνίας για το τμήμα.\n"
                                         "**-books** - Εμφανίζει την λίστα των βιβλίων των εξαμήνων με τους κωδικούς.\n"
                                         "**-lessons** - Εμφανίζει το πρόγραμμα σπουδών όλων των εξαμήνων.\n"
                                         "**-library** - Εμφανίζει τις ώρες λειτουργίας της βιβλιοθήκης.\n"
                                         "**-studyguide** - Εμφανίζει τον οδηγό σπουδών.\n",
                                         inline=False)
    page2 = discord.Embed(
        colour=discord.Colour.blue()
    )

    page2.add_field(name="__Περί Καβάλας__", value="**-bmap <αριθμός γραμμής>** - Δείχνει την διαδρομή του λεωφορείου.", inline=False)

    page3 = discord.Embed(
        colour=discord.Colour.blue()
    )
    page3.add_field(name="__Bot Info__", value="**-ping** - Εμφανίζει την ταχύτητα του μποτ ανα δευτερόλεπτο.\n"
                                            "**-code** - Στέλνει το link με τον κώδικα από το bot.", inline=False)
    
    message = await ctx.send(embed=page1, view=view)

    async def edit_message_and_defer(interaction, page):
        await message.edit(embed=page)
        await interaction.response.defer()

    async def uni_callback(interaction):
        await edit_message_and_defer(interaction, page1)
    
    async def town_callback(interaction):
        await edit_message_and_defer(interaction, page2)
    
    async def bot_callback(interaction):
        await edit_message_and_defer(interaction, page3)

    uni.callback = uni_callback
    town.callback = town_callback
    bot.callback = bot_callback
    

#------------------------------------------------------------Events------------------------------------------------------------

@bot.event
async def on_message(message):
    bot_commands = [f"-{alias}" for command in bot.commands for alias in [command.name, *command.aliases]]
    if message.channel.id == 898491436738174999 and message.content in bot_commands:
        channel = get(bot.get_all_channels(), id=901068164648030228)
        await message.channel.send(f"Οι εντολές εδώ: {channel.mention}")
        return
    await bot.process_commands(message)

#------------------------------------------------------------Test Code------------------------------------------------------------


"""
@bot.tree.command(name = "help", description = "Testing mode", guild=discord.Object(id=898491436738174996)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_command(interaction):
    await interaction.response.send_message("Hello!")
"""
bot.run(TOKEN)
