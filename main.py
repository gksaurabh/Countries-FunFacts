import openai
import os
from dotenv import load_dotenv, dotenv_values
from flask import Flask, render_template
import requests
from dotenv import load_dotenv


load_dotenv()



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/countries')
def countries():
    countries_api = "https://restcountries.com/v3.1/all"
    response = requests.get(countries_api)
    countries = response.json()
    return render_template('countries.html', countries=countries)

@app.route('/country/<name>')
def country_details(name):
    # Fetch country details from REST Countries API
    rest_countries_api = f"https://restcountries.com/v3.1/name/{name}"
    response = requests.get(rest_countries_api)
    
    if response.status_code == 200:
        country_data = response.json()
        country = country_data[0]

        # Debugging: Ensure we get the country name correctly
        print(f"Generating history for {country['name']['common']}")

        # Generate detailed history for the country using OpenAI
        detailed_history = generate_country_history(country['name']['common'])

        # Debugging: Ensure we get the history back from OpenAI
        print(f"History for {country['name']['common']}: {detailed_history[:100]}...")

        # Pass the detailed history to the template
        return render_template('country_details.html', country=country, detailed_history=detailed_history)
    else:
        return f"Country data for {name} not found", 404

def generate_country_history(country_name):
    # Define the prompt to generate the history
    prompt = (f"Write a detailed 500-word history about {country_name}. "
              "Include important events, cultural evolution, economic development, "
              "and political changes that shaped the country.")

    try:
        # Call OpenAI API to generate history using the gpt-3.5-turbo model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a historian."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,  # Approximate 500 words
            temperature=0.7  # Control the creativity of the response
        )

        # Extract the generated text from the response
        history_text = response['choices'][0]['message']['content'].strip()
        return history_text

    except openai.error.OpenAIError as e:
        # Handle specific OpenAI errors
        print(f"OpenAI API Error: {e}")
        return f"An error occurred while generating history for {country_name}. OpenAI Error: {e}"

    except Exception as e:
        # Handle any other errors
        print(f"General error: {e}")
        return f"An error occurred while generating history for {country_name}. General Error: {e}"


@app.route('/news') 
def news():
    news_api_key = "YOUR_NEWS_API_KEY"
    news_url = f"https://newsapi.org/v2/top-headlines?sources=bbc-news,cnn,al-jazeera-english&apiKey={news_api_key}"
    response = requests.get(news_url)
    news_data = response.json()

    headlines = [article['title'] for article in news_data['articles'][:5]]
    generated_images = []

    for headline in headlines:
        image = generate_image_from_text(headline)
        generated_images.append({'headline': headline, 'image_url': image})

    return render_template('news.html', headlines=generated_images)

def generate_image_from_text(text):
    # Use OpenAI or any AI Image Generator API
    
    response = openai.Image.create(prompt=text, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    return image_url

if __name__ == '__main__':
    app.run(debug=True)
