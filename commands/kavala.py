from discord.ext import commands
import discord
import requests
from utils.bearer import fetchBearer
import json

# Define a setup function to allow the main bot file to register this command
async def setup(bot):
    print("Setting up Duth cog...")
    await bot.add_cog(Kavala(bot))

class Kavala(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def telematics(self, ctx, route_number: str = None):
        if route_number is None:
            await ctx.send("Please provide a route number.")
            return
        elif not route_number.isdigit():
            await ctx.send("Please provide a valid route number (numbers only).")
            return
        elif int(route_number) < 0:
            await ctx.send("Please provide a positive number.")
            return

        # First request to get the stop information
        url = f'https://rest.citybus.gr/api/v1/el/123/stops/{route_number}'
        headers = {
            'Authorization': 'Bearer ' + fetchBearer()
        }
        response1 = requests.get(url, headers=headers)
        if response1.status_code == 200:
            data1 = response1.json()
            line_codes = ", ".join([code for code in data1.get('lineCodes', []) if code != '55'])

            # Creating the initial embed for the stop information
            e = discord.Embed(
                title=f"Δρομολόγια {data1.get('name', 'N/A')}",
                description=f"Γραμμές: {line_codes}"
            )
        else:
            await ctx.send(f"Failed to retrieve stop data. Status code: {response1.status_code}")
            return

        # Second request to get live vehicle information
        url = f'https://rest.citybus.gr/api/v1/el/123/stops/live/{route_number}'
        response2 = requests.get(url, headers=headers)
        if response2.status_code == 200:
            data = response2.json()
            
            # Check if 'vehicles' key is in the response
            if 'vehicles' in data and data['vehicles']:
                vehicle_details = ""
                for vehicle in data['vehicles']:
                    line_code = vehicle.get('lineCode', 'N/A')
                    line_name = vehicle.get('lineName', 'N/A')
                    departure_mins = vehicle.get('departureMins', 0)
                    departure_seconds = vehicle.get('departureSeconds', 0)
                    colorr = vehicle.get('lineColor', None)

                    # Add each vehicle's details to the description
                    vehicle_details += (
                        f"**{line_code} {line_name}**\n"
                        f"Arrives in: {departure_mins} mins {departure_seconds} seconds.\n\n"
                    )
                
                # Add vehicle details to the embed's description
                e.add_field(name="Live Arrivals", value=vehicle_details, inline=False)
                e.colour = discord.Colour.from_str(colorr) if colorr else discord.Colour(0x7289DA)

            else:
                e.add_field(name="Live Arrivals", value="Δεν αναμένονται δρομολόγια για τα επόμενα 30 λεπτά.", inline=False)

            # Send the embed with all the details
            await ctx.send(embed=e)

        else:
            await ctx.send(f"Failed to retrieve live vehicle data. Status code: {response2.status_code}")

    async def saveRoutePrefer(self, ctx, route_number):
        user_id = str(ctx.author.id)
        try:
            with open("data/user_routes.json", "r") as f:
                try:
                    user_data = json.load(f)
                except json.JSONDecodeError:
                    user_data = {}
        except FileNotFoundError:
            user_data = {}

        user_data[user_id] = route_number
    
        with open("data/user_routes.json", "w") as f:
            json.dump(user_data, f, indent=4)

        return f"Route number {route_number} saved succesfully for {ctx.author.name}."

    async def getRouteByUserID(self, ctx):
        user_id = str(ctx.author.id)
        try:
            with open("data/user_routes.json", "r") as f:
                try:
                    user_data = json.load(f)
                except json.JSONDecodeError:
                    await ctx.send("Error: The user data file is corrupted.")
        except FileNotFoundError:
            await ctx.send("Error: No saved routes found.")

        if user_id in user_data:
            route_number = user_data[user_id]
            await ctx.send(f"Route number {route_number} found in DB for {ctx.author.name}.")
            return route_number
        else:
            await ctx.send("No route saved for this user.")
            return -1

    @commands.command()
    async def setroute(self, ctx, route_number: str = None):
        if route_number is None:
            await ctx.send("Please provide a route number.")
            return
        elif not route_number.isdigit():
            await ctx.send("Please provide a valid route number (numbers only).")
            return
        elif int(route_number) < 0:
            await ctx.send("Please provide a positive number.")
            return

        await ctx.send(await self.saveRoutePrefer(ctx, route_number))

    @commands.command()
    async def myroute(self, ctx):
        route_number = await self.getRouteByUserID(ctx)
        if (int(route_number) != -1):
            
            url = f'https://rest.citybus.gr/api/v1/el/123/stops/{str(route_number)}'
            headers = {
                'Authorization': 'Bearer ' + fetchBearer()
            }
            response1 = requests.get(url, headers=headers)
            if response1.status_code == 200:
                data1 = response1.json()
                line_codes = ", ".join([code for code in data1.get('lineCodes', []) if code != '55'])

                e = discord.Embed(
                    title=f"Δρομολόγια {data1.get('name', 'N/A')}",
                    description=f"Γραμμές: {line_codes}"
                )
            else:
                await ctx.send(f"Failed to retrieve stop data. Status code: {response1.status_code}")
                return

            url = f'https://rest.citybus.gr/api/v1/el/123/stops/live/{str(route_number)}'
            response2 = requests.get(url, headers=headers)
            if response2.status_code == 200:
                data = response2.json()

                if 'vehicles' in data and data['vehicles']:
                    vehicle_details = ""
                    for vehicle in data['vehicles']:
                        line_code = vehicle.get('lineCode', 'N/A')
                        line_name = vehicle.get('lineName', 'N/A')
                        departure_mins = vehicle.get('departureMins', 0)
                        departure_seconds = vehicle.get('departureSeconds', 0)
                        colorr = vehicle.get('lineColor', None)

                        vehicle_details += (
                            f"**{line_code} {line_name}**\n"
                            f"Arrives in: {departure_mins} mins {departure_seconds} seconds.\n\n"
                        )

                    e.add_field(name="Live Arrivals", value=vehicle_details, inline=False)
                    e.colour = discord.Colour.from_str(colorr) if colorr else discord.Colour(0x7289DA)

                else:
                    e.add_field(name="Live Arrivals", value="Δεν αναμένονται δρομολόγια για τα επόμενα 30 λεπτά.", inline=False)

                await ctx.send(embed=e)

            else:
                await ctx.send(f"Failed to retrieve live vehicle data. Status code: {response2.status_code}")






    @commands.command()
    async def bmap(self, ctx, arg=None):
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