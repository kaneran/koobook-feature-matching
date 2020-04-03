import cv2
import numpy as np
import matplotlib.pyplot as plt
from firebase import Firebase

import urllib.request

def match_captured_image_with_thumbnails(file_path):
  config = {
    "apiKey": "AIzaSyDwu5UlB1jj-rQI05L1VEKJovXYShgWRbk",
    "authDomain": "koobookandroidapp.firebaseapp.com",
    "databaseURL": "https://koobookandroidapp.firebaseio.com",
    "storageBucket": "koobookandroidapp.appspot.com"
  }

  firebase = Firebase(config)
  db = firebase.database()
  storage = firebase.storage()

  # Load photo that was captured from android device
  url = "Photos/" + file_path
  recently_captured_photo_url = storage.child(url).get_url(None)
  req = urllib.request.urlopen(recently_captured_photo_url)
  arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
  img = cv2.imdecode(arr, 0)
  height, width = img.shape[:2]
  img = cv2.resize(img, (round(width / 10), round(height / 10)), interpolation=cv2.INTER_AREA)
  # Get all thumbnail urls from firebase database
  allUrls = db.child("Book_thumbnail_urls").get()
  for i in allUrls.each():
    urls = i.item[1]

  # For each url retrieved from the database, use it to create an image via Cv2 and use it to run the brute force matching
  # Then get the top 5 matches distinace values, average it and store that along with the url in a dictionary
  top_matches_thumbnail_urls = {}

  for url in urls:
    if type(url) is str:
      req = urllib.request.urlopen(url)
      arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
      img2 = cv2.imdecode(arr, 0)
      img2 = cv2.resize(img2, (round(width / 10), round(height / 10)), interpolation=cv2.INTER_AREA)

      # Credit to Pysource for the code https://www.youtube.com/watch?v=Fe-KWKPk9Zc
      # Define detector of similarities
      orb = cv2.ORB_create()

      keypoint1, descriptor1 = orb.detectAndCompute(img, None)
      keypoint2, descriptor2 = orb.detectAndCompute(img2, None)

      # Brute Force Matching
      bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

      # Find matches and sort based on accuracy/confidence
      # The smaller the match distance, the better the match

      if (descriptor1 is None or descriptor2 is None) is False:
        matches = bf.match(descriptor1, descriptor2)
        matches = sorted(matches, key=lambda x: x.distance)
        top_matches = matches[:3]
        sum = 0
        for top_match in top_matches:
          sum += top_match.distance

        avg = sum / 3
        top_matches_thumbnail_urls[url] = avg
  top_matches_thumbnail_urls = sorted(top_matches_thumbnail_urls.items(), key=lambda x:x[1])
  top_matches_thumbnail_urls = top_matches_thumbnail_urls[:6]
  top_matches_thumbnail_urls  =dict(top_matches_thumbnail_urls)
  top_thumbnail_urls = list(top_matches_thumbnail_urls.keys())

  top_thumbnail_urls_concatanated = "#".join(top_thumbnail_urls)


  return top_thumbnail_urls_concatanated
