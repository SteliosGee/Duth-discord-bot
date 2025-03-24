from discord.ext import commands
import discord
import json
import pandas as pd
import asyncio
from datetime import datetime

# Define a setup function to allow the main bot file to register this command
async def setup(bot):
    print("Setting up Duth cog...")
    await bot.add_cog(Duth(bot))

class Duth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def teachers(self, ctx):

        with open("data/teachers.json", "rb") as f:
                teachers = json.load(f)

        e = discord.Embed(
            title=":bookmark_tabs: __Πληροφορίες Καθηγητών__ :bookmark_tabs:",
            colour=discord.Colour.red()
        )
        border = ""
        for i in range(1, len(teachers) + 1):
            border += str(i) + ". " + teachers[str(i)]["name"] + "\n"
        e.add_field(name="Γράψε τον αριθμό του καθηγητή", value=border)
        await ctx.send(embed=e)

        check = lambda m: m.author == ctx.author
        msg = await self.bot.wait_for('message', check=check, timeout=30)

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
                    title=f"__{teacher_info['name']}__",
                    description=response,
                    colour=discord.Colour.orange()
                ))
            else:
                await ctx.send("Δεν υπάρχει καθηγητής με αυτόν τον αριθμό.")
        except ValueError:
            await ctx.send("Δώσε έναν έγκυρο αριθμό.")

    @commands.command()
    async def books(self, ctx):

        books = pd.read_csv('data/books.csv')
        today = datetime.now()
        todayMonthId = today.month 

        pages = []
        TOTAL_PAGES = 8
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
        
        roles = ['1ο Έτος', '2ο Έτος', '3ο Έτος', '4ο Έτος']
        highestRole = -1

        for i, role in enumerate(roles):
            if discord.utils.get(ctx.guild.roles, name=role) in ctx.author.roles:
                highestRole = i

        if highestRole > -1:
            if todayMonthId >= 9 or 1: #vlepei an einai xhmerino h earino eksamino
                pageindex = highestRole
                message = await ctx.send(embed=pages[pageindex])
            else:
                pageindex = highestRole * 2
                message = await ctx.send(embed=pages[pageindex])
        else:
            message = await ctx.send(embed=pages[0])
            pageindex = 0

        reactions = ['⏮', '◀', '▶', '⏭']
        for reaction in reactions:
            await message.add_reaction(reaction)

        def check(reaction, user):
            return user == ctx.author

        reaction = None
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check)
                await message.remove_reaction(reaction, user)
                
                if str(reaction) == '⏮':
                    pageindex = 0
                    await message.edit(embed = pages[pageindex])
                elif str(reaction) == '◀':
                    if pageindex > 0:
                        pageindex -= 1
                        await message.edit(embed = pages[pageindex])
                elif str(reaction) == '▶':
                    if pageindex < TOTAL_PAGES - 1:
                        pageindex += 1
                        await message.edit(embed = pages[pageindex])
                elif str(reaction) == '⏭':
                    pageindex = TOTAL_PAGES - 1
                    await message.edit(embed = pages[pageindex])
            except asyncio.TimeoutError:
                break
            
        await message.clear_reactions()

    @commands.command()
    async def services(self, ctx):
        services = pd.read_csv('data/services.csv')

        e = discord.Embed(
            title=":placard: __CS IHU Υπηρεσίες__ :placard:",
            colour=discord.Colour.orange()
        )
        for i in range(0, len(services)):
            e.add_field(name = services['service'].iloc[i], value = services['link'].iloc[i], inline = False)
        await ctx.send(embed=e)

    @commands.command()
    async def lessons(self, ctx):

        lessons = pd.read_csv('data/lessons.csv')

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
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                await message.remove_reaction(reaction, user)
                if str(reaction) in reactions:
                    i = reactions.index(str(reaction))
                    await message.edit(embed=pages[i])
            except:
                break
        await message.clear_reactions()

    @commands.command()
    async def map(self, ctx):
        e = discord.Embed(
            title=":map: __Χάρτης Κτηρίων__ :map:",
            description="https://www.google.com/maps/d/u/0/viewer?mid=1i-HiiBJ5nmbLTn0ICwlMethic5QNXxj9&femb=1&ll=40.92907370994802%2C24.378847167196625&z=18",
            colour=discord.Colour.blue()
        )
        e.set_footer(text="Το url είναι προσωρινό και θα αντικατασταθεί με χάρτη.")
        await ctx.send(embed=e)

    @commands.command()
    async def foodclub(self, ctx):
        e = discord.Embed(
            title=":fork_and_knife: __Ωράρια Λέσχης__ :fork_and_knife:",
            colour=discord.Colour.blue()
        )
        e.add_field(name="__Πρωί__", value="8:00-9:30", inline=True)
        e.add_field(name="__Μεσημέρι__", value="12:30-16:00", inline=True)
        e.add_field(name="__Βράδυ__", value="18:00-21:00", inline=True)
        await ctx.send(embed=e)

    @commands.command(aliases=["secretariat", "contact"])
    async def secreteriat(self, ctx):
        e = discord.Embed(
            title=":telephone: __Γραμματεία__ :telephone:",
            colour=discord.Colour.red()
        )
        e.add_field(name="__Ώρες Γραφείου__", value="11:00-13:00", inline=False)
        e.add_field(name="__Email__", value="secr@cs.duth.gr", inline=False)
        e.add_field(name="__Τηλέφωνα__", value="2510462147\n2510462341", inline=False)
        e.add_field(name="Website", value="http://www.cs.duth.gr", inline=False)
        await ctx.send(embed=e)

    @commands.command()
    async def library(self, ctx):
        e = discord.Embed(
            title=":books: __Βιβλιοθήκη__ :books:",
            colour=discord.Colour.green()
        )
        e.add_field(name="__Ώρες Λειτουργίας__", value="8:00-14:30", inline=False)
        await ctx.send(embed=e)

    @commands.command()
    async def studyguide(self, ctx):
        e = discord.Embed(
            title=":books: __Οδηγός Σπουδών__ :books:",
            colour=discord.Colour.green()
        )
        e.add_field(name="__Link__", value="https://cs.duth.gr/cs_hosting/attachments/webpages/el_study_guide.pdf", inline=False)
        await ctx.send(embed=e)