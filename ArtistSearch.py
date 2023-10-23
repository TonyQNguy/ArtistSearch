# Tony Nguyen - Music Player with Spotify API Implementation

# libraries used for spotify API
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

# libraries used for displaying the album covers
import pygame
import requests
from io import BytesIO

#------------------------------------------------------------------------------------------------------------------------

pygame.init()
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# token and authentication functions
def getToken():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = { 
        "Authorization": "Basic " + auth_base64,
        "Content-Type":  "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def getAuthHeader(token):
    return {"Authorization": "Bearer " + token}

# query functions
def searchArtist(token, artistName):
    url =  "https://api.spotify.com/v1/search"
    headers = getAuthHeader(token)
    query = f"?q={artistName}&type=artist&limit=1" #artistName is what I am searching for, type=artist limits what we are looking for,limit=1 gives the top artist
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No Artist Found") 
        return None
    
    return json_result[0]

def getSongsByArtist(token, artist_id): 
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = getAuthHeader(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    topNineSongs = json_result[:9]
    return topNineSongs

def getAlbum(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?country=US"
    headers = getAuthHeader(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result
    
def getAlbumCovers(userinput):

    # setting up the display
    screen_width, screen_height = 600, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Image Display')

    token = getToken()
    result = searchArtist(token, userinput)
    artist_id = result["id"]

    songs = getSongsByArtist(token, artist_id)

    print("Top 9 Songs By:", userinput)
    print('-------------------------------')

    image_urls = []
    for idx, song in enumerate(songs):
        album_name = song['album']['name']
        album_image = song['album']['images'][0]['url']
        print(f"{idx + 1}. {song['name']}")
        print(f"Album: {album_name}")
        print('-------------------------------')
        image_urls.append(album_image) # adding the urls to a list

    # adding images to the display
    images = []
    for url in image_urls:
        response = requests.get(url)
        img_data = BytesIO(response.content)
        image = pygame.image.load(img_data).convert()
        image = pygame.transform.scale(image, (200, 200)) # scales the image down to 200 x 200
        images.append(image)

    # setting variables for the spacing between images, the number of columns, and size of each image
    grid_spacing = 0 # spacing between images in the grid
    num_cols = 3  # number of columns in the grid
    image_width, image_height = 200, 200 # image width and height

    # calculates the grid dimensions based on the number of images and columns
    grid_width = num_cols * (image_width + grid_spacing)
    grid_height = image_height * 3

    # calculates the starting position to center the grid on the screen
    start_x = (screen_width - grid_width) // 2
    start_y = (screen_height - grid_height) // 2

    # Runs the pygame window
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Clear the screen

        # Display images in the grid
        for i, image in enumerate(images):
            row = i // num_cols
            col = i % num_cols
            x = start_x + col * (image_width + grid_spacing)
            y = start_y + row * (image_height + grid_spacing)
            screen.blit(image, (x, y))

        # Update the display
        pygame.display.flip()

# program runner
def runProgram():
    print()
    userinput = input("Enter an artist: ")
    getAlbumCovers(userinput)

runProgram()




