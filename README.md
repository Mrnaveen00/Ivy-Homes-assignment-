Overview

This project extracts all possible names from an autocomplete API endpoint at http://35.200.185.69:8000/v1/autocomplete. The solution uses a systematic breadth-first search approach with parallel processing while respecting the API's rate limits.
Features

    Complete Name Extraction: Recovers all available names through the autocomplete API

    Rate Limit Handling: Implements exponential backoff when rate limited

    Parallel Processing: Uses multithreading to speed up extraction

    Efficient Searching: Breadth-first search with prefix pruning

    Result Caching: Saves results to JSON file

API Discoveries

Through exploration, we discovered:

    Endpoint: /v1/autocomplete?query=<string>

    Returns max 5 suggestions per query

    Uses prefix matching (case-insensitive)

    Rate limits after ~10 rapid requests (429 status code)

    Response format:{
  "suggestions": ["name1", "name2", ...]
}


Solution Approach

    Breadth-First Search: Starts with empty prefix, expands character by character

    Parallel Processing: Uses thread pool (conservatively sized) to speed up requests

    Rate Limit Management:

        Exponential backoff when receiving 429 responses

        Delays between batches of requests

    Optimizations:

        Prunes search branches that return no results

        Deduplicates names

        Reuses HTTP session
Requirements

    Python 3.6+

    requests library
esults

After running the extraction, the script reports:

    Total names found

    Total API requests made

    Extraction time
