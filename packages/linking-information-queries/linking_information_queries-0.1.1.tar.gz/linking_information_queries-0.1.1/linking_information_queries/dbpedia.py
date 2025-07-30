from .helpers import get_results

def retrieve_dbpedia_url(url):
    id = url.split("=")[-1].strip()
    query_dbpedia_url = f"""SELECT ?url
        WHERE {{
            ?url dbo:wikiPageID {int(id)} .
            }}
            """
    try:
        results = get_results(query_dbpedia_url, "https://dbpedia.org/sparql/")
        for result in results["results"]["bindings"]:
            for key, value in result.items():
                dbpedia_url = value.get("value", "No DBpedia URL found")
    except:
        dbpedia_url = "No DBpedia URL found"
    return dbpedia_url