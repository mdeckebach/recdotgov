# Goal
Build something that can systematically pull overnight backcountry permit data (starting w/ just Inyo National Forest, as that's what I care most about) from Recreation.gov. Take that data and create a database so I can track how permits are bought up and released over time. I might also be able to use the script to automate alerts whenever a desireable permit becomes available.

In the process, I wanted to learn:
- How to pull data from the web, ideally via API and not via webscraping
- How to set up some sort of personal database that I could write to
- How to write data to a database via script
- How to host and schedule the job on a recurring basis via my NAS
- Python

# Discovery
I started by looking for a publicly available API. I found RIDB API (https://ridb.recreation.gov/docs), which at first I thought would be super promising. However, the /reservations endpoint appears to no longer be functioning, and it appears to contain the necessary information.

I did a bit of poking around the Inyo Backcountry Permit page itself, wondering if maybe I would find any calls that might contain the data I need. Somehow, availability is getting to the webpage! I got the idea from this article, which was doing something similar with campsite avilability: https://emery-44439.medium.com/how-find-openings-in-rec-gov-campsites-using-dart-and-aws-lambda-9bfe3fe29369.

Inspecting the webpage (https://www.recreation.gov/permits/233262/registration/detailed-availability?date=2024-09-18&type=overnight-permit) with Developer Tools, I combed through the network traffic and found two promising API calls:

1. https://www.recreation.gov/api/permitinyo/233262/availabilityv2?start_date=2024-09-01&end_date=2024-09-30&commercial_acct=false

This is the what we're looking for! Brilliant! Only problem is that the entry points are listed using some sort of key instead of the actual name. Knowing 2 of 22 permits remain is useless unless I can figure out what the entry point is.

2. https://www.recreation.gov/api/permitcontent/233262

This second endpoint appears to contain all the metadata (and mapping) for a given area. 233262 appears in both, it's just some sort of permit_id value that represents Inyo National Forest. Combing through all the Inyo Metadata, I see that ['payload']['campsites'] looks to provide the mapping from entry point names to entry points. We're on a roll now!


