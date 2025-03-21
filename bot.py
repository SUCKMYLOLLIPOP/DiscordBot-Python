import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import random
import youtube_dl

PREFIX = "!"
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

items_for_sale = {
    "vip": {"price": 10, "description": "VIP access", "code": "VIP-CODE-123"},
    "nitro": {"price": 5, "description": "Discord Nitro Code", "code": "NITRO-CODE-456"}
}

pending_payments = {}

@bot.command()
async def buy(ctx, item: str):
    item = item.lower()
    if item not in items_for_sale:
        await ctx.send("❌ Item not found!")
        return

    item_details = items_for_sale[item]
    payment_info = (
        f"💰 **Payment Instructions** 💰\n"
        f"Item: {item_details['description']}\n"
        f"Price: ${item_details['price']}\n\n"
        f"🔹 **PayPal:** paypal.me/seuemail\n"
        f"🔹 **Litecoin (LTC):** SEU_LTC_WALLET_ADDRESS\n\n"
        f"After payment, an admin must confirm your purchase with `!confirm {ctx.author.mention} {item}`."
    )
    pending_payments[ctx.author.id] = item
    await ctx.send(payment_info)

@bot.command()
@commands.has_permissions(administrator=True)
async def confirm(ctx, member: discord.Member, item: str):
    item = item.lower()
    if member.id not in pending_payments or pending_payments[member.id] != item:
        await ctx.send("❌ No pending payment for this user/item!")
        return

    item_details = items_for_sale.get(item)
    if not item_details:
        await ctx.send("❌ Item not found!")
        return

    del pending_payments[member.id]
    await member.send(f"✅ Payment confirmed! Here is your item: `{item_details['code']}`")
    await ctx.send(f"✅ {member.mention} has received `{item}` successfully!")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} has been kicked! Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} has been banned! Reason: {reason}")

@bot.command()
async def ticket(ctx):
    class TicketView(View):
        def __init__(self):
            super().__init__()
            self.add_item(Button(label="Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket"))
    
    embed = discord.Embed(title="🎫 Ticket System", description="Click the button below to open a ticket.", color=0x00ff00)
    await ctx.send(embed=embed, view=TicketView())

@bot.command()
async def verify(ctx):
    class VerifyView(View):
        def __init__(self):
            super().__init__()
            self.add_item(Button(label="✅ Click to Verify", style=discord.ButtonStyle.green, custom_id="verify_button"))
    
    embed = discord.Embed(
        title="🔒 Server Verification",
        description="Click the button below to verify yourself and gain access to the server.",
        color=0x00ff00
    )
    embed.set_footer(text="Verification System - Secure Your Access")
    await ctx.send(embed=embed, view=VerifyView())

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"] == "verify_button":
        role = discord.utils.get(interaction.guild.roles, name="Verified")
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ You have been verified! Welcome!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Verification role not found. Please contact an admin.", ephemeral=True)


@bot.command()
async def reactionrole(ctx, message_id: int, emoji: str, role: discord.Role):
    message = await ctx.channel.fetch_message(message_id)
    await message.add_reaction(emoji)
    await ctx.send(f"✅ Reaction role added: {emoji} → {role.mention}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def giveaway(ctx, time: int, *, prize: str):
    embed = discord.Embed(title="🎉 Giveaway Started!", description=f"React with 🎉 to participate!\n**Prize:** {prize}\n**Duration:** {time} seconds", color=0xF49726)
    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")
    await asyncio.sleep(time)
    new_message = await ctx.channel.fetch_message(message.id)
    users = [user async for user in new_message.reactions[0].users() if not user.bot]
    if users:
        winner = random.choice(users)
        await ctx.send(f"🎉 Congratulations {winner.mention}! You won **{prize}**! 🎉")
    else:
        await ctx.send("❌ No valid participants, giveaway canceled.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help Menu", description="List of available commands:", color=0x3498db)
    embed.add_field(name="Moderation", value="`!kick`, `!ban`", inline=False)
    embed.add_field(name="Tickets", value="`!ticket`", inline=False)
    embed.add_field(name="Verification", value="`!verify`", inline=False)
    embed.add_field(name="Reaction Roles", value="`!reactionrole`", inline=False)
    embed.add_field(name="Giveaways", value="`!giveaway`", inline=False)
    embed.add_field(name="Music", value="`!play`", inline=False)
    embed.add_field(name="Instant Delivery", value="`!buy`, `!confirm`", inline=False)
    embed.add_field(name="Shutdown", value="`!shutdown`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("⚠️ Shutting down...")
    await bot.close()


TOKEN = "Bot Token Here"
bot.run(TOKEN)

