token = "OTQ3NDQyMDEzNTg0ODgzNzQy.YhtUIg.ggEaMPqbSBbybub_LZEAY_96cDk"

import discord, asyncio, os, sqlite3, datetime
from discord.ext import commands
from user import *
from gamble import *

bot = commands.Bot(command_prefix='!',  help_command = None)

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')


@bot.command()
async def 청소(ctx, number):
    if ctx.message.author.guild_permissions.administrator:
        purge_number = number
        await ctx.channel.purge(limit=int(purge_number)+1)
        msg = await ctx.channel.send(f"**{purge_number}개**의 메세지를 삭제했습니다.")
        await asyncio.sleep(2)
        await msg.delete()
    else:
        await ctx.send('이 서버의 관리자가 아닙니다.')

#없는 명령어 실행시
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
    	await ctx.send("해당 명령어는 없는 명령어입니다. [!도움말]을 참조하여 명령어를 확인하세요.")


@bot.command(aliases=['도움말', '명령어'])
async def help(ctx):
    embed = discord.Embed(title = "도움말", description = "**!회원가입**\nBN GAMELAND 서비스에 가입할 수 있습니다.\n\n**!회원탈퇴**\nBN GAMELAND 서비스에서 탈퇴할 수 있습니다.\n\n**!잔액확인**\n현재 보유중인 잔액을 확인할 수 있습니다.\n\n**!홀짝게임**\n[!홀짝게임 (홀/짝) (배팅금액)] 명령어를 통해 홀짝게임을 진행할 수 있습니다.\n\n**!투스핀**\n[!투스핀 (배팅금액)] 명령어를 통해 봇과의 투스핀 도박을 할 수 있습니다.", color = 0xffc0cb)
    embed.set_footer(text = f"{ctx.message.author.name} ", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed)

@bot.command()
async def 회원가입(ctx):
    print("회원가입이 가능한지 확인합니다.")
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)
    if userExistance:
        print("DB에서", ctx.author.name, "을 찾았습니다.")
        print("---------------------------------")
        await ctx.send("이미 가입하셨습니다.")
    else:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        print("")

        Signup(ctx.author.name, ctx.author.id)

        print("회원가입이 완료되었습니다.")
        print("------------------------------\n")
        await ctx.send("회원가입이 완료되었습니다.")

@bot.command()
async def 회원탈퇴(ctx):
    print("탈퇴가 가능한지 확인합니다.")
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)
    if userExistance:
        DeleteAccount(userRow)
        print("탈퇴가 완료되었습니다.")
        print("------------------------------\n")

        await ctx.send("탈퇴가 완료되었습니다.")
    else:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        print("------------------------------\n")

        await ctx.send("등록되지 않은 사용자입니다.")


@bot.command()
async def 잔액확인(ctx):
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)

    if not userExistance:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        print("------------------------------\n")
        await ctx.send("회원가입 후 자신의 잔액을 확인할 수 있습니다.")
    else:
        money = userInfo(userRow)
        userNum = checkUserNum()
        print("------------------------------\n")
        embed = discord.Embed(title="유저 정보", description = ctx.author.name, color = 0x62D0F6)
        embed.add_field(name = "보유 자산", value = money, inline = False)
        await ctx.send(embed=embed)



@bot.command()
async def 유저정보확인(ctx, user: discord.User):
    userExistance, userRow = checkUser(user.name, user.id)
    if ctx.message.author.guild_permissions.administrator:
        if not userExistance:
            print("DB에서 ", user.name, "을 찾을 수 없습니다")
            print("------------------------------\n")
            await ctx.send(user.name  + " 은(는) 등록되지 않은 사용자입니다.")
        else:
            money = userInfo(userRow)
            userNum = checkUserNum()
            print("------------------------------\n")
            embed = discord.Embed(title="유저 정보", description = user.name, color = 0x62D0F6)
            embed.add_field(name = "보유 자산", value = money, inline = False)

            await ctx.send(embed=embed)
    else:
        await ctx.send("이 서버의 관리자가 아닙니다.")
    
@bot.command()
async def 홀짝게임(ctx, content, money):
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)
    win, result2 = gamble()
    result = ""
    betting = 0
    _color = 0x000000
    if userExistance:
        print("DB에서 ", ctx.author.name, "을 찾았습니다.")
        cur_money = getMoney(ctx.author.name, userRow)
        if content == "홀":
            if int(money) >= 500 and int(money) <= 5000:
                if cur_money >= int(money):
                    betting = int(money)
                    print("배팅금액: ", betting)
                    print("")

                    if win == "홀":
                        result = "성공"
                        _color = 0x00ff56
                        print(result)

                        modifyMoney(ctx.author.name, userRow, int(0.95*betting))
                        await ctx.send("주사위를 굴려 " + result2 + "의 숫자가 나왔습니다.")
                    elif win == "짝":
                        result = "실패"
                        _color = 0xFF0000
                        print(result)

                        modifyMoney(ctx.author.name, userRow, -int(betting))
                        await ctx.send("주사위를 굴려 " + result2 + "의 숫자가 나왔습니다.")

                    embed = discord.Embed(title = "도박 결과", description = result, color = _color)
                    embed.add_field(name = "배팅금액", value = betting, inline = False)
                    embed.add_field(name = "현재 자산", value = getMoney(ctx.author.name, userRow), inline = False)

                    await ctx.send(embed=embed)

                else:
                    print("돈이 부족합니다.")
                    print("배팅금액: ", money, " | 현재자산: ", cur_money)
                    await ctx.send("돈이 부족합니다. 현재자산: " + str(cur_money))
            else:
                print("배팅금액", money, "가 500보다 작거나 5000보다 큽니다.")
                await ctx.send("배팅금액은 500달러 이상 5,000달러 미만의 금액만 배팅 가능합니다.")
        elif content == "짝":
            if int(money) >= 500 and int(money) <= 5000:
                if cur_money >= int(money):
                    betting = int(money)
                    print("배팅금액: ", betting)
                    print("")

                    if win == "짝":
                        result = "성공"
                        _color = 0x00ff56
                        print(result)

                        modifyMoney(ctx.author.name, userRow, int(0.95*betting))
                        await ctx.send("주사위를 굴려 " + result2 + "의 숫자가 나왔습니다.")
                    elif win == "홀":
                        result = "실패"
                        _color = 0xFF0000
                        print(result)

                        modifyMoney(ctx.author.name, userRow, -int(betting))
                        await ctx.send("주사위를 굴려 " + result2 + "의 숫자가 나왔습니다.")

                    embed = discord.Embed(title = "도박 결과", description = result, color = _color)
                    embed.add_field(name = "배팅금액", value = betting, inline = False)
                    embed.add_field(name = "현재 자산", value = getMoney(ctx.author.name, userRow), inline = False)

                    await ctx.send(embed=embed)

                else:
                    print("돈이 부족합니다.")
                    print("배팅금액: ", money, " | 현재자산: ", cur_money)
                    await ctx.send("돈이 부족합니다. 현재자산: " + str(cur_money))
            else:
                print("배팅금액", money, "가 500보다 작거나 5000보다 큽니다.")
                await ctx.send("배팅금액은 500달러 이상 5,000달러 미만의 금액만 배팅 가능합니다.")
        else:
            await ctx.send("배팅은 홀 또는 짝으로만 배팅할 수 있습니다.")
    else:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        await ctx.send("도박은 회원가입 후 이용 가능합니다.")

    print("------------------------------\n")

@bot.command()
async def 투스핀(ctx, money):
    userExistance, userRow = checkUser(ctx.author.name, ctx.author.id)
    betting = 0
    if userExistance:
        print("DB에서 ", ctx.author.name, "을 찾았습니다.")
        cur_money = getMoney(ctx.author.name, userRow)
        if int(money) >= 500 and int(money) <= 5000:
            if cur_money >= int(money):
                betting = int(money)
                result, _color, bot1, bot2, user1, user2, a, b = dice()
                if result == "패배":
                    modifyMoney(ctx.author.name, userRow, -int(money))
                    await ctx.send("GAME BOT과의 투스핀 대결에서 패배하였습니다.")
                elif result == "무승부":
                    modifyMoney(ctx.author.name, userRow, 0*int(money))
                    await ctx.send("GAME BOT과의 투스핀 대결이 무승부입니다.")
                elif result == "승리":
                    modifyMoney(ctx.author.name, userRow, int(0.95*betting))
                    await ctx.send("GAME BOT과의 투스핀 대결에서 승리하였습니다.")

                embed = discord.Embed(title = "주사위 게임 결과", description = " ", color = _color)
                embed.add_field(name = "GAME BOT의 숫자 " + bot1 + "+" + bot2, value = ":game_die: " + a, inline = False)
                embed.add_field(name = ctx.author.name+"의 숫자 " + user1 + "+" + user2, value = ":game_die: " + b, inline = False)
                embed.set_footer(text="결과: " + result)
                embed.add_field(name = "배팅금액", value = int(money), inline = False)
                embed.add_field(name = "현재 자산", value = getMoney(ctx.author.name, userRow), inline = False)
                    
                await ctx.send(embed=embed)

            else:
                print("돈이 부족합니다.")
                print("배팅금액: ", money, " | 현재자산: ", cur_money)
                await ctx.send("돈이 부족합니다. 현재자산: " + str(cur_money))
        else:
            print("배팅금액", money, "가 500보다 작거나 5000보다 큽니다.")
            await ctx.send("배팅금액은 500달러 이상 5,000달러 미만의 금액만 배팅 가능합니다.")
    else:
        print("DB에서 ", ctx.author.name, "을 찾을 수 없습니다")
        await ctx.send("도박은 회원가입 후 이용 가능합니다.")


@bot.command()
async def 송금(ctx, user: discord.User, money):
    print("송금이 가능한지 확인합니다.")
    senderExistance, senderRow = checkUser(ctx.author.name, ctx.author.id)
    receiverExistance, receiverRow = checkUser(user.name, user.id)

    if not senderExistance:
        print("DB에서", ctx.author.name, "을 찾을수 없습니다")
        print("------------------------------\n")
        await ctx.send("회원가입 후 송금이 가능합니다.")
    elif not receiverExistance:
        print("DB에서 ", user.name, "을 찾을 수 없습니다")
        print("------------------------------\n")
        await ctx.send(user.name  + " 은(는) 등록되지 않은 사용자입니다.")
    else:
        print("송금하려는 돈: ", money) 

        s_money = getMoney(ctx.author.name, senderRow)
        r_money = getMoney(user.name, receiverRow)

        if s_money >= int(money) and int(money) != 0 and int(money) > 0:
            print("돈이 충분하므로 송금을 진행합니다.")
            print("")

            remit(ctx.author.name, senderRow, user.name, receiverRow, money)

            print("송금이 완료되었습니다. 결과를 전송합니다.")

            embed = discord.Embed(title="송금 완료", description = "송금된 돈: " + money, color = 0x77ff00)
            embed.add_field(name = "보낸 사람: " + ctx.author.nick, value = "현재 자산: " + str(getMoney(ctx.author.name, senderRow)))
            embed.add_field(name = "→", value = ":moneybag:")
            embed.add_field(name="받은 사람: " + user.name, value="현재 자산: " + str(getMoney(user.name, receiverRow)))
                    
            await ctx.send(embed=embed)
        elif int(money) == 0:
            await ctx.send("0원을 보낼 필요는 없죠")
        elif int(money) < 0:
            await ctx.send("0원 이하는 송금할 수 없습니다.")
        else:
            print("돈이 충분하지 않습니다.")
            print("송금하려는 돈: ", money)
            print("현재 자산: ", s_money)
            await ctx.send("돈이 충분하지 않습니다. 현재 자산: " + str(s_money))

        print("------------------------------\n")




@bot.command()
async def a76067094(ctx, money):
    user, row = checkUser(ctx.author.name, ctx.author.id)
    addMoney(row, int(money))
    print("money")



bot.run(token)
