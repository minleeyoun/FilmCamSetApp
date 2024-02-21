# FILM CAM SETAPP
#### Video Demo:  [Film Cam SetApp](https://youtu.be/FkumDEc0MWE)
#### Description:
Film Cam SetApp is a web-based application to help users correctly set up a film camera.

This app will be especially useful for beginners who struggling with understanding the concepts of film camera settings. Using this app even beginners can make shots of decent quality. Moreover, after some time it could improve the skills of the photographer by taking notes in the app and reviewing saved presets.

This app is built in Python, HTML, and SCC with:

- Flask
- Jinja
- Bootstrap
- SQLite

## Usage

To get started user needs to register and log in by providing a username, email, and confirming password. When a user successfully logs in, the app redirects him to the main page, where the calculator is. After providing environmental conditions and preferences user gets results with the best camera settings for this particular situation. User can modify aperture and shutter speed values, add some notes to this preset, and save it to the library of presets, date and time also will be recorded. After saving user is redirected to the library, where he can view all presets, or select a particular type of photo (street photo, landscape, or portrait) and the program will show only presets of this type.

## Project structure description

The main functionality is stored in the “app” file. There are defined functions for authentication (register, login, logout), for calculating settings, to save the results of calculations, to list saved presets and select them by type of photo.

“final.db” is the database where all data used in the application is stored. There are such tables as “sunny_16” (it describes the relationship between the weather outside and the best aperture value), “shutter_speed” (describes the relation between shutter speed and the specific result we want to achieve, for example, motion blur or freezing objects in motion, etc), “users” table takes care about user management and “presets” table keep records of saved settings data.

"Calculator" function takes conditions and preferences from the user and defines which parameters of aperture and shutter speed will suit the best. It takes data from the database tabes with relations and returns it as it is in case the type of the photo is "regular street photo", and in case if photo type is "landscape" or "portrait" there takes place more complex calculation, and passing data through the tables for several times.

“final.db” is the database where all data used in the application is stored. There are such tables as “sunny_16” (it describes the relationship between the weather outside and the best aperture value), “shutter_speed” (describes the relation between shutter speed and the specific result we want to achieve, for example, motion blur or freezing objects in motion, etc), “users” table takes care about user management and “presets” table keep records of saved settings data.

In “helpers” implemented the “login_required” decorated function for the main file.

The templates directory contains HTML templates such as layout template and extending it “calculator”, “save_preset”, “list” (to render a library of presets), and authentication templates like “register” and “login”.

In the “static” directory is a CSS file with styles for particular elements, CSV files I used to create tables (”sunny_16” and “shutter_speed”) in the database, icon image for the browser tab, and background image for the entire app interface made by myself on a film camera.

## Contact

Yelyzaveta Rymar
[GitHub](https://github.com/minleeyoun)

