import requests
import random

api_url = 'https://reddit.com' 

class APIError(Exception):
    pass

def get(url, no_cache=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0',
    }
    if no_cache:
        headers['Cache-Control'] = 'private,max-age=0'
    return requests.get(api_url + url, headers=headers)

def get_hot_posts(subreddit):
    """Returns a raw JSON response containing hot posts for the specified
    subreddit from the API.
    """
    url = '/r/%s/hot.json' % subreddit
    r = get(url)
    r.raise_for_status()
    return r.json()

def extract_random_comment(post):
    """Performs an additional API query in order to extract a random post from
    a post. Post parameter should be a data field of a result of a call to
    get_hot_posts.
    """
    url = '%s.json?sort=random' % post['permalink'].rstrip('/')
    r = get(url)
    r.raise_for_status()
    j = r.json()
    comments = j[1]['data']['children']
    if len(comments) > 0:
        return random.choice(comments)
    else:
        raise APIError('The selected post doesn\'t have any comments')

def get_random_comment(subreddit):
    """Returns a text of a random comment from a specified subreddit (for
    a certain value of random).
    """
    # Get the hot posts.
    p = get_hot_posts(subreddit)
    posts = p['data']['children']
    if len(posts) == 0:
        raise APIError('This subreddit contains no posts')

    # Iterate over the random permutation of the hot posts and attempt to
    # select a random comment.
    random.shuffle(posts)
    for post in posts:
        if post['data']['num_comments'] > 0:
            try:
                c = extract_random_comment(post['data'])
                return c['data']['body']
            except APIError:
                # This will be a predicatable error: no comments (maybe they
                # were removed between queries) so we can just carry on
                pass
    raise APIError('Could not find any comments in the top posts')
