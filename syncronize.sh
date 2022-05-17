cp "/home/andres/Insync/luis.andradec14@gmail.com/Google Drive/Projects/MemeBotDatabase/meme_bot_db (2).xlsx" ./data/meme_bot_db.xlsx
sshpass -p "kakaroto" rsync -a bot data pi@192.168.1.6:/home/pi/Projects/memeBot

