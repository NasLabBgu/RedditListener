# Reddit Keyword Listener

## Overview

The `RedditKeywordListener` is a Python-based application that listens to specific Reddit subreddits and fetches posts or comments containing specific keywords. It polls Reddit at regular intervals and appends any matching posts or comments to CSV files. The application uses PRAW (Python Reddit API Wrapper) to interact with the Reddit API and dynamically fetch new posts and comments.

## Features

- Search for specific **keywords** in posts and comments.
- Monitor multiple **subreddits** simultaneously.
- Fetch new posts and comments in **real-time**.
- Append fetched data to separate **CSV files** for posts and comments, stored in **organized folders**.
- **Poll Reddit** at user-defined intervals to continuously update data.

## Files

### 1. `reddit_listener.py`

This file contains the main logic for listening to Reddit posts and comments based on keywords. It:
- Initializes a Reddit client using PRAW.
- Sets up directories for storing posts and comments.
- Polls Reddit subreddits for posts and comments containing the specified keywords.
- Writes the data to CSV files.

### 2. `conf.py`

This configuration file stores the Reddit API credentials and other parameters like:
- `client_id`: Your Reddit application's client ID.
- `client_secret`: Your Reddit application's client secret.
- `user_agent`: The user agent string for your Reddit application.
- `KEYWORDS`: A list of keywords to search for.
- `SUBREDDIT_NAME`: The subreddits to listen to (can be multiple subreddits, separated by a '+' sign).
- `POLL_INTERVAL`: The time interval (in seconds) between polling Reddit for new data.
- `POSTS_FOLDER`: Folder where fetched posts are stored.
- `COMMENTS_FOLDER`: Folder where fetched comments are stored.

### 3. `main.py`

The entry point to the application. It imports the `RedditKeywordListener` from `reddit_listener.py`, creates an instance, and calls the `listen()` method to start the listener.

## Usage

1. **Install dependencies**:
   ```bash
   pip install praw
   ```

2. **Configure your Reddit API credentials**:
   In `conf.py`, set the following fields:
   - `client_id`
   - `client_secret`
   - `user_agent`
   
   Also, configure your keywords, subreddits, and polling interval.

3. **Run the application**:
   Run the `main.py` file to start listening for Reddit posts and comments based on your configuration.
   ```bash
   python main.py
   ```

4. **CSV Output**:
   - Fetched **posts** are saved in the `posts/` folder.
   - Fetched **comments** are saved in the `comments/` folder.
   - Each file is named by the date of the data collection (`YYYYMMDD.csv`).

## How It Works

- **Post and Comment Fetching**: The app fetches posts from specified subreddits, filters them based on the specified keywords, and saves them into CSV files. Similarly, it listens for comments, filters them by keywords, and saves them as well.
- **Polling**: After fetching data, the application waits for the defined polling interval before fetching again.
  
## Customization

You can customize the following parameters in the `conf.py` file:
- **KEYWORDS**: Change the list of keywords to match your interests.
- **SUBREDDIT_NAME**: Specify the subreddit(s) to monitor. Use multiple subreddits separated by a '+' (e.g., `'subreddit1+subreddit2'`).
- **POLL_INTERVAL**: Adjust the frequency of polling Reddit for new posts and comments.
