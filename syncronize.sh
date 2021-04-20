cp "/home/andres/Insync/luis.andradec14@gmail.com/Google Drive/Projects/MemeBotDatabase/meme_bot_db.xlsx" ./data/
sshpass -p "kakaroto" rsync -a bot data pi@192.168.1.4:/home/pi/Projects/memeBot
