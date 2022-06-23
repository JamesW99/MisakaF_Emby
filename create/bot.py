from typing import NoReturn
from time import sleep
from asyncio import sleep
import requests
import re

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text('请输入：/create + 用户名 来注册\n\n例如通过发送"/create helloworld"来注册一个用户名为helloworld的账号\n\n使用： /help 获取帮助')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    chat_id = update.message.chat_id
    update.message.reply_text('chatid:' + str(chat_id) + '\n\n创建账号：/create + 用户名\ne.g：/create helloworld\n\n重置密码：/reset\n\n查询账号信息：/info')


def info(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    file = open('/home/ubuntu/projects/MisakaF_Emby/create/accounts.txt',"r")
    accounts = file.read().splitlines()
    file.close()
    for account in accounts:
        accountss = account.split(' ')
        if(str(chat_id) == accountss[0]):
            userid = accountss[1]
    headers = {
        'accept': 'application/json',
    }

    params = {
        'api_key': 'REPLACE TO YOUR EMBY API',
    }
    response = requests.get('REPLACE TO YOUR EMBY ADDRESS/emby/Users/' + userid, params=params, headers=headers)
    responsejson = response.json()
    name = responsejson['Name']
    createdate = responsejson['DateCreated']
    try:
        lastlogin = responsejson['LastLoginDate']
    except:
        lastlogin = "未登录"
    update.message.reply_text('Emby用户名：' + name + '\n\n注册时间：' + createdate + '\n\n上一次登录时间：' + lastlogin +"\n\n地址：https://emby.ywang.cf:443")
    

def create(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    names = text.split(' ')
    try:
        name = names[1]
    except:
        update.message.reply_text('请输入：/create + 用户名 + 邀请码 来注册\n\n例如通过发送"/create helloworld xxxxxx"来注册一个用户名为helloworld的账号\n\n使用： /help 获取帮助')
    print(names)

    try:
        check_invited = invited(names[2])
    except:
        check_invited = False

    if(check_invited==False):
        update.message.reply_text("请输入正确的邀请码")
        return


    chat_id = update.message.chat_id
    try:
        username = update.message.from_user.username
    except:
        username = "didnt get username!"
    try:
        first_name = update.message.chat.first_name
    except:
        first_name = 'None'
    try:
        last_name = update.message.chat.last_name
    except:
        last_name = "None"

    


    showname = str(first_name + '_'+ last_name)
    print(showname)
    judge_back = judge(chat_id)
    if(judge_back == 1):
        update.message.reply_text('你的账号已经注册过Emby了！')
    elif(judge_back == 0):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        params = (
                    ('api_key', 'REPLACE TO YOUR EMBY API'),
                )

        data = '{"Name":"'+name+'","HasPassword":true}'

        response = requests.post('REPLACE TO YOUR EMBY ADDRESS/emby/Users/New', headers=headers, params=params, data=data)

        status1 = response.status_code
        if(response != '' and status1 == 200):

            id1=re.findall(r'\"(.*?)\"',response.text)
            id=id1[9]

            headers1 = {
                            'accept': '*/*',
                            'Content-Type': 'application/json',
                        }

            params1 = (
                        ('api_key', 'REPLACE TO YOUR EMBY API'),
                    )

            data1 = '{"IsAdministrator":false,"IsHidden":true,"IsHiddenRemotely":true,"IsDisabled":false,"EnableRemoteControlOfOtherUsers":false,"EnableSharedDeviceControl":false,"EnableRemoteAccess":true,"EnableLiveTvManagement":false,"EnableLiveTvAccess":true,"EnableMediaPlayback":true,"EnableAudioPlaybackTranscoding":false,"EnableVideoPlaybackTranscoding":false,"EnablePlaybackRemuxing":false,"EnableContentDeletion":false,"EnableContentDownloading":false,"EnableSubtitleDownloading":false,"EnableSubtitleManagement":false,"EnableSyncTranscoding":false,"EnableMediaConversion":false,"EnableAllDevices":true}'

            requests.post('REPLACE TO YOUR EMBY ADDRESS/emby/Users/'+id+'/Policy', headers=headers1, params=params1, data=data1)

            update.message.reply_text('注册用户名：' + name)
            f = open('/home/ubuntu/projects/MisakaF_Emby/create/accounts.txt', 'a')
            f.write(str(chat_id) + ' ' + id + ' ' + str(username) + ' ' + showname +'\n')
            #  + ' ' + showname
            print('注册用户名：', name, 'username: ', username, 'showname: ', showname)
            f.close()
        elif(status1 == 400):
            update.message.reply_text(response.text)
        else:
            update.message.reply_text('未知错误，请联系TG频道管理员！')


def reset(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    check = judge(chat_id)
    # print(chat_id, check)
    if(check == 0):
        update.message.reply_text('你还未注册过Emby公益服，请先注册！')
    elif(check == 1):
        check3 = passwd(chat_id)
        if(check3 == 1):
            update.message.reply_text('密码移除成功，现密码为空！')
        else:
            update.message.reply_text('未知错误，请联系管理人员解决！')




def nametoid(name):
    headers = {
    'accept': 'application/json',
    }

    params = {
        'IsHidden': 'true',
        'IsDisabled': 'false',
        'Limit': '1',
        'NameStartsWithOrGreater': name,
        'api_key': 'REPLACE TO YOUR EMBY API',
    }

    response = requests.get('REPLACE TO YOUR EMBY ADDRESS/emby/Users/Query', params=params, headers=headers)
    responsejson = response.json()
    id = responsejson['Items'][0]['Id']
    return id


def idtoname(chatid):
    file = open('/home/ubuntu/projects/MisakaF_Emby/create/accounts.txt',"r")
    accounts = file.read().splitlines()
    file.close()
    for account in accounts:
        accountss = account.split(' ')
        if(str(chatid) == accountss[0]):
            userid = accountss[1]
    headers = {
    'accept': 'application/json',
    }

    params = {
        'api_key': 'REPLACE TO YOUR EMBY API',
    }
    response = requests.get('REPLACE TO YOUR EMBY ADDRESS/emby/Users/' + userid, params=params, headers=headers)
    responsejson = response.json()
    name = responsejson['Name']
    return name


def judge(chat_id):
    file = open('/home/ubuntu/projects/MisakaF_Emby/create/accounts.txt',"r")
    kk = 0
    accounts = file.read().splitlines()
    file.close()
    for account in accounts:
        accountss = account.split(' ')
        if(str(chat_id) == accountss[0]):
            kk = 1
    return kk

def invited(checkCode):
    file = open('/home/ubuntu/projects/MisakaF_Emby/create/invited.txt',"r")
    codes = file.read().splitlines()
    file.close()
    
    for code in codes:
        if(code == checkCode):
            delete(checkCode)
            return True
    return False


def delete(target):
    with open("/home/ubuntu/projects/MisakaF_Emby/create/invited.txt","r",encoding="utf-8") as f:
        lines = f.readlines()
    with open("/home/ubuntu/projects/MisakaF_Emby/create/invited.txt","w",encoding="utf-8") as f_w:
        for line in lines:
            if target in line:
                continue
            f_w.write(line)


def passwd(chat_id):
    check = 0
    file = open('/home/ubuntu/projects/MisakaF_Emby/create/accounts.txt',"r")
    accounts = file.readlines()
    file.close()
    for account in accounts:
        accountss = account.split(' ')
        if(str(chat_id) == accountss[0]):
            userid=accountss[1]
            headers = {
                'accept': '*/*',
            }

            params = {
                'api_key': 'REPLACE TO YOUR EMBY API',
            }

            json_data = {
                'ResetPassword': True,
            }

            response = requests.post('REPLACE TO YOUR EMBY ADDRESS/emby/Users/'+userid+'/Password', params=params, headers=headers, json=json_data)
            status2 = response.status_code
            if(status2 == 204):
                check = 1
    return check


def hello(update: Update, context: CallbackContext) -> None:
    try:
        first_name = update.message.chat.first_name
    except:
        first_name = 'None'
    try:
        last_name = update.message.chat.last_name
    except:
        last_name = "None"
    showname = str('hello ' + first_name + '_'+ last_name)
    # print(showname)
    update.message.reply_text( showname)


def main() -> None:
    """Start the bot."""

    updater = Updater("Telegram BOT API")
    
    dispatcher = updater.dispatcher

    # 机器人命令
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("create", create))
    dispatcher.add_handler(CommandHandler("reset", reset))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("hello", hello))
    

    # 启动机器人，勿删
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
