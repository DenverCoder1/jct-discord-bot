import os

def is_admin(member):
	return int(os.getenv('ADMIN_ROLE_ID')) in [role.id for role in member.roles]


async def add_symbol(member, symbol='※'):
	await member.edit(nick=member.nick + ' ' + symbol)


async def remove_symbol(member, symbol='※'):
	await member.edit(nick=member.nick[:-2])