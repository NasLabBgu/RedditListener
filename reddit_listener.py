import praw
import time
import datetime
import os
import csv
from conf import *

class RedditKeywordListener:
    def __init__(self, keyword_search=True):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.keywords = KEYWORDS
        self.keywords_listener = keyword_search
        self.subreddits = SUBREDDIT_NAME  # This can be multiple subreddits (comma-separated)
        self.poll_interval = POLL_INTERVAL

        # Initialize the starting time with the current UTC time
        self.start_time = datetime.datetime.utcnow()

        # Create directories for posts and comments if they don't exist
        if not os.path.exists('posts'):
            os.makedirs('posts')
        if not os.path.exists('comments'):
            os.makedirs('comments')

    def _keyword_in_post(self, content):
        """Check if any of the keywords are in the content (title, body, or comment)."""
        content = content.lower()
        return any(keyword.lower() in content for keyword in self.keywords)

    def _fetch_posts(self, last_post_time):
        """Fetch posts from multiple subreddits and filter them based on keywords and time range."""
        print(f"Fetching posts from: {self.subreddits}")  # Add this line to check subreddits
        query = " OR ".join(self.keywords)
        all_matching_posts = []
        fetched_anything = False

        while True:
            if not self.keywords_listener:
                search_results = self.reddit.subreddit(self.subreddits).new(
                    limit=100
                )
            else:
                search_results = self.reddit.subreddit(self.subreddits).search(
                    query=query,
                    sort='new',
                    time_filter='day',  # Use 'day' to reduce unnecessary old posts
                    limit=100
                )

            batch_posts = []
            for post in search_results:
                post_time = datetime.datetime.utcfromtimestamp(post.created_utc)
                if last_post_time and post_time <= last_post_time:
                    continue  # Skip posts older than or equal to the last processed post
                if post_time >= self.start_time:  # Ensure posts are newer than the start time
                    batch_posts.append(post)
                    fetched_anything = True

            if not batch_posts:
                break  # Exit if no more posts are found

            all_matching_posts.extend(batch_posts)
            last_post_time = datetime.datetime.utcfromtimestamp(batch_posts[-1].created_utc)  # Update the last post timestamp

        # If nothing fetched, update the time to prevent checking the same time range again
        if not fetched_anything:
            last_post_time = datetime.datetime.utcnow()

        return all_matching_posts[::-1], last_post_time

    def _fetch_comments(self, last_comment_time):
        """Fetch comments directly from multiple subreddits, independent of posts."""
        matching_comments = []
        fetched_anything = False

        while True:
            search_results = self.reddit.subreddit(self.subreddits).comments(
                limit=100  # Reduce limit to avoid fetching too many at once
            )

            batch_comments = []
            for comment in search_results:
                comment_time = datetime.datetime.utcfromtimestamp(comment.created_utc)
                if last_comment_time and comment_time <= last_comment_time:
                    continue  # Skip comments older than or equal to the last processed comment
                if comment_time >= self.start_time:  # Ensure comments are newer than the start time
                    if self.keywords_listener and self._keyword_in_post(comment.body):
                        batch_comments.append(comment)
                    else:
                        batch_comments.append(comment)
                    fetched_anything = True

            if not batch_comments:
                break  # Exit if no more comments are found

            matching_comments.extend(batch_comments)
            last_comment_time = datetime.datetime.utcfromtimestamp(batch_comments[-1].created_utc)  # Update the last comment timestamp

        # If nothing fetched, update the time to prevent checking the same time range again
        if not fetched_anything:
            last_comment_time = datetime.datetime.utcnow()

        return matching_comments, last_comment_time

    def _write_to_csv(self, filename, data, fieldnames, folder):
        """Helper function to append data to CSV file."""
        filepath = os.path.join(folder, filename)
        file_exists = os.path.isfile(filepath)

        with open(filepath, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()  # Write header only if the file doesn't exist
            writer.writerows(data)

    def _prepare_post_data(self, post):
        """Extract relevant post data for CSV."""
        return {
            'id': post.id,
            'title': post.title,
            'selftext': post.selftext,
            'subreddit': post.subreddit.display_name,
            'url': post.url,
            'created_utc': datetime.datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            'score': post.score,
            'num_comments': post.num_comments,
            'author': str(post.author)
        }

    def _prepare_comment_data(self, comment):
        """Extract relevant comment data for CSV."""
        return {
            'id': comment.id,
            'body': comment.body,
            'subreddit': comment.subreddit.display_name,
            'created_utc': datetime.datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            'score': comment.score,
            'author': str(comment.author),
            'parent_id': comment.parent_id,
            'link_id': comment.link_id
        }

    def listen(self):
        last_post_time = datetime.datetime.utcnow()  # Initialize to track new posts
        last_comment_time = datetime.datetime.utcnow()  # Initialize to track new comments
        while True:
            current_date = datetime.datetime.utcnow().strftime('%Y%m%d')

            print(f"Checking for new posts since {last_post_time}...")
            posts, last_post_time = self._fetch_posts(last_post_time=last_post_time)
            post_data = [self._prepare_post_data(post) for post in posts]
            if post_data:
                self._write_to_csv(f'{current_date}.csv', post_data, post_data[0].keys(), 'posts')

            print(f"Checking for new comments since {last_comment_time}...")
            comments, last_comment_time = self._fetch_comments(last_comment_time=last_comment_time)
            comment_data = [self._prepare_comment_data(comment) for comment in comments]
            if comment_data:
                self._write_to_csv(f'{current_date}.csv', comment_data, comment_data[0].keys(), 'comments')

            print(f"Fetched {len(posts)} Posts")
            print(f"Fetched {len(comments)} Comments")
            print("Waiting for the next polling interval...")
            time.sleep(self.poll_interval)
