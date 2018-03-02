README - Jack LaRue (ID: jvl13)
Week of March 2nd (Week 2)

Tasks (reverse-chronological order):

-Sketched outline for dropdown button in Conflicts section (i.e. to select preferred file).

-Implemented partial body functionality for “Conflicts” and “Requested Changes” sections (i.e. users can now click accept/decline change buttons, although they have not been hooked up to useful functions yet).

-Made it so that the UI differentiates between owner and subscribed drops (i.e. clicking on a subscribed drop will only display relevant subscriber buttons, likewise for owner drops).

-Added skeleton functions for each of the buttons, each outlining their functionality once we begin working on backend-to-frontend communication.

-Created buttons specifically for the owner drop toolbar (i.e. Conflicts\Add Files buttons, etc.)

Modified Files:
-frontend/frontend/frontend.py
-frontend/frontend/static/style.css
-frontend/frontend/templates/layout.html
-frontend/frontend/templates/show_drops.html
-frontend/tests/test_frontend.py

Documentation:

This week was my first exposure to both HTML5 and CSS, so I spent a decent amount of time both reading and getting used to the syntax. Besides that, I was tasked with implementing the buttons for owned drops, as well as some of the interior functionality of said buttons (specifically for the “Conflicts” and “Requested Changes” buttons). The buttons have been set up, and a decent portion of the interior functionality for said buttons have been implemented. I plan on finishing this within the upcoming week.

***Important note: one of the commits added a fair amount of code (~40 lines) to the style.css file on my branch prior to merging with the master branch. To clarify, that code was from Alex (it helped with implementing buttons in the interior functionality of both Conflicts and Requested Changes” sections). My changes to style.css were for implementing dropdown buttons.
