import requests
from functions.online_ops import find_my_ip, get_latest_news, get_random_advice, get_random_joke, get_trending_movies, get_weather_report, play_on_youtube, search_on_google, search_on_wikipedia, send_email, send_whatsapp_message
from functions.school_ops import school_mode
import speech_recognition as sr
from decouple import config
from datetime import datetime
from functions.os_ops import open_calculator, open_camera, open_cmd, open_notepad, open_discord, open_application
from random import choice
from utils import opening_text, conversation_responses
from pprint import pprint
import os
from pathlib import Path
import webbrowser
import re
import threading
import sys
from PyQt5.QtWidgets import QApplication
from jarvis_ui import launch_ui
import json
from urllib.request import urlopen

USERNAME = config('USER')
BOTNAME = config('BOTNAME')
ELEVENLABS_API_KEY = "sk_94030f3a08a24a9d11ffe8b6d715063b71b62658fe0859c6"

# Set ElevenLabs API key
os.environ["ELEVEN_API_KEY"] = ELEVENLABS_API_KEY

# Global variables
running = False
comm_channel = None

def speak(text):
    """
    Text to speech using ElevenLabs API
    """
    # Update UI status to speaking
    if comm_channel:
        comm_channel.update_status("speaking")
        comm_channel.add_message(text, "assistant")
    
    try:
        print(f"Generating speech for: {text}")
        
        # Create API endpoint URL
        url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"  # Adam's voice ID
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.71,
                "similarity_boost": 0.5
            }
        }
        
        print("Requesting audio from ElevenLabs...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Save audio to file
            temp_file = "temp_audio.mp3"
            with open(temp_file, "wb") as f:
                f.write(response.content)
            
            # Play the audio using mpg123
            print("Playing audio...")
            os.system(f'mpg123 "{temp_file}"')
            
            # Clean up
            os.remove(temp_file)
        else:
            print(f"Error from ElevenLabs API: {response.status_code}")
            print(response.text)
            if comm_channel:
                comm_channel.add_message(f"Error from speech service: {response.status_code}", "error")
            
    except Exception as e:
        print(f"Error with ElevenLabs: {str(e)}")
        print(f"Assistant: {text}")
        if comm_channel:
            comm_channel.add_message(f"Speech error: {str(e)}", "error")
    
    # Set status back to idle or listening
    if comm_channel:
        if running:
            comm_channel.update_status("listening")
        else:
            comm_channel.update_status("idle")

def take_user_input():
    """Takes user input, recognizes it using Speech Recognition module and converts it into text"""
    
    if comm_channel:
        comm_channel.update_status("listening")
    
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print('Listening....')
            # Adjust the recognizer sensitivity to ambient noise
            r.dynamic_energy_threshold = True  # Automatically adjust for ambient noise
            r.energy_threshold = 4000  # Increase energy threshold for better noise filtering
            r.pause_threshold = 0.8  # Reduce pause threshold for faster response
            r.phrase_threshold = 0.3  # Minimum seconds of speaking needed
            r.non_speaking_duration = 0.5  # How long is silence before we stop listening
            
            # Adjust microphone for ambient noise
            print("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            
            try:
                print("Now listening...")
                # Increased timeout and phrase time limit
                audio = r.listen(source, 
                               timeout=7,  # Wait longer for speech to start
                               phrase_time_limit=10,  # Allow longer phrases
                               )
            except sr.WaitTimeoutError:
                speak("I didn't hear anything. Could you please speak again, sir?")
                return "timeout"
            
        try:
            if comm_channel:
                comm_channel.update_status("processing")
                
            print('Recognizing...')
            # Use a more accurate recognition setting
            query = r.recognize_google(audio, 
                                    language='en-in',
                                    show_all=False)  # Get the most confident result
            print(f'User said: {query}\n')
            
            if comm_channel:
                comm_channel.add_message(query, "user")
                
            return query.lower()
        except sr.UnknownValueError:
            speak("I apologize, but I couldn't understand what you said. Could you please repeat that, sir?")
            return "none"
        except sr.RequestError:
            speak("I'm having trouble with my speech recognition service. Please try again in a moment.")
            return "none"
    except KeyboardInterrupt:
        print("\nStopping voice assistant...")
        return "exit"
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if comm_channel:
            comm_channel.add_message(f"Input error: {str(e)}", "error")
        return "none"

def get_reliable_weather(location="Leander,Texas"):
    """Get weather data using a more reliable free API for a specific location"""
    try:
        # Using wttr.in which is more reliable and doesn't require API keys
        # Encode the location for URL
        encoded_location = location.replace(" ", "+")
        response = requests.get(f"https://wttr.in/{encoded_location}?format=j1", timeout=10)
        
        if response.status_code == 200:
            weather_data = response.json()
            current = weather_data["current_condition"][0]
            
            # Extract the data we need
            weather_desc = current["weatherDesc"][0]["value"]
            temp_c = current["temp_C"]
            temp_f = current["temp_F"]  # Adding Fahrenheit for US locations
            feels_like = current["FeelsLikeF"] + "°F"  # Using Fahrenheit for US
            
            # Get location info
            location = weather_data["nearest_area"][0]
            city = location["areaName"][0]["value"]
            region = location["region"][0]["value"]
            country = location["country"][0]["value"]
            
            return {
                "success": True,
                "city": city,
                "region": region,
                "country": country,
                "weather": weather_desc,
                "temperature": f"{temp_f}°F",
                "feels_like": feels_like
            }
    except Exception as e:
        print(f"Weather API error: {str(e)}")
    
    # Fallback to another API if the first one fails
    try:
        # Using another free API as backup
        response = requests.get(f"https://goweather.herokuapp.com/weather/{location}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "city": "Leander",
                "region": "Texas",
                "country": "United States",
                "weather": data.get("description", "unknown"),
                "temperature": data.get("temperature", "unknown"),
                "feels_like": data.get("temperature", "unknown")  # This API doesn't provide feels like
            }
    except Exception as e:
        print(f"Backup weather API error: {str(e)}")
    
    # Return default values if all APIs fail
    return {
        "success": False,
        "city": "Leander",
        "region": "Texas",
        "country": "United States",
        "weather": "unknown",
        "temperature": "unknown",
        "feels_like": "unknown"
    }

def greet_user():
    """Greets the user according to the time and provides weather information"""
    hour = datetime.now().hour
    current_time = datetime.now().strftime("%I:%M %p")
    
    # Get weather information using our reliable function
    weather_data = get_reliable_weather("Leander,Texas")
    
    if weather_data["success"]:
        weather_info = f"The current temperature in {weather_data['city']}, {weather_data['region']} is {weather_data['temperature']}, and it feels like {weather_data['feels_like']}. The weather is {weather_data['weather']}."
    else:
        weather_info = "I apologize, but I couldn't fetch the weather information for Leander, Texas at the moment."
    
    # Morning greeting
    if hour >= 0 and hour < 12:
        speak(f"Good morning {USERNAME} Sir! The time is {current_time}. {weather_info}")
    # Afternoon greeting
    elif hour >= 12 and hour < 16:
        speak(f"Good afternoon {USERNAME} Sir! The time is {current_time}. {weather_info}")
    # Evening greeting
    elif hour >= 16 and hour < 19:
        speak(f"Good evening {USERNAME} Sir! The time is {current_time}. {weather_info}")
    # Night greeting
    else:
        speak(f"Good night {USERNAME} Sir! The time is {current_time}. {weather_info}")
    
    speak("How may I assist you today?")

def handle_conversation(query):
    """Handles conversational queries that don't require specific actions"""
    
    # Check for greetings
    if any(phrase in query for phrase in ["hello", "hi", "hey", "greetings"]):
        speak(choice(conversation_responses["greetings"]))
        return True
        
    # Check for how are you type questions
    elif any(phrase in query for phrase in ["how are you", "how's it going", "how do you do", "how are things"]):
        speak(choice(conversation_responses["how_are_you"]))
        return True
        
    # Check for what can you do questions
    elif any(phrase in query for phrase in ["what can you do", "help me", "your abilities", "your features"]):
        speak(choice(conversation_responses["capabilities"]))
        return True
        
    # Check for thank you responses
    elif any(phrase in query for phrase in ["thank you", "thanks", "appreciate it"]):
        speak(choice(conversation_responses["thanks"]))
        return True
        
    # Check for who are you questions
    elif any(phrase in query for phrase in ["who are you", "what are you", "what's your name"]):
        speak(choice(conversation_responses["identity"]).format(BOTNAME=BOTNAME, USERNAME=USERNAME))
        return True
        
    # Check for time-related questions
    elif any(phrase in query for phrase in ["what time is it", "what's the time", "tell me the time"]):
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}, sir.")
        return True
        
    # Check for date-related questions
    elif any(phrase in query for phrase in ["what date is it", "what's the date", "tell me the date"]):
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {current_date}, sir.")
        return True
    
    # If no conversational patterns matched
    return False

def extract_app_name(query):
    """Extract application name from the query"""
    # Pattern to match "open X" or "launch X" or "start X"
    match = re.search(r'open\s+(.+)|launch\s+(.+)|start\s+(.+)', query)
    if match:
        # Get the first non-None group
        app_name = next((group for group in match.groups() if group is not None), "")
        return app_name.strip()
    return None

def start_assistant():
    """Start the assistant in a separate thread"""
    global running
    if running:
        return  # Already running
        
    running = True
    thread = threading.Thread(target=assistant_thread)
    thread.daemon = True  # Make thread exit when main program exits
    thread.start()

def stop_assistant():
    """Stop the assistant"""
    global running
    running = False
    if comm_channel:
        comm_channel.update_status("idle")
        comm_channel.add_message("Assistant stopped", "status")

def assistant_thread():
    """Main assistant thread that handles voice commands"""
    global running
    
    if comm_channel:
        comm_channel.add_message("Starting Jarvis...", "status")
    
    greet_user()
    
    while running:
        try:
            query = take_user_input()
            
            # Check if we should exit
            if query == "exit" or "stop" in query:
                speak("Goodbye! Have a great day!")
                running = False
                break
                
            # Skip if no valid input
            elif query == "none" or query == "timeout":
                continue
                
            # Process the query
            else:
                # First try to handle it as a conversation
                if handle_conversation(query):
                    continue
                    
                # Then check for specific commands
                if "school mode" in query.lower():
                    speak("Activating school mode. I'll check your emails and Google Classroom assignments.")
                    result = school_mode()
                    
                    if result['success']:
                        speak(f"I found {result['email_count']} new emails and {result['assignment_count']} pending assignments.")
                        speak("I've created a detailed summary document for you.")
                        speak("Would you like me to open the document?")
                        
                        response = take_user_input()
                        if response and ("yes" in response.lower() or "sure" in response.lower() or "okay" in response.lower()):
                            webbrowser.open(result['doc_url'])
                            speak("I've opened the summary document in your browser.")
                    else:
                        speak(f"I encountered an error: {result['error']}")
                        speak("Please make sure you have set up your Google credentials correctly.")
                
                elif 'open notepad' in query:
                    speak("Opening Notepad for you.")
                    open_notepad()

                elif 'open discord' in query:
                    speak("Opening Discord for you.")
                    open_discord()

                elif 'open command prompt' in query or 'open cmd' in query:
                    speak("Opening Command Prompt for you.")
                    open_cmd()

                elif 'open camera' in query:
                    speak("Opening Camera for you.")
                    open_camera()

                elif 'open calculator' in query:
                    speak("Opening Calculator for you.")
                    open_calculator()
                    
                # General app opening functionality
                elif any(phrase in query for phrase in ["open ", "launch ", "start "]):
                    app_name = extract_app_name(query)
                    if app_name:
                        speak(f"Opening {app_name} for you, sir.")
                        success = open_application(app_name)
                        if not success:
                            speak(f"I couldn't find the application {app_name}. Would you like me to search for it online?")
                            response = take_user_input()
                            if response and ("yes" in response.lower() or "sure" in response.lower()):
                                search_on_google(f"{app_name} download mac")
                                speak(f"I've searched for {app_name} online for you.")

                elif 'ip address' in query:
                    ip_address = find_my_ip()
                    speak(f'Your IP Address is {ip_address}.\n For your convenience, I am printing it on the screen sir.')
                    print(f'Your IP Address is {ip_address}')

                elif 'wikipedia' in query:
                    speak('What do you want to search on Wikipedia, sir?')
                    search_query = take_user_input().lower()
                    if search_query not in ["none", "timeout", "exit"]:
                        results = search_on_wikipedia(search_query)
                        speak(f"According to Wikipedia, {results}")
                        speak("For your convenience, I am printing it on the screen sir.")
                        print(results)

                elif 'youtube' in query:
                    speak('What do you want to play on Youtube, sir?')
                    video = take_user_input().lower()
                    if video not in ["none", "timeout", "exit"]:
                        play_on_youtube(video)

                elif 'search on google' in query:
                    speak('What do you want to search on Google, sir?')
                    search_query = take_user_input().lower()
                    if search_query not in ["none", "timeout", "exit"]:
                        search_on_google(search_query)

                elif "send whatsapp message" in query:
                    speak('On what number should I send the message sir? Please enter in the console: ')
                    number = input("Enter the number: ")
                    speak("What is the message sir?")
                    message = take_user_input().lower()
                    if message not in ["none", "timeout", "exit"]:
                        send_whatsapp_message(number, message)
                        speak("I've sent the message sir.")

                elif "send an email" in query:
                    speak("On what email address do I send sir? Please enter in the console: ")
                    receiver_address = input("Enter email address: ")
                    speak("What should be the subject sir?")
                    subject = take_user_input().capitalize()
                    if subject not in ["none", "timeout", "exit"]:
                        speak("What is the message sir?")
                        message = take_user_input().capitalize()
                        if message not in ["none", "timeout", "exit"]:
                            if send_email(receiver_address, subject, message):
                                speak("I've sent the email sir.")
                            else:
                                speak("Something went wrong while I was sending the mail. Please check the error logs sir.")

                elif 'joke' in query:
                    speak(f"Hope you like this one sir")
                    joke = get_random_joke()
                    speak(joke)
                    speak("For your convenience, I am printing it on the screen sir.")
                    pprint(joke)

                elif "advice" in query:
                    speak(f"Here's an advice for you, sir")
                    advice = get_random_advice()
                    speak(advice)
                    speak("For your convenience, I am printing it on the screen sir.")
                    pprint(advice)

                elif "trending movies" in query:
                    speak(f"Some of the trending movies are: {get_trending_movies()}")
                    speak("For your convenience, I am printing it on the screen sir.")
                    print(*get_trending_movies(), sep='\n')

                elif 'news' in query:
                    speak(f"I'm reading out the latest news headlines, sir")
                    speak(get_latest_news())
                    speak("For your convenience, I am printing it on the screen sir.")
                    print(*get_latest_news(), sep='\n')

                elif 'weather' in query:
                    weather_data = get_reliable_weather("Leander,Texas")
                    
                    if weather_data["success"]:
                        speak(f"Getting weather report for {weather_data['city']}, {weather_data['region']}")
                        speak(f"The current temperature is {weather_data['temperature']}, but it feels like {weather_data['feels_like']}")
                        speak(f"Also, the weather report talks about {weather_data['weather']}")
                        speak("For your convenience, I am printing it on the screen sir.")
                        print(f"Location: {weather_data['city']}, {weather_data['region']}, {weather_data['country']}")
                        print(f"Description: {weather_data['weather']}")
                        print(f"Temperature: {weather_data['temperature']}")
                        print(f"Feels like: {weather_data['feels_like']}")
                    else:
                        speak("I apologize, but I couldn't fetch the weather information for Leander, Texas at the moment.")
                        speak("This might be due to network issues or API limitations.")
                
                # If no specific command matched, try to provide a helpful response
                else:
                    speak("I'm not sure how to help with that. Would you like me to search for information about it online?")
                    response = take_user_input()
                    if response and ("yes" in response.lower() or "sure" in response.lower()):
                        search_on_google(query)
                        speak(f"I've searched for information about '{query}' online for you.")
        except KeyboardInterrupt:
            speak("Goodbye! Have a great day!")
            running = False
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            if comm_channel:
                comm_channel.add_message(f"Error: {str(e)}", "error")
            continue

def main():
    """Main function to start the application"""
    global comm_channel
    
    # Initialize UI
    app, window, comm = launch_ui()
    comm_channel = comm
    
    # Connect UI buttons to assistant functions
    window.wake_button.clicked.connect(start_assistant)
    window.stop_button.clicked.connect(stop_assistant)
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
