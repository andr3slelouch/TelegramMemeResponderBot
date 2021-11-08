cp "/home/andres/Insync/luis.andradec14@gmail.com/Google Drive/Projects/MemeBotDatabase/meme_bot_db.xlsx" ./data/
sshpass -p "YOUR PASSWORD" rsync -a bot data pi@"YOUR SERVER IP":/home/pi/Projects/memeBot

