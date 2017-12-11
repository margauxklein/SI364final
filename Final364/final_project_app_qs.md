# SI 364 - Final Project questions

## Overall



* **What's a one-two sentence description of what your app will do?**

## The Data

* **What data will your app use? From where will you get it? (e.g. scraping a site? what site? -- careful not to run it too much. An API? Which API?)**
•	Data will come from iTunes Books
* **What data will a user need to enter into a form?**
* **How many fields will your form have? What's an example of some data user might enter into it?**
•	Data to enter – username, give their email address – 2 fields
	→ Store it into the database
•	Another form – search for books on API that you have read
			-Form fields/input type:
-Enter a book separate by comma (text input)
-Enter what type of data they want to see – summary of book, reviews, rating (in a radio form)
After a user enters data into the form what happens? Does that data help a user search for more data? Does that data get saved in a database? 
			→ Make request to API for that data
			→ stores all data into database list, only show what user asks for 
		-search for books you want to read
			-enter a book separate by comma
			-Repeat steps above
			→ stores it into database

* **After a user enters data into the form, what happens? Does that data help a user search for more data? Does that data get saved in a database? Does that determine what already-saved data the user should see?**

Yes because books you inputted will be stored in database 

* **What models will you have in your application?**
* **What fields will each model have?**
o	Books (every title entered)
•		Author
o	Users
	•	Username
	•	Email
	•	Password – in order to change list
	•	Users have lists 
o	Lists of books
	•	Books they have read
	•	Books they want to read

* **What uniqueness constraints will there be on each table? (e.g. can't add a song with the same title as an existing song)**
-If two users enter the same book, do not need to save all the book’s data twice
-Only can have the same title once in Books table
- Unique username in user table

* **What relationships will exist between the tables? What's a 1:many relationship between? What about a many:many relationship?**
-A single book can be in many lists
-Two lists can have the same book
→ Many to many relationship

-Many:1 
→ one user can have many lists 

* **How many get_or_create functions will you need? In what order will you invoke them? Which one will need to invoke at least one of the others?**


Get_or_create 
-One per model
-Will be invoked in order above
-Need to invoke get or create list of books for users


## The Pages

* **How many pages (routes) will your application have?**

* **How many different views will a user be able to see, NOT counting errors?**

* **Basically, what will a user see on each page / at each route? Will it change depending on something else -- e.g. they see a form if they haven't submitted anything, but they see a list of things if they have?**

-1. Login form
-2. Users page – link to books they have already read, link to books they want to read – which do they want to edit 
-3. Route to books read
	-see all the books they have added
	-Includes form that allows them to add book
-For each book provide three links – link to review, link to summary and link to rating 
4. route to books they want to read
	-See all the books added to this list
	-includes form that allows them to add book
 -For each book provide three links – link to review, link to summary and link to rating
 -4 views and 4 routes
-error if they do not enter a proper book title – 405 and 404



## Extras

* **Why might your application send email?**

* **If you plan to have user accounts, what information will be specific to a user account? What can you only see if you're logged in? What will you see if you're not logged in -- anything?**

* **What are your biggest concerns about the process of building this application?**
-Send them a link to buy book on Itunes whenever they submit a new book to the want to read list (if user wants)

user accounts
-Only you can edit your lists
-Only you can view your lists
-If you are not logged in you cannot see anything




