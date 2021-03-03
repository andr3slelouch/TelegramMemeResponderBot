cp "/home/andres/Insync/luis.andradec14@gmail.com/Google Drive/Projects/MemeBotDatabase/meme_bot_db.xlsx" ./data/
sshpass -p "kakaroto" rsync -a bot data pi@10.42.0.1:/home/pi/Projects/memeBot
