## Capstone 1: Proposal

### SaferSexNYC

**1. What goal will your website be designed to achieve?**

> The goal of this website is to connect users with locations that provide free "safer sex" products within the five boroughs of New York City.

**2. What kind of users will visit your site? In other words, what is the demographic of your users?**

> The target demographic for this website is anyone living in or visiting New York City who may wish to find free access to safer sex products.

**3. What data do you plan on using? You may have not picked your actual API yet, which is fine, just outline what kind of data you would like it to contain.**

> The data for this project will be based on _NYC OpenData API / NYC Condom Availability Program - HIV condom distribution locations_ at "https://dev.socrata.com/foundry/data.cityofnewyork.us/4kpn-sezh". From this dataset, locations are defined with unique identifiers and each instance includes product availability, location information (address, hours, etc.). Other data used by the website will include user data (username, names, emails, passwords), user comments, and private user notes. Ideally, this website will also use embeded map data from an external source such as Google Maps.

**4. In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:**  
 **a. What does your database schema look like?**  
 ![database schema](<QuickDBD-export%20(5).png>)

> The schema will include several internal tables that connect user data with the data located at the external database.

**b. What kinds of issues might you run into with your API?**

> The biggest issues I can anticipate with the API at this time involve missing data. All of the sample requests I have tried produce the results I am hoping for. The database appears to be updated daily, so I am fairly confident that the data is well-maintained.

**c. Is there any sensitive information you need to secure?**

> User passwords will need to be stored securely.

**d. What functionality will your app include?**

> The web application will allow users to search for distribution locations based on input criteria (i.e. zip code, "open now" [this will require some datetime work and comparison to the open hours listed in the API], specific product availabilty [each location has boolean values for male condoms, female condoms, and lubricant]). From search results users will be able to access further location details (hopefully with map functionality), save locations to "favorites", make private notes about a location, and make public comments to be shared between users about a location. The users profile will make suggestions for nearby locations if a user saves a zip code to their preferences. Each location page will also make suggestions for similar locations based on zip code and product availibility.

**e. What will the user flow look like?**

> Users will be able to access the search features of the website without creating a user account. If a user wishes to save notes, save favorites, or make public comments, they must create an account and be logged in.

**f. What features make your site more than CRUD? Do you have any stretch goals?**

> The recommendation features (i.e. "similar" locations) make this website more than CRUD because they analyze the criteria of a specific location to produce similar results. My largest stretch goal is to include the map functionality that will allow users to see the location and generate directions. I have looked into Google Maps and it appears this functionality is still free, but this will require further research.

**OTHER THOUGHTS/NOTES**

> I believe I have worked out the logistics of using the external API data without being able to use foreign key constraints and relationships on the facilityID - from my understanding this will require using unique IDs (primary keys) for each association and using those keys for querying the API. For instance, in order to obtain a user's saved favorite locations, I will need to access internal database information "WHERE username == username" and from that resulting data will need to send the API a 'GET' request where facilityID is "in [list of faciltyIDs]". This will result in user information and "favorites" information being passed to the template page separately since the user object will not be able to directly reference locations.
