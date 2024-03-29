CONTENT_DIRECTORY = "./public/"
SAVING_DIRECTORY = "./save/"

UPGRADE_TO_HTTPS = False

import hashlib
import random
import shutil
import flask
import json
import os
import re

from DotIndex import DotIndex
from typing import Union, Callable
from flask import request, redirect
from werkzeug.middleware.proxy_fix import ProxyFix

app = flask.Flask(__name__)
app.url_map.strict_slashes = False

SOCIALS_REGEX = {
  "discord"   : re.compile(r"^(?!.*\.\.)(?=.{2,32}$)[a-z0-9_.]+$"),
  "twitter"   : re.compile(r"^(?!.*twitter)(?!.*admin)[a-z0-9_]{1,15}$", re.IGNORECASE),
  "github"    : re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?$", re.IGNORECASE),
  "twitch"    : re.compile(r"^[a-z0-9_]{4,25}$", re.IGNORECASE),
  "reddit"    : re.compile(r"^[a-z0-9_-]{3,20}$", re.IGNORECASE),
  "snapchat"  : re.compile(r"^(?=.{3,15}$)[a-z0-9]+(?:[_.-][a-z0-9]+)?$", re.IGNORECASE),
  "instagram" : re.compile(r"^[a-z0-9_.]{1,30}$", re.IGNORECASE),
  "facebook"  : re.compile(r"^([a-z0-9].*){1,50}$", re.IGNORECASE),
  "tiktok"    : re.compile(r"^[a-z0-9_.]{1,25}$", re.IGNORECASE),
  "smiggins"  : re.compile(r"^[a-z0-9_-]{1,18}$"),
  "tringl"    : re.compile(r"^[a-z0-9_]{1,24}$")
}

SOCIAL_ICONS = {
    "discord": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><path d="M524.5 69.8a1.5 1.5 0 0 0-.8-.7A485 485 0 0 0 404.1 32a1.8 1.8 0 0 0-1.9.9 338 338 0 0 0-14.9 30.6 447.8 447.8 0 0 0-134.4 0 310 310 0 0 0-15.1-30.6 1.9 1.9 0 0 0-1.9-.9 483.7 483.7 0 0 0-119.8 37.1 1.7 1.7 0 0 0-.8.7C39.1 183.7 18.2 294.7 28.4 404.4a2 2 0 0 0 .8 1.4A487.7 487.7 0 0 0 176 479.9a1.9 1.9 0 0 0 2.1-.7 348 348 0 0 0 30-48.8 1.9 1.9 0 0 0-1-2.6 321 321 0 0 1-45.9-21.9 1.9 1.9 0 0 1-.2-3.1c3.1-2.3 6.2-4.7 9.1-7.1a1.8 1.8 0 0 1 1.9-.3c96.2 43.9 200.4 43.9 295.5 0a1.8 1.8 0 0 1 1.9.2c2.9 2.4 6 4.9 9.1 7.2a1.9 1.9 0 0 1-.2 3.1 301.4 301.4 0 0 1-45.9 21.8 1.9 1.9 0 0 0-1 2.6 391 391 0 0 0 30 48.8 1.9 1.9 0 0 0 2.1.7 486 486 0 0 0 147.2-74.1 1.9 1.9 0 0 0 .8-1.4c12.2-126.7-20.6-236.8-87-334.5m-302 267.8c-29 0-52.8-26.6-52.8-59.2s23.4-59.3 52.8-59.3c29.7 0 53.3 26.8 52.8 59.2 0 32.7-23.4 59.3-52.8 59.3m195.4 0c-29 0-52.8-26.6-52.8-59.2s23.3-59.3 52.8-59.3c29.7 0 53.3 26.8 52.8 59.2 0 32.7-23.2 59.3-52.8 59.3"/></svg>',
    "facebook": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M512 256C512 114.6 397.4 0 256 0S0 114.6 0 256c0 120 82.7 220.8 194.2 248.5V334.2h-52.8V256h52.8v-33.7c0-87.1 39.4-127.5 125-127.5 16.2 0 44.2 3.2 55.7 6.4V172c-6-.6-16.5-1-29.6-1-42 0-58.2 15.9-58.2 57.2V256h83.6l-14.4 78.2H287v175.9C413.8 494.8 512 386.9 512 256"/></svg>',
    "github": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 496 512"><path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6m-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3m44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9M244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8M97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1m-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7m32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1m-11.4-14.7c-1.6 1-1.6 3.6 0 5.9s4.3 3.3 5.6 2.3c1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2"/></svg>',
    "instagram": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141m0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7m146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8m76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8M398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1"/></svg>',
    "reddit": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M373 138.6c-25.2 0-46.3-17.5-51.9-41-30.6 4.3-54.2 30.7-54.2 62.4v.2c47.4 1.8 90.6 15.1 124.9 36.3 12.6-9.7 28.4-15.5 45.5-15.5 41.3 0 74.7 33.4 74.7 74.7 0 29.8-17.4 55.5-42.7 67.5-2.4 86.8-97 156.6-213.2 156.6S45.5 410.1 43 323.4c-25.4-11.9-43-37.7-43-67.7C0 214.4 33.4 181 74.7 181c17.2 0 33 5.8 45.7 15.6 34-21.1 76.8-34.4 123.7-36.4v-.3c0-44.3 33.7-80.9 76.8-85.5C325.8 50.2 347.2 32 373 32c29.4 0 53.3 23.9 53.3 53.3s-23.9 53.3-53.3 53.3M157.5 255.3c-20.9 0-38.9 20.8-40.2 47.9s17.1 38.1 38 38.1 36.6-9.8 37.8-36.9-14.7-49.1-35.7-49.1zM395 303.1c-1.2-27.1-19.2-47.9-40.2-47.9s-36.9 22-35.7 49.1 16.9 36.9 37.8 36.9 39.3-11 38-38.1zm-60.1 70.8c1.5-3.6-1-7.7-4.9-8.1-23-2.3-47.9-3.6-73.8-3.6s-50.8 1.3-73.8 3.6c-3.9.4-6.4 4.5-4.9 8.1 12.9 30.8 43.3 52.4 78.7 52.4s65.8-21.6 78.7-52.4"/></svg>',
    "smiggins": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><path d="M320 192h17.1c22.1 38.3 63.5 64 110.9 64 11 0 21.8-1.4 32-4v228c0 17.7-14.3 32-32 32s-32-14.3-32-32V339.2L280 448h56c17.7 0 32 14.3 32 32s-14.3 32-32 32H192c-53 0-96-43-96-96V192.5c0-16.1-12-29.8-28-31.8l-7.9-1c-17.5-2.2-30-18.2-27.8-35.7S50.5 94 68 96.2l7.9 1c48 6 84.1 46.8 84.1 95.3v85.3c34.4-51.7 93.2-85.8 160-85.8m160 26.5c-10 3.5-20.8 5.5-32 5.5-28.4 0-54-12.4-71.6-32q-5.55-6.15-9.9-13.2C357.3 164 352 146.6 352 128V10.7C352 4.8 356.7.1 362.6 0h.2c3.3 0 6.4 1.6 8.4 4.2v.1l12.8 17 27.2 36.3L416 64h64l4.8-6.4L512 21.3l12.8-17v-.1c2-2.6 5.1-4.2 8.4-4.2h.2c5.9.1 10.6 4.8 10.6 10.7V128c0 17.3-4.6 33.6-12.6 47.6-11.3 19.8-29.6 35.2-51.4 42.9M432 128a16 16 0 1 0-32 0 16 16 0 1 0 32 0m48 16a16 16 0 1 0 0-32 16 16 0 1 0 0 32"/></svg>',
    "snapchat": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M496.9 366.6c-3.4-9.2-9.8-14.1-17.1-18.2-1.4-.8-2.6-1.5-3.7-1.9-2.2-1.1-4.4-2.2-6.6-3.4-22.8-12.1-40.6-27.3-53-45.4a103 103 0 0 1-9.1-16.1c-1.1-3-1-4.7-.2-6.3a10.2 10.2 0 0 1 2.9-3c3.9-2.6 8-5.2 10.7-7 4.9-3.2 8.8-5.7 11.2-7.4 9.4-6.5 15.9-13.5 20-21.3a42.4 42.4 0 0 0 2.1-35.2c-6.2-16.3-21.6-26.4-40.3-26.4a55.5 55.5 0 0 0-11.7 1.2c-1 .2-2.1.5-3.1.7.2-11.2-.1-22.9-1.1-34.5-3.5-40.8-17.8-62.1-32.7-79.2a130.2 130.2 0 0 0-33.1-26.8C309.5 23.5 283.9 17 256 17s-53.4 6.5-76 19.4a129.7 129.7 0 0 0-33.3 26.8c-14.9 17-29.2 38.4-32.7 79.2-1 11.6-1.2 23.4-1.1 34.5-1-.3-2-.5-3.1-.7a55.5 55.5 0 0 0-11.7-1.2c-18.7 0-34.1 10.1-40.3 26.4a42.4 42.4 0 0 0 2 35.2c4.1 7.8 10.7 14.7 20 21.3 2.5 1.7 6.4 4.2 11.2 7.4 2.6 1.7 6.5 4.2 10.3 6.7a11.1 11.1 0 0 1 3.3 3.3c.8 1.6.8 3.4-.4 6.6a102 102 0 0 1-8.9 15.8c-12.1 17.7-29.4 32.6-51.4 44.6-11.5 6.3-23.7 10.5-28.8 24.4-3.9 10.5-1.3 22.5 8.5 32.6a49.1 49.1 0 0 0 12.4 9.4 134.3 134.3 0 0 0 30.3 12.1 20 20 0 0 1 6.1 2.7c3.6 3.1 3.1 7.9 7.8 14.8a34.5 34.5 0 0 0 9 9.1c10 6.9 21.3 7.4 33.2 7.8 10.8.4 23 .9 36.9 5.5 5.8 1.9 11.8 5.6 18.7 9.9 16.8 10.4 39.7 24.4 78 24.4s61.3-14.1 78.1-24.4c6.9-4.2 12.9-7.9 18.5-9.8 13.9-4.6 26.2-5.1 36.9-5.5 11.9-.5 23.2-.9 33.2-7.8a34.6 34.6 0 0 0 10.2-11.2c3.4-5.8 3.3-9.9 6.6-12.8a19 19 0 0 1 5.8-2.6 135 135 0 0 0 30.7-12.2 48.3 48.3 0 0 0 13-10.2l.1-.1c9.3-9.9 11.6-21.5 7.8-31.8m-34 18.3c-20.7 11.5-34.5 10.2-45.3 17.1-9.1 5.9-3.7 18.5-10.3 23.1-8.1 5.6-32.2-.4-63.2 9.9-25.6 8.5-42 32.8-88 32.8s-62-24.3-88.1-32.9c-31-10.3-55.1-4.2-63.2-9.9-6.6-4.6-1.2-17.2-10.3-23.1-10.7-6.9-24.5-5.7-45.3-17.1-13.2-7.3-5.7-11.8-1.3-13.9 75.1-36.4 87.1-92.6 87.7-96.7.6-5 1.4-9-4.2-14.1-5.4-5-29.2-19.7-35.8-24.3-10.9-7.6-15.7-15.3-12.2-24.6 2.5-6.5 8.5-8.9 14.9-8.9a27.6 27.6 0 0 1 6 .7c12 2.6 23.7 8.6 30.4 10.2a10.7 10.7 0 0 0 2.5.3c3.6 0 4.9-1.8 4.6-5.9-.8-13.1-2.6-38.7-.6-62.6 2.8-32.9 13.4-49.2 26-63.6 6.1-6.9 34.5-37 88.9-37S339 74.3 345 81.2c12.6 14.4 23.2 30.7 26 63.6 2.1 23.9.3 49.5-.6 62.6-.3 4.3 1 5.9 4.6 5.9a10.6 10.6 0 0 0 2.5-.3c6.7-1.6 18.4-7.6 30.4-10.2a27.6 27.6 0 0 1 6-.7c6.4 0 12.4 2.5 14.9 8.9 3.5 9.4-1.2 17-12.2 24.6-6.6 4.6-30.4 19.3-35.8 24.3-5.6 5.1-4.8 9.1-4.2 14.1.5 4.2 12.5 60.4 87.7 96.7 4.3 2.3 11.8 6.8-1.4 14.2"/></svg>',
    "tiktok": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M448 209.9a210.1 210.1 0 0 1-122.8-39.3v178.8A162.6 162.6 0 1 1 185 188.3v89.9a74.6 74.6 0 1 0 52.2 71.2V0h88a121 121 0 0 0 1.9 22.2 122.2 122.2 0 0 0 53.9 80.2 121.4 121.4 0 0 0 67 20.1z"/></svg>',
    "tringl": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M512 240c0 114.9-114.6 208-256 208-37.1 0-72.3-6.4-104.1-17.9-11.9 8.7-31.3 20.6-54.3 30.6C73.6 471.1 44.7 480 16 480c-6.5 0-12.3-3.9-14.8-9.9s-1.1-12.8 3.4-17.4l.3-.3c.3-.3.7-.7 1.3-1.4 1.1-1.2 2.8-3.1 4.9-5.7 4.1-5 9.6-12.4 15.2-21.6 10-16.6 19.5-38.4 21.4-62.9C17.7 326.8 0 285.1 0 240 0 125.1 114.6 32 256 32s256 93.1 256 208"/></svg>',
    "twitch": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M391.2 103.5h-38.7v109.7h38.6zM285 103h-38.6v109.8H285zM120.8 0 24.3 91.4v329.2h115.8V512l96.5-91.4h77.3L487.7 256V0zm328.3 237.8-77.2 73.1h-77.3l-67.6 64v-64h-86.9V36.6h309z"/></svg>',
    "twitter": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M459.4 151.7c.3 4.5.3 9.1.3 13.6 0 138.7-105.6 298.6-298.6 298.6-59.5 0-114.7-17.2-161.1-47.1 8.4 1 16.6 1.3 25.3 1.3 49.1 0 94.2-16.6 130.3-44.8-46.1-1-84.8-31.2-98.1-72.8 6.5 1 13 1.6 19.8 1.6 9.4 0 18.8-1.3 27.6-3.6-48.1-9.7-84.1-52-84.1-103v-1.3c14 7.8 30.2 12.7 47.4 13.3-28.3-18.8-46.8-51-46.8-87.4 0-19.5 5.2-37.4 14.3-53C87.4 130.8 165 172.4 252.1 176.9c-1.6-7.8-2.6-15.9-2.6-24C249.5 95.1 296.3 48 354.4 48c30.2 0 57.5 12.7 76.7 33.1 23.7-4.5 46.5-13.3 66.6-25.3-7.8 24.4-24.4 44.8-46.1 57.8 21.1-2.3 41.6-8.1 60.4-16.2-14.3 20.8-32.2 39.3-52.6 54.3"/></svg>'
}

SOCIAL_INFO = {
  "discord": {
    "link": None,
    "prefix": ""
  },
  "facebook": {
    "link": "https://www.facebook.com/%q",
    "prefix": ""
  },
  "github": {
    "link": "https://github.com/%q",
    "prefix": ""
  },
  "instagram": {
    "link": "https://www.instagram.com/%q/",
    "prefix": ""
  },
  "reddit": {
    "link": "https://www.reddit.com/u/%q",
    "prefix": "/u/"
  },
  "smiggins": {
    "link": "https://trinkey.pythonanywhere.com/u/%q",
    "prefix": "@"
  },
  "snapchat": {
    "link": "https://www.snapchat.com/add/%q",
    "prefix": ""
  },
  "tiktok": {
    "link": "https://www.tiktok.com/@%q",
    "prefix": ""
  },
  "tringl": {
    "link": "https://ngl.pythonanywhere.com/m/%q",
    "prefix": "@"
  },
  "twitch": {
    "link": "https://www.twitch.tv/%q",
    "prefix": ""
  },
  "twitter": {
    "link": "https://twitter.com/%q",
    "prefix": "@"
  }
}

def validate_color(color: str) -> bool:
    if len(color) != 7 or color[0] != "#":
        return False

    for i in color[1::]:
        if i not in "abcdef0123456789":
            return False

    return True

def sort_list(l: list[list[str]], alphabetical=True) -> list[list[str]]:
    output = []
    for i in l:
        if i[0] and (not alphabetical and (i[1] in ["1", "2", "3", "4"]) or (alphabetical and i[1])):
            output.append(i)

    if alphabetical:
        return sorted(output, key=lambda x: x[1] + x[0])
    return sorted(output, key=lambda x: {"1": "d", "2": "c", "3": "b", "4": "a"}[x[1]] + x[0])

def return_dynamic_content_type(content: Union[str, bytes], content_type: str="text/html") -> flask.Response:
    response = flask.make_response(content)
    response.headers["Content-Type"] = content_type
    return response

def sha(string: Union[str, bytes]) -> str:
    if type(string) == str:
        return hashlib.sha256(str.encode(string)).hexdigest()
    elif type(string) == bytes:
        return hashlib.sha256(string).hexdigest()
    return ""

def ensure_file(path: str, *, default_value: str="", folder: bool=False) -> None:
    if os.path.exists(path):
        if folder and not os.path.isdir(path):
            os.remove(path)
            os.makedirs(path)
        elif not folder and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            f = open(path, "w")
            f.write(default_value)
            f.close()
    else:
        if folder:
            os.makedirs(path)
        else:
            f = open(path, "w")
            f.write(default_value)
            f.close()

def escape_html(string: str) -> str:
    return string.replace("&", "&amp;").replace("<", "&lt;").replace("\"", "&quot;")

def generate_token(username: str, passhash: str) -> str:
    return sha(sha(f"{username}:{passhash}") + "among us in real life, sus, sus")

def list_public(
    sort: str="random",
    page: int=0,
    limit: int=25
) -> dict:
    # Sort: "alphabetical", "random"
    # Page: for "alphabetical", page for next. 0 is first page, 1 is second...

    x = json.loads(open(f"{SAVING_DIRECTORY}public/list.json", "r").read())
    output = {
        "end": True,
        "list": []
    }

    if sort == "alphabetical":
        x = x[limit * page::]
        output["end"] = len(x) <= limit
        for i in x[:limit:]:
            q = json.loads(open(f"{SAVING_DIRECTORY}{i}.json", "r").read())
            output["list"].append({
                "colors": q["colors"],
                "display_name": q["display_name"],
                "bio": q["description"],
                "username": i
            })

    elif sort == "random":
        random.shuffle(x)
        for i in x[:limit:]:
            q = json.loads(open(f"{SAVING_DIRECTORY}{i}.json", "r").read())
            output["list"].append({
                "colors": q["colors"],
                "display_name": q["display_name"],
                "bio": q["description"],
                "username": i
            })

    return output

def create_file_serve(file) -> Callable:
    x = lambda property=None: flask.send_file(f"{CONTENT_DIRECTORY}{file}")
    x.__name__ = file
    return x

def create_folder_serve(directory) -> Callable:
    x = lambda file: flask.send_from_directory(f"{CONTENT_DIRECTORY}{directory}", file)
    x.__name__ = directory
    return x

def get_template(json, username):
    def add_to_output(starting, json, key, title):
        starting += f'<div class="added" id="{key}"><h2>{title}</h2>'
        for i in json[key]:
            starting += f"""<div {'class="accent"' if i[1] == '4' else 'style="color: var(--text-low-opacity);"' if i[1] == '1' else ''}>{icons[i[1]]} {escape_html(i[0])}</div>"""
        return starting + "</div>"

    json = DotIndex(json)

    icons = {
        "1": '<svg style="fill: var(--text-low-opacity);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M323.8 477.2c-38.2 10.9-78.1-11.2-89-49.4l-5.7-20c-3.7-13-10.4-25-19.5-35l-51.3-56.4c-8.9-9.8-8.2-25 1.6-33.9s25-8.2 33.9 1.6l51.3 56.4c14.1 15.5 24.4 34 30.1 54.1l5.7 20c3.6 12.7 16.9 20.1 29.7 16.5s20.1-16.9 16.5-29.7l-5.7-20c-5.7-19.9-14.7-38.7-26.6-55.5-5.2-7.3-5.8-16.9-1.7-24.9s12.3-13 21.3-13H448c8.8 0 16-7.2 16-16 0-6.8-4.3-12.7-10.4-15-7.4-2.8-13-9-14.9-16.7s.1-15.8 5.3-21.7c2.5-2.8 4-6.5 4-10.6 0-7.8-5.6-14.3-13-15.7-8.2-1.6-15.1-7.3-18-15.2s-1.6-16.7 3.6-23.3c2.1-2.7 3.4-6.1 3.4-9.9 0-6.7-4.2-12.6-10.2-14.9-11.5-4.5-17.7-16.9-14.4-28.8.4-1.3.6-2.8.6-4.3 0-8.8-7.2-16-16-16h-97.5c-12.6 0-25 3.7-35.5 10.7l-61.7 41.1c-11 7.4-25.9 4.4-33.3-6.7s-4.4-25.9 6.7-33.3l61.7-41.1c18.4-12.3 40-18.8 62.1-18.8H384c34.7 0 62.9 27.6 64 62 14.6 11.7 24 29.7 24 50 0 4.5-.5 8.8-1.3 13 15.4 11.7 25.3 30.2 25.3 51 0 6.5-1 12.8-2.8 18.7 11.6 11.8 18.8 27.8 18.8 45.5 0 35.3-28.6 64-64 64h-92.3c4.7 10.4 8.7 21.2 11.8 32.2l5.7 20c10.9 38.2-11.2 78.1-49.4 89zM32 384c-17.7 0-32-14.3-32-32V128c0-17.7 14.3-32 32-32h64c17.7 0 32 14.3 32 32v224c0 17.7-14.3 32-32 32H32z"/></svg>',
        "2": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M100.5 176c-29 0-52.5 23.5-52.5 52.5V320c0 13.3-10.7 24-24 24S0 333.3 0 320v-91.5C0 173 45 128 100.5 128c29.6 0 57.6 13 76.7 35.6l130.2 153.8c10 11.8 24.6 18.6 40.1 18.6 29 0 52.5-23.5 52.5-52.5V192c0-13.3 10.7-24 24-24s24 10.7 24 24v91.5C448 339 403 384 347.5 384c-29.6 0-57.6-13-76.7-35.6L140.6 194.6c-10-11.8-24.6-18.6-40.1-18.6z"/></svg>',
        "3": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M323.8 34.8c-38.2-10.9-78.1 11.2-89 49.4l-5.7 20c-3.7 13-10.4 25-19.5 35l-51.3 56.4c-8.9 9.8-8.2 25 1.6 33.9s25 8.2 33.9-1.6l51.3-56.4c14.1-15.5 24.4-34 30.1-54.1l5.7-20c3.6-12.7 16.9-20.1 29.7-16.5s20.1 16.9 16.5 29.7l-5.7 20c-5.7 19.9-14.7 38.7-26.6 55.5-5.2 7.3-5.8 16.9-1.7 24.9s12.3 13 21.3 13H448c8.8 0 16 7.2 16 16 0 6.8-4.3 12.7-10.4 15-7.4 2.8-13 9-14.9 16.7s.1 15.8 5.3 21.7c2.5 2.8 4 6.5 4 10.6 0 7.8-5.6 14.3-13 15.7-8.2 1.6-15.1 7.3-18 15.2s-1.6 16.7 3.6 23.3c2.1 2.7 3.4 6.1 3.4 9.9 0 6.7-4.2 12.6-10.2 14.9-11.5 4.5-17.7 16.9-14.4 28.8.4 1.3.6 2.8.6 4.3 0 8.8-7.2 16-16 16h-97.5c-12.6 0-25-3.7-35.5-10.7l-61.7-41.1c-11-7.4-25.9-4.4-33.3 6.7s-4.4 25.9 6.7 33.3l61.7 41.1c18.4 12.3 40 18.8 62.1 18.8H384c34.7 0 62.9-27.6 64-62 14.6-11.7 24-29.7 24-50 0-4.5-.5-8.8-1.3-13 15.4-11.7 25.3-30.2 25.3-51 0-6.5-1-12.8-2.8-18.7 11.6-11.8 18.8-27.8 18.8-45.5 0-35.3-28.6-64-64-64h-92.3c4.7-10.4 8.7-21.2 11.8-32.2l5.7-20c10.9-38.2-11.2-78.1-49.4-89zM32 192c-17.7 0-32 14.3-32 32v224c0 17.7 14.3 32 32 32h64c17.7 0 32-14.3 32-32V224c0-17.7-14.3-32-32-32H32z"/></svg>',
        "4": '<svg class="accent" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="m47.6 300.4 180.7 168.7c7.5 7 17.4 10.9 27.7 10.9s20.2-3.9 27.7-10.9l180.7-168.7c30.4-28.3 47.6-68 47.6-109.5v-5.8c0-69.9-50.5-129.5-119.4-141-45.6-7.6-92 7.3-124.6 39.9l-12 12-1-12c-32.6-32.6-79-47.5-124.6-39.9C50.5 55.6 0 115.2 0 185.1v5.8c0 41.5 17.2 81.2 47.6 109.5z"/></svg>'
    }

    styles = f"--background: {json.colors.background}; --background-low-opacity: {json.colors.background}33; --accent: {json.colors.accent}; --accent-low-opacity: {json.colors.accent}66; --text: {json.colors.text}; --text-low-opacity: {json.colors.text}88;" # type: ignore
    title = f"{escape_html(json.display_name)} (@{username})".replace("{{TEMPLATE}}", "HA" * 50) # type: ignore
    embed = f'<meta name="description" content="{json.display_name} on InfoPage"><meta name="author" content="trinkey"><meta property="og:type" content="website"><meta property="og:title" content="{json.display_name} on InfoPage"><meta property="og:description" content="{json.description}"><meta property="og:url" content="https://infopg.web.app/"><meta property="og:site_name" content="infopg.web.app"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{json.display_name} on InfoPage"><meta name="twitter:description" content="{json.description}">' # type: ignore
    inner = f'<div id="container"><h1 id="name">{escape_html(json.display_name)}</h1><div id="description">{escape_html(json.description)}</div><div id="word-container">' # type: ignore

    inner = add_to_output(inner, json, "names", "Names");
    inner = add_to_output(inner, json, "pronouns", "Pronouns");
    inner = add_to_output(inner, json, "honorifics", "Honorifics");
    inner = add_to_output(inner, json, "compliments", "Compliments");
    inner = add_to_output(inner, json, "relationship", "Relationship<br>Descriptions");

    try:
        social = json.social # type: ignore
        inner += '<div class="added" id="social"><h2>Social Links</h2>'

        for i in social:
            if SOCIAL_INFO[i[1]]["link"]:
                inner += f"<div>{SOCIAL_ICONS[i[1]]} <a href='{SOCIAL_INFO[i[1]]['link'].replace('%q', i[0])}' target='_blank'>{SOCIAL_INFO[i[1]]['prefix']}{escape_html(i[0])}</a></div>"
            else:
                inner += f"<div>{SOCIAL_ICONS[i[1]]} {SOCIAL_INFO[i[1]]['prefix']}{escape_html(i[0])}</div>"

        inner += "</div>"

    except AttributeError as e:
        print(e)

    inner += "</div>"

    return title, inner, styles, embed

def get_user_page(user):
    user = user.lower()
    x = open(f"{CONTENT_DIRECTORY}user.html", "r").read()

    try:
        user_json = json.loads(open(f"{SAVING_DIRECTORY}{user}.json", "r").read())
    except FileNotFoundError:
        return x.replace("{{TEMPLATE}}", '<h1>User not found!</h1><a href="/signup">Sign up</a> - <a href="/login">Log in</a>').replace("{{TITLE}}", "User not found - InfoPage")

    title, inner, styles, embed = get_template(user_json, user)

    return x.replace("<body", f'<body style="{styles}"') \
            .replace("{{TITLE}}", title)                 \
            .replace("<title", embed + "<title", 1)      \
            .replace("{{TEMPLATE}}", inner)              \
            .replace("HA" * 50, "{{TEMPLATE}}")

def api_account_login():
    try:
        x = json.loads(request.data)
        username = x["username"].replace(" ", "").lower()
        passhash = x["password"]
    except json.JSONDecodeError:
        flask.abort(400)
    except KeyError:
        flask.abort(400)

    if len(username) > 24 or len(username) < 1:
        flask.abort(400)

    for i in username:
        if i not in "abcdefghijklmnopqrstuvwxyz0123456789_-":
            return {
                "valid": False,
                "reason": "User doesn't exist."
            }

    try:
        open(f"{SAVING_DIRECTORY}{username}.json", "r")
    except FileNotFoundError:
        return {
            "valid": False,
            "reason": "User doesn't exist."
        }

    token = generate_token(username, passhash)

    try:
        enforced_username = open(f"{SAVING_DIRECTORY}tokens/{token}.txt", "r").read()
    except FileNotFoundError:
        return {
            "valid": False,
            "reason": "Invalid password"
        }

    if enforced_username != username:
        return {
            "valid": False,
            "reason": "Invalid password"
        }

    return {
        "valid": True,
        "token": token
    }

def api_account_signup():
    try:
        x = json.loads(request.data)
        username = x["username"].replace(" ", "").lower()
        passhash = x["password"]
    except json.JSONDecodeError:
        flask.abort(400)
    except KeyError:
        flask.abort(400)

    if len(x["username"]) > 24 or len(username) < 1:
        flask.abort(400)

    if len(passhash) != 64:
        flask.abort(400)

    for i in passhash:
        if i not in "abcdef0123456789":
            flask.abort(400)

    for i in username:
        if i not in "abcdefghijklmnopqrstuvwxyz0123456789_-":
            return {
                "valid": False,
                "reason": "Username can only contain a-z, 0-9, underscores, and hyphens."
            }

    try:
        open(f"{SAVING_DIRECTORY}{username}.json", "r")
        return {
            "valid": False,
            "reason": "Username taken."
        }
    except FileNotFoundError:
        pass

    token = generate_token(username, passhash)
    ensure_file(f"{SAVING_DIRECTORY}tokens/{token}.txt", default_value=username)
    ensure_file(f"{SAVING_DIRECTORY}{username}.json", default_value=json.dumps({
        "username": username,
        "display_name": x["username"],
        "description": "",
        "colors": {
            "accent": "#ff0000",
            "text": "#ffffff",
            "background": "#111122"
        },
        "names": [
            [x["username"], "4"]
        ],
        "pronouns": [
            ["he/him", "3"],
            ["it/its", "3"],
            ["she/her", "3"],
            ["they/them", "3"]
        ],
        "honorifics": [
            ["ma'am", "3"],
            ["madam", "3"],
            ["mir", "3"],
            ["mr.", "3"],
            ["ms.", "3"],
            ["mx.", "3"],
            ["sai", "3"],
            ["shazam", "3"],
            ["sir", "3"],
            ["zam", "3"]
        ],
        "compliments": [
            ["cute", "3"],
            ["handsome", "3"],
            ["hot", "3"],
            ["pretty", "3"],
            ["sexy", "3"]
        ],
        "relationship": [
            ["beloved", "3"],
            ["boyfriend", "3"],
            ["darling", "3"],
            ["enbyfriend", "3"],
            ["friend", "3"],
            ["girlfriend", "3"],
            ["husband", "3"],
            ["partner", "3"],
            ["wife", "3"]
        ],
        "public": False,
        "social": []
    }))

    return return_dynamic_content_type(json.dumps({
        "valid": True,
        "token": token
    }))

def api_account_info_(user):
    try:
        return return_dynamic_content_type(
            open(f"{SAVING_DIRECTORY}{user}.json").read(),
            "application/json"
        )
    except FileNotFoundError:
        flask.abort(404)

def api_account_self():
    try:
        return return_dynamic_content_type(
            open(SAVING_DIRECTORY + open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read() + ".json", 'r').read(),
            "application/json"
        )
    except FileNotFoundError:
        flask.abort(404)

def api_account_change():
    username = open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read()
    x = json.loads(request.data)

    if generate_token(username, x["current"]) != request.cookies["token"]:
        flask.abort(401)

    new = generate_token(username, x["new"])
    os.rename(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', f'{SAVING_DIRECTORY}tokens/{new}.txt')

    return {
        "token": new
    }

def api_account_delete():
    username = open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read()
    x = json.loads(request.data)

    token = generate_token(username, x["passhash"])
    if generate_token(username, x["passhash"]) != request.cookies["token"]:
        flask.abort(401)

    os.remove(f"{SAVING_DIRECTORY}tokens/{token}.txt")
    os.remove(f"{SAVING_DIRECTORY}{username}.json")

    f = json.loads(open(f"{SAVING_DIRECTORY}public/list.json", "r").read())
    if username in f:
        f.remove(username)
        g = open(f"{SAVING_DIRECTORY}public/list.json", "w")
        g.write(json.dumps(f))
        g.close()

    return "200 OK"

def api_save():
    username = open(f'{SAVING_DIRECTORY}tokens/{request.cookies["token"]}.txt', 'r').read()
    x = json.loads(request.data)

    user_data = json.loads(open(f"{SAVING_DIRECTORY}{username}.json", "r").read())

    if "display_name" in x and len(x["display_name"]) < 64 and len(x["display_name"]) > 0:
        user_data["display_name"] = x["display_name"]

    if "description" in x and len(x["description"]) < 512:
        user_data["description"] = x["description"]

    if "public" in x:
        user_data["public"] = bool(x["public"])
        public_list = json.loads(open(f"{SAVING_DIRECTORY}public/list.json", "r").read())

        if user_data["public"] and username not in public_list:
            public_list.append(username)
        elif not user_data["public"] and username in public_list:
            public_list.remove(username)

        f = open(f"{SAVING_DIRECTORY}public/list.json", "w")
        f.write(json.dumps(sorted(public_list)))
        f.close()

    if "colors" in x:
        if "accent" in x["colors"] and validate_color(x["colors"]["accent"]):
            user_data["colors"]["accent"] = x["colors"]["accent"]

        if "background" in x["colors"] and validate_color(x["colors"]["background"]):
            user_data["colors"]["background"] = x["colors"]["background"]

        if "text" in x["colors"] and validate_color(x["colors"]["text"]):
            user_data["colors"]["text"] = x["colors"]["text"]

    if "names" in x:
        names = []
        for i in x["names"]:
            if len(i) == 2 and int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                names.append(i)
        user_data["names"] = sort_list(names)

    if "pronouns" in x:
        pronouns = []
        for i in x["pronouns"]:
            if len(i) == 2 and int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                pronouns.append(i)
        user_data["pronouns"] = sort_list(pronouns)

    if "honorifics" in x:
        honorifics = []
        for i in x["honorifics"]:
            if len(i) == 2 and int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                honorifics.append(i)
        user_data["honorifics"] = sort_list(honorifics)

    if "compliments" in x:
        compliments = []
        for i in x["compliments"]:
            if len(i) == 2 and int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                compliments.append(i)
        user_data["compliments"] = sort_list(compliments)

    if "relationship" in x:
        relationship = []
        for i in x["relationship"]:
            if len(i) == 2 and int(i[1]) in [1, 2, 3, 4] and len(i[0]) > 0 and len(i[0]) < 48:
                relationship.append(i)
        user_data["relationship"] = sort_list(relationship)

    if "social" in x:
        social = []
        for i in x["social"]:
            if len(i) == 2 and i[1] in SOCIALS_REGEX and SOCIALS_REGEX[i[1]].match(i[0]):
                social.append(i)
        user_data["social"] = sort_list(social)

    f = open(f"{SAVING_DIRECTORY}{username}.json", "w")
    f.write(json.dumps(user_data))
    f.close()

    return "200 OK"

def api_browse():
    return list_public(
        request.args.get("sort"), # type: ignore
        int(request.args.get("page")) if "page" in request.args else 0 # type: ignore
    )

def home():
    if "token" not in request.cookies:
        return flask.send_file(f"{CONTENT_DIRECTORY}home.html")

    token = request.cookies['token']

    if len(token) != 64:
        return flask.send_file(f"{CONTENT_DIRECTORY}home.html")

    for i in token:
        if i not in "abcdef0123456789":
            return flask.send_file(f"{CONTENT_DIRECTORY}home.html")

    try:
        username = open(f"{SAVING_DIRECTORY}tokens/{token}.txt", "r").read()
        user_info = json.loads(open(f"{SAVING_DIRECTORY}{username}.json", "r").read())
    except FileNotFoundError:
        return flask.send_file(f"{CONTENT_DIRECTORY}home.html")

    x = open(f"{CONTENT_DIRECTORY}home.html", "r").read()
    x = x.replace("{{USERNAME}}", username)
    x = x.replace("{{DISPL_NAME}}", user_info["display_name"])
    x = x.replace("{{PUBLIC}}", "true" if "public" in user_info and user_info["public"] else "false")
    x = x.replace("{{TOTAL}}", str(len(json.loads(open(f"{SAVING_DIRECTORY}public/list.json", "r").read()))))

    return return_dynamic_content_type(x, "text/html")

ensure_file(SAVING_DIRECTORY, folder=True)
ensure_file(f"{SAVING_DIRECTORY}tokens/", folder=True)
ensure_file(f"{SAVING_DIRECTORY}public", folder=True)
ensure_file(f"{SAVING_DIRECTORY}public/list.json", default_value="[]")

app.route("/")(create_file_serve("index.html"))
app.route("/login")(create_file_serve("login.html"))
app.route("/signup")(create_file_serve("signup.html"))
app.route("/logout")(create_file_serve("logout.html"))
app.route("/browse")(create_file_serve("browse.html"))
app.route("/settings")(create_file_serve("settings.html"))

app.route("/editor")(create_file_serve("editor.html"))
app.route("/u/<path:user>")(get_user_page)
app.route("/home")(home)

app.route("/js/<path:file>")(create_folder_serve("js"))
app.route("/css/<path:file>")(create_folder_serve("css"))

app.route("/api/account/login", methods=["POST"])(api_account_login)
app.route("/api/account/signup", methods=["POST"])(api_account_signup)
app.route("/api/account/info/<path:user>", methods=["GET"])(api_account_info_)
app.route("/api/account/self", methods=["GET"])(api_account_self)
app.route("/api/account/change", methods=["POST"])(api_account_change)
app.route("/api/account/delete", methods=["DELETE"])(api_account_delete)
app.route("/api/save", methods=["PATCH"])(api_save)
app.route("/api/browse", methods=["GET"])(api_browse)

app.errorhandler(404)(create_file_serve("404.html"))

if UPGRADE_TO_HTTPS:
    app.wsgi_app = ProxyFix(app.wsgi_app)

    @app.before_request
    def enforce_https():
        if not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
