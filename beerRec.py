import openai
import random
import nextcord
from nextcord.ext import commands
import config
import requests
import base64

def recommendBeer(beerPref):
    openai.api_key = config.openaikey
    MODEL = "gpt-3.5-turbo"
    beer_key = config.beerApiKey
    url = 'https://api.catalog.beer/beer'
    auth_header = base64.b64encode(f'{beer_key}:'.encode('utf-8')).decode('utf-8')
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Basic {auth_header}'
    }

    beerResponse = requests.get(url, headers=headers)
    if beerResponse.status_code == 200:
        beer_list = "\n".join(beer['name'] for beer in beerResponse.json()['data'])
        prompt = f"Please choose a beer from this list:\n{beer_list}\nI want a beer like this: {beerPref}"
        temperature = random.uniform(.5, 1.0)
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a bartender in Florida and a customer wants a recommendation for a craft beer.  You will be given a beer list and asked which beer on the list most closely matches the customer request"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response['choices'][0]['message']['content']
    else:
        print(f'Error: {beerResponse.status_code} - {beerResponse.text}')

    # temperature is the variable that sets how complex the response can be the higher the number the higher the complexity


bot = commands.Bot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.slash_command(description="Please enter a comparable beer or features you would like in a craft beer", guild_ids=[639278542382694401, 348564060846948363, 934954222829584435, 878487240383295549])
async def beers(interaction: nextcord.Interaction, statement: str):
    # defer the response, so we can take a long time to respond, by default discord give you 3 seconds to send a response
    await interaction.response.defer()
    # call getNpc to generate the character this takes about 5-10 seconds usually sometimes longer
    answer = recommendBeer(statement)
    # followup must be used after defer since a response is already sent this updates the message to include the generated character
    await interaction.followup.send("Features Requested: " + statement + "\n\n" + answer)

bot.run(config.botkey)