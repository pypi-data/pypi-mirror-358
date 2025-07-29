from elasticsearch import Elasticsearch
from urllib.parse import quote
import time 

# elastic_ip = '54.242.127.229' # public
# elastic_ip = '172.31.30.221' # private
def init_elastic(ip='54.242.127.229', port=9200, scheme='https', username='elastic', password='Qcq_h+10MBmO78Y-ncu9', verify_certs=False, ca_certs=None, timeout=300  # Timeout in seconds
):
    """
    Initializes and returns an Elasticsearch client connected to an Elasticsearch service.

    Parameters:
    - opensearch_ip (str): The IP address of the Elasticsearch instance.
    - port (int): The port on which the Elasticsearch service is running.
    - scheme (str): The scheme to use for connecting to Elasticsearch ('http' or 'https').
    - username (str): Username for basic authentication.
    - password (str): Password for basic authentication.
    - verify_certs (bool): Whether to verify the server's TLS certificate.
    - ca_certs (str, optional): Path to the CA bundle file used for verification. Required if verify_certs is True.

    Returns:
    Elasticsearch client object.
    """
    es = Elasticsearch(
        hosts=[{'host': ip, 'port': port, 'scheme': scheme}],
        basic_auth=(username, password),
        verify_certs=verify_certs,
        ca_certs=ca_certs  # Add this if you have a CA certificate file
    )
    """
    es = Elasticsearch(
        hosts=[{'host': ip, 'port': port, 'scheme': scheme}],
        basic_auth=(username, password),
    )
    """
    return es

def search_transcriptions_full(es, speaker, phrase, index_name='transcriptions'):
    """
    This returns the full docs (not just _source) and is used by ngrams for doc to ngram mapping.
    
    Searches the 'text' field of documents in the specified index for a given phrase.

    Parameters:
    - es: The Elasticsearch client instance.
    - phrase (str): The phrase to search for in the 'text' field.
    - index_name (str): The name of the Elasticsearch index to search.

    Returns:
    A list of documents that include the specified phrase in the 'text' field.
    """
    query = {
        "query": {
            "match": {
                "text": phrase
            }
        }
    }

    # Execute the search query
    #results = es.search(index=index_name, body=query)
    results = es.search(index="*", body=query)
    results = results['hits']['hits']

    return results

def s3_path_to_cf_path(s3_path):
  """
  output: 
  https://d1gpacof5b9lyu.cloudfront.net/HotOnes/video_data/A%20Very%20Spicy%20Holiday%20Special%20%EF%BD%9C%20Hot%20Ones-_yJq9SeGLhg/clips/131.mp4

  Out[4]: 'http://d1gpacof5b9lyu.cloudfront.net/video_data/video1/clips/clip1.mp4'
  """

  # no clip_path minus s3/bucket
  clip_path_base = '/'.join(s3_path.split('/')[3:])

  # Encode only the necessary parts of the URL
  encoded_clip_path_base = '/'.join([quote(segment) for segment in clip_path_base.split('/')])
  
  # Construct the full CloudFront URL
  cf_clip_path = f'http://d1gpacof5b9lyu.cloudfront.net/{encoded_clip_path_base}'
  return cf_clip_path

def search_transcriptions(es, channel, phrase, index_name='transcriptions', scroll_timeout='1m', size_per_page=100, exact_match=True, min_duration=0, max_duration=200):

    """
    Searches the 'text' and 'channel' fields of documents in the specified index for a given phrase and channel using the Scroll API.
    Optionally performs an exact phrase match if exact_match is True.

    Parameters:
    - es: The Elasticsearch client instance.
    - channel (str): The channel to filter by.
    - speaker (str): The speaker to filter by, or 'All speakers' to match any.
    - phrase (str): The phrase to search for in the 'text' field.
    - index_name (str): The name of the Elasticsearch index to search.
    - scroll_timeout (str): The duration each scroll request should be kept alive ('1m' for one minute).
    - size_per_page (int): Number of search hits to return per batch.
    - exact_match (bool): If True, performs an exact phrase match, otherwise a standard full-text search.

    Returns:
    A list of documents that include the specified phrase and channel in the 'text' and 'channel' fields.
    """
    query_body = {
        "bool": {
            "must": [
                {"match": {"channel": channel}}  # Filter by channel
            ]
        }
    }
    
    if exact_match:
        query_body['bool']['must'].append({"match_phrase": {"text": phrase}})
    else:
        query_body['bool']['must'].append({"match": {"text": phrase}})

    query = {
        "size": size_per_page,
        "query": query_body
    }

    # Initialize the scroll
    results = es.search(index=index_name, body=query, scroll=scroll_timeout)
    scroll_id = results['_scroll_id']
    hits = results['hits']['hits']

    # Collect all results from scroll
    all_results = []
    while hits:
        all_results.extend(hits)
        response = es.scroll(scroll_id=scroll_id, scroll=scroll_timeout)
        hits = response['hits']['hits']
        scroll_id = response['_scroll_id']
    
    # Clear the scroll when done
    es.clear_scroll(scroll_id=scroll_id)

    # Extract _source from hits and include _id
    filtered_documents = []
    for result in all_results:
        source = result['_source']
        source['_id'] = result['_id']  # Add the _id to the document
        if source['end'] - source['start'] <= max_duration:
            filtered_documents.append(source)
    return filtered_documents

def s3_paths_to_docs(es, res_json):
    """
    inputs:
    response json 

    outputs:
    response json paths replace with - shortened docs with cloudfront paths
    """
    for video_name in res_json['results'].keys():
        transcription_paths = res_json['results'][video_name]
        # get es docs from transcription paths
        docs = search_transcriptions_by_transcription_paths(es, transcription_paths)
        shortened_docs = []
        for doc in docs:
            # get length of clip, segments is a list or float
            # list
            if type(doc['segments']) is list:
                length = doc['segments'][-1]['end'] - doc['segments'][0]['start']
            else: # float, int
                length = doc['segments']['end'] - doc['segments']['start']
            shortened_docs.append({
                'clip_path': s3_path_to_cf_path(doc['clip_path']) ,
                'transcription': doc['text'],
                'length': length  # Add the calculated length to the dictionary
                # segments.end in kibana, omits index in data display
                # may be an integer not a list
            })
        res_json['results'][video_name] = shortened_docs  # Update the results with shortened_docs
    return res_json

def search_transcriptions_by_transcription_paths(es, transcription_paths, index_name='transcriptions', min_duration=0, max_duration=20):
    """
    ######
    This is not perfect in that it filters by video_title AFTER getting what could be a lot of results. Works for this stage.
    ######

    Searches the 's3_path' field of documents in the specified index for any of the given clip paths,
    ensuring the 's3_path' includes the video title.

    Parameters:
    - es: The Elasticsearch client instance.
    - clip_paths (list of str): The list of clip paths to search for in the 's3_path' field.
    - index_name (str): The name of the Elasticsearch index to search.
    - min_duration (int): Minimum duration of the clips to include.
    - max_duration (int): Maximum duration of the clips to include.

    Returns:
    A list of documents where the 's3_path' field matches any of the clip paths and includes the video title.
    """
    query = {
        "query": {
            "bool": {
                "must": [
                    {"terms": {"s3_path.keyword": transcription_paths}}
                ],
            }
        }
    }

    # Execute the search query
    results = es.search(index=index_name, body=query, size=len(transcription_paths))
    results = results['hits']['hits']
    # _source is the original document, other _* include metadata like hits, time, etc.
    results = [r['_source'] for r in results]
    return results
    # Extract _source from hits
    #filtered_results = [r['_source'] for r in results if 'video_title' in r['_source']['s3_path']]
    #return filtered_results

def search_transcriptions_by_clip_paths(es, clip_paths, index_name='transcriptions', min_duration=0, max_duration=20):
    """
    Searches the 'clip_path' field of documents in the specified index for any of the given clip paths.

    Parameters:
    - es: The Elasticsearch client instance.
    - clip_paths (list of str): The list of clip paths to search for in the 'clip_path' field. i.e. s3://cliptu/Rick Steves' Europe — Season 12 /video_data/Art of the Florentine Renaissance-qi5uyN6D97g/clips/1.mp4
    - index_name (str): The name of the Elasticsearch index to search.

    Returns:
    A list of documents where the 'clip_path' field matches any of the clip paths in the list.
    """

    query = {
        "query": {
            "bool": {
                "must": [
                    {"terms": {"clip_path.keyword": clip_paths}}
                ]
            }
        }
    }

    # Execute the search query
    results = es.search(index=index_name, body=query, size=len(clip_paths))
    results = results['hits']['hits']
    # _source is the original document, other _* include metadata like hits, time, etc.
    results = [r['_source'] for r in results]
    return results


def search_transcriptions_no_channel(es, channel, speaker, phrase, index_name='transcriptions', scroll_timeout='1m', size_per_page=100, exact_match=False):
    """
    Searches the 'text' field of documents in the specified index for a given phrase using the Scroll API.
    Optionally performs an exact phrase match if exact_match is True.

    Parameters:
    - es: The Elasticsearch client instance.
    - phrase (str): The phrase to search for in the 'text' field.
    - index_name (str): The name of the Elasticsearch index to search.
    - scroll_timeout (str): The duration each scroll request should be kept alive ('1m' for one minute).
    - size_per_page (int): Number of search hits to return per batch.
    - exact_match (bool): If True, performs an exact phrase match, otherwise a standard full-text search.

    Returns:
    A list of documents that include the specified phrase in the 'text' field.
    """
    if exact_match:
        query_type = "match_phrase"  # Use match_phrase for exact phrase matching
    else:
        query_type = "match"  # Use match for broader matching

    query = {
        "size": size_per_page,
        "query": {
            query_type: {
                "text": phrase
            }
        }
    }

    # Initialize the scroll
    results = es.search(index=index_name, body=query, scroll=scroll_timeout)
    scroll_id = results['_scroll_id']
    hits = results['hits']['hits']

    # Collect all results from scroll
    all_results = []
    while hits:
        all_results.extend(hits)
        response = es.scroll(scroll_id=scroll_id, scroll=scroll_timeout)
        hits = response['hits']['hits']
        scroll_id = response['_scroll_id']
    
    # Clear the scroll when done
    es.clear_scroll(scroll_id=scroll_id)

    # Extract _source from hits
    documents = [result['_source'] for result in all_results]
    return documents

def search_transcriptions_wild(es, speaker, phrase, index_name='transcriptions'):
  # This does not work exactly
    query = {
        "query": {
            "bool": {
                "must": [
                    {"wildcard": {"text": f"*{phrase}*"}}
                ]
            }
        }
    }

    if speaker != 'All speakers':
        query['query']['bool']['must'].append({"match": {"speaker": speaker}})

    results = es.search(index=index_name, body=query)
    return results['hits']['hits']

def get_n_transcriptions(es, channel, index_name='transcriptions', n=1000):
    """
    Fetches all transcription documents from the specified Elasticsearch index using the Scroll API,
    retrieving 'n' documents per batch and filtering by the specified channel.

    Parameters:
    - es: The Elasticsearch client instance.
    - channel (str): The channel to filter the documents by.
    - index_name (str): The name of the Elasticsearch index to search.
    - n (int): Number of documents to fetch per batch.

    Returns:
    A list of all documents in the specified index that match the given channel.
    """
    # Define the initial search query to filter by channel
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"channel": channel}}
                ]
            }
        }
    }

    # Initialize the scroll
    result = es.search(
        index=index_name,
        body=query,  # Include the query in the search request
        scroll='2m',  # Keep the search context alive for 2 minutes
        size=n  # Fetch 'n' documents at a time
    )
    scroll_id = result['_scroll_id']
    hits = result['hits']['hits']

    # Start scrolling
    while True:
        # Fetch the next batch
        result = es.scroll(scroll_id=scroll_id, scroll='2m')
        # Break the loop if no more results
        if not result['hits']['hits']:
            break
        hits.extend(result['hits']['hits'])
    
    # Close the scroll context after use
    es.clear_scroll(scroll_id=scroll_id)

    return hits

def get_all_transcriptions(es, index_name='transcriptions'):
    """
    Fetches all transcription documents from the specified Elasticsearch index using the Scroll API.

    Parameters:
    - es: The Elasticsearch client instance.
    - index_name (str): The name of the Elasticsearch index to search.

    Returns:
    A list of all documents in the specified index.
    """
    # Initialize the scroll
    result = es.search(
        index=index_name,
        scroll='2m',  # Keep the search context alive for 2 minutes
        size=1000  # Fetch 1000 documents at a time
    )
    scroll_id = result['_scroll_id']
    hits = result['hits']['hits']

    # Start scrolling
    while True:
        # Fetch the next batch
        result = es.scroll(scroll_id=scroll_id, scroll='2m')
        # Break the loop if no more results
        if not result['hits']['hits']:
            break
        hits.extend(result['hits']['hits'])
    
    # Close the scroll context after use
    es.clear_scroll(scroll_id=scroll_id)

    #return [hit['_source'] for hit in hits]
    return hits
def delete_index_contents(es, index_name):
    """
    Deletes all documents in the specified index without deleting the index itself.

    Parameters:
    - es (Elasticsearch): An instance of the Elasticsearch client.
    - index_name (str): The name of the index from which to delete all documents.

    Returns:
    The response from the Elasticsearch delete by query operation.
    """
    response = es.delete_by_query(
        index=index_name,
        body={
            "query": {
                "match_all": {}
            }
        },
        conflicts='proceed'
    )
    return response

"""
# working curl
curl -X POST "https://localhost:9200/_analyze?pretty" \
     -H 'Content-Type: application/json' \
     -u 'elastic:Qcq_h+10MBmO78Y-ncu9' \
     -d'
{
  "analyzer": "whitespace",
  "text":     "The quick brown fox."
}
' --insecure

curl -X POST "https://localhost:9200/_analyze?pretty" \
     -H 'Content-Type: application/json' \
     -u 'elastic:Qcq_h+10MBmO78Y-ncu9' \
     -d'
{
  "analyzer": "whitespace",
  "text":     "The quick brown fox."
}
' --insecure



GET /my-index-000001/_search
{
  "query": {
    "match": {
      "user.id": "kimchy"
    }
  }
}

curl -X POST "https://172.31.30.221:9200/transcriptions/_search?pretty" \
     -H 'Content-Type: application/json' \
     -u 'elastic:Qcq_h+10MBmO78Y-ncu9' \
     -d'
{
  "query": {
    "match": {
      "text": "million years ago"
    }
  }
}' --insecure > results.txt

curl -X POST "https://172.31.30.221:9200/transcriptions/_search?pretty" \
     -H 'Content-Type: application/json' \
     -u 'elastic:Qcq_h+10MBmO78Y-ncu9' \
     -d'
{
  "query": {
    "match": {
      "text": "million years ago"
    }
  },
  "size": 100
}' --insecure > results.txt


stories of depression or days of struggling to work from famous people?
"""