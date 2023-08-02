# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from src.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from src.home.models import Organization
import json

from src.home.vocabulary_model import Vocabulary
from src.home.vocabulary_service import VocabularyService
from src.home.dashboard_service import DashboardService
from src.home.weakness_service import WeaknessService
from src.home.attack_service import AttackService
from src.home.asset_service import AssetService
from src.home.product_service import ProductService
from src.home.organization_service import OrganizationService
from src.home.threat_service import ThreatService
from src.home.node_service import NodeService
from src.home.threatmodel_service import ThreatModelService
from src.home.element_service import ElementService
from src.home.recommendation_service import RecommendationService

import src.home.util as util


from flask import Flask
import traceback

import yaml

app = Flask(__name__)

@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')


@blueprint.route('/organizations', methods=['GET', 'POST'])
def organizations(): 
    try:
        organizations = None
        query = None
        if request.method == 'GET': 
            organizations = OrganizationService().load(limit=1000)
        else:
            query = request.form['query']
            organizations = OrganizationService().find(query)
        total = len(organizations[0])
        return render_template("home/organizations.html",organizations=organizations, total=total, last_query=query)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/assets', methods=['GET', 'POST'])
def assets():
    try:
        assets = None
        query = None
        if request.method == 'GET': 
            assets = AssetService().load(limit=1000)
        else:
            query = request.form['query']
            assets = AssetService().find(query)
        total = len(assets[0])
        
        return render_template("home/assets.html",assets=assets, total=total, last_query=query)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/show/<string:node_type>/<string:propertyname>/<string:id>', methods=['GET', 'POST'])
def details(node_type, propertyname, id):
    try:
        node = NodeService().find(node_type, propertyname, id)
        node_as_json = json.dumps(node)
        return render_template("home/details.html",details=node_as_json)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500
    
@blueprint.route('/products', methods=['GET', 'POST'])
def products():
    try:
        products = None
        query = None
        if request.method == 'GET': 
            products = ProductService().load(limit=1000)
        else:
            query = request.form['query']
            products = ProductService().find(query)
        total = len(products[0])
        
        return render_template("home/products.html",products=products, total=total, last_query=query)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/weakness', methods=['GET', 'POST'])
def weakness():
    try:
        weaknesses = None
        query = None
        if request.method == 'GET': 
            weaknesses = WeaknessService().load(limit=1500)
        else:
            query = request.form['query']
            weaknesses = WeaknessService().find(query)
        total = len(weaknesses[0])
        
        return render_template("home/weakness.html",weaknesses=weaknesses, total=total, last_query=query)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/weakness/attacks/<string:CWE>', methods=['GET', 'POST'])
def weakness_attacks(CWE):
    try:
        attacks = WeaknessService().find_weakness_attacks(CWE)
        total = 0
        return render_template("home/weakness_attacks.html",CWE=CWE, attacks=attacks, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500
@blueprint.route('/weakness/attacks/likelihood/<string:likelihood>', methods=['GET', 'POST'])
def weakness_by_likelihood_of_attacks(likelihood):
    try:
        weaknesses = WeaknessService().find_weakness_by_likelihood_of_attack(likelihood)
        total = 0
        return render_template("home/weakness_by_likelihood_of_attack.html",likelihood=likelihood, weaknesses=weaknesses, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500
@blueprint.route('/weakness/likelihood_of_exploits/<string:likelihood>', methods=['GET', 'POST'])
def weakness_by_likelihood_of_exploits(likelihood):
    try:
        weaknesses = WeaknessService().find_weakness_by_likelihood_of_exploits(likelihood)
        total = 0
        return render_template("home/weakness_by_likelihood_of_exploit.html",likelihood=likelihood, weaknesses=weaknesses, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/attacks', methods=['GET', 'POST'])
def attacks():
    try:
        attacks = None
        query = None
        if request.method == 'GET': 
            attacks = AttackService().load(limit=1000)
        else:
            query = request.form['query']
            attacks = AttackService().find(query)
        total = len(attacks[0])
        
        return render_template("home/attacks.html",attacks=attacks, total=total, last_query=query)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/threats', methods=['GET', 'POST'])
def threats():
    try:
        threats = None
        query = None
        if request.method == 'GET':
            threats = ThreatService().load(limit=1000)
        else:
            query = request.form['query']
            threats = ThreatService().find(query)
        total = len(threats[0])
        
        return render_template("home/threats.html",threats=threats, total=total, last_query=query)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/deletethreat/<string:ThreatID>', methods=['GET', 'POST'])
def deletethreat(ThreatID):
    try:
        threats = None
        query = None
       
        ThreatService().delete(ThreatID)
        threats = ThreatService().load(limit=1000)
        total = 0
        if threats is not None and threats[0] is not None: 
            total = len(threats[0])
        else: 
            total = 0
        return render_template("home/threats.html",threats=threats, total=total, last_query=query)


    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/createthreat', methods=['GET', 'POST'])
def createthreat():
    try:
        threats = None
        form_result=None
        if request.method == 'GET':
            form_result=None
        else:
            threatid = request.form['threatid'] 
            catalog = request.form['catalog']
            category = request.form['category']
            stride = request.form['stride']
            name = request.form['name']
            description = request.form['description']
            cve = request.form['cve']

            result = ThreatService().create(
                threatid=threatid,
                catalog=catalog,
                category=category,
                stride=stride,
                name=name,
                description=description,
                cve=cve,
            )
            form_result='Threat created with success!'

        return render_template("home/create_threat.html",form_result=form_result)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/deletethreatweakness/<string:ThreatID>/<string:CWE>', methods=['GET', 'POST'])
def deletethreatweakness(ThreatID, CWE):
    try:
        threats = None
        query = None
        total_weaknesses = WeaknessService().load(limit=1500)
        ThreatService().delete_threat_weakness(ThreatID,CWE)
        weaknesses = ThreatService().find_threat_weaknesses(ThreatID)

        total = util.safe_list_len_neomodel(weaknesses)
        return render_template("home/bindthreatweakness.html",total_weaknesses=total_weaknesses, threats=threats, weaknesses=weaknesses, ThreatID=ThreatID, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/bindthreatweakness/<string:ThreatID>', methods=['GET', 'POST'])
def bindthreatweakness(ThreatID):
    try:
        threats = None
        query = None
        total_weaknesses = WeaknessService().load(limit=1500)
        if request.method == 'GET': 
            weaknesses = ThreatService().find_threat_weaknesses(ThreatID)
        else:
            cwe = request.form['cwe']
            ThreatService().bind_threat_weakness(ThreatID,cwe)
            weaknesses = ThreatService().find_threat_weaknesses(ThreatID)
        total = util.safe_list_len_neomodel(weaknesses)
        return render_template("home/bindthreatweakness.html",total_weaknesses=total_weaknesses, threats=threats, weaknesses=weaknesses, ThreatID=ThreatID, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/deleteproductasset/<string:ProductID>/<string:AssetID>', methods=['GET', 'POST'])
def deleteproductasset(ProductID, AssetID):
    try:
        products = None
        query = None
        assets = None
        total_assets = AssetService().load(limit=1500)
        ProductService().delete_product_asset(ProductID,AssetID)
        assets = ProductService().find_product_assets(ProductID)

        total = util.safe_list_len_neomodel(assets)

        return render_template("home/bindproductasset.html",total_assets=total_assets, products=products, assets=assets, ProductID=ProductID, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/bindproductasset/<string:ProductID>', methods=['GET', 'POST'])
def bindproductasset(ProductID):
    try:
        products = None
        query = None
        assets = None
        total_assets = AssetService().load(limit=1500)
        if request.method == 'GET': 
            assets = ProductService().find_product_assets(ProductID)
        else:
            assetid = request.form['assetid']
            ProductService().bind_product_asset(ProductID,assetid)
            assets = ProductService().find_product_assets(ProductID)
            
        total = util.safe_list_len_neomodel(assets)
     
        return render_template("home/bindproductasset.html",total_assets=total_assets, products=products, assets=assets, ProductID=ProductID, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/deleteproductasset/<string:ProductID>/<string:threat_model_uid>', methods=['GET', 'POST'])
def deleteproductthreatmodel(ProductID, threat_model_uid):
    try:
        products = None
        query = None
        threatmodels = None
        full_threatmodels = ThreatModelService().load(limit=1500)
        ProductService().delete_product_threatmodel(ProductID,threat_model_uid)
        threatmodels = ProductService().find_product_threatmodels(ProductID)
        total = util.safe_list_len_neomodel(threatmodels)
        return render_template("home/bindproductthreatmodel.html",full_threatmodels=full_threatmodels, products=products, threatmodels=threatmodels, ProductID=ProductID, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/recommend_threats/<string:threat_model_uid>', methods=['GET', 'POST'])
def recommend_threats(threat_model_uid):
    try:
        recommended_threats = RecommendationService().recommendation_threats(threat_model_uid)
        
        return render_template("home/recommended_threats.html",recommended_threats=recommended_threats)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500


@blueprint.route('/bindproductthreatmodel/<string:ProductID>', methods=['GET', 'POST'])
def bindproductthreatmodel(ProductID):
    try:
        products = None
        query = None
        threatmodels = None
        full_threatmodels = ThreatModelService().load(limit=1500)
        
        if request.method == 'GET': 
            threatmodels = ProductService().find_product_threatmodels(ProductID)
        else:
            threat_model_uid = request.form['threat_model_uid']
            ProductService().bind_product_threatmodel(ProductID, threat_model_uid)
            threatmodels = ProductService().find_product_threatmodels(ProductID)
            
        total = util.safe_list_len_neomodel(threatmodels)
     
        return render_template("home/bindproductthreatmodel.html",full_threatmodels=full_threatmodels, products=products, threatmodels=threatmodels, ProductID=ProductID, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/dash', methods=['GET'])
def dash():
    try:   
        ds = DashboardService()
        counts = [ds.count_nodes('Weakness'), ds.count_nodes('Attack'), ds.count_nodes('Threat')] 
        weakness_classes = ds.count_nodes_by_property("Weakness","Abstraction","DESC")
        weakness_classes_total = sum(x[1] for x in weakness_classes)
        attack_abstractions = ds.count_nodes_by_property("Attack","Abstraction","DESC")
        attack_abstractions_total = sum(x[1] for x in attack_abstractions)
        
        threat_categories = ds.count_nodes_by_property("Threat","ThreatCategory","DESC")
        threat_categories_total = sum(x[1] for x in threat_categories)
        return render_template("home/dashboard.html",
        counts = counts, 
        weakness_classes = weakness_classes, 
        weakness_classes_total = weakness_classes_total, 
        attack_abstractions = attack_abstractions,
        attack_abstractions_total = attack_abstractions_total,
        threat_categories = threat_categories,
        threat_categories_total = threat_categories_total       
        )
    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 50


@blueprint.route('/loadvocabulary', methods=['GET'])
def get_vocabulary():
    try:
        return render_template("home/load_vocabulary.html",form_result=None)
    except:
        return render_template('home/page-500.html'), 500

@blueprint.route('/loadvocabulary', methods=['POST'])
def post_vocabulary():
    try:   
        content = request.form['content']
        VocabularyService().save(content)
        return render_template("home/load_vocabulary.html",form_result="Sucessfuly Loaded!")
    except yaml.YAMLError as e:
        print (e)
        return render_template("home/load_vocabulary.html",form_result="Loading error! ")
    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/loadthreatmodel', methods=['GET', 'POST'])
def loadthreatmodel():
    try:
        if request.method == 'GET': 
            return render_template("home/load_threatmodel.html",form_result=None)
        else:
            content = request.form['content']
            ThreatModelService().save(content)
            return render_template("home/load_threatmodel.html",form_result="Sucessfuly Loaded!")
    except yaml.YAMLError as e:
        print (e)
        return render_template("home/load_threatmodel.html",form_result="Loading error! ")
    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/threatmodel', methods=['GET', 'POST'])
def threatmodel():
    try:
        weaknesses = None
        query = None
        if request.method == 'GET': 
            threatmodels = ThreatModelService().load(limit=1500)
        else:
            query = request.form['query']
            threatmodels = ThreatModelService().find(query)

        if util.safe_is_empty_list(threatmodels) is False: 
            total = len(threatmodels[0])
        else: 
            total = 0
        
        return render_template("home/threatmodels.html",threatmodels=threatmodels, total=total, last_query=query)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/deletethreatmodel/<string:threat_model_uid>', methods=['GET', 'POST'])
def deletethreatmodel(threat_model_uid):
    try:
        threats = None
        query = None
       
        ThreatModelService().delete(threat_model_uid)
        threatmodels = ThreatService().load(limit=1000)
        total = 0
        if util.safe_is_empty_list(threatmodels) is False: 
            total = len(threatmodels[0])
        else: 
            total = 0
        return render_template("home/threatmodels.html",threatmodels=threatmodels, total=total, last_query=query)


    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/threatmodel/<string:threat_model_uid>/elements', methods=['GET', 'POST'])
def elements(threat_model_uid):
    try:
        elements = None
        query = None
        if request.method == 'GET': 
            elements = ThreatModelService().find_threatmodel_elements(threat_model_uid)
            print(elements)
        else:
            query = request.form['query']
            elements = ThreatModelService().find_threatmodel_elements_with_query(threat_model_uid, query)

        if util.safe_is_not_empty_list(elements): 
            total = len(elements[0])
        else: 
            total = 0
        
        return render_template("home/elements.html",elements=elements, total=total, last_query=query)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/bindelementthreat/<string:element_type>/<string:uid>', methods=['GET', 'POST'])
def bindthreatelement(element_type, uid):
    try:
        threats = None
        query = None
        full_threats = ThreatService().load(limit=1500)
        ThreatID = None
        if request.method == 'GET': 
            threats = ElementService().find_element_threats(element_type,uid)
            
        else:
            threatID = request.form['ThreatID']
            ElementService().bind_element_threat(element_type, uid, threatID)
            threats = ElementService().find_element_threats(element_type,uid)
      
        total = 0
        if util.safe_is_not_empty_list(threats): 
            total = len(threats[0])
        else: 
            total = 0
     
        return render_template("home/bindelementthreat.html",full_threats=full_threats, threats=threats, element_type=element_type, element_uid=uid, ThreatID=ThreatID, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/deleteelementthreat/<string:element_type>/<string:uid>/<string:ThreatID>', methods=['GET', 'POST'])
def deleteelementthreat(element_type, uid, ThreatID):
    try:
        threats = None
        query = None
        full_threats = ThreatService().load(limit=1500)
        ElementService().delete_element_threat(element_type,uid,ThreatID)
        threats = ElementService().find_element_threats(element_type,uid)

        total = 0
        if util.safe_is_not_empty_list(threats): 
            total = len(threats[0])
        else: 
            total = 0
        return render_template("home/bindelementthreat.html",full_threats=full_threats, threats=threats, element_type=element_type, element_uid=uid, ThreatID=ThreatID, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/bindelementasset/<string:element_type>/<string:uid>', methods=['GET', 'POST'])
def bindelementasset(element_type, uid):
    try:
        assets = None
        query = None
        full_assets = AssetService().load(limit=1500)
        asset_id = None
        if request.method == 'GET': 
            assets = ElementService().find_element_assets(element_type,uid)
            
        else:
            asset_id = request.form['asset_id']
            ElementService().bind_element_asset(element_type, uid, asset_id)
            assets = ElementService().find_element_assets(element_type,uid)
      
        total = 0
        if util.safe_is_not_empty_list(assets): 
            total = len(assets[0])
        else: 
            total = 0
     
        return render_template("home/bindelementasset.html",full_assets=full_assets, assets=assets, element_type=element_type, element_uid=uid, asset_id=asset_id, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/deleteelementasset/<string:element_type>/<string:uid>/<string:asset_id>', methods=['GET', 'POST'])
def deleteelementasset(element_type, uid, asset_id):
    try:
        assets = None
        query = None
        full_assets = AssetService().load(limit=1500)
        ElementService().delete_element_asset(element_type,uid,asset_id)
        assets = ElementService().find_element_assets(element_type,uid)

        total = 0
        if util.safe_is_not_empty_list(assets): 
            total = len(assets[0])
        else: 
            total = 0
        return render_template("home/bindelementasset.html",full_assets=full_assets, assets=assets, element_type=element_type, element_uid=uid, asset_id=asset_id, total=total)

    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/vocabulary', methods=['GET', 'POST'])
def vocabulary():
    try:
        threats = None
        query = None
        store_terms = VocabularyService().load(node_type='StoreTerm', limit=1000)
        dataflow_terms = VocabularyService().load(node_type='DataFlowTerm', limit=1000)
        interactor_terms = VocabularyService().load(node_type='InteractorTerm', limit=1000)
        process_terms = VocabularyService().load(node_type='ProcessTerm', limit=1000)

        
        total = 0

        return render_template(
            "home/vocabulary.html",
            store_terms=store_terms,
            dataflow_terms=dataflow_terms,
            interactor_terms=interactor_terms,
            process_terms=process_terms,
            total=total, 
            last_query=query)
    except Exception as e:
        traceback.print_exc()
        return render_template('home/page-500.html'), 500

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
