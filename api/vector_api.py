from flask import jsonify
from bson.json_util import dumps
from flask import Flask, request, jsonify
import requests
import os
import time
import re
import numpy as np
import random
import string
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
from datetime import datetime
from collections import defaultdict
from werkzeug.utils import secure_filename
import csv
import pysolr
import json
import uuid
import pandas as pd

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

EXTERNAL_API_URL = "http://pyeongyang-search-clone.qa2-sg.cld/backend/search/products"
SOLR_URL = "http://xsearch-solr-vector-2.qa2-sg.cld:8983/solr/"
SOLR_COLLECTION = "retailCollectionAlias"
SOLR_FL = "sku,score,images,name,itemSku,productImages,mediumImage"
SOLR_FQ = "{!collapse field = sku}"
MILVUS_URL = 'http://search-milvus-attu.qa2-sg.cld/api/v1/collections/l4_vector_collection/search'
mongo_client = MongoClient(
    "mongodb://xsearch_user:qW6ej1HAMh9c@central-mongo-v60-01.qa2-sg.cld:27017/xsearch?connectTimeoutMS=30000&socketTimeoutMS=30000&readPreference=secondaryPreferred")
db = mongo_client["xsearch"]
audit_collection = db["vector_ndcg_audits"]
audit_campaign_collection = db["audit_campaign_collection"]

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}


def get_search_milvus_res(vector, topK):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': '',
        'DNT': '1',
        'milvus-address': 'search-milvus:19530',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
    }

    json_data = {
        'output_fields': [
            'brandSearch',
            'salesCatalogCategoryIds',
            'merchantCode',
            'color',
            'size',
            'rating',
            'isOfficial',
            'sku',
            'modelVersion',
            'lastUpdatedTimeStamp',
            'itemSku',
        ],
        'expr': '',
        'search_params': {
            'params': '{"ef":850}',
            'anns_field': 'product_vector',
            'topk': topK,
            'metric_type': 'IP',
            'round_decimal': -1,
        },
        'vectors': [vector],
        'vector_type': 101,
    }

    response = requests.post(
        MILVUS_URL,
        headers=headers,
        json=json_data,
        verify=False,
    )

    response_json = response.json()
    if response_json["data"]["status"]["error_code"] == 'Success':
        return response_json["data"]["results"]
    return []


def get_ds_query_vector(query):
    url = "http://ds-vector-search.qa2-sg.cld/query_vector/"

    payload = json.dumps({
        "requestId": "12345",
        "query": query,
        "modelVersion": "2.0.0"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    if response_json["success"]:
        return response_json["vectorEmbedding"]
    return []


def custom_sort(item, sku_scores):
    return sku_scores.get(item["sku"], 0)


def search_pure_vector_results(search_term, topK, start, start_time):
    search_products = []
    if search_term:
        response_json = get_search_milvus_res(
            get_ds_query_vector(search_term), topK)
        skus_scores = []

        # Forming the Solr query
        solr_query_parts = []
        unique_skus = set()
        for record in response_json:
            sku = record["sku"]
            score = record["score"]

            # Append the SKU and score to the list
            if (sku not in unique_skus):
                unique_skus.add(sku)
                skus_scores.append({"sku": sku, "score": score})
        counter = 0
        for sku_score in skus_scores:
            counter += 1
            sku = sku_score["sku"]
            score = sku_score["score"]
            score_multiplier = score * 1000
            if counter <= 40:
                solr_query_part = f'{sku}^{score_multiplier}'
                solr_query_parts.append(solr_query_part)
        counter = 0
        # Combine Solr query parts with OR operator
        solr_query = ' OR '.join(solr_query_parts)
        solr_query = 'sku:(' + solr_query + ')'
        # Make a call to Solr
        solr = pysolr.Solr(f'{SOLR_URL}{SOLR_COLLECTION}')
        results = solr.search(q=solr_query, fq=SOLR_FQ, fl=SOLR_FL, rows=40)
        numFound = 0
        sku_scores_dict = {item['sku']: item['score'] for item in skus_scores}
        for i, product in enumerate(results.docs, start=1):
            rank = start + i
            sku = product.get("sku", "N/A")
            itemSku = product.get("itemSku", "N/A")
            tags = product.get("tags", [])
            name = product.get("name", "N/A")
            url = "https://www.blibli.com" + product.get("url", "")
            if product.get("productImages") is not None:
                image = "https://www.static-src.com/wcsstore/Indraprastha/images/catalog/medium/" + \
                        product.get("productImages")[0]
            else:
                image = "https://www.static-src.com/wcsstore/Indraprastha/images/catalog/medium/" + \
                        product.get("mediumImage", "")
            relevant = False
            score = sku_scores_dict.get(product.get("sku", "N/A"))
            vector_boost = None
            comment = '',
            is_paling = any("paling" in tag.lower() for tag in tags)
            is_trending = any("trending" in tag.lower() for tag in tags)
            is_pilihan_blibli = any("manual" in tag.lower() for tag in tags)
            products_items = {
                "position": rank,
                "sku": sku,
                "itemSku": itemSku,
                "name": name,
                "url": url,
                "image": image,
                "relevance": relevant,
                "comment": comment,
                "score": score,
                "vectorBoost": vector_boost,
            }
            if is_pilihan_blibli:
                products_items["tag"] = 'MANUAL_MERCHANDISED'
            if is_paling or is_trending:
                products_items["tag"] = 'TRENDING'
            search_products.append(products_items)
            numFound = results.raw_response.get("response").get("numFound")
        sorted_products = sorted(
            search_products, key=lambda x: custom_sort(x, sku_scores_dict), reverse=True)
        for i, product in enumerate(sorted_products, start=1):
            rank = start + i
            product["position"] = rank

        end_time = time.time()
        response_time = "{:.2f}".format(end_time - start_time)
        return jsonify({'responseTime': response_time, 'products': sorted_products, 'numFound': numFound})
    else:
        end_time = time.time()
        response_time = "{:.2f}".format(end_time - start_time)
        return jsonify({'responseTime': response_time, 'products': search_products, 'numFound': len(search_products)})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def replace_image_url(url):
    return url.replace(
        "https://static-uatb.gdn-app.com/wcsstore/",
        "https://www.static-src.com/wcsstore/",
    )


def calculate_ndcg(rankings, relevance):
    sorted_relevance = sorted(relevance, reverse=True)
    ideal_dcg = sum((2 ** rel - 1) / np.log2(i + 2)
                    for i, rel in enumerate(sorted_relevance))
    actual_dcg = sum((2 ** rel - 1) / np.log2(i + 2)
                     for i, rel in enumerate(relevance))
    return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0


@app.route('/relevant_counts', methods=['GET'])
def relevant_counts():
    auditor = request.args.get('auditor')
    auditors = []
    if auditor is not None:
        auditors = list(auditor)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    start_timestamp = 0
    end_timestamp = 0
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(
            end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        # Convert datetime objects to timestamps
        start_timestamp = time.mktime(start_date.timetuple())
        end_timestamp = time.mktime(end_date.timetuple())
    # Match conditions based on timestamp and auditors
    match_conditions = {}
    if start_date_str is not None and end_date_str is not None:
        match_conditions["timestamp"] = {
            "$gte": start_timestamp, "$lte": end_timestamp}
    # if auditors is not None:
    #     match_conditions["auditor"] = {"$in": auditors}
    pipeline = [
        {"$match": match_conditions},  # Added match stage
        {
            "$group": {
                "_id": {
                    "searchTerm": "$search_term",
                    "auditor": "$auditor",
                    "algo": "$algo"
                },
                "relevantCountLexical": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$search_type", "Lexical"]},
                            "$relevant_count",
                            0
                        ]
                    }
                },
                "irrelevantCountLexical": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$search_type", "Lexical"]},
                            "$irrelevant_count",
                            0
                        ]
                    }
                },
                "relevantCountHybrid": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$search_type", "Hybrid"]},
                            "$relevant_count",
                            0
                        ]
                    }
                },
                "irrelevantCountHybrid": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$search_type", "Hybrid"]},
                            "$irrelevant_count",
                            0
                        ]
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "searchTerm": "$_id.searchTerm",
                "relevantCountLexical": 1,
                "irrelevantCountLexical": 1,
                "relevantCountHybrid": 1,
                "irrelevantCountHybrid": 1,
                "auditor": "$_id.auditor"
            }
        }
    ]
    result = list(audit_collection.aggregate(pipeline))
    with open('audit-results.csv', "w", newline="") as csvfile:
        fieldnames = ["searchTerm", "relevantCountLexical", "irrelevantCountLexical",
                      "relevantCountHybrid", "irrelevantCountHybrid", "auditor"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write CSV header
        writer.writeheader()

        # Write data rows
        writer.writerows(result)

    return result


def generate_audit_campaign_id():
    return str(uuid.uuid4())


@app.route('/upload-audit-assignment', methods=['POST'])
@cross_origin()
def upload_audit_assignment():
    try:
        if request.form.get('campaignOwner') is None:
            return jsonify({'error': 'Campaign owner not set'})
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            campaign_owner = request.form.get('campaignOwner')

            # Read the Excel file into a DataFrame
            try:
                df = pd.read_excel(file_path, sheet_name='Audit')
            except Exception as excel_error:
                return jsonify({'error': f'Error reading Excel file: {str(excel_error)}'})
            audit_campaign_id = generate_audit_campaign_id()
            # Assign a unique campaign id to all rows
            df['audit_campaign_id'] = audit_campaign_id

            unique_auditors = df['Auditors'].dropna().unique()

            num_search_terms = len(df)
            num_auditors = len(unique_auditors)
            num_search_terms_per_auditor, remainder = divmod(
                num_search_terms, num_auditors)

            # Repeat each unique auditor's email to get equal distribution
            repeated_auditors = np.tile(
                unique_auditors, num_search_terms_per_auditor)

            # Append additional auditors to match the length if there's a remainder
            repeated_auditors = np.concatenate(
                [repeated_auditors, unique_auditors[:remainder]])

            # Shuffle the order if needed
            np.random.shuffle(repeated_auditors)

            # Assign the auditors based on the repetition
            df['auditor'] = repeated_auditors[:len(df)]
            df['owner'] = campaign_owner
            df['campaign_start_date'] = datetime.now()

            # Create the final structure with the specified columns
            result_df = df[[
                'audit_campaign_id',
                'search_internal_keyword',
                'auditor',
                'search_loads',
                'search_clicks',
                'ctr',
                'c1CategoryCode',
                'c2CategoryCode',
                'c3CategoryCode',
                'c3_name',
                'c3_category',
                'owner',
                'campaign_start_date',
            ]]

            # Convert the result DataFrame to a list of dictionaries
            result_data = result_df.to_dict(orient='records')
            # inserting to mongo collection
            try:
                audit_collection.insert_many(result_data)
            except Exception as e:
                print(e)
            response_data = []
            for result_dict in result_data:
                result_dict.pop('_id', None)
                response_data.append(result_dict)
            return jsonify({'message': 'File uploaded successfully',
                            'data': {'audit_campaign_id': audit_campaign_id, 'campaign_owner': campaign_owner,
                                     'data': response_data}})
        else:
            return jsonify({'error': 'Invalid file extension'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/fetch-audited-terms', methods=['GET'])
@cross_origin()
def fetch_audited_terms():
    try:
        auditor = request.args.get('auditor')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 30))

        query = {
            "auditor": auditor
        }
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(
                end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

            # Convert datetime objects to timestamps
            start_timestamp = time.mktime(start_date.timetuple())
            end_timestamp = time.mktime(end_date.timetuple())
            query["timestamp"] = {
                "$gte": start_timestamp, "$lte": end_timestamp}

        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$search_type", "audited_terms": {
                "$addToSet": "$search_term"}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
            {"$project": {"_id": 1, "audited_terms": {"$slice": [
                {"$setUnion": ["$audited_terms"]}, (page - 1) * per_page, per_page]},
                          "count": {"$size": {"$setUnion": ["$audited_terms"]}}}}
        ]
        result = list(audit_collection.aggregate(pipeline))

        return jsonify({"audited_terms": result})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/fetch-top-search-terms', methods=['GET'])
@cross_origin()
def fetch_top_search_terms():
    relevant_lexical_search_terms = list(audit_collection.find(
        {"audits.relevance": 1, "search_type": "Lexical"},
        {"search_term": 1, "_id": 0}
    ).distinct("search_term"))

    relevant_hybrid_search_terms = list(audit_collection.find(
        {"audits.relevance": 1, "search_type": "Hybrid"},
        {"search_term": 1, "_id": 0}
    ).distinct("search_term"))

    irrelevant_lexical_search_terms = list(audit_collection.find(
        {"audits.relevance": 0, "search_type": "Lexical"},
        {"search_term": 1, "_id": 0}
    ).distinct("search_term"))

    irrelevant_hybrid_search_terms = list(audit_collection.find(
        {"audits.relevance": 0, "search_type": "Hybrid"},
        {"search_term": 1, "_id": 0}
    ).distinct("search_term"))

    top_relevant_lexical_search_terms = relevant_lexical_search_terms[:10]
    top_relevant_hybrid_search_terms = relevant_hybrid_search_terms[:10]
    top_irrelevant_lexical_search_terms = irrelevant_lexical_search_terms[:10]
    top_irrelevant_hybrid_search_terms = irrelevant_hybrid_search_terms[:10]

    return jsonify({
        'topRelevantLexicalSearchTerms': top_relevant_lexical_search_terms,
        'topRelevantHybridSearchTerms': top_relevant_hybrid_search_terms,
        'topIrrelevantLexicalSearchTerms': top_irrelevant_lexical_search_terms,
        'topIrrelevantHybridSearchTerms': top_irrelevant_hybrid_search_terms
    })


@app.route('/fetch-auditors', methods=['GET'])
@cross_origin()
def fetch_auditors():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(
        end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    start_timestamp = time.mktime(start_date.timetuple())
    end_timestamp = time.mktime(end_date.timetuple())

    pipeline = [
        {
            '$match': {
                'timestamp': {
                    '$gte': start_timestamp,
                    '$lte': end_timestamp
                }
            }
        },
        {
            '$group': {
                '_id': {
                    'auditor': '$auditor',
                    'search_type': '$search_type'
                },
                'auditCount': {'$sum': 1}
            }
        },
        {
            '$project': {
                'auditor': '$_id.auditor',
                'search_type': '$_id.search_type',
                'auditCount': 1,
                '_id': 0
            }
        },
        {
            '$sort': {
                'auditCount': -1
            }
        }
    ]

    audit_counts = list(audit_collection.aggregate(pipeline))
    auditor_counts = defaultdict(
        lambda: {'total_audit': 0, 'lexical_count': 0, 'hybrid_count': 0})

    # Populate the defaultdict with counts
    for item in audit_counts:
        auditor = item['auditor']
        search_type = item['search_type']
        audit_count = item['auditCount']

        auditor_counts[auditor]['total_audit'] += audit_count

        if search_type == 'Lexical':
            auditor_counts[auditor]['lexical_count'] += audit_count
        elif search_type == 'Hybrid':
            auditor_counts[auditor]['hybrid_count'] += audit_count

    # Convert defaultdict to a list of dictionaries
    result = [{'auditor': key, **value}
              for key, value in auditor_counts.items()]

    return jsonify({'auditors': result})


@app.route('/fetch-audit', methods=['GET'])
@cross_origin()
def fetch_audit_results():
    audit_id = request.args.get('auditId')
    auditor = request.args.get('auditor')
    search_term = request.args.get('searchTerm')
    algo = request.args.get('algo')
    search_type = request.args.get('searchTsype')

    query = {}

    if audit_id:
        query['audit_id'] = audit_id

    if auditor:
        query['auditor'] = auditor

    if search_term:
        query['search_term'] = search_term

    if algo:
        query['algo'] = algo

    if search_type:
        query['search_type'] = search_type

    results = list(audit_collection.find(query))

    serializable_results = []
    for result in results:
        result_dict = dict(result)
        result_dict.pop('_id', None)
        serializable_results.append(result_dict)

    return jsonify({'results': serializable_results})


@app.route('/submit-audit', methods=['POST'])
@cross_origin()
def submit_audit():
    try:
        data = request.get_json()
        audits = data.get('audits', [])
        auditor = data.get('auditor', "Search System")
        algo = data.get('algo', '')
        search_type = data.get('searchType', '')
        page_number = int(data.get('pageNumber', '0'))
        query = data.get('searchTerm', '')
        audit_id = ''.join(random.choice(string.ascii_uppercase +
                                         string.ascii_lowercase + string.digits) for _ in range(8))
        relevant_count = 0
        irrelevant_count = 0

        search_products = []
        for i, audit in enumerate(audits, start=1):
            sku = audit.get('sku', "N/A")
            relevance = audit.get('relevance', 0)
            comment = audit.get('comment', '')
            products_items = {
                "sku": sku,
                "relevance": relevance,
                "comment": comment
            }

            search_products.append(products_items)
            if relevance == 1:
                relevant_count += 1
            else:
                irrelevant_count += 1

        relevance_scores = [audit['relevance'] for audit in audits]
        ndcg = calculate_ndcg(search_products, relevance_scores)

        audit_data = {
            'audit_id': audit_id,
            'search_term': query,
            'ndcg': ndcg,
            'auditor': auditor,
            'algo': algo,
            'search_type': search_type,
            'page_number': page_number,
            'relevant_count': relevant_count,
            'irrelevant_count': irrelevant_count,
            'audits': audits,
            'timestamp': time.time()
        }
        audit_collection.insert_one(audit_data)

        return jsonify({'audit_id': audit_id, 'search_term': query, 'ndcg': ndcg})
    except Exception as e:
        return jsonify({'error': 'Failed to parse JSON data from the request body'})


@app.route('/search', methods=['GET'])
@cross_origin()
def search_products():
    search_term = request.args.get('searchTerm')
    hybrid_query = request.args.get('hybridQuery')
    vector_query = request.args.get('vectorQuery')
    page = int(request.args.get('page', 1))
    rows = int(request.args.get('itemPerPage', 40))
    boost_value = int(request.args.get('boostValue', 3))
    top_k = int(request.args.get('topK', 800))
    max_unions = int(request.args.get('vectorUnion', 500))
    debug_vector = request.args.get('QUi58PyL')
    algo = request.args.get('algo')
    intent = request.args.get('intent', True)
    user_identifier = request.args.get('userIdentifier', '500681720')

    start = (page - 1) * rows

    params = {
        'searchTerm': search_term,
        'hybridQuery': hybrid_query,
        'showFacet': 'false',
        'channelId': 'web',
        'multiCategory': 'true',
        'intent': intent,
        'page': page,
        'start': start,
        'updateCache': 'true',
        'itemPerPage': rows,
        'boostValue': boost_value,
        'topK': top_k,
        'vectorUnion': max_unions,
        'QUi58PyL': debug_vector,
        'userIdentifier': user_identifier,
        'algo': algo
    }

    cookies = {"Blibli-Cookie-Email": "akhilesh.k@gdn-commerce.com"}
    start_time = time.time()
    response = requests.get(EXTERNAL_API_URL, params=params, cookies=cookies)
    if vector_query:
        response = search_pure_vector_results(
            search_term, 200, start, start_time)
        return response
    end_time = time.time()
    response_time = "{:.2f}".format(end_time - start_time)
    search_products = []
    num_found = None
    if response.status_code == 200:
        products = response.json().get("data", {}).get("products", [])
        for i, product in enumerate(products, start=1):
            rank = start + i
            sku = product.get("sku", "N/A")
            itemSku = product.get("itemSku", "N/A")
            tags = product.get("tags", [])
            name = product.get("name", "N/A")
            url = "https://www.blibli.com" + product.get("url", "")
            image = replace_image_url(product.get("images")[0])
            relevant = False
            score = None
            vector_boost = None
            if debug_vector:
                print(response.get("solrQuery"))
                explanation_semi_summary = product.get("debugData").get(
                    "explanationSemiSummary")
                if explanation_semi_summary is not None:
                    score = product.get("debugData").get("score")
                    for element in explanation_semi_summary:
                        if "ConstantScore" in element:
                            # Use regular expressions to find and extract the number
                            pattern = r"\d+\.\d+"
                            match = re.search(pattern, element)
                            if match:
                                number = float(match.group(0))
                                vector_boost = number
                                break
            comment = '',
            is_paling = any("paling" in tag.lower() for tag in tags)
            is_trending = any("trending" in tag.lower() for tag in tags)
            is_pilihan_blibli = any("manual" in tag.lower() for tag in tags)
            products_items = {
                "position": rank,
                "sku": sku,
                "itemSku": itemSku,
                "name": name,
                "url": url,
                "image": image,
                "relevance": relevant,
                "comment": comment,
                "score": score,
                "vectorBoost": vector_boost,
            }
            if is_pilihan_blibli:
                products_items["tag"] = 'MANUAL_MERCHANDISED'
            if is_paling or is_trending:
                products_items["tag"] = 'TRENDING'
            search_products.append(products_items)
            num_found = response.json().get("data", {}).get(
                "paging").get("total_item")
        return jsonify({'responseTime': response_time, 'products': search_products, 'numFound': num_found})
    else:
        return jsonify({'responseTime': response_time, 'products': search_products, 'numFound': len(search_products)})


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host="0.0.0.0", debug=True)
