import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from youtube_search import YoutubeSearch

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_member_join(member):
	await member.create_dm()
	await member.dm_channel.send(
		f'Hi {member.name}, welcome to my Discord server! Type !help for commands. :)'
	)

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	if message.content == 'kill':
		await message.channel.send('ok bye :(')
		await bot.logout()
	elif message.content == 'raise-exception':
		raise discord.DiscordException

	await bot.process_commands(message)	

@bot.event
async def on_error(event, *args, **kwargs):
	with open('err.log', 'a') as f:
		if event == 'on_message':
			f.write(f'Unhandled message: {args[0]}\n')
		else:
			raise

@bot.command(name='join')
async def join(ctx):
	channel = ctx.message.author.voice.channel
	await channel.connect()

@bot.command(name='leave')
async def leave(ctx):
	server = ctx.message.guild.voice_client
	await server.disconnect()

@bot.command(name='roll', help='rng simulator')
async def roll(ctx, number_of_rolls: int, min_num: int, max_num: int):
	if number_of_rolls <= 0:
		await ctx.send('Why are you even rolling?')
	elif min_num < 0 or max_num < 0:
		await ctx.send('No negative numbers.')
	elif min_num > max_num:
		await ctx.send('Min is greater than max.')
	else:
		outcome = [
			str(random.choice(range(min_num, max_num + 1)))
			for _ in range(number_of_rolls)
		]
		await ctx.send(' '.join(outcome))

@bot.command(name='blackjack', help='blackjack card game')
async def blackjack(ctx):
	A = 11
	J = 10
	Q = 10
	K = 10

	deck = [A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K]

	hand = [
			random.choice(deck)
			for _ in range(2)
		   ]

	await ctx.send(hand)

	hand_count = hand[0] + hand[1]

	await ctx.send(hand_count)

	if hand_count == 21:
		await ctx.send('Blackjack!')

	dealer_count = random.choice(range(17,22)) #psuedo-dealer

	while (hand_count < 21):
		msg = await bot.wait_for('message', 
			check=lambda message: message.author == ctx.author, timeout=15)
		if msg.content == 'hit':
			next_card = random.choice(deck)
			hand.append(next_card)
			hand_count += int(next_card)
			await ctx.send(hand)
			await ctx.send(hand_count)
		elif msg.content == "stand":
			if hand_count > dealer_count:
				await ctx.send(f'You got {hand_count}. Dealer has {dealer_count}. You win.')
			elif hand_count < dealer_count:
				await ctx.send(f'You got {hand_count}. Dealer has {dealer_count}. You lose.')
			elif hand_count == dealer_count:
				await ctx.send(f'You got {hand_count}. Dealer has {dealer_count}. Push.')
			hand_count = 21
		elif msg.content == "fold":
			await ctx.send("Good luck next time!")
			hand_count = 21

	if hand_count > 21:
		await ctx.send("Bust.")

@bot.command(name='youtube', help='searches and returns first link from youtube')
async def youtube(ctx,*,search_term):
	results = YoutubeSearch(search_term, max_results=1).to_dict()

	results_dict = results[0]

	url = "https://www.youtube.com" + results_dict["link"]

	await ctx.send(url)

bot.run(token)