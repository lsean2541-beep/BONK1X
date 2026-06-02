import os
import telebot
from gtts import gTTS
from flask import Flask
import threading

# Initialize Flask for Render web service port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "BonkXbot is running perfectly!"

# Fetch environment variables
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 10000))

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# Welcome & About Handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Welcome to Bonk1XBot! 🎤\n"
        "Send me any text, and I'll turn it into a voice message instantly. Try it now."
    )
    bot.reply_to(message, welcome_text)

# Text-to-Speech conversion logic
@bot.message_handler(func=lambda message: True)
def text_to_speech(message):
    # Ignore commands
    if message.text.startswith('/'):
        return

    # Let the user know the bot is working
    status_msg = bot.reply_to(message, "⏳ Converting your text to speech...")
    
    audio_path = f"tts_{message.message_id}.ogg"
    
    try:
        # Generate speech using gTTS
        tts = gTTS(text=message.text, lang='en', slow=False)
        tts.save(audio_path)
        
        # Send the audio file back as a native voice note
        with open(audio_path, 'rb') as audio:
            bot.send_voice(message.chat.id, audio, reply_to_message_id=message.message_id)
            
        # Clean up the status message
        bot.delete_message(message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error generating audio: {str(e)}", message.chat.id, status_msg.message_id)
        
    finally:
        # Local file cleanup to save Render disk space
        if os.path.exists(audio_path):
            os.remove(audio_path)

# Run Flask web server in a separate background thread
def run_flask():
    app.run(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable is missing!")
        exit(1)
        
    # Start web server thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("BonkXbot pulling for updates...")
    # Start bot polling loop
    bot.infinity_polling()
